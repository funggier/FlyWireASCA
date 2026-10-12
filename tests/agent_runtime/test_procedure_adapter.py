from .conftest import api
from .test_execution import plan_for,execute

def test_child_completion_contract_is_trusted_and_shared(configuration,registry,schemas,clock):
    text="Please approve invoice I1 under its valid limit policy."
    plan,goal,context,c=plan_for(text,configuration,registry,schemas,clock)
    compiled=api("adapters.procedures").compile_procedure(plan,configuration.catalog,registry)
    from flywire_asca.procedural_memory.models import ProcedureStepKind
    definition=compiled.library.get(compiled.root_id)
    call=next(s for s in definition.steps if s.kind is ProcedureStepKind.CALL_PROCEDURE)
    child=compiled.library.get(call.callee_procedure_id)
    assert call.expected_outcome.expected_payload_ref==child.completion_outcome.expected_payload_ref
    assert "approved" not in call.expected_outcome.expected_payload_ref
    attempt=execute(plan,goal,context,c,configuration,registry)
    assert attempt.procedure_state=="COMPLETED"
    assert c.snapshot().metrics.counters["procedure_calls"]==1
