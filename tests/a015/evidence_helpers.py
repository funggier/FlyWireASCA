"""Synthetic protocol fixtures stay outside production code."""
from dataclasses import replace
from datetime import datetime,timezone
import uuid
from project_asca.evaluation.evidence import (PhysicalRunMetadata,source_fingerprint,build_evidence,
    G2_COMMIT,SPEC_COMMIT,PLAN_COMMIT,SPEC_PATH,git)
from project_asca.evaluation.physical import execute_schedule
from project_asca.evaluation.schedule import trial_schedule
from project_asca.evaluation.fixture import bounds_from_workload,load_frozen_workload
from project_asca.evaluation.freeze import validate_freeze
from project_asca.evaluation.portable import PortableIdentity,ScriptedModel,ScriptedEmbedding
from project_asca.agent_runtime.contracts import PhysicalIdentity,Usage
from project_asca.agent_runtime.domain import load_public_configuration
from project_asca.agent_runtime.factory import build_stage_a_runtime
from project_asca.agent_runtime.ports import RuntimePorts
from project_asca.agent_runtime.control import MonotonicClock
from project_asca.agent_runtime.broker import ModelBroker
from project_asca.evaluation.direct import DirectPinnedRunner
from project_asca.evaluation.oracle import RawTrial,evaluate_trial
from project_asca.agent_runtime.values import fingerprint,RunVariant
def make_contract_evidence(workload,*,root):
    cfg=load_public_configuration(workload.public,workload.profile)
    identity=PhysicalIdentity(**workload.certificate["identity"]);bounds=bounds_from_workload(workload)
    model=ScriptedModel(cfg,identity);clock=MonotonicClock()
    runtime=build_stage_a_runtime(cfg,RuntimePorts(model,ScriptedEmbedding(identity),bounds,PortableIdentity(identity),clock))
    direct=DirectPinnedRunner(cfg,ModelBroker(model,bounds,identity),clock=clock)
    trials=execute_schedule(workload,runtime,direct,trial_schedule(workload),clock=clock)
    head=git(root,"rev-parse","HEAD").decode().strip();source=source_fingerprint(root,head,workload.lock["source_universe"])
    freeze=validate_freeze(workload,bounds);now=datetime.now(timezone.utc).isoformat()
    metadata=PhysicalRunMetadata(str(uuid.uuid4()),head,source,G2_COMMIT,freeze.aggregate_hash,freeze.components,
        SPEC_COMMIT,PLAN_COMMIT,git(root,"rev-parse",SPEC_COMMIT+":"+SPEC_PATH).decode().strip(),
        identity,identity,{"hostname":"HARNESS","os":"scripted","python":"test"},
        {"scripted":True},{},False,"HARNESS_CONTRACT_TEST",3,0,now,now,True)
    return build_evidence(trials,metadata)
def with_unknown_usage(evidence,root):
    workload=load_frozen_workload(root/"fixtures/a015/stage-a-v1")
    cfg=load_public_configuration(workload.public,workload.profile)
    identity=evidence.metadata.identity_before
    class UnknownModel(ScriptedModel):
        def generate(self,*args,**kwargs):
            response=super().generate(*args,**kwargs)
            return replace(response,usage=Usage(None,response.usage.output_tokens,False))
    clock=MonotonicClock();model=UnknownModel(cfg,identity)
    runner=DirectPinnedRunner(cfg,ModelBroker(model,bounds_from_workload(workload),identity),clock=clock)
    trials=list(evidence.trials)
    index=next(i for i,t in enumerate(trials) if t.variant is RunVariant.DIRECT_PINNED_MODEL)
    old=trials[index];case=next(c for c in workload.cases if c.case_id==old.case_id)
    start=clock.now();result=runner.run(case.text)
    trials[index]=RawTrial(case.case_id,old.variant,old.repetition,fingerprint(case.text),result,
        evaluate_trial(case,workload.oracle[case.case_id],result),tuple(runner.model_records),clock.now()-start)
    return build_evidence(tuple(trials),evidence.metadata)
