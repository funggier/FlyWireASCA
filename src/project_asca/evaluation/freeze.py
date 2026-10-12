"""Canonical G2 workload freeze; source policy is distinct from behavior identity."""
from dataclasses import dataclass
from collections import Counter
from pathlib import Path
import json
from .fixture import INPUT_FILES,render_direct_prompt
from project_asca.agent_runtime.domain import load_public_configuration
from project_asca.agent_runtime.prompts import SCHEMAS,template_bundle
from project_asca.agent_runtime.values import fingerprint,canonical_bytes
from flywire_asca.structural_routing.model_router import router_prompt_fingerprint

SOURCE_UNIVERSE={
 "patterns":["src/project_asca/**/*.py","scripts/*agent_runtime*a015*.py"],
 "explicit":["pyproject.toml","scripts/audit_agent_runtime_contract.py",
             "scripts/audit_architecture_contract.py","scripts/verify_a011_frozen_profile_preservation.py"],
 "fixture":"fixtures/a015/stage-a-v1/*.json",
 "legacy_leaf_roots":["contracts","familiarity","model","embedding","vector_memory","selective_activation",
                     "uncertainty_expansion","procedural_memory","relational_activation","structural_routing"],
 "legacy_closure":"Static import and package-initializer closure, including incidental initializer imports; no omitted leaf dependency",
 "exclude":["docs/**","tests/**","artifacts/**",".superpowers/**"],
 "freeze_lock":"Excluded from its own aggregate; included in final behavior file identity",
}
APPROVALS={"spec_commit":"cccbf0fc47ca301bef8a6b7ac25398c2e1eb4447",
           "plan_commit":"4ca246df6976c7aa21ad07826017f167f0ee27da"}

@dataclass(frozen=True,slots=True)
class FreezeValidation:
    valid:bool
    errors:tuple[str,...]
    aggregate_hash:str
    components:dict
    direct_prompts:tuple
    max_prompt_upper_bound:int
    assembled_templates:dict
    source_universe:dict

def validate_freeze(workload,bounds):
    errors=[];w=workload
    cases=w.cases
    families=Counter(c.family for c in cases)
    if (len(cases)!=64 or len({c.pair_id for c in cases})!=32
        or Counter(c.language for c in cases)!={"en":32,"th":32}
        or len(families)!=8 or set(families.values())!={8}):
        errors.append("bilingual/family universe mismatch")
    for pair in {c.pair_id for c in cases}:
        matched=[c for c in cases if c.pair_id==pair]
        if len(matched)!=2 or {c.language for c in matched}!={"en","th"}:
            errors.append("pair completeness")
        elif w.oracle[matched[0].case_id]!=w.oracle[matched[1].case_id]:
            errors.append("pair oracle mismatch")
    counts=Counter(o.status for o in w.oracle.values())
    if counts!={"SUCCEEDED":48,"NEEDS_CLARIFICATION":4,"UNSUPPORTED":4,"BOUNDED_FAILURE":8}:
        errors.append("status denominator mismatch")
    try:load_public_configuration(w.public,w.profile)
    except ValueError as exc:errors.append("public/profile: "+str(exc))
    if w.schemas!=SCHEMAS:errors.append("frozen schema differs from assembled schema")
    normalizers={"numeric":"exact finite numeric equality; booleans excluded",
      "boolean":"exact bool","name":"case-preserving exact Unicode","list":"ordered exact values",
      "map":"key-order-insensitive exact keys and values","judge":"none","partial_credit":False}
    if w.normalizers!=normalizers:errors.append("oracle normalizer changed")
    components={}
    for name in INPUT_FILES:
        # JSON semantic bytes are stable across Git newline configurations.
        value=json.loads((w.root/name).read_text(encoding="utf-8"))
        components[name]=fingerprint(value)
    templates=template_bundle()
    components["assembled-templates"]=fingerprint(templates)
    components["a014-router-prompt"]=router_prompt_fingerprint()
    components["source-universe-policy"]=fingerprint(SOURCE_UNIVERSE)
    prompt_records=[]
    for case in cases:
        prompt=render_direct_prompt(case.text,w.public)
        bound=bounds.bound(prompt)
        if bound.upper_tokens+1024>8192:errors.append("direct prompt context overflow "+case.case_id)
        prompt_records.append({"case_id":case.case_id,"prompt_hash":fingerprint(prompt),
                               "upper_tokens":bound.upper_tokens,"output_allowance":1024})
    components["direct-prompt-instances"]=fingerprint(prompt_records)
    aggregate=fingerprint({"workload":"a015-bilingual-stage-a-v1","components":components,
                           "order":"matrix rows EN then TH","seed":0})
    if w.lock:
        if (w.lock.get("aggregate_hash")!=aggregate or w.lock.get("components")!=components
            or w.lock.get("direct_prompts")!=prompt_records
            or w.lock.get("assembled_templates")!=templates
            or w.lock.get("source_universe")!=SOURCE_UNIVERSE):
            errors.append("freeze lock mismatch")
    return FreezeValidation(not errors,tuple(errors),aggregate,components,tuple(prompt_records),
                            max((r["upper_tokens"] for r in prompt_records),default=0),
                            templates,SOURCE_UNIVERSE)

def write_freeze_lock(root,validation):
    if not validation.valid:raise ValueError("invalid freeze: "+repr(validation.errors))
    path=Path(root)/"freeze.lock.json"
    value={"workload":"a015-bilingual-stage-a-v1","aggregate_hash":validation.aggregate_hash,
      "components":validation.components,"direct_prompts":validation.direct_prompts,
      "max_prompt_upper_bound":validation.max_prompt_upper_bound,"order":"matrix rows EN then TH","seed":0,
      "assembled_templates":validation.assembled_templates,"source_universe":validation.source_universe,
      "approval_metadata":APPROVALS}
    if path.exists():
        existing=json.loads(path.read_text(encoding="utf-8"))
        if canonical_bytes(existing)!=canonical_bytes(value):
            raise ValueError("first freeze is immutable; create a disclosed new workload version")
        return validation.aggregate_hash
    path.write_text(canonical_bytes(value).decode("utf-8")+"\n",encoding="utf-8")
    return validation.aggregate_hash
