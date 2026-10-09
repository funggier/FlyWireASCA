# FlyWireASCA A007 Surprise, Uncertainty & Expansion Qualification

Date: 2026-10-09
Task: A007 — Surprise, Uncertainty & Expansion
GitHub Issue: #7
Branch: research/a007-uncertainty-expansion

## Decision

A007 engineering qualification is GREEN on exact branch candidate:

`d76084178a3fca84208794efca7a46330785eb6e`

Exact branch CI:

`37940884611` — success

The A007 structural expansion controller is implemented as a deterministic,
bounded three-round policy over the qualified A005 retrieval and A006
`SINGLE_BEST` selector.

**Primary physical research result: `SUPPORTED`**

Under the frozen physical fixture, SIGNAL_DRIVEN expansion recovered three
declared required memories missed by NO_EXPANSION, produced zero regressions,
matched ALWAYS_EXPAND required-memory coverage, caused zero unnecessary
expansion on initially sufficient cases, exhausted the persistent-insufficient
case correctly, and executed fewer total rounds than ALWAYS_EXPAND.

This physical result does not rewrite the A006 finding. A006 remains
`NOT_SUPPORTED` for its separate bounded-union convergence-vs-SINGLE_BEST
hypothesis.

## Scope actually qualified

A007 v0.1 qualifies **structural uncertainty-driven bounded expansion** only.

Structural expansion triggers are derived from:

- `INSUFFICIENT_EVIDENCE`;
- memory-budget truncation;
- working-set-budget truncation;
- memory boundary ties;
- working-set boundary ties.

The controller emits:

- `STOP`;
- `EXPAND`;
- `EXHAUSTED`.

Prediction surprise is not qualified in A007 v0.1.

A007 does not assign a scalar uncertainty or surprise score. Existing A002
`UncertaintySignal` is not populated with invented values.

A007 does not:

- lower the A005 similarity threshold;
- generate cues with `qwen3.5:4b`;
- ask `qwen3.5:4b` to judge evidence sufficiency or expansion;
- create or traverse a typed graph;
- alter A005 vector-retrieval semantics;
- alter A006 SINGLE_BEST semantics.

## Qualified architecture

```text
predeclared cue tiers
       |
       v
A005 vector retrieval
       |
       v
A006 SINGLE_BEST
       |
       v
A007 structural assessment
       |
       +-- no trigger ----------------> STOP
       |
       +-- trigger + next scope ------> EXPAND
       |
       +-- trigger + max scope -------> EXHAUSTED
```

Policy controls:

- `NO_EXPANSION`: evaluate round 0 only;
- `SIGNAL_DRIVEN`: obey controller decisions;
- `ALWAYS_EXPAND`: evaluate all three scopes.

Controller assessment is recorded independently from policy termination. This
prevents baseline behavior from being mislabeled as a controller decision.

## Frozen expansion profile

Similarity threshold remains:

`0.5037018224299838`

Primary selector:

`SINGLE_BEST`

Frozen profile:

| Round | Cue tiers | top_k | max_memory_nodes | max_working_set_items |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 1 | 12 | 8 | 4 |
| 1 | 2 | 24 | 12 | 8 |
| 2 | 3 | 32 | 16 | 12 |

Every scope uses:

- relation hops = 0;
- nested A006 expansions = 0;
- model-input tokens = 0.

The controller permits at most two expansions after the initial round.

## Portable engineering qualification

Portable fixture:

- case count: 13;
- total declared required-memory IDs: 6;
- NO_EXPANSION required-memory coverage: 0.6666666666666666;
- SIGNAL_DRIVEN required-memory coverage: 1.0;
- ALWAYS_EXPAND required-memory coverage: 1.0;
- portable SIGNAL_DRIVEN recovery count: 2;
- portable SIGNAL_DRIVEN regression count: 0;
- easy unnecessary expansion count: 0;
- persistent-insufficient expected/exhausted: 1/1;
- ambiguity failure count: 0;
- structural validation failure count: 0;
- max SIGNAL_DRIVEN rounds: 3;
- portable NO_EXPANSION total rounds: 11;
- portable SIGNAL_DRIVEN total rounds: 21;
- portable ALWAYS_EXPAND total rounds: 33;
- NO_EXPANSION policy termination count: 11;
- ALWAYS_EXPAND policy termination count: 11;
- SIGNAL_DRIVEN controller stop count: 10;
- SIGNAL_DRIVEN controller exhausted count: 1;
- deterministic repeat: PASS.

