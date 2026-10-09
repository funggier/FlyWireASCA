# A007 Surprise, Uncertainty & Expansion Design Specification

Date: 2026-10-09
Status: DESIGN FOR USER REVIEW
Planned task: A007 — Surprise, Uncertainty & Expansion
Branch: research/a007-uncertainty-expansion
Base: ASCA main at 8bdf87d19147cd30ccfbd8cd07238ab07c389dc0

## 1. Purpose

A007 adds a deterministic controller that decides whether an initially bounded
retrieval/working-set route should stop, expand once more, or terminate because
its declared expansion budget is exhausted.

A007 is motivated by the original ASCA hypothesis that uncertainty or failed
retrieval should be allowed to increase retrieval/reasoning scope, while easy
predictable cases should remain narrow.

A007 v0.1 intentionally tests only **structural uncertainty-driven retrieval
expansion**. It does not claim to implement prediction surprise, subjective
uncertainty, calibrated epistemic uncertainty, or risk estimation.

The research question is:

> Can explicit structural retrieval signals trigger bounded expansion that
> recovers useful memory after an initially insufficient route, while avoiding
> unnecessary expansion on easy cases and terminating deterministically when
> recovery remains impossible?

## 2. Historical numbering note

The original architecture design written before the local-model milestone was
inserted called this milestone A006.

The live roadmap is authoritative:

- A004 — Local Model Adapter & Qwen3.5:4B Baseline
- A005 — Semantic Vector Memory Retrieval
- A006 — Working Set / Selective Activation
- **A007 — Surprise, Uncertainty & Expansion**

Historical architecture documents are not rewritten merely to renumber old
research milestones.

## 3. Architectural decision

A007 uses **typed structural signals + a frozen bounded expansion ladder**.

The core flow is:

```text
predeclared cue tier(s)
        |
        v
A005 Vector Retrieval
        |
        v
A006 SINGLE_BEST Working Set
        |
        v
A007 Structural Assessment
        |
        +-- no trigger ----------------------> STOP
        |
        +-- trigger + next scope available --> EXPAND
        |                                      |
        |                                      v
        |                              next frozen scope
        |                                      |
        +--------------------------------------+
        |
        +-- trigger + no scope left ----------> EXHAUSTED
```

A007 does not generate a new cue with an LLM and does not change the A005
similarity threshold.

## 4. Why SINGLE_BEST is the primary A007 selector

A006 qualified the selective-activation subsystem as engineering-correct, but
its frozen physical research result was:

`NOT_SUPPORTED`

for the claim that bounded-union multi-query convergence improves required
memory selection over `SINGLE_BEST`.

A007 therefore uses `SINGLE_BEST` as the primary physical selector.

`SELECTIVE_CONVERGENCE` remains available as a secondary control or diagnostic
comparison. A007 must not silently promote it to the default selector merely
because it exists.

This keeps A007 attributable to expansion policy rather than to an A006 policy
whose physical selection advantage has not been demonstrated.

## 5. What “uncertainty” means in A007 v0.1

A007 v0.1 uses only structural uncertainty that is directly observable from
A006 output.

Initial trigger vocabulary:

- `INSUFFICIENT_EVIDENCE`
- `MEMORY_BUDGET_TRUNCATED`
- `WORKING_SET_BUDGET_TRUNCATED`
- `MEMORY_BOUNDARY_TIE`
- `WORKING_SET_BOUNDARY_TIE`

These are operational reasons to reconsider the current retrieval scope.

They are not probabilities.

A007 does not combine them into an arbitrary scalar uncertainty score.

## 6. Existing UncertaintySignal contract

A002 already defines:

```python
UncertaintySignal(
    uncertainty: float,
    surprise: float,
    risk: float,
    reasons: tuple[str, ...],
)
```

A007 v0.1 does not modify or populate this record merely to satisfy the project
name.

The scalar contract remains reserved for future stages that have defensible
sources for those values, such as:

- prediction-vs-observation mismatch;
- procedure outcome failure;
- calibrated model confidence;
- explicit risk policy.

A007 structural triggers are represented by a new typed vocabulary instead.

## 7. Surprise boundary

A007 keeps “Surprise” in the milestone title because it is part of the planned
ASCA controller family, but **prediction surprise is not qualified in A007
v0.1**.

There is not yet a complete Prediction Monitor producing expected-vs-observed
state.

A007 must therefore not fake prediction mismatch using retrieval scores.

