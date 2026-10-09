# A009 — Integrated Cognitive Loop

Status: DONE (closure candidate; Issue #9 remains open until exact final-main evidence)
GitHub Issue: #9
Branch: research/a009-integrated-cognitive-loop

## Goal

Integrate the qualified A003 familiarity, A005 vector retrieval, A006 working-set,
A007 bounded expansion, and A008 procedural-memory mechanisms into one bounded,
inspectable cognitive loop. Qualify whether an A008 checked procedure mismatch
can drive a higher-level bounded evidence expansion and fresh CHUNKED replay
without hidden retry or subsystem-boundary collapse.

Primary loop policy: `MISMATCH_DRIVEN_RECOVERY`.

Controls:

- `NO_PROCEDURE_RECOVERY`;
- `ALWAYS_MAX_SCOPE`.

Primary selector: `SINGLE_BEST`.

Primary procedural representation: `CHUNKED`.

Recovery event: `PROCEDURE_OUTCOME_MISMATCH`.

Maximum procedure attempts: 3.

## Scope

Approved design:

`docs/superpowers/specs/2026-10-10-a009-integrated-cognitive-loop-design.md`

Approved implementation plan:

`docs/superpowers/plans/2026-10-10-a009-integrated-cognitive-loop.md`

A009 preserves the already-qualified historical outcomes:

- A006: `NOT_SUPPORTED`;
- A007: `SUPPORTED`;
- A008: `SUPPORTED`.

A009 does not reinterpret A006 convergence evidence. `SINGLE_BEST` remains the
primary selector and `SELECTIVE_CONVERGENCE` is diagnostic only.

A009 does not add procedure mismatch to the A007 structural
`ExpansionTrigger` vocabulary. A009 owns procedure-mismatch recovery.

A008 remains zero-auto-retry. Every A009 replay is a separate procedure attempt
with a fresh execution ID and a fresh deterministic simulator constructed from
the same immutable pre-execution snapshot.

A009 v0.1 has no real OS/API/LConnect/BConnect action execution. The procedure
path remains deterministic simulation only.

A004 model generation is optional terminal-only diagnostic/fallback evidence.
It may not control retrieval scope, procedure identity, expected-outcome
verification, replay eligibility, deterministic termination, or the primary
A009 research outcome.

FlyWireLLM remains separate and untouched.

## Activation Evidence

Activation base:

`8d0721a77abaae5d0cc6d6c7c81d4795c5d355fa`

Activation-base exact main CI:

`37989472394` — success

Issue #9 was created only after the approved design/spec/plan gate and exact
activation-base CI were GREEN.

Isolated implementation worktree:

`T:\Space\Projects\ProjectsAI\FlyWireASCA-A009`

Implementation branch:

`research/a009-integrated-cognitive-loop`

Baseline before Task 1 implementation:

- worktree clean;
- HEAD = activation base;
- `python -m pytest -q`: 387 passed.

## Acceptance Criteria

- [x] Immutable A009 request/evidence/trace/result contracts validated.
- [x] A003 familiarity is integrated without acting as a semantic-retrieval veto.
- [x] A005 real vector-index path is exercised in portable integration.
- [x] A006 `SINGLE_BEST` is the primary selector.
- [x] A007 `SIGNAL_DRIVEN` remains the initial structural-expansion policy.
- [x] A007 trigger vocabulary remains unchanged.
- [x] A008 `CHUNKED` remains the primary procedure mode.
- [x] A008 performs zero hidden automatic retry.
- [x] Procedure mismatch becomes typed A009 recovery evidence.
- [x] Recovery advances exactly one frozen scope at a time.
- [x] Every replay has a unique execution ID and fresh snapshot-based executor.
- [x] Maximum procedure attempts is 3.
- [x] Deterministic portable A009 fixture is frozen and fingerprinted.
- [x] Primary outcome is exactly SUPPORTED/MIXED/NOT_SUPPORTED.
- [x] Valid MIXED/NOT_SUPPORTED is accepted as research evidence.
- [x] Physical A005/A004 integration is qualified locally when prerequisites match.
- [x] Model output is proven non-controlling.
- [x] No real OS/API/LConnect/BConnect procedure action is introduced.
- [x] A006/A007/A008 historical outcomes remain unchanged.
- [x] FlyWireLLM remains untouched.
- [ ] Exact branch CI, whole-branch review, final-main CI and synchronization pass.

## Evidence

Design commit sequence on main:

- `00c8aa9` — Design A009 integrated cognitive loop;
- `f58316f` — Harden A009 memory requirement contract.

Plan commit:

- `8d0721a` — Plan A009 integrated cognitive loop.

Exact plan-gate CI:

- run `37989472394`;
- conclusion: success.

Task 1: `394e91f` — Activate A009 integrated cognitive loop contracts. Full Task 1 gate: 401 passed; architecture/repository/A003/A008 gates PASS.

Task 2: `80b4ac1` — Add A009 integrated retrieval expansion. Full Task 2 gate: 410 passed; architecture/repository/A003/A008 gates PASS.

Task 3: `931211e` — Add A009 context-bound procedure replay. Full Task 3 gate: 417 passed; architecture/repository/A008 gates PASS.

Task 4: `7b3b35a` — Add A009 bounded cognitive controller. Full Task 4 gate: 428 passed; architecture/repository/A003/A008 gates PASS.

Task 5: `eecca7d842753fd2b39e8c565c704fb2e6303896` — Add A009 integrated loop qualification. Frozen fixture fingerprint: `2f92b5092de346f62879ac2cbb9f96d6de5d6f919e12d0693345c8228b01ab2a`. Portable primary outcome: `SUPPORTED`. Task 5 full gate: 455 passed; architecture/repository/A003/A008 gates PASS.

Exact branch qualification: GREEN.
- SHA: `eecca7d842753fd2b39e8c565c704fb2e6303896`;
- exact branch CI: `37992245085` — success;
- genuine recoveries: 2;
- regressions: 0;
- primary / always-max total scope evaluations: 19 / 27;
- primary / always-max successful cases: 6 / 6;
- maximum procedure attempts: 3;
- maximum scope index: 2;
- model-control leakage failures: 0.

Physical qualification: GREEN.
- embedding: `qwen3-embedding:0.6b`;
- embedding digest: `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`;
- embedding dimension: 1024;
- frozen threshold: `0.5037018224299838`;
- terminal model: `qwen3.5:4b`;
- terminal model digest: `2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd`;
- physical integrated success case: GREEN;
- physical terminal-fallback case: GREEN;
- terminal model request count: 1.

Whole-branch review: GREEN.
- method: author self-review; no independent reviewer/subagent was available;
- Critical findings: 0;
- Important findings: 5;
- reviewed behavior SHA: `4796d28e9285dc395240010987126a45c4e5ed5d`;
- exact post-review CI: `37999918527` - success;
- post-review full suite: 463 passed;
- post-review portable fingerprint unchanged:
  `2f92b5092de346f62879ac2cbb9f96d6de5d6f919e12d0693345c8228b01ab2a`;
- post-review primary outcome: `SUPPORTED`;
- post-review physical qualification: GREEN;
- A007/A008 source unchanged from activation base;
- review fixes cover completed-primitive evidence, fail-closed replay/snapshot
  result invariants, exact terminal-model digest pin, aggregate-vs-case
  evidence recomputation, and raw `model_control_isolated` evidence;
- final-main integration/CI/synchronization remain pending.

Qualification report:
`docs/development/reports/ASCA-20261010-A009-integrated-cognitive-loop.md`.

## Current Action

A009 is a DONE closure candidate with exact branch qualification, physical
integration, whole-branch author self-review, and exact post-review branch CI
GREEN. Issue #9 intentionally remains open while Task 7 performs reviewed
final-main integration and synchronization.

A010 remains PLANNED and has no GitHub issue.

## Next Action

Execute the remaining A009 Task 7 integration steps: verify clean/synchronized
main preconditions, fast-forward main only, rerun merged-main gates, push main,
require exact final-main CI, record final-main evidence, synchronize 0/0, and
only then close Issue #9.

## Resume Rule

Use Git/GitHub/runtime as authoritative over stale prose. Resume from the first
unfinished task in the approved A009 plan and the ignored SDD progress ledger.
Do not reset/clean/rebase/force-push. Do not resume A008 Task 4. Do not modify
or restart FlyWireLLM.
