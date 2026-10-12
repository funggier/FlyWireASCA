"""A006 SINGLE_BEST for vector evidence; separate atomic heterogeneous merger."""
from dataclasses import replace
from ..values import EvidenceKind,TaskKind,fingerprint,canonical_bytes
from ..semantics import EvidenceRecord,EvidenceCoverage,WorkingContext,Deficit
from flywire_asca.contracts import ActivationBudget
from flywire_asca.contracts.enums import MemoryKind
from flywire_asca.vector_memory.models import VectorMemoryHit,VectorMemoryResult
from flywire_asca.selective_activation.models import SelectiveRetrievalEvidence
from flywire_asca.selective_activation import baselines

class SelectionAdapter:
    def select(self,batches,*,capacity):
        evidence=[];records={};catalog=[];by_query={}
        for batch in batches:
            for hit in batch.hits:
                if hit.evidence.kind is EvidenceKind.CATALOG_ENTRY:
                    catalog.append(hit);continue
                by_query.setdefault(hit.query_id,{}).setdefault(hit.evidence.evidence_id,hit)
                records[hit.evidence.evidence_id]=hit.evidence
        for query,hits in sorted(by_query.items()):
            items=tuple(hits.values());first=items[0]
            local=tuple(VectorMemoryHit(h.evidence.evidence_id,h.similarity,MemoryKind.SEMANTIC,
                                       h.evidence.payload.get("confidence",.9),(h.evidence.origin_id,),
                                       h.entity_ids,(),()) for h in items)
            result=VectorMemoryResult(query,local,len(local),len(local),len(local),len(local),len(local),
                                      first.embedding_name,first.embedding_digest,first.embedding_profile)
            evidence.append(SelectiveRetrievalEvidence(query,result))
        selected=[]
        if evidence:
            budget=ActivationBudget(max_memory_nodes=max(1,capacity),max_working_set_items=max(1,capacity),
                                    max_relation_hops=0,max_expansions=0,max_model_input_tokens=0)
            result=baselines.select_single_best(tuple(evidence),budget=budget)
            selected=[records[e.ref_id] for e in result.working_set.entries]
        unique={}
        for hit in sorted(catalog,key=lambda h:(-h.similarity,h.evidence.evidence_id)):
            unique.setdefault(hit.evidence.evidence_id,hit.evidence)
        return tuple(unique.values())+tuple(selected)
    @staticmethod
    def assemble(goal,selected,paths,*,snapshot,capacity):
        return assemble_context(goal,selected,paths,snapshot=snapshot,capacity=capacity)

def _goal_items(goal,snapshot):
    sid=snapshot.snapshot_id
    items=[EvidenceRecord("goal-frame:"+goal.goal_id,EvidenceKind.USER_INPUT,goal.goal_id,sid,
                          {"record_kind":"goal","parameters":goal.parameters,"predicates":goal.predicates})]
    for i,span in enumerate(goal.parameters.get("spans",())):
        items.append(EvidenceRecord("input-binding:"+goal.goal_id+":"+str(i),EvidenceKind.USER_INPUT,goal.goal_id,sid,
                                    {"record_kind":"request_binding","binding":span}))
    return items

def _proof_valid(path,snapshot):
    try:
        p=path.payload;nodes=p["node_ids"];edges=p["edge_ids"];records=p["records"]
        if (path.snapshot_id!=snapshot.snapshot_id or not edges or len(nodes)!=len(edges)+1
            or len(set(nodes))!=len(nodes) or len(set(edges))!=len(edges)
            or tuple(r.evidence_id for r in records)!=path.constituent_ids):
            return False
        entities={e["id"]:e for e in snapshot.entities};edge_table={e["id"]:e for e in snapshot.edges}
        authoritative={}
        for node in nodes:
            authoritative["node:"+node]=(node,{"record_kind":"node",**dict(entities[node])})
        evidence_ids=[]
        for i,identifier in enumerate(edges):
            edge=edge_table[identifier]
            if edge["source"]!=nodes[i] or edge["target"]!=nodes[i+1] or edge["confidence"]<.5:return False
            authoritative["edge:"+identifier]=(identifier,{"record_kind":"edge",**dict(edge)})
            eid="evidence:"+identifier;evidence_ids.append(eid)
            authoritative[eid]=(identifier,{"record_kind":"edge_evidence","id":eid,"edge_id":identifier,
                                           "confidence":edge["confidence"],"version":edge["version"]})
        if set(p["evidence_ids"])!=set(evidence_ids) or set(authoritative)!=set(path.constituent_ids):return False
        for record in records:
            origin,payload=authoritative[record.evidence_id]
            if (record.snapshot_id!=snapshot.snapshot_id or record.origin_id!=origin
                or record.kind is not EvidenceKind.RELATION_PATH
                or canonical_bytes(record.payload)!=canonical_bytes(payload)):
                return False
        return True
    except (KeyError,TypeError,ValueError):
        return False

