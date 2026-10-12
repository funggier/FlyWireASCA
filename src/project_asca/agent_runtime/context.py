"""Bounded selective acquisition owned by the new top-level runtime."""
from .values import TaskKind
from .semantics import RetrievalQuery,Deficit,WorkingContext
from .budgets import Resource,IntegrityStop

class ContextAcquirer:
    def __init__(self,retrieval,relations,routing,selection,broker,*,snapshot=None):
        self.retrieval=retrieval;self.relations=relations;self.routing=routing
        self.selection=selection;self.broker=broker;self.snapshot=snapshot
    def acquire(self,goal,request,*,previous,deficits,control):
        control.check_dispatch()
        snapshot=self.snapshot
        if snapshot is None:raise IntegrityStop(message="configured knowledge snapshot required")
        resource=control.ledger.reserve(Resource.CONTEXT_ROUNDS,1)
        control.ledger.reconcile(resource,1);control.ledger.record("context_rounds")
        round_number=control.ledger.snapshot().counters["context_rounds"]
        control.query_round_id=control.run_id+":context:"+str(round_number)
        capacity=min(control.profile.context_items,8 if previous is None else min(24,8*round_number))
        if previous is not None and not deficits and not previous.deficits:capacity=min(8,control.profile.context_items)
        source=goal.parameters.get("source",{})
        self_contained=(goal.kind is TaskKind.TRANSFORM and "literal" in source) or (
                        goal.kind is TaskKind.STATE_GOAL and goal.parameters.get("task") in ("set","state_range"))
        if self_contained:
            context=self.selection.assemble(goal,(),(),snapshot=snapshot,capacity=capacity)
            self._account(context,control);return context
        queries=[]
        entity=goal.parameters.get("entity") or source.get("entity")
        filters={"entity_ids":(entity,)} if entity else ({"entity_kind":source["collection"]} if "collection" in source else {})
        text=request.text
        if deficits:
            refs=tuple(ref for d in deficits for ref in d.required_refs)
            if refs:text+=" "+" ".join(refs)
        queries.append(RetrievalQuery(text,"memory",filters,capacity))
        if goal.kind is TaskKind.STATE_GOAL:
            queries.append(RetrievalQuery(request.text,"catalog",{"task":goal.parameters["task"]},capacity))
        batches=tuple(self.retrieval.search(q,control=control) for q in queries)
        selected=self.selection.select(batches,capacity=capacity)
        if previous:
            new_ids={i.evidence_id for i in selected}
            selected+=tuple(i for i in previous.items if i.evidence_id not in new_ids and
                            i.kind.value not in ("USER_INPUT","RELATION_PATH"))
        paths=()
        if goal.kind is TaskKind.RELATION:
            route=self.routing.route(request,control=control)
            if route.status not in ("DECIDED_RELATIONAL","DECIDED_NON_RELATIONAL"):
                context=self.selection.assemble(goal,selected,(),snapshot=snapshot,capacity=capacity)
                context=WorkingContext(context.context_id,context.snapshot_id,context.items,context.coverage,
                    context.deficits+(Deficit("ROUTING_UNRESOLVED",explanation=route.status),))
                self._account(context,control);return context
            if route.relational:
                seeds=(entity,) if entity else ()
                if seeds:paths=self.relations.expand(seeds,route,control=control).paths
        context=self.selection.assemble(goal,selected,paths,snapshot=snapshot,capacity=capacity)
        self._account(context,control);return context
    @staticmethod
    def _account(context,control):
        if len(context.items)>control.profile.context_items or context.canonical_bytes>control.profile.context_bytes:
            raise IntegrityStop(message="working context exceeds profile")
        control.ledger.peak("active_context_peak",len(context.items))
        control.ledger.peak("active_context_bytes_peak",context.canonical_bytes)
        control.event("context",{"context_fingerprint":context.fingerprint,"items":len(context.items),
                                "bytes":context.canonical_bytes,"deficits":tuple(d.kind for d in context.deficits)})
