# A007 — Surprise, Uncertainty & Expansion

Status: DONE
GitHub Issue: #7
Branch: research/a007-uncertainty-expansion

## Goal

Add deterministic structural-uncertainty assessment and a finite bounded
retrieval/working-set expansion controller over the qualified A005+A006 path.

## Scope

Delivered:

- typed structural expansion triggers;
- frozen three-round expansion profile;
- STOP / EXPAND / EXHAUSTED assessment;
- NO_EXPANSION / SIGNAL_DRIVEN / ALWAYS_EXPAND policies;
- portable engineering benchmark;
- physical A005 + A006 SINGLE_BEST + A007 qualification.

A006 physical research outcome `NOT_SUPPORTED` remains authoritative for its
bounded-union convergence hypothesis. A007 uses `SINGLE_BEST` as the primary
physical selector.

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
- Exact qualification / branch CI / closure candidate: DONE.
- Whole-branch review / final integration: pending external finishing gates.

## Frozen Primary Profile

A005 similarity threshold remains `0.5037018224299838`.

- round 0: cue tiers 1, `top_k = 12`, memory 8, working set 4;
- round 1: cue tiers 2, `top_k = 24`, memory 12, working set 8;
- round 2: cue tiers 3, `top_k = 32`, memory 16, working set 12;
- relation hops / nested expansions / model-input tokens = 0.

Primary selector: `SINGLE_BEST`.

A007 does not qualify scalar surprise or true prediction surprise.

## Acceptance Criteria

- [x] Typed expansion contracts/profile are immutable and validated.
- [x] Structural contradictions fail closed.
- [x] Trigger ordering is deterministic.
- [x] STOP / EXPAND / EXHAUSTED behavior is deterministic.
- [x] NO_EXPANSION / SIGNAL_DRIVEN / ALWAYS_EXPAND preserve distinct policy termination semantics.
- [x] No policy evaluates a speculative scope.
- [x] Portable engineering fixture passes declared gates.
- [x] Physical setup cost is separated from per-policy query/expansion cost.
- [x] Valid physical outcome is exactly SUPPORTED, MIXED, or NOT_SUPPORTED.
- [x] Physical primary outcome is `SUPPORTED` under the frozen rule.
- [x] A006 `NOT_SUPPORTED` conclusion is preserved.
- [x] No prediction-surprise qualification claim is made.
- [x] No typed graph or Qwen3.5:4b cue generation is introduced.
- [x] FlyWireLLM remains paused and untouched.
- [x] Exact branch CI passes.
- [ ] Whole-branch review Critical/Important findings resolved.
- [ ] Final-main CI and clean/synchronized 0/0 integration gates pass.

## Evidence

Approved spec:

`docs/superpowers/specs/2026-10-09-a007-uncertainty-expansion-design.md`

Approved Native implementation plan:

`docs/superpowers/plans/2026-10-09-a007-uncertainty-expansion.md`

Exact branch candidate:

`d76084178a3fca84208794efca7a46330785eb6e`

Exact branch CI:

`37940884611` — success

Fresh branch gates:

- pytest: 308 passed;
- architecture contract audit: PASS;
- repository qualification: PASS;
- A003 familiarity qualification: PASS;
- diff check: PASS.

Portable evidence:

- cases: 13;
- NO_EXPANSION coverage: 0.6666666666666666;
- SIGNAL_DRIVEN coverage: 1.0;
- ALWAYS_EXPAND coverage: 1.0;
- portable SIGNAL_DRIVEN recovery count: 2;
- regression count: 0;
- easy unnecessary expansion: 0;
- persistent expected/exhausted: 1/1;
- SIGNAL_DRIVEN rounds: 21;
- ALWAYS_EXPAND rounds: 33;
- deterministic repeat: PASS.

Physical evidence on behavior commit
`c29563fc3c2cf643338fdb21021d2f9e834d1cde`:

- experiment validity: PASS;
- final outcome: `SUPPORTED`;
- fixture: `a007-physical-v1`;
- fingerprint:
  `59f95ef115534fe24e59570cb281c0564ab75aadf364f4c26feba0d4078213c9`;
- model/digest:
  `qwen3-embedding:0.6b` /
  `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`;
- NO_EXPANSION coverage: 0.5714285714285714;
- SIGNAL_DRIVEN coverage: 1.0;
- ALWAYS_EXPAND coverage: 1.0;
- SIGNAL_DRIVEN recovery count: 3;
- SIGNAL_DRIVEN regression count: 0;
- easy unnecessary expansion: 0;
- persistent expected/exhausted: 1/1;
- ambiguity failures: 0;
- rounds NO/SIGNAL/ALWAYS: 8/15/24;
- setup embedding requests/inputs: 8/32;
- policy embedding requests NO/SIGNAL/ALWAYS: 8/24/48;
- policy embedding inputs NO/SIGNAL/ALWAYS: 8/24/48;
- deterministic logical replay: PASS.

These are local workload-specific measurements and do not imply FLOP, power,
energy, or general speed savings.

Detailed report:

`docs/development/reports/ASCA-20261009-A007-surprise-uncertainty-expansion.md`

## Current Action

A007 branch closure candidate is qualified. Perform the required whole-branch
review/fix pass and post-review exact CI before integration.

## Next Action

After review/integration gates are complete, A008 — Procedural Memory / Skill
Chunking remains PLANNED as a separate architectural task. Do not create its
GitHub issue automatically.