def assemble_context(goal,selected,paths,*,snapshot,capacity):
    if not 1<=capacity<=24:raise ValueError("context capacity")
    items=_goal_items(goal,snapshot);dropped=[];chosen_paths=[]
    if len(items)>capacity or len(canonical_bytes(items))>16000:
        return WorkingContext("context:"+fingerprint(goal),snapshot.snapshot_id,(),
            EvidenceCoverage(goal.required_evidence,(),False),(Deficit("CONTEXT_CAPACITY",explanation="goal/bindings overflow"),))
    seen={i.evidence_id for i in items}
    paths=list(paths)
    if goal.parameters.get("top_level") and paths:
        longest=max(len(p.payload["edge_ids"]) for p in paths)
        paths=[p for p in paths if len(p.payload["edge_ids"])==longest]
    for path in paths:
        records=tuple(path.payload.get("records",()))
        if not _proof_valid(path,snapshot):
            dropped.append(Deficit("PROVENANCE_INVALID",explanation="incomplete proof records"));continue
        wrapper=replace(path,payload={k:v for k,v in path.payload.items() if k!="records"})
        additions=[r for r in records+(wrapper,) if r.evidence_id not in seen]
        if len(items)+len(additions)>capacity or len(canonical_bytes(items+additions))>15500:
            dropped.append(Deficit("CONTEXT_CAPACITY",(path.evidence_id,),explanation="atomic proof overflow"));continue
        items+=additions;seen.update(r.evidence_id for r in additions);chosen_paths.append(wrapper)
    task=goal.parameters.get("task")
    ordered=sorted(enumerate(selected),key=lambda iv:(0 if iv[1].kind is EvidenceKind.CATALOG_ENTRY and iv[1].payload.get("id")==task
                       else 1 if iv[1].kind is EvidenceKind.CATALOG_ENTRY else 2,iv[0]))
    for _,record in ordered:
        if record.evidence_id in seen:continue
        if record.snapshot_id!=snapshot.snapshot_id:
            dropped.append(Deficit("PROVENANCE_INVALID",(record.evidence_id,)));continue
        if len(items)>=capacity or len(canonical_bytes(items+[record]))>15500:
            dropped.append(Deficit("CONTEXT_CAPACITY",(record.evidence_id,),explanation="selection drop"));continue
        items.append(record);seen.add(record.evidence_id)
    satisfied=[]
    for reference in goal.required_evidence:
        if reference.startswith("relation:"):
            _,entity,relation=reference.split(":",2)
            edge_by_id={e["id"]:e for e in snapshot.edges}
            if any(p.payload["node_ids"][0]==entity and all(edge_by_id[e]["relation"]==relation
                   for e in p.payload["edge_ids"]) for p in chosen_paths):satisfied.append(reference)
        elif reference.startswith("collection:"):
            kind=reference.split(":",1)[1]
            entity_ids={e["id"] for e in snapshot.entities if e["kind"]==kind}
            required={(e,f["field"]) for e in entity_ids for f in snapshot.facts if f["subject"]==e}
            actual={(i.payload.get("subject"),i.payload.get("field")) for i in items}
            if required<=actual:satisfied.append(reference)
        else:
            entity,field=reference.rsplit(".",1)
            if any(i.payload.get("subject")==entity and i.payload.get("field")==field and
                   i.payload.get("confidence",0)>=.5 and i.kind in (EvidenceKind.VECTOR_HIT,EvidenceKind.STORED_FACT)
                   for i in items):satisfied.append(reference)
    missing=tuple(r for r in goal.required_evidence if r not in satisfied)
    if missing:dropped.append(Deficit("MISSING_EVIDENCE",missing))
    relation_complete=goal.kind is TaskKind.RELATION and all(r in satisfied for r in goal.required_evidence)
    coverage=EvidenceCoverage(goal.required_evidence,tuple(satisfied),relation_complete)
    identity=fingerprint({"goal":goal.goal_id,"items":items,"capacity":capacity})
    return WorkingContext("context:"+identity,snapshot.snapshot_id,tuple(items),coverage,tuple(dropped))