Portable qualification is an engineering correctness gate. It does not by
itself determine the physical research outcome.

## Frozen physical identity

Physical model:

`qwen3-embedding:0.6b`

Full digest:

`ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`

Observed local backend:

- Ollama runtime: `0.32.15`;
- architecture: `qwen3`;
- parameter count: 595,776,512;
- parameter size: `595.78M`;
- quantization: `Q8_0`;
- context length: 32768;
- embedding dimension: 1024.

Physical fixture:

- version: `a007-physical-v1`;
- fingerprint:
  `59f95ef115534fe24e59570cb281c0564ab75aadf364f4c26feba0d4078213c9`.

The final fixture contains:

- English easy;
- Thai easy;
- English later-tier recovery;
- Thai later-tier recovery;
- cross-lingual recovery;
- budget truncation;
- same-name ambiguity;
- persistent insufficient.

No threshold/profile/cue text/fixture label was changed after observing the
final physical outcome.

## Physical research result

Experiment validity: PASS.

Primary result:

- NO_EXPANSION required-memory coverage: 0.5714285714285714
- SIGNAL_DRIVEN required-memory coverage: 1.0
- ALWAYS_EXPAND required-memory coverage: 1.0
- SIGNAL_DRIVEN recovery count: 3
- SIGNAL_DRIVEN regression count: 0
- easy unnecessary expansion count: 0
- persistent-insufficient expected/exhausted: 1/1
- ambiguity failure count: 0
- deterministic logical replay: PASS
- NO_EXPANSION total rounds: 8
- SIGNAL_DRIVEN total rounds: 15
- ALWAYS_EXPAND total rounds: 24

The three physical recovery cases were:

- English;
- Thai;
- cross-lingual.

Each omitted its declared required memory under NO_EXPANSION and recovered it
after a later predeclared cue tier under SIGNAL_DRIVEN.

Both easy cases stopped after round 0.

The same-name ambiguity case retained both distinct memories.

The persistent-insufficient case evaluated all three scopes and terminated with
`CONTROLLER_EXHAUSTED`, with no hidden fourth round.

## Physical cost evidence

The document-index build is shared case setup and is reported separately from
policy execution.

Shared setup across the eight cases:

- setup embedding requests: 8
- setup embedding inputs: 32
- setup prompt tokens: 499
- setup total duration: 4,385,491,900 ns
- setup load duration: 2,614,980,600 ns

Policy query work, excluding shared index build:

### NO_EXPANSION

- embedding requests: 8
- embedding inputs: 8
- prompt tokens: 239
- total duration: 984,632,200 ns
- load duration: 11,766,700 ns

### SIGNAL_DRIVEN

- SIGNAL_DRIVEN embedding requests: 24
- embedding inputs: 24
- prompt tokens: 727
- total duration: 1,075,732,500 ns
- load duration: 34,764,300 ns

### ALWAYS_EXPAND

- ALWAYS_EXPAND embedding requests: 48
- embedding inputs: 48
- prompt tokens: 1,512
- total duration: 2,871,959,400 ns
- load duration: 70,010,300 ns

The measured physical fixture therefore used 15 SIGNAL_DRIVEN rounds versus 24
ALWAYS_EXPAND rounds, and 24 policy query embedding requests versus 48.

These are workload-specific round/request/input/token/backend timing
measurements. They are not evidence of FLOP, electrical power, energy, or
general hardware-performance savings.

## Physical per-case outcome

### physical-en-easy

Required memory selected by all policies.

SIGNAL_DRIVEN rounds: 1.

Termination: `CONTROLLER_STOP`.

### physical-th-easy

Required memory selected by all policies.

SIGNAL_DRIVEN rounds: 1.

Termination: `CONTROLLER_STOP`.

### physical-en-recovery

NO_EXPANSION selected no required memory.

