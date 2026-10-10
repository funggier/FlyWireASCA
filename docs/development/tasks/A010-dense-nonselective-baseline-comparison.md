# A010 — Dense/Non-selective Baseline Comparison

Status: ACTIVE
GitHub Issue: #10
Branch: research/a010-dense-nonselective-baseline-comparison
Activation base: 6846c17d17fd4f6fa2963fd4ad0586b60f5e4fee

Approved design:
`docs/superpowers/specs/2026-10-10-a010-dense-nonselective-baseline-comparison-design.md`

Approved implementation plan:
`docs/superpowers/plans/2026-10-10-a010-dense-nonselective-baseline-comparison.md`

## Goal

Compare the real A009 selective cognitive loop against a deliberately
non-selective A005+A006 exhaustive baseline on a frozen controlled workload.

## Primary comparison

ASCA_PRIMARY:
- A009 `MISMATCH_DRIVEN_RECOVERY`
- A006 `SINGLE_BEST`
- A007 `SIGNAL_DRIVEN`
- A008 `CHUNKED`

DENSE_EXHAUSTIVE:
- same A005 corpus, query texts, embedding evidence and threshold
- all declared cue tiers immediately
- full-index top-k
- A006 `select_exhaustive()`
- same explicit A008 root procedure
- one `CHUNKED` attempt

## Historical outcomes to preserve

- A006: `NOT_SUPPORTED`
- A007: `SUPPORTED`
- A008: `SUPPORTED`
- A009: `SUPPORTED`

FlyWireLLM remains untouched.

## Phases

- [x] Design spec approved.
- [x] Implementation plan approved.
- [x] Task activated and GitHub Issue #10 created.
- [ ] A010 comparison contracts implemented.
- [ ] Dense exhaustive runner implemented.
- [ ] ASCA normalization and ablations implemented.
- [ ] Deterministic fixture/classifier frozen.
- [ ] Portable and physical qualification completed.
- [ ] Exact feature-branch CI GREEN.
- [ ] Whole-branch review GREEN.
- [ ] Reviewed main integration and exact final-main CI GREEN.
- [ ] Issue closed after final-main evidence.

## Acceptance criteria

- ASCA_PRIMARY delegates to the real A009 controller.
- DENSE_EXHAUSTIVE uses real A005 retrieval and A006 `select_exhaustive()`.
- Shared-input fairness is validated.
- Dense-only success remains first-class evidence.
- Primary outcome is exactly `SUPPORTED`, `MIXED`, or `NOT_SUPPORTED`.
- Valid negative outcomes remain valid research evidence.
- No synthetic scalar efficiency score.
- No FLOP, energy, RAM-byte, hardware-bandwidth, or general-latency claim.
- No real OS/API/LConnect/BConnect side effects.
- A006/A007/A008/A009 historical outcomes remain unchanged.
- FlyWireLLM remains untouched.

## Current action

Task 1 — comparison contracts and activation ledger.

## Next action

Implement the dense exhaustive runner after Task 1 RED→GREEN verification.
