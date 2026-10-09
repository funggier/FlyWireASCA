import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"src"
if str(SRC) not in sys.path:
    sys.path.insert(0,str(SRC))

from flywire_asca.integrated_loop import (
    LoopPolicy,
    build_a009_deterministic_fixture,
    classify_a009_hypothesis,
    fixture_fingerprint,
    qualify_a009_report,
    run_a009_benchmark,
)

QUALIFICATION_SCOPE="deterministic_integrated_cognitive_loop_a009"
FIXTURE_VERSION="a009-deterministic-v1"
EXPECTED_FIXTURE_FINGERPRINT="2f92b5092de346f62879ac2cbb9f96d6de5d6f919e12d0693345c8228b01ab2a"
MAX_SCOPE_COUNT=3
MAX_PROCEDURE_ATTEMPTS=3
PRIMARY_SELECTOR="SINGLE_BEST"
PRIMARY_PROCEDURE_MODE="CHUNKED"
POLICIES=[
    LoopPolicy.NO_PROCEDURE_RECOVERY.value,
    LoopPolicy.MISMATCH_DRIVEN_RECOVERY.value,
    LoopPolicy.ALWAYS_MAX_SCOPE.value,
]

_INT_METRICS=(
    "case_count","valid_case_count","invalid_case_count","recoverable_case_count",
    "genuine_recovery_count","regression_count",
    "primary_recoverable_success_count","always_recoverable_success_count",
    "primary_total_scope_evaluations","always_total_scope_evaluations",
    "primary_success_count","always_success_count",
    "primary_final_state_correct_count",
    "primary_same_name_ambiguity_failure_count",
    "chunked_flat_diagnostic_case_count","chunked_flat_equivalence_count",
    "max_procedure_attempt_count","max_scope_index",
    "duplicate_execution_id_failure_count","model_fallback_call_count",
    "model_control_leakage_failure_count",
)

def _policy_payload(item):
    return {
        "policy":item.policy.value,
        "termination_reason":item.termination_reason.value,
        "evaluated_scope_indices":list(item.evaluated_scope_indices),
        "forced_recovery_scope_count":item.forced_recovery_scope_count,
        "procedure_attempt_count":item.procedure_attempt_count,
        "execution_ids":list(item.execution_ids),
        "procedure_states":list(item.procedure_states),
        "final_working_set_ids":list(item.final_working_set_ids),
        "final_world_state_ref":item.final_world_state_ref,
        "procedure_success":item.procedure_success,
        "final_state_correct":item.final_state_correct,
        "same_name_ambiguity_preserved":item.same_name_ambiguity_preserved,
        "model_fallback_called":item.model_fallback_called,
        "trace_signature":[[kind,list(refs)] for kind,refs in item.trace_signature],
    }

def _case_payload(item):
    return {
        "case_id":item.case_id,
        "recoverable":item.recoverable,
        "validation_error_observed":item.validation_error_observed,
        "validation_error":item.validation_error,
        "policy_results":[_policy_payload(value) for value in item.policy_results],
        "chunked_flat_equivalent":item.chunked_flat_equivalent,
        "model_control_isolated":item.model_control_isolated,
    }

def _aggregate_payload(report):
    return {name:getattr(report,name) for name in _INT_METRICS} | {
        "deterministic_repeat_match":report.deterministic_repeat_match,
    }

def _classify_aggregate(aggregate):
    if aggregate["genuine_recovery_count"]<=0:
        return "NOT_SUPPORTED"
    supported=(
        aggregate["regression_count"]==0
        and aggregate["primary_recoverable_success_count"]==aggregate["always_recoverable_success_count"]
        and aggregate["primary_recoverable_success_count"]==aggregate["recoverable_case_count"]
        and aggregate["primary_total_scope_evaluations"]<aggregate["always_total_scope_evaluations"]
        and aggregate["duplicate_execution_id_failure_count"]==0
        and aggregate["max_procedure_attempt_count"]<=MAX_PROCEDURE_ATTEMPTS
        and aggregate["max_scope_index"]<MAX_SCOPE_COUNT
        and aggregate["primary_final_state_correct_count"]==aggregate["primary_success_count"]
        and aggregate["primary_same_name_ambiguity_failure_count"]==0
        and aggregate["model_control_leakage_failure_count"]==0
        and aggregate["chunked_flat_equivalence_count"]==aggregate["chunked_flat_diagnostic_case_count"]
        and aggregate["deterministic_repeat_match"] is True
    )
    return "SUPPORTED" if supported else "MIXED"

