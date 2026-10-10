# A010 — Dense/Non-selective Baseline Comparison

Status: DONE
GitHub Issue: #10 (closed as completed)
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
- [x] Whole-branch review GREEN.
- [x] Reviewed main integration and exact final-main CI GREEN.
- [x] Issue closed after final-main evidence.

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

## Whole-branch review evidence

Whole-branch review: GREEN

Review method: author self-review only; no independent reviewer/subagent mechanism was available in this harness.

- Critical findings: 0
- Important findings: 5 — fixed
- Minor findings: 1 — deferred documentation-formatting issue only
- post-review hardening SHA: `4db95323a0b5d8476c85f114a702f4371ab76ba9`
- exact post-review branch CI: `38017518584` — success
- local post-review full suite: `528 passed`
- post-review physical rerun: GREEN
- physical model: `qwen3-embedding:0.6b`
- physical ASCA / dense query counts: 1 / 3
- physical ASCA / dense scored-vector counts: 3 / 9
- portable primary outcome remains `NOT_SUPPORTED`

The five Important findings hardened frozen identity, shared-input fingerprint coverage, final-state correctness, A003 preservation in the structural ablation, and primary/diagnostic variant membership validation.

## Main integration evidence

Main integration: GREEN

- reviewed main SHA: `a0833c3b072ab27d331bfab9c3e8b8f509fac366`
- exact reviewed-main CI: `38017717305` — success
- merged-main local full suite: `529 passed`
- integration method: fast-forward only
- merge commit: none
- main behavior is identical to the reviewed feature SHA

Final-main evidence is GREEN and GitHub Issue #10 is closed as completed.

## Repository closure

A010 repository state: DONE

- GitHub Issue #10 closure: completed
- final-main evidence SHA: `fc41a238877e51599f451b811246129b77b006e1`
- exact final-main evidence CI: `38017919305` — success
- local final-main gate: `530 passed`
- A011 remains PLANNED with no GitHub issue

## Current action

A010 is closed with primary outcome `NOT_SUPPORTED`.

## Next action

A011 - ASCA v0.x Qualification may be activated later under a separate design/plan/task gate.
