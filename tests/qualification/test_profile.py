import hashlib
import json
from pathlib import Path
import pytest
from flywire_asca.qualification.profile import EXPECTED_PROFILE_SHA256, FrozenProfile, load_frozen_profile
from flywire_asca.qualification.records import QualificationError

ROOT = Path(__file__).resolve().parents[2]
PROFILE = ROOT / "docs/development/qualification/a011-v0x-profile-v1.json"


def reviewed_values():
    plan = (ROOT / "docs/superpowers/plans/2026-10-10-a011-asca-v0x-qualification.md").read_text(encoding="utf-8")
    appendix = plan.split("## Appendix A:", 1)[1]
    return json.loads(appendix.split("```json\n", 1)[1].split("\n```", 1)[0])


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def paths(value, prefix=()):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from paths(child, prefix + (key,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from paths(child, prefix + (index,))
    else:
        yield prefix


def test_reviewed_profile_hash_is_literal_and_exact():
    raw = PROFILE.read_bytes()
    assert len(raw) == 7481
    assert EXPECTED_PROFILE_SHA256 == "add06f285bf6decc7d492b987d3769dc64db4cb3d0177c8c6586d50ee5f6d46d"
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_PROFILE_SHA256
    assert raw == canonical(reviewed_values())
    profile = load_frozen_profile(raw)
    assert profile.raw == raw and profile.sha256 == EXPECTED_PROFILE_SHA256
    with pytest.raises(TypeError):
        profile.values["embedding"]["dimension"] = 1


@pytest.mark.parametrize("path", list(paths(reviewed_values())), ids=lambda p: ".".join(map(str,p)))
def test_every_frozen_identity_mutation_is_rejected(path):
    value = reviewed_values()
    node = value
    for key in path[:-1]:
        node = node[key]
    original = node[path[-1]]
    node[path[-1]] = original + 1 if type(original) in (int, float) else str(original) + "-drift"
    with pytest.raises(QualificationError) as exc:
        load_frozen_profile(canonical(value))
    assert exc.value.code == "PROFILE_DRIFT"


def test_profile_bytes_cannot_bless_changed_values(tmp_path):
    value = reviewed_values()
    value["research_outcomes"]["A010"] = "SUPPORTED"
    copy = tmp_path / "profile.json"
    copy.write_bytes(canonical(value))
    with pytest.raises(QualificationError) as exc:
        load_frozen_profile(copy.read_bytes())
    assert exc.value.code == "PROFILE_DRIFT"
    with pytest.raises(QualificationError):
        FrozenProfile(copy.read_bytes(), hashlib.sha256(copy.read_bytes()).hexdigest(), value)


@pytest.mark.parametrize("mutation", ["unknown", "bool", "nan", "duplicate", "newline"])
def test_profile_rejects_unknown_keys_bool_dimension_and_nonfinite_threshold(mutation):
    value = reviewed_values()
    if mutation == "unknown":
        value["extra"] = True
    elif mutation == "bool":
        value["embedding"]["dimension"] = True
    elif mutation == "nan":
        value["a005_threshold"] = float("nan")
    raw = canonical(value)
    if mutation == "duplicate":
        raw = b'{"schema_version":1,' + raw[1:]
    elif mutation == "newline":
        raw += b"\n"
    with pytest.raises(QualificationError) as exc:
        load_frozen_profile(raw)
    assert exc.value.code == "PROFILE_DRIFT"