True prediction surprise is deferred until a later stage, most naturally after
procedural execution and/or the integrated loop can generate an expected
outcome and a real observation.

## 8. Trigger enum

A007 introduces:

```python
class ExpansionTrigger(str, Enum):
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    MEMORY_BUDGET_TRUNCATED = "MEMORY_BUDGET_TRUNCATED"
    WORKING_SET_BUDGET_TRUNCATED = "WORKING_SET_BUDGET_TRUNCATED"
    MEMORY_BOUNDARY_TIE = "MEMORY_BOUNDARY_TIE"
    WORKING_SET_BOUNDARY_TIE = "WORKING_SET_BOUNDARY_TIE"
```

Trigger tuples are canonical, unique, and sorted by the explicit enum order
above rather than alphabetically.

No free-form trigger string controls behavior.

## 9. Decision enum

A007 introduces:

```python
class ExpansionDecisionKind(str, Enum):
    STOP = "STOP"
    EXPAND = "EXPAND"
    EXHAUSTED = "EXHAUSTED"
```

Semantics:

- `STOP`: current result has no structural expansion trigger.
- `EXPAND`: at least one trigger exists and another frozen scope is available.
- `EXHAUSTED`: trigger(s) remain but the profile has no wider scope.

`EXHAUSTED` is a normal bounded outcome, not an exception.

## 10. Supported A006 retrieval states

A007 v0.1 accepts A006 results whose `WorkingSet.retrieval_state` is:

- `RECALLED`
- `PARTIAL_RECALL`
- `INSUFFICIENT_EVIDENCE`

Other retrieval states are rejected in v0.1 because A006 does not currently
produce them and A007 has no validated policy for them.

In particular, A007 does not invent behavior for:

- `CONFLICTING_RECALL`
- `KNOWN_BUT_NOT_RECALLED`
- `UNFAMILIAR`
- `FAMILIAR`

Those can be integrated later when the corresponding producer is part of the
same qualified loop.

## 11. Structural trigger derivation

Given a `SelectiveWorkingSetResult`, triggers are derived exactly as follows.

### INSUFFICIENT_EVIDENCE

Present when:

`working_set.retrieval_state == INSUFFICIENT_EVIDENCE`

For a valid A006 result this corresponds to zero positive selected evidence.

### MEMORY_BUDGET_TRUNCATED

Present when:

`dropped_by_memory_budget_count > 0`

### WORKING_SET_BUDGET_TRUNCATED

Present when:

`dropped_by_working_set_budget_count > 0`

### MEMORY_BOUNDARY_TIE

Present when:

`memory_budget_boundary_tie is True`

### WORKING_SET_BOUNDARY_TIE

Present when:

`working_set_boundary_tie is True`

A boundary tie is additional evidence, not a replacement for its associated
truncation trigger.

## 12. Fail-closed consistency checks

A007 rejects structurally inconsistent A006 inputs.

Examples:

- `RECALLED` with a positive budget-drop count;
- `PARTIAL_RECALL` with no positive budget-drop count;
- `INSUFFICIENT_EVIDENCE` with selected working-set entries;
- a memory-boundary tie with no memory-budget drop;
- a working-set-boundary tie with no working-set-budget drop.

A007 does not repair these states silently.

## 13. Expansion scope

A007 introduces an immutable `ExpansionScope` conceptually equivalent to:

```python
ExpansionScope(
    round_index: int,
    enabled_cue_tier_count: int,
    top_k: int,
    budget: ActivationBudget,
)
```

Requirements:

- `round_index >= 0`;
- `enabled_cue_tier_count > 0`;
- `top_k > 0`;
- A007 remains no-graph:
  - `max_relation_hops == 0`;
- model context is not assembled:
  - `max_model_input_tokens == 0`;
- `max_expansions` in the per-round A006 budget remains 0 because the A007
  runner itself owns round expansion;
- `max_working_set_items <= max_memory_nodes`.

## 14. Frozen A007 v0.1 expansion ladder

The primary A007 profile is:

### Round 0 — BASE

- enabled cue tiers: 1
- A005 `top_k = 12`
- A006 `max_memory_nodes = 8`
- A006 `max_working_set_items = 4`

### Round 1 — WIDEN

- enabled cue tiers: 2
- A005 `top_k = 24`
- A006 `max_memory_nodes = 12`
- A006 `max_working_set_items = 8`

### Round 2 — MAX

