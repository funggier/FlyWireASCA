# A009 Integrated Cognitive Loop Design Specification

Date: 2026-10-10
Status: APPROVED FOR IMPLEMENTATION-PLAN GATE
Planned task: A009 — Integrated Cognitive Loop
Repository: `funggier/FlyWireASCA`
Base: ASCA main at `c3feaf0b08f525276d8efa95801a161e2638821a`

## 1. Purpose

A009 composes the already-qualified FlyWireASCA mechanisms into one bounded,
inspectable cognitive control loop.

The milestone does not attempt to prove general intelligence, human cognition,
energy efficiency, or production tool autonomy.

The primary research question is:

> Can A003 familiarity evidence, A005 vector retrieval, the A006-qualified
> SINGLE_BEST selector, A007 bounded structural expansion, and A008 CHUNKED
> procedure execution be composed so that a real procedure-outcome mismatch
> becomes an explicit higher-level recovery signal, allowing bounded evidence
> expansion and fresh procedure replay without hidden retry, boundary collapse,
> or uncontrolled looping?

A004 remains the model boundary for optional terminal diagnostic/fallback
reasoning. Model generation must not decide retrieval scope, procedure identity,
procedure verification, retry eligibility, or the primary A009 hypothesis
outcome.

## 2. Historical results that remain binding

A009 must preserve the historical milestone results exactly.

### A003 Familiarity

- exact cheap familiarity lookup;
- deterministic;
- familiarity is not truth, semantic identity, or semantic equivalence.

### A004 Model Adapter

- model-independent `ModelAdapter` contract;
- local baseline model `qwen3.5:4b`;
- model reasoning remains separate from control and memory evidence.

### A005 Vector Memory Retrieval

- physical retrieval result: `VECTOR_SUFFICIENT` for the qualified retrieval scope;
- physical embedding model: `qwen3-embedding:0.6b`;
- pinned digest:
  `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`;
- embedding dimension: 1024;
- frozen physical threshold: `0.5037018224299838`.

### A006 Working Set / Selective Activation

- deterministic bounded working-set mechanism is engineering-qualified;
- frozen physical convergence-benefit outcome: `NOT_SUPPORTED`;
- `SINGLE_BEST` was the stronger physical selector under the frozen fixture.

A009 therefore uses `SINGLE_BEST` as its primary selector.

`SELECTIVE_CONVERGENCE` may be used only as a separately labelled diagnostic
control. It cannot determine the primary A009 outcome.

### A007 Surprise, Uncertainty & Expansion

- structural expansion result: `SUPPORTED`;
- primary selector: `SINGLE_BEST`;
- primary policy: `SIGNAL_DRIVEN`;
- A007 triggers describe structural retrieval/working-set state only;
- those triggers are not true prediction-surprise signals.

A009 must not add procedure mismatch to the A007 `ExpansionTrigger` enum.
Procedure mismatch is an A009-level control event.

### A008 Procedural Memory / Skill Chunking

- final result: `SUPPORTED`;
- primary representation: `CHUNKED`;
- exact internal primitive checks are preserved;
- CALL completion boundaries are preserved;
- interruption is immediate on checked mismatch;
- A008 performs zero automatic retry;
- recursion remains forbidden;
- maximum procedure call depth remains 8.

A009 uses `CHUNKED` as the primary procedural execution mode.

## 3. Architecture decision

A009 uses a typed finite-state orchestrator with immutable evidence records.

The controller owns:

- phase transitions;
- outer recovery eligibility;
- bounded recovery-scope advancement;
- creation of fresh procedure attempts;
- terminal state;
- optional terminal model invocation;
- final trace assembly.

The existing subsystems retain their own semantics and evidence.

High-level flow:

```text
Input / Goal
    |
    v
A003 Exact Familiarity
    |
    v
A005 Retrieval
    |
    v
A006 SINGLE_BEST Working Set
    |
    v
A007 SIGNAL_DRIVEN Structural Expansion
    |
    v
Explicit Root Procedure
    |
    v
A008 CHUNKED Procedure Attempt
    |
    +---- COMPLETED ------------------------------> SUCCESS
    |
    +---- INTERRUPTED
             |
             v
       A009 Procedure Mismatch Event
             |
             +---- wider frozen scope remains ----> forced A009 recovery scope
             |                                       |
             |                                       v
             |                                  fresh executor
             |                                  fresh execution_id
             |                                  replay from snapshot
             |                                       |
             |                                       +---- success -> RECOVERED
             |                                       |
             |                                       +---- mismatch -> repeat only
             |                                            while a wider frozen scope
             |                                            remains
             |
             +---- no wider scope -----------------> terminal control failure
                                                        |
                                                        v
                                               optional A004 model
                                               diagnostic/fallback
```

A009 does not modify the internal semantics of A003-A008 to make this flow work.

## 4. Why A009 owns procedure-mismatch recovery

A007 cannot own procedure-outcome mismatch because A007 was qualified before
procedural execution existed.

Its trigger vocabulary is intentionally structural:

- insufficient evidence;
- memory-budget truncation;
- working-set-budget truncation;
- memory-boundary tie;
- working-set-boundary tie.

A008 now supplies a qualitatively different signal: an expected observation did
not match an actual procedure observation.

A009 therefore introduces a distinct typed recovery cause:

`PROCEDURE_OUTCOME_MISMATCH`

This is the first FlyWireASCA control stage where a real expected-vs-observed
procedure event may drive wider retrieval.

A009 still does not claim that this is calibrated probabilistic surprise.

## 5. Familiarity ownership

A003 familiarity is always evaluated once at loop start.

A009 records the exact `FamiliarityResult`.

Familiarity does not terminate retrieval and does not decide whether a semantic
memory is true.

An `UNFAMILIAR` result may still proceed to A005 semantic retrieval.

A009 v0.1 does not use A003 candidate regions to narrow the A005 index because
that would introduce a new region-to-memory routing hypothesis into the same
milestone.

This keeps A003 integrated but attribution-safe.

## 6. Retrieval and working-set ownership

A009 retrieval scopes reuse A007 `ExpansionScope`.

For every evaluated scope:

1. enable the declared cue tiers;
2. run A005 retrieval for every enabled cue using the scope `top_k`;
3. preserve the frozen similarity threshold for physical qualification;
4. wrap results as `SelectiveRetrievalEvidence`;
5. build the working set with A006 `select_single_best`;
6. return one `SelectiveWorkingSetResult`.

The primary A009 path never promotes `SELECTIVE_CONVERGENCE` to default.

## 7. Initial A007 path

The initial retrieval path uses:

`ExpansionPolicy.SIGNAL_DRIVEN`

with the existing A007 primary profile:

| Round | Cue tiers | top_k | max_memory_nodes | max_working_set_items |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 1 | 12 | 8 | 4 |
| 1 | 2 | 24 | 12 | 8 |
| 2 | 3 | 32 | 16 | 12 |

The A007 runner remains authoritative for structural STOP / EXPAND / EXHAUSTED
behavior during this initial phase.

If A007 stops at round 0 or 1, later procedure mismatch may cause A009 to
evaluate a wider scope even though A007 had no structural trigger.

That later expansion is explicitly labelled A009 recovery expansion rather than
an A007 decision.

## 8. Procedure routing

A009 v0.1 uses an explicit deterministic root procedure ID supplied by the
request/fixture.

Natural-language procedure selection is out of scope.

The model adapter is not allowed to select, rewrite, generate, or rank
procedures.

The selected procedure ID is recorded in the trace together with routing source:

`EXPLICIT_ROOT_PROCEDURE`

A009 reuses the existing A002/A008 `ProcedureRef` identity model and does not
introduce a duplicate procedure identity type.

## 9. Context-sensitive simulated procedure execution

A009 must connect retrieved evidence to procedural behavior in a measurable way.

The deterministic A009 fixture therefore adds procedure action memory
requirements external to A008 procedure definitions.

Conceptually:

```python
ActionMemoryRequirement(
    action_ref: str,
    required_memory_ids: tuple[str, ...],
)
```

A deterministic context-bound simulator checks these requirements before an
A008 primitive action is executed.

If every required memory ID is present in the current working set, the simulator
delegates to the normal deterministic action behavior.

