"""Semantic discovery, finite composition and charged closed plan validation."""
from collections.abc import Mapping
import uuid
from .values import TaskKind,EffectClass,EvidenceKind,ModelPurpose,canonical_bytes,fingerprint
from .plans import ActionProposal,PlanStep,ValueBinding,Resolution,ValidatedPlan,PlanValidation
from .semantics import Deficit
from .budgets import Resource,BudgetStop
from .capabilities import bound_fact
from .broker import strict_json_object
from .prompts import render_role_prompt

def execution_permit_key(plan,goal,context):
    return fingerprint((plan,goal,context))

def charge_candidate(control):
    control.check_dispatch()
    r=control.ledger.reserve(Resource.STRATEGY_ATTEMPTS,1)
    control.ledger.reconcile(r,1);control.ledger.record("strategy_attempts")

def parse_plan_proposal(raw):
    if not isinstance(raw,Mapping):raise ValueError("plan object")
    kind=raw.get("type")
    if kind=="stored-root":
        if set(raw)!={"type","root","bindings"}:raise ValueError("closed stored root schema")
        return ActionProposal("plan:"+str(uuid.uuid4()),0,(),raw["bindings"],raw["root"])
    if kind=="bounded-steps":
        if set(raw)!={"type","steps","bindings"}:raise ValueError("closed finite plan schema")
        steps=[]
        for step in raw["steps"]:
            if not isinstance(step,Mapping) or set(step)!={"id","capability","version","inputs"}:
                raise ValueError("closed step schema")
            if not isinstance(step["inputs"],Mapping):raise ValueError("inputs object")
            inputs={}
            for name,binding in step["inputs"].items():
                if not isinstance(binding,Mapping) or set(binding) not in ({"source","value"},{"source","reference"}):
                    raise ValueError("typed value binding")
                inputs[name]=ValueBinding(**dict(binding))
            steps.append(PlanStep(step["id"],step["capability"],step["version"],inputs))
        return ActionProposal("plan:"+str(uuid.uuid4()),0,tuple(steps),raw["bindings"])
    raise ValueError("finite plan or stored root required")

def root_layout(catalog,root):
    by_id={r["id"]:r for r in catalog.procedures};output=[];max_depth=1
    def walk(identifier,path):
        nonlocal max_depth
        if identifier in path or len(path)>=8:raise ValueError("procedure recursion/depth")
        if identifier not in by_id:raise ValueError("unknown root")
        path=path+(identifier,);max_depth=max(max_depth,len(path))
        for index,(op,args) in enumerate(by_id[identifier]["steps"],1):
            if op=="call":walk(args,path)
            else:
                inputs={k:ValueBinding("request",v[1:]) if isinstance(v,str) and v.startswith("$")
                        else ValueBinding("literal",value=v) for k,v in args.items()}
                local="s"+str(index)
                output.append((PlanStep("/".join(path)+"::"+local,op,by_id[identifier]["version"],inputs),path,local))
                if len(output)>32:raise ValueError("procedure primitive bound")
    walk(root,())
    if len({s.step_id for s,_,_ in output})!=len(output):
        raise ValueError("ambiguous legacy primitive ownership")
    return tuple(output),max_depth

def source_value(goal,context,registry):
    source=goal.parameters.get("source",{})
    if "literal" in source:return source["literal"]
    if "entity" in source:return bound_fact(context,registry,source["entity"],source["field"])
    if "collection" in source:
        rows=[]
        for entity in registry.configuration.knowledge.entities:
            if entity["kind"]!=source["collection"]:continue
            row={"name":entity["name"]}
            for fact in registry.configuration.knowledge.facts:
                if fact["subject"]==entity["id"]:
                    row[fact["field"]]=bound_fact(context,registry,entity["id"],fact["field"])
            rows.append(row)
        return tuple(rows)
    raise ValueError("source binding")