SIGNAL_DRIVEN recovered `en-recovery-target` in round 1 and stopped.

### physical-th-recovery

NO_EXPANSION selected no required memory.

SIGNAL_DRIVEN recovered `th-recovery-target` in round 1 and stopped.

### physical-cross-lingual-recovery

NO_EXPANSION selected no required memory.

SIGNAL_DRIVEN recovered `cross-recovery-target` in round 1 and stopped.

### physical-budget-truncation

Round 0 was PARTIAL_RECALL with memory and working-set truncation.

Round 1 remained PARTIAL_RECALL because the working set was still truncated.

Round 2 became RECALLED and stopped.

This case has no arbitrarily declared required memory ID; it is an engineering
scope/budget case.

### physical-same-name-ambiguity

Both `somchai-a` and `somchai-b` remained present.

SIGNAL_DRIVEN stopped in round 0.

No same-person identity claim was inferred.

### physical-persistent-insufficient

No positive candidate passed the frozen threshold in any round.

SIGNAL_DRIVEN reached round 2 and terminated
`CONTROLLER_EXHAUSTED`.

## Why the primary outcome is SUPPORTED

The outcome rules were frozen before the live run.

All SUPPORT conditions passed:

1. at least one declared recovery: PASS — 3;
2. SIGNAL_DRIVEN regression count = 0: PASS;
3. SIGNAL_DRIVEN coverage equals ALWAYS_EXPAND coverage: PASS — 1.0 vs 1.0;
4. easy unnecessary expansion count = 0: PASS;
5. persistent-insufficient bounded exhaustion: PASS — 1/1;
6. SIGNAL_DRIVEN total rounds < ALWAYS_EXPAND total rounds:
   PASS — 15 < 24.

Therefore:

**Final A007 hypothesis outcome: `SUPPORTED`**

This is fixture-scoped evidence for structural signal-driven expansion. It is
not a general claim that every adaptive retrieval controller is superior.

## Exact branch qualification

Candidate SHA:

`d76084178a3fca84208794efca7a46330785eb6e`

Fresh local branch gates:

- `python -m pytest -q`: **308 passed**
- architecture contract audit: PASS
- repository qualification: PASS
- A003 familiarity qualification: PASS
- `git diff --check HEAD^ HEAD`: PASS
- worktree: clean

Exact branch CI:

- run: `37940884611`
- head SHA: `d76084178a3fca84208794efca7a46330785eb6e`
- conclusion: **success**

GitHub CI remains portable. It does not execute the local A007 physical
qualification script.

## Isolation evidence

A007 branch diff from base
`8bdf87d19147cd30ccfbd8cd07238ab07c389dc0`
contains no changes under:

- A004 model adapter;
- A005 embedding/vector-memory implementation;
- A006 selective-activation implementation;
- A004/A005/A006 physical qualification scripts;
- the A006 closure report.

A006 therefore retains:

**Final A006 hypothesis outcome: `NOT_SUPPORTED`**

for its distinct convergence-vs-SINGLE_BEST question.

FlyWireLLM was checked read-only before branch publication:

- HEAD: `9aa8acba1ecdefcdce4678b2914fc2d2dcaacc14`;
- branch: `research/l004-base50m-pretraining`;
- clean: yes;
- ahead/behind: 0/0;
- no FlyWireLLM training runner observed.

FlyWireLLM remains paused and untouched by A007.

## Claims boundary

A007 does not qualify true prediction surprise.

A007 does not claim calibrated scalar uncertainty, scalar surprise, or risk.

A007 does not claim biological attention or human-like cognition.

A007 does not claim fewer rounds or requests imply lower FLOPs, lower power,
lower energy, or universal speed improvement.

A007 demonstrates only the declared structural-trigger behavior and measured
fixture-specific recovery/cost evidence.

## Deferred questions

A007 does not answer:

- whether a prediction monitor can produce a defensible surprise signal;
- whether procedure execution failures should drive the same controller;
- whether threshold relaxation is useful;
- whether generative query reformulation is useful;
- whether graph traversal should become an expansion action;
- whether the same policy gains persist on larger or different workloads;
- whether fewer retrieval rounds reduce hardware compute or energy.

