"""Deterministic publication of exactly the candidate independently verified."""
import json
from .values import fingerprint,thaw_json

def render_result_data(candidate,verification,*,language=None):
    if language not in (None,"en","th"):raise ValueError("render language")
    if not verification.passed:
        return "ยังยืนยันผลลัพธ์ไม่ได้" if language=="th" else "Unverified result."
    if (verification.candidate_fingerprint!=fingerprint(candidate)
        or verification.data_fingerprint!=fingerprint(candidate.data)
        or candidate.attempt is None or verification.execution_id!=candidate.attempt.execution_id
        or not candidate.attempt.observations
        or verification.run_id!=candidate.attempt.observations[0].run_id):
        raise ValueError("verified candidate identity mismatch")
    prefix="ผลลัพธ์ที่ตรวจสอบแล้ว: " if language=="th" else "Verified result: "
    rendered=json.dumps(thaw_json(candidate.data),ensure_ascii=False,sort_keys=True,separators=(",",":"))
    evidence=(" | evidence: "+", ".join(candidate.evidence_refs)) if candidate.evidence_refs else ""
    return prefix+rendered+evidence
