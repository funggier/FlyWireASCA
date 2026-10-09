# A009 — Integrated Cognitive Loop

Status: ACTIVE
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

- [ ] Immutable A009 request/evidence/trace/result contracts validated.
- [ ] A003 familiarity is integrated without acting as a semantic-retrieval veto.
- [ ] A005 real vector-index path is exercised in portable integration.
- [ ] A006 `SINGLE_BEST` is the primary selector.
- [ ] A007 `SIGNAL_DRIVEN` remains the initial structural-expansion policy.
- [ ] A007 trigger vocabulary remains unchanged.
- [ ] A008 `CHUNKED` remains the primary procedure mode.
- [ ] A008 performs zero hidden automatic retry.
- [ ] Procedure mismatch becomes typed A009 recovery evidence.
- [ ] Recovery advances exactly one frozen scope at a time.
- [ ] Every replay has a unique execution ID and fresh snapshot-based executor.
- [ ] Maximum procedure attempts is 3.
- [ ] Deterministic portable A009 fixture is frozen and fingerprinted.
- [ ] Primary outcome is exactly SUPPORTED/MIXED/NOT_SUPPORTED.
- [ ] Valid MIXED/NOT_SUPPORTED is accepted as research evidence.
- [ ] Physical A005/A004 integration is qualified locally when prerequisites match.
- [ ] Model output is proven non-controlling.
- [ ] No real OS/API/LConnect/BConnect procedure action is introduced.
- [ ] A006/A007/A008 historical outcomes remain unchanged.
- [ ] FlyWireLLM remains untouched.
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

Task implementation evidence will be appended as Tasks 1-7 complete.

## Current Action

Task 1 is ACTIVE: add the core integrated-loop contracts and task activation
under TDD in the isolated A009 worktree.

## Next Action

Complete Task 1 RED -> GREEN gates and commit
`Activate A009 integrated cognitive loop contracts`, then continue Task 2
without pausing.

## Resume Rule

Use Git/GitHub/runtime as authoritative over stale prose. Resume from the first
unfinished task in the approved A009 plan and the ignored SDD progress ledger.
Do not reset/clean/rebase/force-push. Do not resume A008 Task 4. Do not modify
or restart FlyWireLLM.
