# A007 — Surprise, Uncertainty & Expansion

Status: ACTIVE
GitHub Issue: #7
Branch: research/a007-uncertainty-expansion

## Goal

Add deterministic structural-uncertainty assessment and a finite bounded
retrieval/working-set expansion controller over the qualified A005+A006 path.

## Scope

In scope:

- typed structural expansion triggers;
- frozen three-round expansion profile;
- STOP / EXPAND / EXHAUSTED assessment;
- NO_EXPANSION / SIGNAL_DRIVEN / ALWAYS_EXPAND policies;
- portable engineering benchmark;
- physical A005 + A006 SINGLE_BEST + A007 qualification.

A006 physical research outcome `NOT_SUPPORTED` remains authoritative for its
bounded-union convergence hypothesis. A007 therefore uses `SINGLE_BEST` as
the primary physical selector.

A007 does not fabricate scalar surprise/uncertainty values, does not populate
`UncertaintySignal`, does not lower the A005 threshold, does not build or
traverse a typed graph, and does not use `qwen3.5:4b` to generate cues or
judge expansion.

## Phases

- A007 contracts / frozen profile / task activation: DONE.
- Structural trigger derivation / controller: DONE.
- Bounded policy runner / controls: DONE.
- Portable benchmark / engineering qualification: ACTIVE.
- Physical A005+A006+A007 qualification: PLANNED.
- Exact qualification / review / integration: PLANNED.

## Frozen Primary Profile

A005 similarity threshold remains `0.5037018224299838`.

- round 0: cue tiers 1, `top_k = 12`, memory 8, working set 4;
- round 1: cue tiers 2, `top_k = 24`, memory 12, working set 8;
- round 2: cue tiers 3, `top_k = 32`, memory 16, working set 12;
- relation hops / nested expansions / model-input tokens = 0.

Physical model remains `qwen3-embedding:0.6b` with pinned A005 digest and
dimension. Cue texts/labels/profile are frozen before final physical outcomes.

## Acceptance Criteria

- [ ] Typed expansion contracts/profile are immutable and validated.
- [ ] Structural contradictions fail closed.
- [ ] Trigger ordering is deterministic.
- [ ] STOP / EXPAND / EXHAUSTED behavior is deterministic.
- [ ] NO_EXPANSION / SIGNAL_DRIVEN / ALWAYS_EXPAND preserve distinct policy termination semantics.
- [ ] No policy evaluates a speculative scope.
- [ ] Portable engineering fixture passes declared gates.
- [ ] Physical setup cost is separated from per-policy query/expansion cost.
- [ ] Valid physical outcome is exactly SUPPORTED, MIXED, or NOT_SUPPORTED.
- [ ] Negative physical outcome remains valid research evidence.
- [ ] A006 NOT_SUPPORTED conclusion is preserved.
- [ ] No prediction-surprise qualification claim is made.
- [ ] No typed graph or Qwen3.5:4b cue generation is introduced.
- [ ] FlyWireLLM remains paused and untouched.
- [ ] Exact branch/final-main CI and main synchronization gates pass.

## Evidence

Approved spec:

`docs/superpowers/specs/2026-10-09-a007-uncertainty-expansion-design.md`

Approved Native implementation plan:

`docs/superpowers/plans/2026-10-09-a007-uncertainty-expansion.md`

Activation baseline:

- base main: `8bdf87d19147cd30ccfbd8cd07238ab07c389dc0`;
- branch: `research/a007-uncertainty-expansion`;
- GitHub Issue: #7;
- A006 physical outcome: `NOT_SUPPORTED`;
- A005 threshold: `0.5037018224299838`;
- FlyWireLLM: paused/untouched.

## Current Action

Implement Task 4 portable A007 benchmark and engineering qualification gates
under TDD using deterministic fake scope evaluators only.

## Next Action

After portable qualification is GREEN and committed, implement the frozen
physical A005+A006+A007 qualification runner.

The next milestone after qualified A007 remains A008 — Procedural Memory /
Skill Chunking.