- enabled cue tiers: 3
- A005 `top_k = 32`
- A006 `max_memory_nodes = 16`
- A006 `max_working_set_items = 12`

All rounds use:

- `max_relation_hops = 0`
- `max_expansions = 0`
- `max_model_input_tokens = 0`

The ladder allows exactly two expansions after the initial round.

No fourth round exists in A007 v0.1.

## 15. Similarity threshold is frozen

A007 retains the qualified A005 physical threshold:

`0.5037018224299838`

A007 does not lower the threshold during expansion.

Reason:

Lowering the threshold at the same time as widening cue breadth, top_k, and
working-set budgets would confound two distinct hypotheses:

1. “more search scope helps”;
2. “accepting weaker semantic matches helps.”

Threshold relaxation, if needed, must be a separate research variable.

## 16. Cue tiers

Cue text is supplied in predeclared tiers.

Conceptually:

```python
ExpansionCueTier(
    tier_index: int,
    cues: tuple[ExpansionCue, ...],
)
```

A physical benchmark case contains exactly three ordered tiers for the primary
profile.

Round N enables tiers `0..enabled_cue_tier_count-1`.

A007 never asks Qwen3.5:4b to invent a new query.

Cue tiers are frozen before the final physical run.

## 17. Cue identity and replay

Each cue has:

- `source_cue_id`
- `query_id`
- `query_text`

IDs are unique across the whole case.

When a wider round enables an earlier tier again, the same cue identity and
text are reused.

Because `top_k` grows across rounds, previously enabled cues are searched
again under the new round scope rather than assuming the narrower result is
equivalent.

This makes each round a complete auditable evaluation of its declared scope.

## 18. Decision record

A007 produces an immutable record conceptually equivalent to:

```python
ExpansionDecision(
    round_index: int,
    kind: ExpansionDecisionKind,
    triggers: tuple[ExpansionTrigger, ...],
    current_scope: ExpansionScope,
    next_scope: ExpansionScope | None,
)
```

Invariants:

- `STOP` has no triggers and no next scope;
- `EXPAND` has at least one trigger and a next scope;
- `EXHAUSTED` has at least one trigger and no next scope;
- `next_scope.round_index == current_scope.round_index + 1` for `EXPAND`.

## 19. Assessment interface

Primary pure interface:

```python
assess_expansion(
    result: SelectiveWorkingSetResult,
    *,
    current_scope: ExpansionScope,
    next_scope: ExpansionScope | None,
) -> ExpansionDecision
```

This function does not perform retrieval itself.

It is deterministic and side-effect free.

## 20. Runner interface

A007 also introduces a bounded policy runner.

Conceptually:

```python
run_signal_driven_expansion(
    profile: ExpansionProfile,
    evaluate_scope: Callable[[ExpansionScope], SelectiveWorkingSetResult],
) -> ExpansionRunResult
```

The callback is responsible for A005 retrieval + A006 selection for that scope.
It is called exactly once for every scope that the selected policy evaluates.
The runner never invokes it speculatively for a scope that is not part of that
policy's executed path.

The controller:

1. evaluates round 0;
2. derives structural triggers;
3. stops, expands, or exhausts;
4. never evaluates a scope after STOP;
5. evaluates each scope at most once;
6. terminates after at most three rounds in the v0.1 profile.

Portable unit tests use a fake callback.

Physical qualification uses a real A005+A006 callback.

## 21. Expansion run evidence

A007 records each round explicitly.

Conceptually:

```python
ExpansionRoundResult(
    scope: ExpansionScope,
    working_set_result: SelectiveWorkingSetResult,
    decision: ExpansionDecision,
)
```

Final run:

```python
ExpansionRunResult(
    policy: ExpansionPolicy,
    rounds: tuple[ExpansionRoundResult, ...],
    final_result: SelectiveWorkingSetResult,
    final_assessment: ExpansionDecision,
    termination_reason: ExpansionTerminationReason,
)
```

`final_assessment` is the structural assessment of the last evaluated round.
It is not always the reason a control baseline stopped.

A007 therefore also records:

```python
class ExpansionTerminationReason(str, Enum):
    CONTROLLER_STOP = "CONTROLLER_STOP"
    CONTROLLER_EXHAUSTED = "CONTROLLER_EXHAUSTED"
    POLICY_NO_EXPANSION = "POLICY_NO_EXPANSION"
    POLICY_MAX_SCOPE = "POLICY_MAX_SCOPE"
```

