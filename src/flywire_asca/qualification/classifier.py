"""Fail-closed decisions independent of the sign of research results."""
from __future__ import annotations

from datetime import datetime, timezone
from .records import (
    BLOCKER_CODES, REASON_CODES, EngineeringVerdict, GateStatus,
    PHYSICAL_GATE_IDS, PORTABLE_GATE_IDS, Reason, Scope,
)


def utc_time(value):
    if type(value) is not str:
        raise ValueError("Missing UTC time")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ValueError("Time must be UTC")
    return parsed


def gate_issues(gates, required):
    issues = []
    ids = [gate.gate_id for gate in gates]
    known = PORTABLE_GATE_IDS + PHYSICAL_GATE_IDS

    def issue(gate_id, message):
        issues.append(Reason("EVIDENCE_INVALID", gate_id, message, ()))

    if len(ids) != len(set(ids)) or any(g not in known for g in ids):
        issue(required[0], "Duplicate or unknown gate")
    selected = [g for g in gates if g.gate_id in required]
    if set(g.gate_id for g in selected) != set(required):
        issue(required[0], "Missing mandatory gate")
    by_id = {g.gate_id: g for g in gates}
    order = {name: index for index, name in enumerate(known)}
    for gate in selected:
        expected_scope = Scope.PORTABLE_ONLY if gate.gate_id.startswith("P") else Scope.FULL_SYSTEM
        if gate.scope != expected_scope:
            issue(gate.gate_id, "Gate scope differs")
        if gate.status == GateStatus.NOT_RUN:
            if (gate.command is not None or gate.started_at is not None or
                gate.finished_at is not None or gate.exit_code is not None or
                gate.artifacts or gate.errors or not gate.cause_ids):
                issue(gate.gate_id, "NOT_RUN needs null execution fields and causes")
        else:
            if not gate.command or not gate.artifacts:
                issue(gate.gate_id, "Executed gate needs command and raw evidence")
            try:
                if utc_time(gate.finished_at) < utc_time(gate.started_at):
                    raise ValueError("Finish before start")
            except (ValueError, TypeError):
                issue(gate.gate_id, "Invalid UTC execution interval")
            if gate.status == GateStatus.PASS and (gate.errors or gate.exit_code != 0 or gate.cause_ids):
                issue(gate.gate_id, "PASS contradicts errors, exit, or causes")
            if gate.status == GateStatus.FAIL and not gate.errors:
                issue(gate.gate_id, "FAIL needs a reason")
            if gate.status == GateStatus.BLOCKED and (
                not gate.errors or any(r.code not in BLOCKER_CODES or
                r.gate_id != gate.gate_id or not r.evidence_refs for r in gate.errors)):
                issue(gate.gate_id, "BLOCKED needs independent prerequisite evidence")
        if len(set(gate.cause_ids)) != len(gate.cause_ids):
            issue(gate.gate_id, "Duplicate cause")
        for cause in gate.cause_ids:
            previous = by_id.get(cause)
            if (previous is None or previous.status not in (GateStatus.FAIL, GateStatus.BLOCKED)
                or order.get(cause, 999) >= order.get(gate.gate_id, -1)):
                issue(gate.gate_id, "Cause must be an earlier failed or blocked gate")
        for reason in gate.errors:
            if reason.code not in REASON_CODES or reason.gate_id != gate.gate_id:
                issue(gate.gate_id, "Invalid gate reason")
    return tuple(issues)


def _decision(gates, errors, blockers, required):
    relevant = tuple(g for g in gates if g.gate_id in required)
    errors = tuple(r for r in errors if r.gate_id in required)
    blockers = tuple(r for r in blockers if r.gate_id in required)
    if gate_issues(gates, required) or errors or any(g.status == GateStatus.FAIL for g in relevant):
        return GateStatus.FAIL
    if any(r.code not in BLOCKER_CODES or not r.evidence_refs for r in blockers):
        return GateStatus.FAIL
    blocked = tuple(g for g in relevant if g.status == GateStatus.BLOCKED)
    if blocked:
        if any(not all(r in blockers for r in g.errors) for g in blocked):
            return GateStatus.FAIL
        return GateStatus.BLOCKED
    if blockers or any(g.status != GateStatus.PASS for g in relevant):
        return GateStatus.FAIL
    return GateStatus.PASS


def classify_portable(gates, errors, blockers):
    return _decision(gates, errors, blockers, PORTABLE_GATE_IDS)


def classify_full(gates, errors, blockers):
    status = _decision(gates, errors, blockers, PORTABLE_GATE_IDS + PHYSICAL_GATE_IDS)
    return {
        GateStatus.PASS: EngineeringVerdict.ENGINEERING_QUALIFIED,
        GateStatus.FAIL: EngineeringVerdict.ENGINEERING_NOT_QUALIFIED,
        GateStatus.BLOCKED: EngineeringVerdict.QUALIFICATION_BLOCKED,
    }[status]


def pack_exit_code(pack):
    # A declared verdict alone cannot turn inconsistent evidence into success.
    from .manifest import manifest_issues
    if manifest_issues(pack):
        return 1
    status = classify_portable(pack.gates, pack.errors, pack.blockers)
    if pack.scope == Scope.FULL_SYSTEM:
        verdict = classify_full(pack.gates, pack.errors, pack.blockers)
        return {EngineeringVerdict.ENGINEERING_QUALIFIED: 0,
                EngineeringVerdict.ENGINEERING_NOT_QUALIFIED: 1,
                EngineeringVerdict.QUALIFICATION_BLOCKED: 2}[verdict]
    return {GateStatus.PASS: 0, GateStatus.FAIL: 1, GateStatus.BLOCKED: 2,
            GateStatus.NOT_RUN: 1}[status]
