from .conftest import api
from .test_interpretation import interpret,NoBroker

def goal_context(text,schemas,clock,configuration,*,fields=None):
    goal=interpret(text,schemas,clock).goal
    entity=goal.parameters.get("entity")
    s=api("semantics");v=api("values");selected=[]
    for f in configuration.knowledge.facts:
        if f["subject"]==entity and (fields is None or f["field"] in fields):
            selected.append(s.EvidenceRecord(f["id"],v.EvidenceKind.STORED_FACT,f["id"],configuration.knowledge.snapshot_id,f))
    for p in configuration.catalog.procedures:
        if p["task"]==goal.parameters["task"]:
            selected.append(s.EvidenceRecord("catalog:"+p["id"],v.EvidenceKind.CATALOG_ENTRY,"catalog:"+p["id"],configuration.knowledge.snapshot_id,p))
    context=api("adapters.selection").assemble_context(goal,tuple(selected),(),snapshot=configuration.knowledge,capacity=24)
    return goal,context

def control(text,clock):return api("control").RunControl.create(api("contracts").AgentRequest(text),clock=clock)

def test_compatible_strategy_discovery_does_not_spend_attempt(configuration,registry,schemas,clock):
    text="Please approve invoice I1 under its valid limit policy."
    goal,context=goal_context(text,schemas,clock,configuration)
    c=control(text,clock)
    resolver=api("strategy").StrategyResolver(configuration.catalog,registry,NoBroker())
    result=resolver.resolve(goal,context,previous=None,deficits=(),control=c)
    assert result.candidate.root_ref=="approve"
    assert c.snapshot().metrics.strategy_attempts==0

def test_finite_composition_has_no_stored_complete_root(configuration,registry,schemas,clock):
    text="Sort 13, 2 and 7 ascending and give the sum."
    goal,context=goal_context(text,schemas,clock,configuration)
    candidate=api("strategy").StrategyResolver(configuration.catalog,registry,NoBroker()).resolve(
        goal,context,previous=None,deficits=(),control=control(text,clock)).candidate
    assert candidate.root_ref is None
    assert {s.capability_id for s in candidate.steps}=={"sort","sum"}
