from .conftest import api
from .test_knowledge_adapter import knowledge,control

def test_single_best_is_used_without_fake_relation_vector_scores(configuration,clock,monkeypatch):
    k,_,_=knowledge(configuration);s=api("semantics");c=control(clock)
    batch=k.search(s.RetrievalQuery("policy","memory",{"entity_ids":["I1"]},8),control=c)
    import flywire_asca.selective_activation.baselines as legacy
    original=legacy.select_single_best;calls=[]
    def spy(*args,**kwargs):calls.append(kwargs["budget"]);return original(*args,**kwargs)
    monkeypatch.setattr(legacy,"select_single_best",spy)
    adapter=api("adapters.selection").SelectionAdapter()
    selected=adapter.select((batch,),capacity=8)
    assert selected and len(calls)==1
    assert calls[0].max_relation_hops==0 and calls[0].max_expansions==0
    assert calls[0].max_model_input_tokens==0

def test_atomic_proof_overflow_and_distinct_names(configuration,clock):
    k,_,_=knowledge(configuration);s=api("semantics")
    relation=k.expand(("S1",),s.RouteDecision("DECIDED_RELATIONAL",("PART_OF",),True),control=control(clock))
    deep=tuple(path for path in relation.paths if len(path.payload["edge_ids"])==2)
    g=s.GoalContract("dev",api("values").TaskKind.RELATION,{"entity":"S1"},
       (s.GoalPredicate("p",api("values").PredicateOperator.RELATION_PATH,{"entity":"S1","relation":"PART_OF","top_level":True}),),
       ("relation:S1:PART_OF",))
    adapter=api("adapters.selection")
    small=adapter.assemble_context(g,(),deep,snapshot=configuration.knowledge,capacity=8)
    assert not small.coverage.required_relation_complete and small.deficits
    assert not any(item.kind==api("values").EvidenceKind.RELATION_PATH for item in small.items)
    large=adapter.assemble_context(g,(),deep,snapshot=configuration.knowledge,capacity=16)
    assert large.coverage.required_relation_complete
    assert len(large.items)>8
    assert all(i.kind!=api("values").EvidenceKind.VECTOR_HIT for i in large.items)
    assert len({e["id"] for e in configuration.knowledge.entities if e["name"]=="Alex"})==2

def test_detached_path_endpoint_fails_provenance_before_coverage(configuration,clock):
    from dataclasses import replace
    k,_,_=knowledge(configuration);sem=api("semantics");v=api("values")
    path=k.expand(("Ada",),sem.RouteDecision("DECIDED_RELATIONAL",("WORKS_AT",),True),control=control(clock)).paths[0]
    payload=dict(path.payload);payload["node_ids"]=("Ada","Aero")
    forged=replace(path,payload=payload)
    goal=sem.GoalContract("dev",v.TaskKind.RELATION,{"entity":"Ada"},
        (sem.GoalPredicate("p",v.PredicateOperator.RELATION_PATH,{"entity":"Ada","relation":"WORKS_AT"}),),
        ("relation:Ada:WORKS_AT",))
    context=api("adapters.selection").assemble_context(goal,(),(forged,),snapshot=configuration.knowledge,capacity=16)
    assert not context.coverage.required_relation_complete
    assert any(d.kind=="PROVENANCE_INVALID" for d in context.deficits)
