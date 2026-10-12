"""Offline frozen inputs and full-information direct-model prompt assembly."""
from dataclasses import dataclass
from pathlib import Path
from collections.abc import Mapping
from project_asca.agent_runtime.contracts import AgentRequest,PhysicalIdentity,ModelPrompt,ModelMessage
from project_asca.agent_runtime.prompts import SCHEMAS,template
from project_asca.agent_runtime.values import canonical_bytes
from project_asca.agent_runtime.broker import strict_json_object
from project_asca.agent_runtime.adapters.token_bounds import TokenBoundCertificate,PinnedTokenBounds

@dataclass(frozen=True,slots=True)
class FrozenCase:
    case_id:str
    pair_id:str
    family:str
    language:str
    text:str
    def request(self):return AgentRequest(self.text)

@dataclass(frozen=True,slots=True)
class OracleExpectation:
    status:str
    reason_category:str
    required_values:object
    required_state:Mapping
    recovery_required:bool
    required_relations:tuple=()
    min_path_hops:int=0

@dataclass(frozen=True,slots=True)
class FrozenWorkload:
    root:Path
    cases:tuple
    oracle:Mapping
    public:Mapping
    schemas:Mapping
    profile:Mapping
    certificate:Mapping
    normalizers:Mapping
    lock:Mapping

INPUT_FILES=("public.json","requests.json","oracle.json","schemas.json","profile.json","token-bound-certificate.json")

def _read(path):
    from project_asca.agent_runtime.values import thaw_json
    return thaw_json(strict_json_object(path.read_text(encoding="utf-8")))

def load_frozen_workload(root):
    import json
    root=Path(root)
    # Requests are an array, parsed with the same duplicate/non-finite checks
    # by embedding the serialized array inside a temporary object.
    from project_asca.agent_runtime.values import thaw_json
    requests=thaw_json(strict_json_object('{"requests":'+(root/"requests.json").read_text(encoding="utf-8")+'}'))["requests"]
    cases=[]
    for r in requests:
        if set(r)!={"case_id","pair_id","family","language","text"}:raise ValueError("case schema")
        c=FrozenCase(**r);AgentRequest(c.text);cases.append(c)
    if len({c.case_id for c in cases})!=len(cases):raise ValueError("duplicate case identity")
    oracle=_read(root/"oracle.json")
    expected={key:OracleExpectation(**value) for key,value in oracle["cases"].items()}
    if set(expected)!={c.case_id for c in cases}:raise ValueError("oracle/case universe")
    lock=_read(root/"freeze.lock.json") if (root/"freeze.lock.json").exists() else {}
    return FrozenWorkload(root,tuple(cases),expected,_read(root/"public.json"),_read(root/"schemas.json"),
                          _read(root/"profile.json"),_read(root/"token-bound-certificate.json"),
                          oracle["normalizers"],lock)

def bounds_from_workload(workload):
    value=dict(workload.certificate);claimed=value.pop("certificate_hash",None)
    value["identity"]=PhysicalIdentity(**value["identity"])
    certificate=TokenBoundCertificate(**value)
    if claimed!=certificate.fingerprint:raise ValueError("certificate hash")
    return PinnedTokenBounds.from_certificate(certificate)

def render_direct_prompt(text,public):
    system,digest=template("DIRECT")
    return ModelPrompt((ModelMessage("system",system),
        ModelMessage("user",canonical_bytes({"text":text,"public":public}).decode("utf-8"))),
        "a015-direct-v1",digest)