If one or more required memory IDs are absent:

- no action state write occurs;
- the executor returns an observation that does not match the A008
  `ExpectedOutcome`;
- A008 CHUNKED detects the mismatch normally;
- A008 interrupts immediately;
- A009 receives the resulting `ProcedureInterruption`.

A008 itself remains unchanged and has no knowledge of A009 memory requirements.

## 10. Fresh-attempt snapshot rule

A009 recovery must not replay a partially executed real side-effect path.

A009 v0.1 therefore supports deterministic simulated procedure execution only.

Before the first procedure attempt, the fixture defines an immutable
pre-execution world snapshot.

Every procedure attempt:

- gets a fresh executor constructed from that same snapshot;
- gets the current working-set memory IDs;
- gets a unique execution ID;
- starts the root procedure from its first step.

This guarantees that an A009 replay does not duplicate writes from a previous
interrupted attempt.

Real OS/API/LConnect/BConnect actions remain out of scope until a later
transaction/compensation design exists.

## 11. A008 zero-auto-retry preservation

A009 never asks A008 to retry internally.

One call to `run_procedure(..., mode=CHUNKED, execution_id=X)` is one procedure
attempt.

If A009 decides to try again, it creates:

- a new A009 attempt record;
- a new execution ID;
- a fresh executor from the immutable snapshot;
- a wider declared retrieval scope.

The trace must make the distinction observable.

No two attempts may share an execution ID.

## 12. Recovery-scope advancement

After a procedure mismatch, A009 may advance exactly one frozen scope at a time.

If the initial A007 final scope index is `r`, the next possible recovery scope
is `r + 1`.

A009 never skips directly from round 0 to round 2.

For each recovery scope:

1. evaluate the wider scope using the same A005 + A006 SINGLE_BEST evaluator;
2. record `RecoveryCause.PROCEDURE_OUTCOME_MISMATCH`;
3. create a fresh procedure executor from the pre-execution snapshot;
4. replay the same explicit root procedure using CHUNKED;
5. stop immediately on procedure success;
6. otherwise advance again only if another declared scope remains.

Because the primary A007 profile contains exactly three scopes, the maximum
number of A009 procedure attempts is 3.

No fourth scope and no fourth procedure attempt may occur.

## 13. Model-use boundary

A009 integrates A004 only as optional terminal diagnostic/fallback generation.

Initial policies:

```python
class ModelUsePolicy(str, Enum):
    DISABLED = "DISABLED"
    TERMINAL_ONLY = "TERMINAL_ONLY"
```

The model may be called only after deterministic control can no longer recover,
for example:

- procedure mismatch persists at the maximum scope;
- no wider recovery scope exists;
- the final structural retrieval state remains insufficient and the procedure
  cannot complete.

The model is not called on a successful procedure path.

The model cannot:

- choose the next retrieval scope;
- generate new A005 cues;
- change the similarity threshold;
- choose a procedure;
- modify an A008 expected outcome;
- decide whether an observation matched;
- authorize another procedure replay;
- mutate world state;
- change the primary A009 research outcome.

## 14. Model request content

A terminal A004 request is assembled from bounded inspectable evidence.

It contains:

- original goal text;
- familiarity state;
- final evaluated retrieval scope;
- final working-set memory IDs;
- stable human-readable memory text supplied by the A009 fixture/context
  resolver;
- final A008 expected outcome;
- final observed mismatch;
- failing procedure ID;
- failing step ID;
- call path;
- explicit statement that the model is producing a diagnostic/fallback answer,
  not a control decision.

The model response is recorded as `ModelResponse | None`.

Portable qualification uses a deterministic fake `ModelAdapter`.

Local physical qualification may use the already-qualified A004
`qwen3.5:4b` adapter and must record its model identity/digest separately.

## 15. Core A009 enums

A009 introduces a small typed vocabulary.

Conceptually:

```python
class CognitiveLoopPhase(str, Enum):
    FAMILIARITY = "FAMILIARITY"
    INITIAL_EXPANSION = "INITIAL_EXPANSION"
    PROCEDURE_EXECUTION = "PROCEDURE_EXECUTION"
    RECOVERY_EXPANSION = "RECOVERY_EXPANSION"
    MODEL_FALLBACK = "MODEL_FALLBACK"
    TERMINAL = "TERMINAL"

class RecoveryCause(str, Enum):
    PROCEDURE_OUTCOME_MISMATCH = "PROCEDURE_OUTCOME_MISMATCH"

class LoopPolicy(str, Enum):
    NO_PROCEDURE_RECOVERY = "NO_PROCEDURE_RECOVERY"
    MISMATCH_DRIVEN_RECOVERY = "MISMATCH_DRIVEN_RECOVERY"
    ALWAYS_MAX_SCOPE = "ALWAYS_MAX_SCOPE"

class CognitiveTerminationReason(str, Enum):
    PROCEDURE_COMPLETED = "PROCEDURE_COMPLETED"
    RECOVERED_AFTER_MISMATCH = "RECOVERED_AFTER_MISMATCH"
    PROCEDURE_MISMATCH_EXHAUSTED = "PROCEDURE_MISMATCH_EXHAUSTED"
```

Additional validation-specific states may exist, but malformed inputs fail
closed rather than being converted into a successful terminal result.

## 16. Cognitive-loop request

Conceptual immutable request:

```python
CognitiveLoopRequest(
    loop_id: str,
    goal_text: str,
    familiarity_cue: Cue,
    root_procedure_id: str,
    policy: LoopPolicy,
    model_use_policy: ModelUsePolicy,
)
```

Requirements:

- all IDs/text are nonblank;
- `familiarity_cue` is a real A002 `Cue`;
- the root procedure must exist in the supplied A008 `ProcedureLibrary`;
- only declared `LoopPolicy` and `ModelUsePolicy` values are accepted.

## 17. Scope evaluation record

Each evaluated scope is retained as evidence.

Conceptually:

```python
IntegratedScopeEvaluation(
    scope: ExpansionScope,
    retrieval_results: tuple[VectorMemoryResult, ...],
    working_set_result: SelectiveWorkingSetResult,
)
```

The record preserves A005 evidence instead of storing only the final working
set.

The number of retrieval results must equal the number of enabled cues evaluated
for the scope.

## 18. Procedure attempt record

Conceptually:

```python
CognitiveProcedureAttempt(
    attempt_index: int,
    execution_id: str,
    scope: ExpansionScope,
    working_set_memory_ids: tuple[str, ...],
    execution: ProcedureExecutionResult,
    recovery_cause: RecoveryCause | None,
)
```

Invariants:

- attempt indices start at 0 and are contiguous;
- execution IDs are unique;
- attempt 0 has no recovery cause;
- attempts >0 use `PROCEDURE_OUTCOME_MISMATCH`;
- every execution mode is `CHUNKED` in the primary policy;
- the scope index never decreases;
- recovery attempts increase scope index by exactly 1;
- no attempt occurs after a completed attempt.

## 19. Trace events

A009 produces immutable trace events so control ownership is inspectable.

Minimum event kinds:

- familiarity assessed;
- initial expansion round evaluated;
- A007 initial policy terminated;
- root procedure selected;
- procedure attempt started;
- procedure completed;
- procedure mismatch observed;
- A009 recovery scope forced;
- model fallback invoked;
- terminal state reached.

Each event has:

- a sequence number;
- a typed event kind;
- stable reference IDs to subsystem evidence;
- no wall-clock time requirement for deterministic qualification.

Portable repeat qualification compares the logical trace exactly.

## 20. Final result

Conceptually:

```python
CognitiveLoopResult(
    loop_id: str,
    policy: LoopPolicy,
    familiarity: FamiliarityResult,
    initial_expansion: ExpansionRunResult,
    scope_evaluations: tuple[IntegratedScopeEvaluation, ...],
    procedure_attempts: tuple[CognitiveProcedureAttempt, ...],
    termination_reason: CognitiveTerminationReason,
    final_working_set: WorkingSet,
    final_world_state_ref: str | None,
    model_response: ModelResponse | None,
    trace: tuple[CognitiveTraceEvent, ...],
)
```

The result is an evidence container, not a claim of factual truth.