This distinction matters for the control policies:

- NO_EXPANSION can terminate with `POLICY_NO_EXPANSION` even when its last
  structural assessment is `EXPAND`;
- ALWAYS_EXPAND may continue after a `STOP` assessment and terminates at the
  maximum scope with `POLICY_MAX_SCOPE`;
- SIGNAL_DRIVEN terminates only with `CONTROLLER_STOP` or
  `CONTROLLER_EXHAUSTED`.

No hidden retry or hidden extra round is permitted.

## 22. Policy baselines

A007 compares three policies.

### NO_EXPANSION

- evaluate round 0 only;
- return its result;
- do not expand even when structural triggers exist.

Purpose: baseline for whether A007 recovery adds value.

### ALWAYS_EXPAND

- evaluate round 0, round 1, and round 2 in order;
- do not stop early;
- final output is round 2.

Purpose: upper-scope control and cost baseline.

### SIGNAL_DRIVEN

- evaluate round 0;
- use A007 decisions;
- stop when no trigger exists;
- otherwise advance one frozen scope at a time;
- terminate with `EXHAUSTED` if structural triggers remain at round 2.

Purpose: test whether structural signals can recover useful evidence without
always paying maximal expansion cost.

## 23. Policy enum

A007 introduces:

```python
class ExpansionPolicy(str, Enum):
    NO_EXPANSION = "NO_EXPANSION"
    SIGNAL_DRIVEN = "SIGNAL_DRIVEN"
    ALWAYS_EXPAND = "ALWAYS_EXPAND"
```

The policy is always recorded in qualification evidence.

## 24. Selector policy inside physical A007

Primary physical qualification uses:

`SINGLE_BEST`

at every round for all three expansion policies.

This prevents the A006 `SELECTIVE_CONVERGENCE` research result from becoming an
uncontrolled confound.

A secondary diagnostic may run `SELECTIVE_CONVERGENCE`, but it is reported
separately and cannot determine the primary A007 outcome.

## 25. No graph expansion

The word “expansion” in A007 v0.1 means:

- enable more predeclared cues;
- increase A005 top_k;
- increase A006 active-memory budget;
- increase A006 working-set budget.

It does not mean graph traversal.

A007 does not create or follow:

- `AssociationEdge`
- `RelationType`
- causal paths
- temporal paths
- identity paths

All relation hops remain zero.

## 26. No generative-model expansion

A007 does not use the A004 Qwen3.5:4b adapter to:

- generate search queries;
- judge whether evidence is sufficient;
- score uncertainty;
- select memories;
- decide STOP/EXPAND/EXHAUSTED.

This is deliberate attribution control.

Generative query reformulation can be studied later as a separate policy.

## 27. Recovery definition

Recovery is a benchmark/evaluation label, not a runtime oracle.

For a case with declared required memory IDs:

A policy **recovers** a required memory when:

- NO_EXPANSION final working set omits at least one declared required ID; and
- the policy final working set contains all declared required IDs.

Runtime A007 does not know which memory is “correct.”

Only benchmark fixtures know expected required IDs.

## 28. Regression definition

A SIGNAL_DRIVEN regression occurs when:

- NO_EXPANSION contains all declared required IDs; and
- SIGNAL_DRIVEN final output does not.

Regression count must be reported separately from recovery.

## 29. Easy-case unnecessary expansion

A benchmark case can be declared `initially_sufficient=True`.

For such a case:

- round 0 contains all required IDs;
- the round-0 A006 state must be structurally non-triggering by fixture design.

SIGNAL_DRIVEN should STOP after one round.

If it expands anyway, it is counted as an unnecessary expansion.

This tests selectivity rather than only final quality.

## 30. Persistent-insufficient behavior

At least one fixture intentionally remains structurally uncertain through round
2.

SIGNAL_DRIVEN must:

- execute at most three rounds;
- produce final decision `EXHAUSTED`;
- not loop;
- not invent a fourth scope;
- not silently lower the retrieval threshold.

This is a required boundedness test.

## 31. Boundary truncation behavior

A fixture includes budget truncation and/or boundary ties.

The controller may expand because these are declared structural triggers.

Qualification records whether widening the scope:

- recovers required evidence;
- merely increases state size;
- leaves ambiguity unresolved.

A trigger firing is not itself a success.

## 32. Same-name ambiguity boundary

A007 expansion must not collapse two same-name memories into one identity.