def _root_fits(root,goal,catalog):
    task=goal.parameters.get("task")
    descriptor=next((d for d in catalog.descriptors if d.root_ref==root),None)
    if descriptor is None or descriptor.goal_compatibility.get("task")!=task or goal.kind.value not in descriptor.task_kinds:
        return False
    layout,_=root_layout(catalog,root)
    effects={"pack":{"status"},"seal":{"sealed"},"approve":{"status"},"calibrate":{"calibrated"},
             "ready":{"ready"},"reconcile":{"quantity","checked"},"package":{"package"}}
    covered=set().union(*(effects.get(s.capability_id,set()) for s,_,_ in layout))
    required={p.arguments["field"] for p in goal.predicates if "field" in p.arguments}
    return bool(required) and required<=covered

def _binding_check(value,bindings,context,seen):
    if not isinstance(value,ValueBinding):raise ValueError("typed binding required")
    if value.source=="step" and value.reference not in seen:raise ValueError("forward step reference")
    if value.source=="request" and value.reference not in bindings:raise ValueError("unavailable request binding")
    if value.source=="context":
        match=next((i for i in context.items if value.reference in (i.evidence_id,i.origin_id)),None)
        if match is None or match.kind is EvidenceKind.HYPOTHESIS:raise ValueError("unavailable factual binding")
    if len(canonical_bytes(value))>65536:raise ValueError("binding byte bound")

def validate_plan(proposal,goal,context,*,catalog,registry,control):
    charge_candidate(control)
    try:
        if not isinstance(proposal,ActionProposal):raise ValueError("typed proposal")
        if proposal.root_ref is not None:
            if proposal.steps or not _root_fits(proposal.root_ref,goal,catalog):raise ValueError("root goal compatibility")
            layout,depth=root_layout(catalog,proposal.root_ref)
            steps=tuple(s for s,_,_ in layout)
            if set(proposal.bindings)!={"entity"} or proposal.bindings["entity"]!=goal.parameters.get("entity"):
                raise ValueError("root parameter binding")
        else:
            steps=proposal.steps;depth=1
        if not steps or len(steps)>control.profile.actions_per_attempt or depth>control.profile.call_depth:
            raise ValueError("finite action/depth bound")
        seen=set()
        for step in steps:
            descriptor=registry.get(step.capability_id,step.capability_version)
            if descriptor.effect_class not in goal.effect_scope:raise ValueError("goal effect scope")
            required=set(descriptor.input_schema["required"]);optional={"field"} if step.capability_id in ("filter","sort") else set()
            if set(step.inputs)-required or required-set(step.inputs)-optional:raise ValueError("input schema")
            for binding in step.inputs.values():_binding_check(binding,proposal.bindings,context,seen)
            seen.add(step.step_id)
        if len(steps)+control.ledger.snapshot().action_reservations>control.profile.actions:
            raise BudgetStop(message="remaining action budget")
        plan=ValidatedPlan(proposal,goal.goal_id,registry.fingerprint,len(steps),depth)
        # One successful validation grants one execution, not unlimited reuse.
        if not hasattr(control,"validation_permits"):control.validation_permits={}
        key=execution_permit_key(plan,goal,context);control.validation_permits[key]=control.validation_permits.get(key,0)+1
        return PlanValidation(plan)
    except (ValueError,TypeError,KeyError,RecursionError) as exc:
        return PlanValidation(rejection="INVALID_PLAN",deficits=(Deficit("INVALID_PLAN",explanation=str(exc)),))