## 21. Primary policy: MISMATCH_DRIVEN_RECOVERY

The primary A009 policy is:

`MISMATCH_DRIVEN_RECOVERY`

Semantics:

1. run A003 familiarity;
2. run A007 `SIGNAL_DRIVEN` using A005 retrieval and A006 `SINGLE_BEST`;
3. execute the explicit root procedure with A008 `CHUNKED`;
4. on success, terminate;
5. on mismatch, force the next wider frozen scope if one remains;
6. replay from the immutable snapshot with a new execution ID;
7. continue one scope at a time until success or maximum scope;
8. when deterministic recovery is exhausted, optionally call A004 under
   `TERMINAL_ONLY`;
9. terminate explicitly.

## 22. Control policy: NO_PROCEDURE_RECOVERY

`NO_PROCEDURE_RECOVERY` runs the same A003/A005/A006/A007 initial path and the
same A008 CHUNKED procedure attempt, but a procedure mismatch terminates the
deterministic control path immediately.

It may still invoke terminal model fallback when configured.

Purpose:

Measure whether A009 procedure-mismatch recovery adds genuine recovery beyond
the already-qualified A007 structural policy.

## 23. Control policy: ALWAYS_MAX_SCOPE

`ALWAYS_MAX_SCOPE` uses the A007 `ALWAYS_EXPAND` policy before the first
procedure attempt.

It therefore evaluates all three frozen A007 scopes and executes the procedure
once using the maximum-scope working set.

It does not perform later mismatch-driven recovery because no wider scope
exists.

Purpose:

Provide an upper-scope correctness and retrieval-round control.

## 24. CHUNKED vs FLAT diagnostic

A009 primary policy always uses CHUNKED.

The deterministic benchmark additionally runs declared success cases with
A008 FLAT as a diagnostic equivalence check.

The diagnostic requires:

- identical ordered primitive action references;
- identical deterministic final world state;
- identical success/failure classification where the same working set is used.

FLAT cannot change the primary A009 outcome.

BLIND_CHUNKED remains an A008 negative control and is not a primary A009 runtime
policy.

## 25. SELECTIVE_CONVERGENCE diagnostic

A009 may run selected fixture cases with A006 `SELECTIVE_CONVERGENCE`.

The diagnostic must be labelled secondary.

It cannot:

- change the primary selector;
- alter the frozen primary fixture;
- change the primary A009 outcome;
- rewrite A006 `NOT_SUPPORTED`.

## 26. Deterministic portable fixture

The A009 deterministic fixture is frozen before final qualification.

Required case families:

1. `easy-familiar-success`
   - exact A003 familiarity;
   - A007 stops early;
   - required procedure memory already selected;
   - procedure succeeds on first attempt.

2. `unfamiliar-semantic-success`
   - A003 returns UNFAMILIAR;
   - A005 semantic evidence is still sufficient;
   - procedure succeeds;
   - proves familiarity is not a retrieval veto.

3. `structural-expansion-success`
   - A007 structural trigger expands before procedure execution;
   - final selected evidence supports successful procedure execution.

4. `procedure-recovery-round-one`
   - A007 stops at a structurally valid narrow scope;
   - a procedure action requires memory absent from that scope;
   - A008 interrupts;
   - A009 forced next scope recovers the memory;
   - fresh CHUNKED replay succeeds.

5. `procedure-recovery-round-two`
   - first mismatch-driven recovery scope remains insufficient for the
     procedure requirement;
   - second and final scope recovers it;
   - third procedure attempt succeeds.

6. `persistent-procedure-mismatch`
   - mismatch is not repairable by wider memory;
   - A009 advances only through declared scopes;
   - final result is mismatch exhausted;
   - no fourth attempt occurs.

7. `max-scope-mismatch`
   - initial A007 path already reaches maximum scope;
   - procedure mismatches;
   - A009 performs zero replay because no wider scope exists.

8. `same-name-ambiguity-preserved`
   - distinct same-name memories remain distinct through retrieval, working set,
     recovery, and trace.

9. `model-terminal-fallback`
   - deterministic recovery exhausts;
   - TERMINAL_ONLY calls the model exactly once;
   - model response cannot alter control termination.

