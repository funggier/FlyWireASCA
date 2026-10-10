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
- [x] A010 comparison contracts implemented.
- [x] Dense exhaustive runner implemented.
- [x] ASCA normalization and ablations implemented.
- [x] Deterministic fixture/classifier frozen.
- [x] Portable and physical qualification completed.
- [x] Exact feature-branch CI GREEN.
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

## Qualification evidence

Portable qualification: GREEN
Physical qualification: GREEN
Exact feature-branch CI: GREEN
Primary outcome: `NOT_SUPPORTED`

Frozen fixture fingerprint:
`69d20542cd1e7e5c25a0fb61b9060f622379206b519da3cec7624e00bb6e5d4c`

Qualified implementation candidate:
`234bc090dc068447c1830fa79337745b7796f25f`

Exact candidate CI:
`38014300995` — success

Local full suite at candidate: `515 passed`

Key frozen metrics:
- ASCA / dense procedure success: 7 / 8
- dense-only / ASCA-only success: 1 / 0
- ASCA / dense query count: 28 / 27
- ASCA / dense scored-vector count: 1984 / 1440
- ASCA / dense cumulative selected count: 66 / 480
- ASCA / dense procedure attempts: 14 / 9
- identity failures: 0
- duplicate execution-ID failures: 0
- post-completion extra-attempt failures: 0

Physical secondary evidence is GREEN with pinned `qwen3-embedding:0.6b`;
ASCA / dense physical query counts are 1 / 3 and scored-vector counts are 3 / 9.
Physical evidence cannot change the frozen portable primary outcome.

## Current action

Task 6 — closure candidate and whole-branch review.

## Next action

Run whole-branch review, resolve every Critical/Important finding with RED→GREEN evidence, then integrate reviewed behavior to main.
