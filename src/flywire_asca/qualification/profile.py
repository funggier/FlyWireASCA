"""Reviewed literal profile trust anchor; no runtime blessing or generation."""
from dataclasses import dataclass
import hashlib
import json
from collections.abc import Mapping

from .manifest import json_value, strict_json_object
from .records import JsonObject, PHYSICAL_GATE_IDS, PORTABLE_GATE_IDS, QualificationError, freeze_json

EXPECTED_PROFILE_SHA256 = "add06f285bf6decc7d492b987d3769dc64db4cb3d0177c8c6586d50ee5f6d46d"
EXPECTED_PROTECTED_SHA256 = "8df49f05fe54de43667ab2f8ef5de2caae9376ffedf2cb8f8d26f0e4abcca6b6"
DEFAULT_PROFILE_PATH = "docs/development/qualification/a011-v0x-profile-v1.json"


def _validated_values(raw):
    if type(raw) is not bytes or len(raw) != 7481 or hashlib.sha256(raw).hexdigest() != EXPECTED_PROFILE_SHA256:
        raise QualificationError("PROFILE_DRIFT", "Profile bytes differ from the independently reviewed anchor")
    try:
        values = strict_json_object(raw)
        canonical = json.dumps(values, ensure_ascii=False, sort_keys=True,
                               separators=(",", ":"), allow_nan=False).encode("utf-8")
        if canonical != raw or type(values["schema_version"]) is not int or values["schema_version"] != 1:
            raise ValueError("Profile is not canonical schema v1")
        if (tuple(values["portable_gate_ids"]) != PORTABLE_GATE_IDS or
            tuple(values["physical_gate_ids"]) != PHYSICAL_GATE_IDS or
            values["protected_source"]["sha256"] != EXPECTED_PROTECTED_SHA256 or
            type(values["embedding"]["dimension"]) is not int):
            raise ValueError("Profile vocabulary/type differs")
        # The literal byte anchor validates every reviewed key/value, including nested
        # schemas, policies, threshold, counts, fingerprints, paths and semantic digests.
        return freeze_json(values)
    except (QualificationError, ValueError, KeyError, TypeError) as exc:
        raise QualificationError("PROFILE_DRIFT", f"Invalid frozen profile: {exc}") from exc


@dataclass(frozen=True)
class FrozenProfile:
    raw: bytes
    sha256: str
    values: JsonObject

    def __post_init__(self):
        checked = _validated_values(self.raw)
        if type(self.sha256) is not str or self.sha256 != EXPECTED_PROFILE_SHA256:
            raise QualificationError("PROFILE_DRIFT", "FrozenProfile hash differs")
        if not isinstance(self.values, Mapping) or json_value(freeze_json(self.values)) != json_value(checked):
            raise QualificationError("PROFILE_DRIFT", "FrozenProfile values differ from its anchored bytes")
        object.__setattr__(self, "values", checked)


def load_frozen_profile(raw):
    values = _validated_values(raw)
    return FrozenProfile(raw, EXPECTED_PROFILE_SHA256, values)