10. `invalid-contract`
    - malformed request/evidence fails closed before uncontrolled execution.

## 27. Fixture identity

The portable fixture receives:

- qualification scope: `deterministic_integrated_cognitive_loop_a009`;
- fixture version: `a009-deterministic-v1`;
- an exact SHA-256 fingerprint over canonical fixture data;
- a frozen ordered case-ID set;
- frozen policy names;
- frozen A007 scope values;
- frozen maximum procedure attempts = 3.

The fingerprint is frozen before the first final qualification outcome is
accepted.

## 28. Portable benchmark metrics

Record raw counts before ratios.

At minimum:

- case count;
- policy case count;
- familiarity FAMILIAR/UNFAMILIAR counts;
- evaluated retrieval scope count;
- A005 retrieval result count;
- A005 scored-vector count;
- working-set selected-item count;
- A007 initial rounds;
- A009 forced recovery-scope count;
- procedure attempt count;
- unique execution-ID count;
- first-attempt procedure success count;
- mismatch-recovery success count;
- persistent mismatch count;
- post-completion extra-attempt count;
- maximum observed procedure attempts;
- maximum observed scope index;
- final world-state correctness count;
- CHUNKED/FLAT diagnostic equivalence count;
- same-name ambiguity failure count;
- model fallback call count;
- deterministic replay result.

No FLOP, power, energy, or general latency claim is derived from these counts.

## 29. Recovery definition

A case is a genuine A009 mismatch recovery when:

- `NO_PROCEDURE_RECOVERY` does not complete the procedure;
- `MISMATCH_DRIVEN_RECOVERY` completes the same declared root procedure;
- success requires at least one A009 forced recovery scope;
- the successful attempt uses a fresh execution ID;
- success occurs with the same immutable pre-execution world snapshot.

Recovery is benchmark evidence, not a runtime oracle.

## 30. Regression definition

A primary-policy regression occurs when:

- `NO_PROCEDURE_RECOVERY` completes a declared case;
- `MISMATCH_DRIVEN_RECOVERY` fails to complete the same case.

Regression count is reported separately from recovery.

## 31. Primary A009 hypothesis outcome

A009 produces exactly one primary research outcome:

- `SUPPORTED`
- `MIXED`
- `NOT_SUPPORTED`

These are valid research outcomes, not process exit states.

### SUPPORTED

Require all:

- at least one genuine procedure-mismatch recovery over
  `NO_PROCEDURE_RECOVERY`;
- mismatch-driven regression count = 0;
- primary final procedure-success coverage equals `ALWAYS_MAX_SCOPE` on
  declared recoverable cases;
- primary total evaluated retrieval scopes are fewer than
  `ALWAYS_MAX_SCOPE` across the full frozen fixture;
- every replay uses a unique execution ID;
- no A008 attempt performs hidden automatic retry;
- maximum observed procedure attempts <= 3;
- no fourth retrieval scope is evaluated;
- final-state correctness passes for every successful deterministic case;
- same-name ambiguity failures = 0;
- CHUNKED/FLAT declared diagnostic equivalence passes;
- deterministic logical replay passes.

### MIXED

Use when at least one genuine mismatch recovery exists but one or more
SUPPORTED conditions fail, for example:

- a regression exists;
- final success coverage is below ALWAYS_MAX_SCOPE;
- primary scope evaluations are not lower than ALWAYS_MAX_SCOPE;
- a declared diagnostic equivalence fails while the core recovery mechanism
  still demonstrates some value.

### NOT_SUPPORTED

Use when:

- no genuine procedure-mismatch recovery over NO_PROCEDURE_RECOVERY occurs; or
- valid frozen evidence shows no benefit for the declared mismatch-driven
  recovery objective.

A valid MIXED or NOT_SUPPORTED experiment exits successfully.

## 32. Experiment validity vs research outcome

Portable qualification exits nonzero for invalid evidence or architecture
breach, including:

- fixture fingerprint drift;
- case-ID drift;
- malformed A009 contracts;
- duplicate procedure execution IDs;
- replay from a non-fresh snapshot;
- non-contiguous procedure attempts;
- recovery scope skipping;
- scope index above 2;
- procedure attempt count above 3;
- unsupported A008 execution mode in the primary policy;
- primary selector other than SINGLE_BEST;
- A007 trigger semantics changed;
- model output influencing deterministic control;
- same-name identity collapse;
- nondeterministic repeated trace;
- impossible metric relationships.

A valid negative research outcome remains exit code 0.

## 33. Determinism

Portable A009 qualification contains no timing requirement and no randomness.

Given identical:

- familiarity traces;
- vector documents and deterministic embeddings;
- cue tiers;
- A007 profile;
- A006 selector;
- procedure library;
- action-memory requirements;
- initial world snapshot;
- failure map;
- loop policy;
- model fake response;

the logical A009 result and trace must be identical.

## 34. Portable A005 integration

Portable A009 qualification should exercise the real
`ExactVectorMemoryIndex` using a deterministic qualification-only embedding
adapter.

The adapter:

- implements the existing generic `EmbeddingAdapter` protocol;
- returns predeclared vectors;
- has a fixed model name/digest/dimension;
- performs no network call;
- exists only to make A005 retrieval deterministic in portable CI.

This is preferred over fabricating final working-set objects because A009 is an
integration milestone.

## 35. Local physical qualification

A009 also has a local physical integration layer.

Physical qualification may use:

- A005 `qwen3-embedding:0.6b`;
- the frozen A005 threshold `0.5037018224299838`;
- A006 SINGLE_BEST;
- A007 frozen primary scope ladder;
- A008 CHUNKED deterministic simulated procedures;
- A004 `qwen3.5:4b` only for TERMINAL_ONLY model fallback cases.

The physical fixture must be frozen before final outcomes.

A009 must not retune:

- the A005 threshold;
- A007 scope values;
- A008 expected outcomes;
- action-memory requirements;

after observing final physical results.

## 36. Physical-model boundary

A004 Qwen generation is secondary evidence in A009.

Physical qualification records:

- whether the model was invoked;
- model tag;
- full digest;
- request count;
- prompt/generated token metadata when reported;
- backend timing when reported;
- whether content was nonempty.

The model response is not machine-scored as proof of A009 recovery and cannot
turn a failed deterministic control case into a successful primary case.

## 37. CI boundary

GitHub CI may run:

- full unit tests;
- deterministic A009 portable benchmark;
- deterministic A009 qualification CLI;
- existing architecture/repository/A003/A008 portable gates.

GitHub CI must not:

- require Ollama;
- download Qwen models;
- execute the physical A005 embedding qualification;
- execute the physical A009 Qwen fallback qualification.

Local physical evidence remains separate.

## 38. Planned package boundaries

Proposed package:

```text
src/flywire_asca/integrated_loop/
    __init__.py
    models.py
    retrieval.py
    procedure.py
    controller.py
    benchmark.py
```

Responsibilities:

- `models.py`: immutable A009 enums/evidence/result contracts;
- `retrieval.py`: A005 + A006 scope evaluator and A007 scope integration;
- `procedure.py`: deterministic context-bound procedure executor/factory and
  memory-requirement contracts;
- `controller.py`: finite-state A009 orchestration only;
- `benchmark.py`: frozen deterministic integration fixture, policies, metrics,
  classification, payload generation.

Qualification scripts:

```text
scripts/
    qualify_integrated_loop_a009.py
    qualify_integrated_loop_a009_physical.py
```

The physical script remains local-only.

## 39. Error handling

A009 fails closed on:

- blank loop/goal/procedure IDs;
- unknown root procedure;
- invalid policy;
- duplicate familiarity trace IDs;
- malformed A005 results;
- unsupported A006 result shape;
- invalid A007 profile;
- non-contiguous scope progression;
- duplicate execution IDs;
- attempt index drift;
- attempt after successful completion;
- recovery without preceding A008 interruption;
- recovery scope that is not exactly the next declared scope;
- missing fresh executor snapshot;
- primary procedure mode other than CHUNKED;
- primary selector other than SINGLE_BEST;
- model adapter response with request-ID mismatch;
- malformed model response;
- impossible benchmark counters.

