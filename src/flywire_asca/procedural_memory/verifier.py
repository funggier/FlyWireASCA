from __future__ import annotations

from flywire_asca.contracts import Observation

from .models import ExpectedOutcome, OutcomeMatcherKind, OutcomeVerification


def verify_outcome(
    expected: ExpectedOutcome,
    observed: Observation,
) -> OutcomeVerification:
    if not isinstance(expected, ExpectedOutcome):
        raise ValueError("expected must be an ExpectedOutcome")
    if not isinstance(observed, Observation):
        raise ValueError("observed must be an Observation")
    if expected.matcher is not OutcomeMatcherKind.EXACT:
        raise ValueError("unsupported outcome matcher")
    matched = (
        observed.kind is expected.observation_kind
        and observed.payload_ref == expected.expected_payload_ref
    )
    return OutcomeVerification(
        expectation_id=expected.expectation_id,
        observation_id=observed.observation_id,
        matched=matched,
    )
