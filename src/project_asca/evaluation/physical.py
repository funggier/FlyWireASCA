"""Fixed native physical protocol; setup and every failed trial remain visible."""
from pathlib import Path
from datetime import datetime,timezone
from dataclasses import replace
import os,platform,socket,time,uuid,json,urllib.request
from .schedule import trial_schedule
from .oracle import RawTrial,evaluate_trial
from .evidence import (PhysicalRunMetadata,build_evidence,write_evidence,verify_evidence,
                       source_fingerprint,G2_COMMIT,SPEC_COMMIT,PLAN_COMMIT,SPEC_PATH,git)
from .fixture import bounds_from_workload
from .freeze import validate_freeze
from .direct import DirectPinnedRunner
from project_asca.agent_runtime.values import RunVariant,fingerprint,canonical_bytes,thaw_json
from project_asca.agent_runtime.domain import load_public_configuration
from project_asca.agent_runtime.factory import build_stage_a_runtime
from project_asca.agent_runtime.ports import RuntimePorts
from project_asca.agent_runtime.control import MonotonicClock,RunControl
from project_asca.agent_runtime.contracts import AgentRequest,ModelPrompt,ModelMessage,BrokerModelRequest
from project_asca.agent_runtime.broker import ModelBroker
from project_asca.agent_runtime.adapters.model import probe_physical_identity,PinnedModelPort,PinnedEmbeddingPort
BASE_URL="http://localhost:11434"
def execute_schedule(workload,unified,direct,slots,*,clock,on_trial=None):
    trials=[]
    for slot in slots:
        runner=unified if slot.variant is RunVariant.UNIFIED_RUNTIME else direct
        prior=len(runner.model_records);started=clock.now()
        result=runner.run(slot.case.text);wall=max(0.0,clock.now()-started)
        trial=RawTrial(slot.case.case_id,slot.variant,slot.repetition,fingerprint(slot.case.text),result,
                       evaluate_trial(slot.case,workload.oracle[slot.case.case_id],result),
                       tuple(runner.model_records[prior:]),wall)
        trials.append(trial)
        if on_trial:on_trial(trial)
    return tuple(trials)
def residence():
    with urllib.request.urlopen(BASE_URL+"/api/ps",timeout=10) as response:
        body=response.read(2*1024*1024+1)
    if len(body)>2*1024*1024:raise ValueError("residence metadata bound")
    return json.loads(body)
def environment():
    result={"hostname":socket.gethostname(),"os":platform.platform(),"python":platform.python_version(),
            "machine":platform.machine(),"processor":platform.processor(),"timing":"monotonic client wall; exclusive FSM phases; nested spans separate"}
    if os.name=="nt":
        import ctypes,winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as key:
            result["processor"]=winreg.QueryValueEx(key,"ProcessorNameString")[0]
        memory=ctypes.c_ulonglong()
        if ctypes.windll.kernel32.GetPhysicallyInstalledSystemMemory(ctypes.byref(memory)):result["installed_ram_bytes"]=memory.value*1024
    return result
