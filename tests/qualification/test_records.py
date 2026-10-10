from dataclasses import FrozenInstanceError, replace
import pytest
from flywire_asca.qualification.records import FrozenCheck, GateStatus, PhysicalEnvironment, QualificationError


def test_records_deep_copy_and_freeze_nested_values():
    value = {"items": [{"dimension": 1024}]}
    record = FrozenCheck("copy", value, value, GateStatus.PASS, ("raw/x.json",))
    value["items"][0]["dimension"] = 9
    assert record.expected["items"][0]["dimension"] == 1024
    with pytest.raises(TypeError):
        record.expected["items"][0]["dimension"] = 2
    with pytest.raises(FrozenInstanceError):
        record.identity = "mutated"


@pytest.mark.parametrize("value", [True, 1.2, "2", -1])
def test_artifact_counts_require_nonnegative_exact_int(make_pack, value):
    with pytest.raises(QualificationError):
        replace(make_pack().artifact_index[0], byte_length=value)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), {1: "invalid"}])
def test_json_values_are_finite_with_string_keys(value):
    with pytest.raises(QualificationError):
        FrozenCheck("invalid", value, None, GateStatus.FAIL, ())


def test_primitive_types_are_not_coerced(make_pack):
    with pytest.raises(QualificationError):
        replace(make_pack(), schema_version=True)
    with pytest.raises(QualificationError):
        replace(make_pack().gates[0], exit_code=True)
