"""Script-owned pure-validator bridge; importing/validating performs no inference."""
from functools import lru_cache
import importlib.util
from pathlib import Path
import sys
from types import MappingProxyType
from uuid import uuid4

ALLOWLIST = {
    "A006": "qualify_selective_activation_a006.py",
    "A007": "qualify_uncertainty_expansion_a007.py",
    "A008": "qualify_procedural_memory_a008.py",
    "A009": "qualify_integrated_loop_a009.py",
    "A010": "qualify_baseline_comparison_a010.py",
}


@lru_cache(maxsize=8)
def load_legacy_validators(repo_root):
    root = Path(repo_root).resolve()
    validators = {}
    for milestone, filename in ALLOWLIST.items():
        name = "_a011_legacy_" + milestone.lower() + "_" + uuid4().hex
        spec = importlib.util.spec_from_file_location(name, root / "scripts" / filename)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        if milestone in ("A006", "A007"):
            def validate(payload, function=module.validate_physical_experiment):
                return tuple(function(payload.get("experiment")))
        else:
            def validate(payload, function=module.validate_qualification_payload):
                return tuple(function(payload))
        validators[milestone] = validate
    return MappingProxyType(validators)