An ambiguity fixture keeps distinct entity IDs across rounds.

Expansion may retrieve more evidence, but it does not create a `SAME_PERSON`
claim.

Ambiguity preservation is an engineering gate.

## 33. Portable benchmark

Portable qualification uses deterministic synthetic
`SelectiveWorkingSetResult` values or fake scope evaluators.

It does not require Ollama.

The fixture covers at least:

1. easy recalled case -> STOP at round 0;
2. initial insufficient -> recovery at round 1;
3. initial insufficient -> recovery at round 2;
4. memory-budget truncation -> expand;
5. working-set truncation -> expand;
6. memory-boundary tie -> expand;
7. working-set-boundary tie -> expand;
8. persistent insufficient -> EXHAUSTED at round 2;
9. no uncontrolled fourth round;
10. same-name ambiguity preservation;
11. no regression from an initially sufficient route;
12. unsupported A006 retrieval state -> fail closed;
13. malformed/inconsistent structural state -> fail closed;
14. deterministic repeated run;
15. policy comparison NO_EXPANSION / SIGNAL_DRIVEN / ALWAYS_EXPAND.

## 34. Portable engineering gates

Portable qualification requires:

- deterministic trigger ordering;
- deterministic decisions;
- all STOP/EXPAND/EXHAUSTED invariants pass;
- easy-case unnecessary expansion count = 0;
- declared portable recovery cases recover;
- SIGNAL_DRIVEN regression count = 0;
- persistent-insufficient case ends EXHAUSTED;
- max observed SIGNAL_DRIVEN rounds <= 3;
- no graph dependency;
- no generative-model dependency;
- count invariants pass.

Portable qualification is an engineering gate.

It does not predetermine the physical research outcome.

## 35. Physical embedding/retrieval profile

Physical A007 qualification continues to use the already-qualified A005 model:

- model: `qwen3-embedding:0.6b`
- digest:
  `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`
- dimension: 1024
- similarity threshold: `0.5037018224299838`

A007 does not repull, modify, or retrain the embedding model.

## 36. Physical expansion profile

Frozen primary scope ladder:

| Round | Cue tiers enabled | top_k | max_memory_nodes | max_working_set_items |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 1 | 12 | 8 | 4 |
| 1 | 2 | 24 | 12 | 8 |
| 2 | 3 | 32 | 16 | 12 |

All rounds:

- threshold unchanged at `0.5037018224299838`;
- relation hops = 0;
- expansions inside A006 budget = 0;
- model-input token budget = 0.

This profile is frozen before final physical outcomes are observed.

## 37. Physical fixture categories

The final physical fixture includes at least:

1. English easy case that should stop at round 0;
2. Thai easy case that should stop at round 0;
3. English recovery case requiring a later cue tier;
4. Thai recovery case requiring a later cue tier;
5. cross-lingual recovery case;
6. budget-truncation case;
7. same-name ambiguity case;
8. persistent-insufficient case that must exhaust.

Each case has:

- fixed document corpus;
- exactly three ordered cue tiers;
- declared required memory IDs where correctness is meaningful;
- `initially_sufficient` label where applicable;
- ambiguity/persistent-insufficient labels where applicable.

Texts and labels are frozen before the final physical run.

If a fixture-validity bug is later demonstrated under TDD, only the invalid
fixture property may be corrected; result chasing is forbidden.

## 38. Physical execution model

For each case:

1. build the A005 exact vector-memory index once;
2. record index construction as fixed case-setup cost, separate from policy
   execution cost;
3. run each policy separately against the same immutable index,
   documents/cue tiers/profile;
4. snapshot embedding/retrieval counters before and after each policy so
   per-policy query cost excludes the shared document-index build;
5. within each evaluated round, search every cue enabled by that round using the
   round's top_k and the frozen threshold;
6. combine the resulting A005 results through A006 `SINGLE_BEST`;
7. assess structural triggers on every evaluated round, including control
   policies, while only SIGNAL_DRIVEN obeys the assessment for control flow;
8. record every round, assessment, policy termination reason, and counter delta.

Previously enabled cues are searched again when top_k increases.

No cached wider-scope result is used to make the narrow baseline cheaper or
smarter after the fact.

## 39. Physical cost/evidence metrics

Record fixed case-setup metrics separately:

- index-build embedding request count;
- index-build embedding input count;
- index-build token/timing metadata when reported.

Record raw execution metrics by policy:

- cases;
- rounds executed;
- A005 query/retrieval request count;
- policy-specific embedding request count;
- policy-specific embedding input count;
- prompt tokens when reported for policy queries;
- backend timing when reported;
- upstream vectors scored;
- A006 input hits;
- positive candidates;
- active-memory candidates;
- selected working-set items;
- expansion count;
- STOP count;
- EXHAUSTED count;
- unnecessary expansion count;
- required-memory coverage;
- recovery count;
- regression count;
- ambiguity failures.

These are workload-specific software/backend measurements.

No FLOP, power, energy, or general speed claim follows automatically.

## 40. Primary physical research comparison

Compare:

- `NO_EXPANSION`
- `SIGNAL_DRIVEN`
- `ALWAYS_EXPAND`

using the same primary `SINGLE_BEST` selector.

Important comparisons:

- SIGNAL_DRIVEN recovery vs NO_EXPANSION;
- SIGNAL_DRIVEN regressions vs NO_EXPANSION;
- SIGNAL_DRIVEN required-memory coverage vs ALWAYS_EXPAND;
- SIGNAL_DRIVEN rounds/retrieval/embedding cost vs ALWAYS_EXPAND;
- unnecessary expansion on easy cases;
- bounded exhaustion on persistent-insufficient cases.

## 41. Physical hypothesis outcome

A007 produces exactly one primary outcome:

- `SUPPORTED`
- `MIXED`
- `NOT_SUPPORTED`

These are research outcomes, not process exit states.

### SUPPORTED

Require all:

- at least one declared physical recovery over NO_EXPANSION;
- SIGNAL_DRIVEN regression count = 0;
- SIGNAL_DRIVEN required-memory coverage equals ALWAYS_EXPAND required-memory
  coverage;
- initially sufficient/easy cases have unnecessary expansion count = 0;
- persistent-insufficient cases terminate EXHAUSTED;
- SIGNAL_DRIVEN total rounds are fewer than ALWAYS_EXPAND total rounds across
  the full fixture.

### MIXED

Used when there is at least one genuine recovery, but one or more SUPPORT
conditions fail, for example:

- a regression exists;
- SIGNAL_DRIVEN coverage is below ALWAYS_EXPAND;
- easy cases unnecessarily expand;
- SIGNAL_DRIVEN does not reduce total rounds.

### NOT_SUPPORTED

Used when:

- no declared recovery over NO_EXPANSION occurs; or
- valid physical behavior provides no evidence that signal-driven expansion
  improves the declared recovery objective.

A valid `MIXED` or `NOT_SUPPORTED` experiment still exits successfully.

## 42. Structural experiment validity vs hypothesis outcome

Physical CLI exits nonzero only for invalid execution/evidence such as:

- model identity/digest/dimension mismatch;
- physical profile drift;
- fixture identity/fingerprint drift;
- malformed retrieval/working-set result;
- trigger/decision invariant failure;
- ambiguity-preservation engineering failure;
- persistent-insufficient case failing bounded termination;
- nondeterministic repeated controller execution.

A structurally valid negative research outcome exits 0.

This follows the same evidence discipline established in A006.

## 43. SELECTIVE_CONVERGENCE diagnostic

A007 may report a secondary diagnostic using A006
`SELECTIVE_CONVERGENCE` over the same physical fixture.

If present:

- it uses the same scope ladder and cue tiers;
- it is labeled secondary;
- it cannot change the primary A007 `SUPPORTED/MIXED/NOT_SUPPORTED` outcome;
- its metrics are not merged with the SINGLE_BEST primary metrics.

This preserves the A006 negative physical finding rather than erasing it.

## 44. Package structure

Planned package:

```text
src/flywire_asca/uncertainty_expansion/
    __init__.py
    models.py
    controller.py
    runner.py
    benchmark.py
```

Physical qualification:

```text
scripts/
    qualify_uncertainty_expansion_a007.py
```

Tests:

```text
tests/
    test_uncertainty_expansion_models.py
    test_uncertainty_expansion_controller.py
    test_uncertainty_expansion_runner.py
    test_uncertainty_expansion_benchmark.py
    test_uncertainty_expansion_qualification_cli.py
    test_a007_task_ledger.py
```

## 45. Error handling

A007 fails closed on:

- empty expansion profile;
- non-contiguous round indices;
- decreasing cue-tier count;
- decreasing top_k;
- shrinking memory/working-set budgets;
- a next scope that is identical to the previous scope across cue-tier count,
  top_k, memory budget, and working-set budget (a no-op expansion);