def utc():return datetime.now(timezone.utc).isoformat()
def run_physical_comparison(workload,*,output,repetitions,seed):
    slots=trial_schedule(workload,repetitions=repetitions,seed=seed)
    output=Path(output)
    if output.exists():raise ValueError("preserve existing run; choose a new disclosed output")
    root=workload.root.resolve().parents[2];head=git(root,"rev-parse","HEAD").decode().strip()
    source=source_fingerprint(root,head,workload.lock["source_universe"])
    bounds=bounds_from_workload(workload);freeze=validate_freeze(workload,bounds)
    if not freeze.valid:raise ValueError("frozen direct prompt preflight")
    g4_path=os.environ.get("A015_G4_RECORD")
    if not g4_path:raise ValueError("source/CI G4 preflight record required")
    g4=json.loads(Path(g4_path).read_text(encoding="utf-8"))
    if (g4.get("head_sha")!=head or g4.get("source_fingerprint")!=source.fingerprint
        or g4.get("conclusion")!="success"):raise ValueError("G4 exact source/CI mismatch")
    expected=workload.certificate["identity"];identity=probe_physical_identity(BASE_URL)
    if fingerprint(identity)!=fingerprint(expected):raise ValueError("fresh pinned physical identity preflight")
    clock=MonotonicClock();setup_control=RunControl.create(AgentRequest("Configured common warm-up and index setup"),clock=clock)
    model=PinnedModelPort(BASE_URL,setup_control,identity);embedding=PinnedEmbeddingPort(BASE_URL,setup_control,identity)
    class Identity:
        def inspect(self):return identity
    cfg=load_public_configuration(workload.public,workload.profile)
    before=residence();cold_start=clock.now()
    unified=build_stage_a_runtime(cfg,RuntimePorts(model,embedding,bounds,Identity(),clock))
    cold_seconds=clock.now()-cold_start
    warm=RunControl.create(AgentRequest("Common non-workload inference warm-up"),clock=clock)
    prompt=ModelPrompt((ModelMessage("user","Return a short acknowledgment."),),"setup-common-v1",fingerprint("common non-workload warm-up"))
    warm_start=clock.now()
    response=model.for_control(warm).generate(BrokerModelRequest(warm.run_id+":warmup",prompt,16),
                                             deadline=warm.ledger.deadline,cancellation=warm.cancellation)
    embed_response=embedding.for_control(warm).embed(("common non-workload embedding warm-up",),deadline=warm.ledger.deadline,cancellation=warm.cancellation)
    setup={"index_setup":unified.setup_metrics,"cold_index_seconds":cold_seconds,"residence_before":before,
           "residence_after_warmup":residence(),"common_warmup":{"generation_calls":1,"embedding_calls":1,
                "prompt":prompt,"generation_response":response,"embedding_inputs":1,
                "embedding_prompt_tokens":embed_response.prompt_tokens,"seconds":clock.now()-warm_start},
           "historical_setup_probe":{"generic_generation_calls":1,"prompt_tokens":23,"output_tokens":1,
                                    "reason":"Task3 wrong render-only flag; excluded from all primary denominators"}}
    direct=DirectPinnedRunner(cfg,ModelBroker(model,bounds,identity),clock=clock)
    run_id=str(uuid.uuid4());started=utc();trials=[]
    metadata=PhysicalRunMetadata(run_id,head,source,G2_COMMIT,freeze.aggregate_hash,freeze.components,
        SPEC_COMMIT,PLAN_COMMIT,git(root,"rev-parse",SPEC_COMMIT+":"+SPEC_PATH).decode().strip(),
        identity,identity,environment(),setup,g4,True,"PHYSICAL_MODEL_COMPARISON",3,0,started,started,False)
    partial=output.with_name(output.stem+".partial-"+run_id+".json")
    def progress(trial):
        trials.append(trial)
        checkpoint=build_evidence(tuple(trials),replace(metadata,finished_at=utc(),complete=False,
                                      interruption="RUNNING checkpoint; never a completed comparison"))
        # Checkpoint after every request; no rerun of a failed request.
        write_evidence(checkpoint,partial)
        print(json.dumps({"completed":len(trials),"total":384,"repetition":trial.repetition,
                          "variant":trial.variant.value,"status":trial.result.status.value}),flush=True)
    try:
        execute_schedule(workload,unified,direct,slots,clock=clock,on_trial=progress)
        after=probe_physical_identity(BASE_URL)
        source_fingerprint(root,head,workload.lock["source_universe"])
        metadata=replace(metadata,identity_after=after,finished_at=utc(),complete=True)
        evidence=build_evidence(tuple(trials),metadata);write_evidence(evidence,output)
        validation=verify_evidence(evidence,root=root)
        if not validation.valid:raise ValueError("saved evidence failed offline checks: "+repr(validation.errors))
        print(json.dumps({"complete":True,"trials":len(trials),"outcome":evidence.outcome.value,
                          "usage_complete":validation.usage_complete,"source_fingerprint":source.fingerprint}),flush=True)
        return evidence
    except BaseException as exc:
        try:after=probe_physical_identity(BASE_URL)
        except Exception:after=None
        metadata=replace(metadata,identity_after=after,finished_at=utc(),complete=False,
                         interruption=type(exc).__name__+": "+str(exc)[:500])
        write_evidence(build_evidence(tuple(trials),metadata),partial)
        raise