class StrategyResolver:
    def __init__(self,catalog,registry,broker):self.catalog=catalog;self.registry=registry;self.broker=broker
    def resolve(self,goal,context,*,previous,deficits,control):
        control.check_dispatch()
        candidates=[]
        repair=previous is not None and any(d.kind in ("PRECONDITION_UNSATISFIED","OBSERVED_MISMATCH","INVALID_PLAN") for d in deficits)
        visible={i.payload.get("id") for i in context.items if i.kind is EvidenceKind.CATALOG_ENTRY}
        for descriptor in self.catalog.descriptors:
            if descriptor.root_ref not in visible:continue
            if repair and descriptor.root_ref==previous.root_ref:continue
            if _root_fits(descriptor.root_ref,goal,self.catalog):
                coverage=sum(any(i.payload.get("field")==ref for i in context.items)
                             for ref in descriptor.evidence_requirements)
                candidates.append((-coverage,descriptor.cost,descriptor.strategy_id,descriptor))
        control.ledger.record("strategy_candidates_considered",len(candidates))
        if candidates:
            chosen=min(candidates,key=lambda c:c[:3])[-1]
            return Resolution(ActionProposal("plan:"+str(uuid.uuid4()),0,(),
                                               {"entity":goal.parameters["entity"]},chosen.root_ref))
        try:
            composed=None if repair and previous.steps else self._compose(goal,context)
            if composed:return Resolution(composed)
        except ValueError as exc:
            if str(exc)=="NO_VALID_PLAN":return Resolution(deficits=(Deficit("NO_VALID_PLAN"),))
        purpose=ModelPurpose.PLAN_REPAIR if previous is not None else ModelPurpose.PLAN_PROPOSAL
        prompt=render_role_prompt(purpose,{"goal":goal,"context":context,"deficits":deficits,
                                          "capabilities":tuple(self.registry.descriptors.values())})
        proposed=self.broker.generate(purpose,prompt,control=control,max_output_tokens=1024)
        if proposed.error:return Resolution(deficits=(Deficit(proposed.error),))
        try:
            return Resolution(parse_plan_proposal(strict_json_object(proposed.response.content)))
        except (ValueError,TypeError,KeyError):
            charge_candidate(control)
            return Resolution(deficits=(Deficit("INVALID_PLAN",explanation="malformed model candidate"),))
    def _compose(self,goal,context):
        steps=[];bindings={};task=goal.parameters["task"]
        def literal(value):return ValueBinding("literal",value=value)
        def add(cap,inputs):
            identifier="s"+str(len(steps)+1);steps.append(PlanStep(identifier,cap,"1",inputs))
            return ValueBinding("step",identifier)
        if task=="transform":
            values=source_value(goal,context,self.registry)
            bindings["source_values"]=values;current=ValueBinding("request","source_values")
            for operation in goal.parameters["operations"]:
                op=operation["op"];args={"items":current}
                if op=="filter":args.update(field=literal(operation.get("field")),op=literal(operation["comparison"]),value=literal(operation["value"]))
                elif op=="sort":args["field"]=literal(operation.get("field"))
                elif op=="group":args.update(key=literal(operation["key"]),value=literal(operation["value"]))
                elif op=="format":args["separator"]=literal(operation["separator"])
                elif op=="select":args["fields"]=literal(operation["fields"])
                current=add(op,args)
        elif task in ("set","state_range"):
            entity=goal.parameters["entity"];field=goal.parameters["field"]
            if task=="state_range":
                lo,hi=goal.parameters["min"],goal.parameters["max"]
                if lo>hi:raise ValueError("NO_VALID_PLAN")
                value=literal(lo)
            else:
                requested=goal.parameters["value"]
                value=add("sum",{"items":literal(requested["sum"])}) if isinstance(requested,Mapping) else literal(requested)
            add("set",{"entity":literal(entity),"field":literal(field),"value":value})
            if task=="set" and isinstance(goal.parameters["value"],Mapping) and "verify" in goal.parameters["value"]:
                add("assert",{"actual":value,"op":literal("eq"),"value":literal(goal.parameters["value"]["verify"])})
        elif task=="fact":
            entity,field=goal.parameters["entity"],goal.parameters["field"]
            item=next((i for i in context.items if i.payload.get("subject")==entity and i.payload.get("field")==field),None)
            if item is None:return None
            current=ValueBinding("context",item.evidence_id)
            add("assert",{"actual":current,"op":literal("eq"),"value":current})
        elif task=="relation":
            paths=tuple(i for i in context.items if i.payload.get("record_kind")=="path")
            if not paths:return None
            bindings["paths"]=tuple(p.payload for p in paths)
            current=ValueBinding("request","paths")
            add("assert",{"actual":current,"op":literal("eq"),"value":current})
        if not steps:return None
        return ActionProposal("plan:"+str(uuid.uuid4()),0,tuple(steps),bindings)