Those remain future research questions.

## Next milestone

A008 — Procedural Memory / Skill Chunking remains **PLANNED**.

A008 may later provide real expected outcomes and execution failures that can
support richer prediction-surprise semantics.

## Whole-branch review and post-review qualification

The required final whole-branch review was performed as a separate author
self-review because no fresh reviewer/subagent tool was available in this
harness.

Two findings were graded **Important**:

1. the physical validator accepted any vocabulary-valid hypothesis outcome and
   did not recompute the frozen outcome from aggregate evidence, so
   research-outcome drift could be emitted as structurally valid;
2. metric validation accepted nonnegative counters without rejecting impossible
   metric-counter relationships such as observed-response counts exceeding
   embedding requests or positive embedding inputs with zero requests.

Both findings were fixed under RED -> GREEN tests. The hardened behavior
candidate is:

`5495ca909d141a8ad27dd29863d3926f24254b46`

The validator now:

- recomputes the expected `SUPPORTED / MIXED / NOT_SUPPORTED` result from the
  frozen recovery/regression/coverage/easy/persistent/round aggregates and
  rejects research-outcome drift;
- rejects impossible embedding metric-counter relationships while preserving
  the setup-vs-policy accounting boundary.

Exact post-review branch CI:

`37942219656` — success

Head SHA:

`5495ca909d141a8ad27dd29863d3926f24254b46`

Because validation behavior changed, the frozen physical qualification was run
again on this post-review HEAD.

Post-review physical rerun:

- experiment validity: PASS;
- primary outcome: `SUPPORTED`;
- fixture fingerprint unchanged:
  `59f95ef115534fe24e59570cb281c0564ab75aadf364f4c26feba0d4078213c9`;
- SIGNAL_DRIVEN recovery count: 3;
- SIGNAL_DRIVEN regression count: 0;
- required-memory coverage NO/SIGNAL/ALWAYS:
  `0.5714285714285714 / 1.0 / 1.0`;
- easy unnecessary expansion count: 0;
- persistent-insufficient exhaustion: 1/1;
- ambiguity failures: 0;
- deterministic logical replay: PASS;
- rounds: 8/15/24 for NO_EXPANSION / SIGNAL_DRIVEN / ALWAYS_EXPAND;
- setup embedding requests/inputs: 8/32;
- SIGNAL_DRIVEN embedding requests/inputs: 24/24;
- ALWAYS_EXPAND embedding requests/inputs: 48/48.

Backend timing values varied between physical runs and are not part of the
logical determinism claim. The frozen fixture, threshold, selector, scope ladder,
required-memory outcomes, and policy-round aggregates remained unchanged.

## Main integration evidence

A007 was fast-forward integrated into `main` from the reviewed branch.

Merged main behavior/evidence SHA:

`61cf9053b39f8d4aed413058cd99e4ec664c8a42`

Fresh local merged-main gates:

- `python -m pytest -q`: **318 passed**;
- architecture contract audit: PASS;
- repository qualification: PASS;
- A003 familiarity qualification: PASS;
- `git diff --check origin/main..HEAD`: PASS;
- main worktree: clean before push;
- main was synchronized 0/0 before integration.

Exact first final-main CI:

- run: `37945417867`;
- head SHA: `61cf9053b39f8d4aed413058cd99e4ec664c8a42`;
- conclusion: **success**.

This proves the reviewed A007 tree passed the portable CI gates after
fast-forward integration into main. A documentation-only closure-evidence
commit may follow and is required to receive its own exact-main CI before
Issue #7 is closed.

## Closure-evidence main CI

The documentation-only main integration evidence commit is:

`794428389e632c241fbd8c15100b86c84cbd7dd4`

Exact CI for that evidence commit:

- run: `37945872610`;
- head SHA: `794428389e632c241fbd8c15100b86c84cbd7dd4`;
- conclusion: **success**.

This CI validates the repository state that records the first merged-main
behavior CI and integration evidence. One final ledger commit records this
closure-evidence CI; Issue #7 remains open until that final ledger commit also
receives exact-main CI and main is clean/synchronized 0/0.