- relation hops != 0;
- nested A006 max_expansions != 0;
- model-input token budget != 0;
- unsupported A006 retrieval state;
- inconsistent retrieval state/drop/tie semantics;
- duplicate cue IDs or query IDs in a physical case;
- profile/fixture/model identity drift.

A007 does not silently skip malformed rounds.

## 46. Determinism

Given identical profile, cues, A005 results, and A006 results, A007 must produce:

- identical trigger tuples;
- identical decisions;
- identical evaluated round sequence;
- identical final scope;
- identical STOP/EXPAND/EXHAUSTED outcome;
- identical policy metrics.

No random tie-break or random expansion is used.

## 47. CI boundary

Portable GitHub CI:

- runs A007 unit/portable tests through full pytest;
- does not require Ollama;
- does not execute the physical A007 script;
- does not download multi-GB models;
- preserves existing A003/A004/A005/A006 portable gates.

Physical A007 qualification remains local evidence.

## 48. Claims boundary

A007 may claim only what is measured.

Permitted examples:

- structural trigger accuracy on declared fixtures;
- recovery count;
- regression count;
- unnecessary expansion count;
- rounds avoided relative to ALWAYS_EXPAND;
- retrieval/embedding requests observed;
- working-set sizes observed;
- backend timing/token metadata observed.

A007 must not claim without separate evidence:

- calibrated uncertainty;
- biological surprise;
- human-like attention;
- lower energy use;
- lower FLOPs;
- general compute superiority;
- general superiority over dense models.

## 49. FlyWireLLM boundary

FlyWireLLM remains paused and untouched.

A007 does not restart its training runner.

A007 qualification uses the existing local embedding model, not FlyWireLLM.

## 50. A007 completion evidence

A007 can close only when:

- live task/roadmap state is recoverable;
- typed trigger/decision/scope/profile contracts pass tests;
- structural consistency checks fail closed;
- SIGNAL_DRIVEN runner is deterministic and bounded;
- NO_EXPANSION and ALWAYS_EXPAND controls are qualified;
- portable engineering benchmark passes;
- frozen physical A005+A006+A007 composition executes validly;
- primary physical outcome is recorded without result chasing;
- raw cost/evidence metrics are retained;
- A006 physical `NOT_SUPPORTED` conclusion is not rewritten;
- FlyWireLLM remains paused/untouched;
- exact branch CI passes;
- whole-branch review addresses Critical/Important findings;
- final main CI passes;
- main is clean/synchronized 0/0.

## 51. Non-goals

A007 v0.1 does not:

- implement a real Prediction Monitor;
- assign a scalar surprise score;
- calibrate `UncertaintySignal`;
- lower the A005 similarity threshold;
- generate cues with Qwen3.5:4b;
- ask Qwen3.5:4b whether to expand;
- build or traverse a typed graph;
- change A005 vector-retrieval semantics;
- promote A006 SELECTIVE_CONVERGENCE to the default;
- detect semantic contradiction;
- execute or learn procedures;
- assemble final model prompts;
- implement A008 Procedural Memory;
- claim compute/energy savings from fewer rounds alone.

## 52. Next milestone boundary

If A007 qualifies as engineering-correct, the next roadmap milestone remains:

`A008 — Procedural Memory / Skill Chunking`

A008 may later produce real expected outcomes and execution failures that can
feed a richer surprise controller.

The later integrated loop can then combine:

- A003 Familiarity;
- A005 retrieval;
- A006 working set;
- A007 bounded expansion;
- A008 procedures;
- A004 model adapter.

A007 v0.1 should not prematurely implement that integration.

## 53. Success definition

A007 succeeds as an engineering milestone when FlyWireASCA can deterministically
derive typed structural uncertainty from A006 output, expand through a finite
predeclared retrieval/working-set ladder, stop early when the narrow route is
structurally sufficient, and terminate explicitly when the maximum scope is
exhausted.

The research hypothesis is separately supported only if the frozen physical
fixture shows that SIGNAL_DRIVEN expansion produces genuine recovery over
NO_EXPANSION, avoids regressions/unnecessary easy-case expansion, matches
ALWAYS_EXPAND required-memory coverage, and executes fewer total rounds than
ALWAYS_EXPAND.

A negative research outcome remains a valid A007 result and must be recorded
rather than tuned away.