def run_qualification():
    cases=build_a009_deterministic_fixture()
    report=run_a009_benchmark(cases)
    errors=qualify_a009_report(report)
    return {
        "qualification_scope":QUALIFICATION_SCOPE,
        "fixture_version":FIXTURE_VERSION,
        "fixture_fingerprint":fixture_fingerprint(cases),
        "case_ids":[case.case_id for case in cases],
        "policies":POLICIES,
        "primary_selector":PRIMARY_SELECTOR,
        "primary_procedure_mode":PRIMARY_PROCEDURE_MODE,
        "max_scope_count":MAX_SCOPE_COUNT,
        "max_procedure_attempts":MAX_PROCEDURE_ATTEMPTS,
        "aggregate_metrics":_aggregate_payload(report),
        "cases":[_case_payload(item) for item in report.case_results],
        "primary_hypothesis_outcome":classify_a009_hypothesis(report),
        "experiment_valid":not errors,
        "errors":errors,
        "claims_boundary":"deterministic control/recovery evidence only; no hardware, energy, token, latency, or real-tool autonomy claim",
    }

def _nonnegative_int(errors,name,value):
    if not isinstance(value,int) or isinstance(value,bool) or value<0:
        errors.append(f"{name} must be a nonnegative integer")


def _derive_metrics_from_case_evidence(case_payloads):
    errors=[]
    derived={
        "case_count":len(case_payloads),
        "valid_case_count":0,
        "invalid_case_count":0,
        "recoverable_case_count":0,
        "genuine_recovery_count":0,
        "regression_count":0,
        "primary_recoverable_success_count":0,
        "always_recoverable_success_count":0,
        "primary_total_scope_evaluations":0,
        "always_total_scope_evaluations":0,
        "primary_success_count":0,
        "always_success_count":0,
        "primary_final_state_correct_count":0,
        "primary_same_name_ambiguity_failure_count":0,
        "chunked_flat_diagnostic_case_count":0,
        "chunked_flat_equivalence_count":0,
        "max_procedure_attempt_count":0,
        "max_scope_index":0,
        "duplicate_execution_id_failure_count":0,
        "model_fallback_call_count":0,
        "model_control_leakage_failure_count":0,
    }
    for case in case_payloads:
        if not isinstance(case,dict):
            errors.append("cases entries must be objects")
            continue
        invalid=case.get("validation_error_observed") is True
        if invalid:
            derived["invalid_case_count"]+=1
            if case.get("policy_results") not in ([],()):
                errors.append("invalid cases must not contain policy_results")
            continue
        derived["valid_case_count"]+=1
        recoverable=case.get("recoverable") is True
        if recoverable:
            derived["recoverable_case_count"]+=1
        results=case.get("policy_results")
        if not isinstance(results,list):
            errors.append("policy_results must be a list")
            continue
        names=[item.get("policy") for item in results if isinstance(item,dict)]
        if names!=POLICIES:
            errors.append("valid case policy_results must match frozen policies")
            continue
        by_policy={item["policy"]:item for item in results}
        no=by_policy[LoopPolicy.NO_PROCEDURE_RECOVERY.value]
        primary=by_policy[LoopPolicy.MISMATCH_DRIVEN_RECOVERY.value]
        always=by_policy[LoopPolicy.ALWAYS_MAX_SCOPE.value]

        no_success=no.get("procedure_success") is True
        primary_success=primary.get("procedure_success") is True
        always_success=always.get("procedure_success") is True
        primary_scopes=primary.get("evaluated_scope_indices")
        always_scopes=always.get("evaluated_scope_indices")
        primary_ids=primary.get("execution_ids")
        if not isinstance(primary_scopes,list) or not isinstance(always_scopes,list):
            errors.append("policy scope evidence must be lists")
            continue
        if not isinstance(primary_ids,list):
            errors.append("primary execution_ids must be a list")
            continue

        derived["primary_total_scope_evaluations"]+=len(primary_scopes)
        derived["always_total_scope_evaluations"]+=len(always_scopes)
        derived["primary_success_count"]+=int(primary_success)
        derived["always_success_count"]+=int(always_success)
        derived["primary_final_state_correct_count"]+=int(
            primary_success and primary.get("final_state_correct") is True
        )
        derived["primary_same_name_ambiguity_failure_count"]+=int(
            primary.get("same_name_ambiguity_preserved") is not True
        )
        derived["max_procedure_attempt_count"]=max(
            derived["max_procedure_attempt_count"],
            primary.get("procedure_attempt_count",0)
            if isinstance(primary.get("procedure_attempt_count"),int)
            and not isinstance(primary.get("procedure_attempt_count"),bool)
            else 0,
        )
        if primary_scopes:
            numeric_scopes=[
                item for item in primary_scopes
                if isinstance(item,int) and not isinstance(item,bool)
            ]
            if len(numeric_scopes)==len(primary_scopes):
                derived["max_scope_index"]=max(
                    derived["max_scope_index"],
                    max(numeric_scopes),
                )
        derived["duplicate_execution_id_failure_count"]+=int(
            len(primary_ids)!=len(set(primary_ids))
        )
        derived["model_fallback_call_count"]+=int(
            primary.get("model_fallback_called") is True
        )
        if recoverable:
            derived["primary_recoverable_success_count"]+=int(primary_success)
            derived["always_recoverable_success_count"]+=int(always_success)
        if no_success and not primary_success:
            derived["regression_count"]+=1
        if (
            not no_success
            and primary_success
            and isinstance(primary.get("forced_recovery_scope_count"),int)
            and not isinstance(primary.get("forced_recovery_scope_count"),bool)
            and primary.get("forced_recovery_scope_count")>0
            and len(primary_ids)==len(set(primary_ids))
        ):
            derived["genuine_recovery_count"]+=1
        diagnostic=case.get("chunked_flat_equivalent")
        if diagnostic is not None:
            derived["chunked_flat_diagnostic_case_count"]+=1
            derived["chunked_flat_equivalence_count"]+=int(diagnostic is True)
        model_control_isolated=case.get("model_control_isolated")
        if model_control_isolated not in (None,True,False):
            errors.append("model_control_isolated must be bool or null")
        derived["model_control_leakage_failure_count"]+=int(
            model_control_isolated is False
        )
    return derived,errors

