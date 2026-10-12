from .conftest import api

class NoBroker:
    def generate(self,*args,**kwargs):raise AssertionError("rule path called broker")

def test_hybrid_router_query_only_and_once_per_run(clock,monkeypatch):
    import flywire_asca.structural_routing.runner as legacy
    original=legacy.run_structural_routing;seen=[]
    def spy(request,**kwargs):
        seen.append((request,kwargs["policy"]))
        return original(request,**kwargs)
    monkeypatch.setattr(legacy,"run_structural_routing",spy)
    request=api("contracts").AgentRequest("Where does Ada work currently, according to the recorded relation?","same","en")
    control=api("control").RunControl.create(request,clock=clock)
    router=api("adapters.routing").RoutingAdapter(NoBroker())
    a=router.route(request,control=control);b=router.route(request,control=control)
    assert a==b and a.relational and len(seen)==1
    assert seen[0][1].value=="HYBRID_RULE_THEN_MODEL"
    assert seen[0][0].query_text==request.text
    assert control.run_id in seen[0][0].request_id
    assert set(seen[0][0].__dataclass_fields__)=={"request_id","query_text","language_hint"}

def test_model_error_is_not_a_decided_negative(clock,monkeypatch):
    import flywire_asca.structural_routing.runner as legacy
    from flywire_asca.structural_routing.models import StructuralRoutingResult,RoutingInferenceStatus,RoutingInferenceSource
    from flywire_asca.relational_activation.models import StructuralNeed
    def failure(request,**kwargs):
        return StructuralRoutingResult(request.request_id,kwargs["policy"],
            RoutingInferenceStatus.MODEL_ERROR,RoutingInferenceSource.FAIL_CLOSED,StructuralNeed(),False)
    monkeypatch.setattr(legacy,"run_structural_routing",failure)
    request=api("contracts").AgentRequest("development relation")
    control=api("control").RunControl.create(request,clock=clock)
    route=api("adapters.routing").RoutingAdapter(NoBroker()).route(request,control=control)
    assert route.status=="MODEL_ERROR" and not route.relational
