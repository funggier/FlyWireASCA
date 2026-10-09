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
- Portable benchmark / engineering qualification: DONE.
- Physical A005+A006+A007 qualification: DONE.
- Exact qualification / review / integration: ACTIVE.

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

Physical qualification on behavior commit
`c29563fc3c2cf643338fdb21021d2f9e834d1cde`:

- experiment validity: PASS;
- primary A007 hypothesis outcome: `SUPPORTED`;
- fixture version: `a007-physical-v1`;
- fixture fingerprint:
  `59f95ef115534fe24e59570cb281c0564ab75aadf364f4c26feba0d4078213c9`;
- primary selector: `SINGLE_BEST`;
- model: `qwen3-embedding:0.6b`;
- full digest:
  `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`;
- Ollama runtime: `0.32.15`;
- embedding dimension: 1024;
- threshold: `0.5037018224299838`;
- NO_EXPANSION required-memory coverage:
  `0.5714285714285714`;
- SIGNAL_DRIVEN required-memory coverage: `1.0`;
- ALWAYS_EXPAND required-memory coverage: `1.0`;
- SIGNAL_DRIVEN recovery count: 3;
- SIGNAL_DRIVEN regression count: 0;
- easy unnecessary expansion count: 0;
- persistent-insufficient expected/exhausted: 1/1;
- ambiguity failure count: 0;
- deterministic logical replay: PASS;
- total rounds:
  - NO_EXPANSION: 8;
  - SIGNAL_DRIVEN: 15;
  - ALWAYS_EXPAND: 24.

Shared case-setup/index-build embedding evidence:

- requests: 8;
- inputs: 32;
- prompt tokens: 499;
- total duration: 4,385,491,900 ns;
- load duration: 2,614,980,600 ns.

Per-policy query evidence, excluding shared index build:

- NO_EXPANSION:
  - requests/inputs: 8/8;
  - prompt tokens: 239;
  - total duration: 984,632,200 ns;
  - load duration: 11,766,700 ns;
- SIGNAL_DRIVEN:
  - requests/inputs: 24/24;
  - prompt tokens: 727;
  - total duration: 1,075,732,500 ns;
  - load duration: 34,764,300 ns;
- ALWAYS_EXPAND:
  - requests/inputs: 48/48;
  - prompt tokens: 1,512;
  - total duration: 2,871,959,400 ns;
  - load duration: 70,010,300 ns.

Recovery cases were English, Thai, and cross-lingual; each failed to select
the declared required memory under NO_EXPANSION and recovered it under
SIGNAL_DRIVEN by round 1. The two easy cases stopped at round 0. The same-name
case preserved both memories. The persistent-insufficient case terminated
`CONTROLLER_EXHAUSTED` after round 2.

These request/input/token/timing values are workload-specific local backend
evidence. They are not FLOP, power, energy, or general speed claims.

## Current Action

Run Task 6 exact branch qualification on the physically qualified A007
candidate, publish the branch for exact portable CI, then write closure
evidence and perform whole-branch review.

## Next Action

After exact branch CI is GREEN, transition A007 DONE / A008 PLANNED, perform
the required whole-branch review/fix pass, and prepare integration.

The next milestone after qualified A007 remains A008 — Procedural Memory /
Skill Chunking.