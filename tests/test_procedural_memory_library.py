import pytest

from flywire_asca.contracts import ObservationKind, ProcedureRef
from flywire_asca.procedural_memory import (
    ExpectedOutcome,
    ProcedureDefinition,
    ProcedureLibrary,
    ProcedureStep,
    ProcedureStepKind,
    canonical_explanation_memory_ids,
    canonical_primitive_step_path,
    flatten_procedure,
)


def exp(eid, payload, kind=ObservationKind.RESULT):
    return ExpectedOutcome(eid, kind, payload)


def proc(pid, steps, done, explanations=()):
    return ProcedureDefinition(ProcedureRef(pid, pid, "1", explanations), tuple(steps), done)


def action(step_id, action_ref, payload="ok", explanations=()):
    return ProcedureStep(step_id, ProcedureStepKind.ACTION, exp(f"e-{step_id}", payload), explanations, action_ref=action_ref)


def call(step_id, callee, payload, eid=None):
    return ProcedureStep(step_id, ProcedureStepKind.CALL_PROCEDURE, exp(eid or f"e-{step_id}", payload), callee_procedure_id=callee)


def test_library_lookup_call_contract_and_missing_callee():
    child = proc("child", [action("a", "act", "child-ok")], exp("child-done", "child-ready"))
    root = proc("root", [call("c", "child", "child-ready", "parent-own-id")], exp("root-done", "root-ready"))
    lib = ProcedureLibrary((root, child))
    assert lib.get("child") == child
    with pytest.raises(ValueError, match="unknown procedure_id"):
        lib.get("missing")

    bad_root = proc("bad-root", [call("c", "child", "wrong")], exp("root-done", "root-ready"))
    with pytest.raises(ValueError, match="completion_outcome"):
        ProcedureLibrary((bad_root, child))

    missing = proc("missing-root", [call("c", "not-there", "x")], exp("d", "x"))
    with pytest.raises(ValueError, match="callee"):
        ProcedureLibrary((missing,))


def test_library_rejects_duplicate_ids_and_recursion():
    leaf = proc("leaf", [action("a", "act")], exp("d", "done"))
    with pytest.raises(ValueError, match="procedure_id"):
        ProcedureLibrary((leaf, leaf))

    direct = proc("direct", [call("c", "direct", "done")], exp("d", "done"))
    with pytest.raises(ValueError, match="recursion"):
        ProcedureLibrary((direct,))

    a = proc("a", [call("ab", "b", "b-done")], exp("a-d", "a-done"))
    b = proc("b", [call("ba", "a", "a-done")], exp("b-d", "b-done"))
    with pytest.raises(ValueError, match="recursion"):
        ProcedureLibrary((a, b))


def test_static_depth_counts_root_as_one_and_rejects_nine():
    defs = []
    for i in range(8, 0, -1):
        pid = f"p{i}"
        done = exp(f"d{i}", f"done-{i}")
        if i == 8:
            steps = [action("a", "act")]
        else:
            steps = [call("c", f"p{i+1}", f"done-{i+1}")]
        defs.append(proc(pid, steps, done))
    lib = ProcedureLibrary(tuple(reversed(defs)), max_call_depth=8)
    assert lib.static_call_depth("p1") == 8

    p9 = proc("p0", [call("c", "p1", "done-1")], exp("d0", "done-0"))
    with pytest.raises(ValueError, match="max_call_depth"):
        ProcedureLibrary(tuple(reversed(defs)) + (p9,), max_call_depth=8)


def test_flatten_preserves_order_paths_and_canonical_provenance():
    grand = proc(
        "grand",
        [action("g1", "grand-act", explanations=("step-grand",))],
        exp("gd", "grand-done"),
        ("mem-grand",),
    )
    child = proc(
        "child",
        [action("c1", "child-act"), call("cg", "grand", "grand-done")],
        exp("cd", "child-done"),
        ("mem-child", "shared"),
    )
    root = proc(
        "root",
        [action("r1", "root-act"), call("rc", "child", "child-done"), action("r2", "root-last")],
        exp("rd", "root-done"),
        ("mem-root", "shared"),
    )
    lib = ProcedureLibrary((root, child, grand))
    flat = flatten_procedure(lib, "root")
    assert [x.action_ref for x in flat] == ["root-act", "child-act", "grand-act", "root-last"]
    assert [x.primitive_step_path for x in flat] == [
        "root::r1",
        "root/child::c1",
        "root/child/grand::g1",
        "root::r2",
    ]
    assert flat[2].call_path == ("root", "child", "grand")
    assert flat[2].explanation_memory_ids == ("mem-root", "shared", "mem-child", "mem-grand", "step-grand")
    assert canonical_primitive_step_path(("root", "child"), "c1") == "root/child::c1"
    assert canonical_explanation_memory_ids(lib, ("root", "child", "grand"), grand.steps[0]) == flat[2].explanation_memory_ids
    assert flatten_procedure(lib, "root") == flat


def test_provenance_rejects_invalid_call_path():
    child = proc("child", [action("a", "act")], exp("cd", "child-done"))
    root = proc("root", [action("r", "root-act")], exp("rd", "root-done"))
    lib = ProcedureLibrary((root, child))
    with pytest.raises(ValueError, match="call_path"):
        canonical_explanation_memory_ids(lib, ("root", "child"), child.steps[0])
