import math
import pytest
from .conftest import api

class Embedding:
    def __init__(self):self.calls=[]
    def embed(self,texts,*,deadline,cancellation):
        self.calls.append(texts)
        c=api("contracts");p=api("profile")
        vectors=tuple((1.0,)+(0.0,)*1023 for _ in texts)
        return c.EmbeddingBatch("qwen3-embedding:0.6b",p.EMBEDDING_DIGEST,1024,vectors,0,{})

def knowledge(configuration):
    e=Embedding();k=api("adapters.knowledge").KnowledgeAdapter(configuration,e)
    setup=k.setup();return k,e,setup

def control(clock):
    return api("control").RunControl.create(api("contracts").AgentRequest("development"),clock=clock)

def test_actual_searches_are_cached_only_per_run_and_share_catalog_budget(configuration,clock):
    k,e,setup=knowledge(configuration);s=api("semantics");c=control(clock)
    q=s.RetrievalQuery("invoice policy","memory",{"entity_ids":["I1"]},8)
    a=k.search(q,control=c);b=k.search(q,control=c)
    assert a.actual_queries==1 and b.cache_hits==1
    assert c.snapshot().metrics.actual_retrieval_queries==1
    assert setup.document_count<=256 and setup.document_embedding_calls==2
    other=control(clock);k.search(q,control=other)
    assert other.snapshot().metrics.actual_retrieval_queries==1
    for i in range(5):k.search(s.RetrievalQuery("catalog "+str(i),"catalog",{},8),control=c)
    assert c.snapshot().metrics.actual_retrieval_queries==6
    with pytest.raises(api("budgets").BudgetStop):
        k.search(s.RetrievalQuery("seventh","catalog",{},8),control=c)

def test_relation_direction_confidence_and_repeated_work_are_preserved(configuration,clock):
    k,_,_=knowledge(configuration);s=api("semantics");c=control(clock)
    a=k.expand(("Ada",),s.RouteDecision("DECIDED_RELATIONAL",("WORKS_AT",),True),control=c)
    assert a.paths and a.paths[0].payload["node_ids"]==("Ada","Boreal")
    reverse=k.expand(("Boreal",),s.RouteDecision("DECIDED_RELATIONAL",("WORKS_AT",),True),control=c)
    assert not reverse.paths
    low=k.expand(("Echo",),s.RouteDecision("DECIDED_RELATIONAL",("CAUSED_BY",),True),control=c)
    assert not low.paths and low.scanned_edges==1
    assert c.snapshot().metrics.relation_invocations==3
    assert c.snapshot().metrics.counters["relation_visit_events"]==4

def test_three_seeds_are_rejected_before_invocation(configuration,clock):
    k,_,_=knowledge(configuration);c=control(clock)
    with pytest.raises(ValueError):
        k.expand(("Ada","Delta","K1"),api("semantics").RouteDecision("DECIDED_RELATIONAL",("WORKS_AT",),True),control=c)
    assert c.snapshot().metrics.relation_invocations==0

def test_failed_query_keeps_unknown_scoring_but_records_known_dispatch(configuration,clock):
    k,e,_=knowledge(configuration);c=control(clock)
    def failed(*args,**kwargs):raise TimeoutError("development timeout")
    e.embed=failed
    with pytest.raises(TimeoutError):
        k.search(api("semantics").RetrievalQuery("policy","memory",{"entity_ids":["I1"]},8),control=c)
    metrics=c.snapshot().metrics
    assert metrics.actual_retrieval_queries==1
    assert metrics.reported["retrieval_queries"]==1
    assert "vectors_scored" in metrics.unavailable and "retrieval_queries" not in metrics.unavailable
    assert metrics.counters["query_embedding_calls"]==1

def test_collection_query_uses_public_entity_metadata_not_answer_ids(configuration,clock):
    k,_,_=knowledge(configuration);c=control(clock)
    batch=k.search(api("semantics").RetrievalQuery("component costs","memory",{"entity_kind":"component"},24),control=c)
    allowed={e["id"] for e in configuration.knowledge.entities if e["kind"]=="component"}
    assert batch.hits and all(set(h.entity_ids)<=allowed for h in batch.hits)
    assert batch.vectors_scored<len(configuration.knowledge.entities)+len(configuration.knowledge.facts)
