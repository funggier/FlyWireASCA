from .conftest import api
from .test_interpretation import interpret,NoBroker

class Forbidden:
    def __getattr__(self,name):raise AssertionError("self-contained task touched "+name)

def test_self_contained_transform_has_zero_query_and_router_calls(configuration,schemas,clock):
    request=api("contracts").AgentRequest("Add 18, 4 and 9.")
    control=api("control").RunControl.create(request,clock=clock)
    goal=interpret(request.text,schemas,clock).goal
    acquirer=api("context").ContextAcquirer(Forbidden(),Forbidden(),Forbidden(),
           api("adapters.selection").SelectionAdapter(),NoBroker(),snapshot=configuration.knowledge)
    context=acquirer.acquire(goal,request,previous=None,deficits=(),control=control)
    assert context.coverage.complete
    assert control.snapshot().metrics.actual_retrieval_queries==0
    assert control.snapshot().metrics.relation_invocations==0

def test_knowledge_path_never_calls_incidentally_loaded_legacy_fixture_builders(configuration,schemas,clock,monkeypatch):
    import sys
    from .test_knowledge_adapter import knowledge
    from .test_routing_adapter import NoBroker as RoutingNoBroker
    def denied(*args,**kwargs):raise AssertionError("legacy fixture behavior was called")
    patched=0
    for name,module in tuple(sys.modules.items()):
        if name.startswith("flywire_asca.") and "benchmark" in name and module is not None:
            for binding in tuple(vars(module)):
                if binding.startswith("build_") and ("fixture" in binding or "benchmark" in binding):
                    monkeypatch.setattr(module,binding,denied);patched+=1
    k,_,_=knowledge(configuration)
    request=api("contracts").AgentRequest("Please approve invoice I1 under its valid limit policy.")
    control=api("control").RunControl.create(request,clock=clock)
    goal=interpret(request.text,schemas,clock).goal
    acquisition=api("context").ContextAcquirer(k,k,api("adapters.routing").RoutingAdapter(RoutingNoBroker()),
        api("adapters.selection").SelectionAdapter(),NoBroker(),snapshot=configuration.knowledge)
    context=acquisition.acquire(goal,request,previous=None,deficits=(),control=control)
    assert patched>0 and context.coverage.complete
    assert control.snapshot().metrics.actual_retrieval_queries==2