Malformed inputs are not silently skipped.

## 40. Claims boundary

A009 may claim only evidence it measures, such as:

- deterministic subsystem composition;
- exact control trace;
- mismatch-driven recovery count;
- regression count;
- bounded procedure-attempt count;
- bounded retrieval-scope count;
- final-state correctness;
- A007/A008 semantic preservation;
- CHUNKED/FLAT equivalence on declared integrated cases;
- model invocation metadata.

A009 must not claim without separate evidence:

- human-like cognition;
- biological surprise;
- calibrated uncertainty;
- autonomous real-world tool recovery;
- lower FLOPs;
- lower energy or power;
- general token savings;
- production latency superiority;
- superiority over dense/non-selective systems.

The latter system-level comparison belongs to A010.

## 41. FlyWireLLM boundary

FlyWireLLM remains a separate repository and must remain untouched.

A009 does not:

- restart FlyWireLLM training;
- read or modify FlyWireLLM checkpoints;
- import FlyWireLLM code;
- use FlyWireLLM as a model adapter.

A009 model qualification, when enabled, uses the existing A004 Qwen adapter.

## 42. Task activation gate

A009 is still PLANNED while this design and its implementation plan are being
prepared.

No A009 GitHub issue may exist before the approved plan reaches its explicit
activation task.

At activation:

- create Issue #9 (or the next actual GitHub issue number);
- create the A009 task ledger;
- mark A009 ACTIVE;
- create the feature branch/worktree according to the approved execution plan;
- preserve main clean/synchronized state.

The issue number must be taken from GitHub's actual create result rather than
hard-coded into repository documents before creation.

## 43. Completion evidence

A009 may close only when:

- A009 contracts and controller tests pass;
- deterministic A003/A005/A006/A007/A008 integration benchmark is frozen;
- deterministic A009 qualification is valid;
- the primary outcome is recorded as exactly SUPPORTED/MIXED/NOT_SUPPORTED;
- A006 NOT_SUPPORTED remains unchanged;
- A007 SUPPORTED remains unchanged;
- A008 SUPPORTED remains unchanged;
- SINGLE_BEST remains the primary selector;
- CHUNKED remains the primary procedural representation;
- zero hidden A008 retry is demonstrated;
- mismatch-driven replay is explicitly bounded;
- local physical qualification is recorded when runtime prerequisites are
  available;
- model fallback is proven non-controlling;
- FlyWireLLM remains untouched;
- exact branch CI passes;
- whole-branch Critical/Important findings are resolved;
- reviewed behavior is integrated to main;
- exact final-main CI passes;
- final main is clean and synchronized 0/0;
- the A009 GitHub issue is closed only after final-main evidence is GREEN.

## 44. Non-goals

A009 v0.1 does not:

- execute real OS/API/LConnect/BConnect actions;
- implement transactional real-world tool replay;
- generate procedures;
- learn procedures;
- select procedures from natural language;
- modify A008 procedure definitions based on model output;
- add procedure mismatch to A007 trigger enums;
- calibrate `UncertaintySignal`;
- lower the A005 similarity threshold during recovery;
- build or traverse a typed semantic graph;
- promote A006 SELECTIVE_CONVERGENCE to primary;
- use BLIND_CHUNKED as a primary policy;
- let Qwen control retry/verification/procedure selection;
- touch FlyWireLLM;
- perform the A010 dense/non-selective system comparison.

## 45. Success definition

A009 succeeds as an engineering integration milestone when one finite typed
controller can run A003 familiarity, A005 retrieval, A006 SINGLE_BEST
selection, A007 SIGNAL_DRIVEN structural expansion, and A008 CHUNKED procedure
execution while preserving each subsystem's evidence boundaries.

The A009 mismatch-recovery research hypothesis is supported only if the frozen
fixture demonstrates genuine procedure-mismatch recovery over a no-recovery
control, no regressions, final success coverage equal to the always-max-scope
control, fewer total retrieval-scope evaluations than always-max across the
fixture, unique fresh procedure attempts, bounded termination, correct final
state, and deterministic replay.

A negative outcome remains valid evidence and must be reported rather than tuned
away.