def validate_qualification_payload(payload):
    errors=[]
    cases=build_a009_deterministic_fixture()
    if payload.get("qualification_scope")!=QUALIFICATION_SCOPE:
        errors.append("qualification_scope mismatch")
    if payload.get("fixture_version")!=FIXTURE_VERSION:
        errors.append("fixture_version mismatch")
    if payload.get("fixture_fingerprint")!=EXPECTED_FIXTURE_FINGERPRINT:
        errors.append("fixture_fingerprint mismatch")
    if payload.get("case_ids")!=[case.case_id for case in cases]:
        errors.append("case_ids mismatch")
    if payload.get("policies")!=POLICIES:
        errors.append("policies mismatch")
    if payload.get("primary_selector")!=PRIMARY_SELECTOR:
        errors.append("primary_selector mismatch")
    if payload.get("primary_procedure_mode")!=PRIMARY_PROCEDURE_MODE:
        errors.append("primary_procedure_mode mismatch")
    if payload.get("max_scope_count")!=MAX_SCOPE_COUNT:
        errors.append("max_scope_count mismatch")
    if payload.get("max_procedure_attempts")!=MAX_PROCEDURE_ATTEMPTS:
        errors.append("max_procedure_attempts mismatch")
    aggregate=payload.get("aggregate_metrics")
    if not isinstance(aggregate,dict):
        return errors+["aggregate_metrics must be an object"]
    for name in _INT_METRICS:
        _nonnegative_int(errors,name,aggregate.get(name))
    if not isinstance(aggregate.get("deterministic_repeat_match"),bool):
        errors.append("deterministic_repeat_match must be bool")
    if aggregate.get("case_count")!=aggregate.get("valid_case_count",0)+aggregate.get("invalid_case_count",0):
        errors.append("case_count must equal valid_case_count + invalid_case_count")
    if aggregate.get("recoverable_case_count",0)>aggregate.get("valid_case_count",0):
        errors.append("recoverable_case_count cannot exceed valid_case_count")
    for name in ("primary_recoverable_success_count","always_recoverable_success_count"):
        if aggregate.get(name,0)>aggregate.get("recoverable_case_count",0):
            errors.append(f"{name} cannot exceed recoverable_case_count")
    if aggregate.get("primary_final_state_correct_count",0)>aggregate.get("primary_success_count",0):
        errors.append("primary_final_state_correct_count cannot exceed primary_success_count")
    if aggregate.get("chunked_flat_equivalence_count",0)>aggregate.get("chunked_flat_diagnostic_case_count",0):
        errors.append("chunked_flat_equivalence_count cannot exceed chunked_flat_diagnostic_case_count")
    if aggregate.get("max_procedure_attempt_count",0)>MAX_PROCEDURE_ATTEMPTS:
        errors.append("max_procedure_attempt_count exceeds frozen maximum")
    if aggregate.get("max_scope_index",0)>=MAX_SCOPE_COUNT:
        errors.append("max_scope_index exceeds frozen maximum")
    if aggregate.get("duplicate_execution_id_failure_count",0)!=0:
        errors.append("duplicate_execution_id_failure_count must be 0")
    if aggregate.get("model_control_leakage_failure_count",0)!=0:
        errors.append("model_control_leakage_failure_count must be 0")
    case_payloads=payload.get("cases")
    if not isinstance(case_payloads,list):
        errors.append("cases must be a list")
    else:
        observed_case_ids=[case.get("case_id") for case in case_payloads if isinstance(case,dict)]
        if observed_case_ids!=payload.get("case_ids"):
            errors.append("cases order/identity must match case_ids")
        for case in case_payloads:
            if not isinstance(case,dict):
                errors.append("cases entries must be objects")
                continue
            for policy_result in case.get("policy_results",[]):
                if not isinstance(policy_result,dict):
                    errors.append("policy_results entries must be objects")
                    continue
                execution_ids=policy_result.get("execution_ids")
                if (
                    not isinstance(execution_ids,list)
                    or any(not isinstance(item,str) or not item for item in execution_ids)
                ):
                    errors.append("execution_ids must be a list of nonblank strings")
                elif len(execution_ids)!=len(set(execution_ids)):
                    errors.append("execution_ids must be unique within a policy result")
                scope_indices=policy_result.get("evaluated_scope_indices")
                if (
                    not isinstance(scope_indices,list)
                    or any(not isinstance(item,int) or isinstance(item,bool) or item<0 for item in scope_indices)
                    or not scope_indices
                ):
                    errors.append("evaluated scope indices must be nonempty nonnegative integers")
                elif scope_indices!=list(range(scope_indices[-1]+1)):
                    errors.append("evaluated scope indices must be contiguous without scope skipping")
                attempt_count=policy_result.get("procedure_attempt_count")
                if isinstance(execution_ids,list) and attempt_count!=len(execution_ids):
                    errors.append("procedure_attempt_count must equal len(execution_ids)")
        derived,derive_errors=_derive_metrics_from_case_evidence(case_payloads)
        errors.extend(derive_errors)
        for name,value in derived.items():
            if aggregate.get(name)!=value:
                errors.append(f"{name} does not match case evidence")
    outcome=payload.get("primary_hypothesis_outcome")
    if outcome not in {"SUPPORTED","MIXED","NOT_SUPPORTED"}:
        errors.append("primary_hypothesis_outcome has invalid vocabulary")
    elif all(name in aggregate for name in _INT_METRICS) and isinstance(aggregate.get("deterministic_repeat_match"),bool):
        expected=_classify_aggregate(aggregate)
        if outcome!=expected:
            errors.append(f"primary hypothesis outcome drift: expected {expected}")
    return errors

def _emit(payload,output_path):
    line=json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n"
    encoded=line.encode("utf-8")
    stream=getattr(sys.stdout,"buffer",None)
    if stream is not None:
        stream.write(encoded); stream.flush()
    else:
        sys.stdout.write(line)
    if output_path is not None:
        output_path.parent.mkdir(parents=True,exist_ok=True)
        output_path.write_bytes(encoded)

def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path)
    parser.add_argument("--note")
    args=parser.parse_args(argv)
    payload=run_qualification()
    if args.note is not None:
        payload["note"]=args.note
    errors=validate_qualification_payload(payload)
    if errors:
        payload["experiment_valid"]=False
        payload["errors"]=errors
        _emit(payload,args.output)
        return 1
    payload["experiment_valid"]=True
    payload["errors"]=[]
    _emit(payload,args.output)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
