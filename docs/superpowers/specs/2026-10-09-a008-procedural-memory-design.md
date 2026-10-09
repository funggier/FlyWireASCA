# A008 Procedural Memory / Skill Chunking Design Specification

Date: 2026-10-09
Status: APPROVED CONVERSATIONAL DESIGN — WRITTEN SPEC FOR USER REVIEW
Planned task: A008 — Procedural Memory / Skill Chunking
Branch: research/a008-procedural-memory
Base: ASCA main at d5342fbb74f7dc49e5fcc5472847495ba1212434

## 1. Purpose

A008 adds a deterministic procedural-memory subsystem that can represent,
validate, reuse, and execute hierarchical procedures composed from primitive
actions and reusable procedure chunks.

The primary research question is:

> Can a reusable hierarchical procedural representation reduce the number of
> decisions exposed to the parent controller while preserving primitive
> execution correctness, exact expected-outcome verification, and precise
> interruption evidence compared with a flat procedure representation?

A008 v0.1 deliberately uses abstract actions and a deterministic simulator
instead of real OS/API/tool execution. This isolates procedural-memory and
skill-chunking semantics from external runtime failures.

## 2. Historical context

A007 qualified structural uncertainty-driven bounded expansion with a frozen
physical result of `SUPPORTED`.

A007 did not qualify true prediction surprise. A008 provides the first
qualified source of explicit expected-vs-observed procedural outcomes that a
later integrated loop can use as real execution-mismatch evidence.

A008 does not retroactively change A007's scope or outcome.

## 3. Existing contracts reused

A008 reuses A002 contracts:

```python
ProcedureRef(
    procedure_id: str,
    name: str,
    version: str,
    explanation_memory_ids: tuple[str, ...] = (),
)

Observation(
    observation_id: str,
    kind: ObservationKind,
    payload_ref: str,
    expected_match: bool | None = None,
    evidence_ids: tuple[str, ...] = (),
)
```

A008 does not create a second procedure-identity or observation-identity
contract.

`ProcedureRef.explanation_memory_ids` remains provenance. It is not converted
into a causal truth claim.

## 4. Architectural decision

A008 uses:

**Hierarchical Procedure + Step-Level Expected Outcome Checkpoints**

Core flow:

```text
ProcedureLibrary
      |
      v
ProcedureDefinition
      |
      +-- ACTION
      |
      +-- CALL_PROCEDURE
      |
      v
ProcedureRunner
      |
      v
Deterministic Action Executor
      |
      v
Observation
      |
      v
Exact Expected-Outcome Verifier
      |
      +-- MATCH ------> next step / return from child
      |
      +-- MISMATCH ---> INTERRUPT
                         |
                         +--> failing step
                         +--> call path
                         +--> expected/observed
                         +--> explanation memory refs
```

The runner never retries a failed step automatically.

## 5. A008 package boundary

Planned package:

```text
src/flywire_asca/procedural_memory/
    __init__.py
    models.py
    library.py
    verifier.py
    runner.py
    simulator.py
    benchmark.py
```

Qualification script:

```text
scripts/qualify_procedural_memory_a008.py
```

Tests:

```text
tests/
    test_procedural_memory_models.py
    test_procedural_memory_library.py
    test_procedural_memory_verifier.py
    test_procedural_memory_runner.py
    test_procedural_memory_simulator.py
    test_procedural_memory_benchmark.py
    test_procedural_memory_qualification_cli.py
    test_a008_task_ledger.py
```

## 6. Step kinds

A008 introduces:

```python
class ProcedureStepKind(str, Enum):
    ACTION = "ACTION"
    CALL_PROCEDURE = "CALL_PROCEDURE"
```

Every step is exactly one of those kinds.

There is no implicit third state and no free-form step kind.

## 7. Expected-outcome matcher

A008 v0.1 introduces only:

```python
class OutcomeMatcherKind(str, Enum):
    EXACT = "EXACT"
```

No semantic similarity, embedding distance, model judgment, fuzzy threshold, or
probabilistic matcher is allowed in v0.1.

## 8. ExpectedOutcome

A008 introduces an immutable record conceptually equivalent to:

```python
ExpectedOutcome(
    expectation_id: str,
    observation_kind: ObservationKind,
    expected_payload_ref: str,
    matcher: OutcomeMatcherKind = OutcomeMatcherKind.EXACT,
)
```

Requirements:

- expectation ID nonblank;
- expected payload reference nonblank;
- observation kind is a valid `ObservationKind`;
- matcher is `EXACT`.

An expected outcome is an execution checkpoint, not a confidence score.

## 9. ProcedureStep

A008 introduces:

```python
ProcedureStep(
    step_id: str,
    kind: ProcedureStepKind,
    expected_outcome: ExpectedOutcome,
    explanation_memory_ids: tuple[str, ...] = (),
    action_ref: str | None = None,
    callee_procedure_id: str | None = None,
)
```

Requirements:

### ACTION

- `action_ref` must be nonblank;
- `callee_procedure_id` must be `None`.

### CALL_PROCEDURE

- `callee_procedure_id` must be nonblank;
- `action_ref` must be `None`.

All steps require an explicit `expected_outcome`.

Explanation-memory IDs are unique nonblank references and are never interpreted
as causal truth by A008.

## 10. ProcedureDefinition

A008 introduces:

```python
ProcedureDefinition(
    procedure: ProcedureRef,
    steps: tuple[ProcedureStep, ...],
    completion_outcome: ExpectedOutcome,
)
```

Requirements:

- `procedure` is a valid A002 `ProcedureRef`;
- at least one step;
- step IDs unique within that procedure;
- step ordering is declaration ordering;
- `completion_outcome` is required and defines the observable state contract
  when this procedure is invoked as a chunk;
- immutable after construction.

Procedure ID identity comes only from `ProcedureRef.procedure_id`.

## 11. ProcedureLibrary

A008 introduces an immutable procedure registry:

```python
ProcedureLibrary(
    procedures: tuple[ProcedureDefinition, ...],
    max_call_depth: int = 8,
)
```

Requirements:

- at least one procedure;
- procedure IDs unique;
- every `CALL_PROCEDURE` callee resolves;
- direct recursion forbidden;
- indirect recursion forbidden;
- maximum static call depth <= 8;
- duplicate procedure IDs fail closed;
- missing callees fail closed;
- invalid hierarchy fails before execution.

The library exposes deterministic lookup by procedure ID.

It does not perform semantic retrieval.

## 12. Recursion boundary

A008 v0.1 forbids recursion.

Invalid examples:

```text
A -> A
```

and:

```text
A -> B -> C -> A
```

Both fail during library validation.

The maximum permitted static call depth is:

`8`

Depth is the number of procedure IDs in the root-to-current call path, so the
root procedure has depth 1.

The depth bound is configurable only downward in tests/fixtures; the primary
qualification profile uses 8.

## 13. Execution modes

A008 compares exactly three modes:

```python
class ProcedureExecutionMode(str, Enum):
    FLAT = "FLAT"
    CHUNKED = "CHUNKED"
    BLIND_CHUNKED = "BLIND_CHUNKED"
```

### FLAT

Hierarchy is deterministically expanded into primitive ACTION steps before
execution.

Every primitive expected outcome is verified.

The parent controller is exposed to every primitive dispatch.

### CHUNKED

Hierarchy is preserved.

The parent controller dispatches a child procedure as one chunk call.

Primitive steps inside the chunk still execute and each primitive expected
outcome is verified.

This is the primary A008 mode.

### BLIND_CHUNKED

Hierarchy is preserved.

Primitive actions inside child chunks execute, but internal primitive outcome
checks are suppressed for the chunk body. Only the child procedure's synthetic
completion observation is verified at the parent's CALL_PROCEDURE boundary.

This is a negative control for the trade-off between reduced parent-visible
control and precise failure localization.

BLIND_CHUNKED is not the recommended runtime policy.

## 14. CALL_PROCEDURE completion observation

A CALL_PROCEDURE step is verified against an explicit child-completion
observation, not against a synthetic unconditional "completed" token.

Each `ProcedureDefinition.completion_outcome` declares what must be observable
after that procedure's body executes successfully as a chunk.

The executor boundary therefore includes a second deterministic interface:

```python
observe_procedure_completion(
    *,
    procedure_id: str,
    execution_id: str,
    call_path: tuple[str, ...],
) -> Observation
```

After a child procedure body finishes:

1. the runner asks the executor/completion observer for the child's completion
   observation;
2. the parent CALL_PROCEDURE step verifies that observation against its own
   `expected_outcome`;
3. the CALL step expectation must be exactly equal to the callee
   `ProcedureDefinition.completion_outcome`.

A library definition with a CALL_PROCEDURE expectation that differs from the
callee completion contract is rejected before execution.

This boundary is essential for the BLIND_CHUNKED negative control:

- CHUNKED checks primitive outcomes inside the child and also verifies the child
  completion observation at the call boundary;
- BLIND_CHUNKED suppresses internal primitive checks but still verifies the
  child completion observation at the call boundary;
- therefore a primitive failure that corrupts simulated state can be localized
  exactly at the primitive under CHUNKED but only at the CALL_PROCEDURE boundary
  under BLIND_CHUNKED.

The root procedure does not need a parent CALL boundary; final root-world-state
correctness is checked independently by qualification evidence.

## 15. Primitive action executor interface

The core runner depends on an abstract deterministic interface conceptually
equivalent to:

```python
execute_action(
    *,
    action_ref: str,
    execution_id: str,
    call_path: tuple[str, ...],
    step_id: str,
) -> Observation

observe_procedure_completion(
    *,
    procedure_id: str,
    execution_id: str,
    call_path: tuple[str, ...],
) -> Observation
```

A008 does not define real OS/API/tool semantics.

The primary qualification uses a deterministic simulator implementing both
interfaces.

A009 may later adapt this boundary to real tools without changing procedure
definitions.

## 16. Exact outcome verification

A008 verifier:

1. requires observation kind to equal expected observation kind;
2. requires `payload_ref` to equal `expected_payload_ref`;
3. returns a typed match result;
4. does not modify the observation.

A008 does not use `Observation.expected_match` as an oracle supplied by the
executor.

Instead, the verifier computes expected-match truth itself and may create an
execution evidence record that stores the computed result.

## 17. Verification result

A008 introduces:

```python
OutcomeVerification(
    expectation_id: str,
    observation_id: str,
    matched: bool,
)
```

This is deterministic under EXACT matching.

It is not a confidence estimate.

## 18. Execution states

A008 introduces:

```python
class ProcedureExecutionState(str, Enum):
    READY = "READY"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    INTERRUPTED = "INTERRUPTED"
    FAILED_VALIDATION = "FAILED_VALIDATION"
```

Library-definition failures happen before normal execution and are represented
as validation failures/exceptions rather than partially executed procedures.

## 19. Step execution result

A008 records each executed step:

```python
StepExecutionResult(
    procedure_id: str,
    step_id: str,
    call_path: tuple[str, ...],
    kind: ProcedureStepKind,
    observation: Observation,
    expected_outcome: ExpectedOutcome,
    verification: OutcomeVerification | None,
    primitive_action_executed: bool,
)
```

For BLIND_CHUNKED internal primitive steps:

- primitive action executes;
- observation is recorded;
- `verification is None` for suppressed internal checks.

"Internal" means ACTION steps executed below the root procedure. Root ACTION
steps remain checked. CALL_PROCEDURE completion-boundary verification is never
suppressed, including nested call boundaries.

## 20. Procedure interruption

A008 introduces:

```python
ProcedureInterruption(
    root_procedure_id: str,
    failing_procedure_id: str,
    failing_step_id: str,
    call_path: tuple[str, ...],
    expected_outcome: ExpectedOutcome,
    observed: Observation,
    explanation_memory_ids: tuple[str, ...],
    completed_primitive_step_paths: tuple[str, ...],
)
```

The interruption is emitted immediately after a checked mismatch.

No subsequent action executes.

## 21. Explanation-memory provenance

Interruption explanation-memory IDs are the canonical unique union of:

1. root-to-failing-procedure `ProcedureRef.explanation_memory_ids`;
2. failing step `explanation_memory_ids`.

The order follows call-path order, then failing-step order, with duplicates
removed while preserving first occurrence.

A008 preserves these references only.

It does not retrieve their content automatically and does not infer causal
truth.

## 22. Immediate interruption rule

For FLAT and CHUNKED:

- every checked mismatch interrupts immediately;
- no later primitive executes;
- no automatic retry;
- no automatic alternate procedure;
- no A007 expansion call;
- no LLM call.

For BLIND_CHUNKED:

- a mismatch in an internal primitive ACTION is not checked at that primitive;
- corrupted simulator state can therefore propagate until the nearest
  CALL_PROCEDURE completion observer/check;
- interruption is attributed to that CALL_PROCEDURE step rather than the
  original primitive;
- this reduced localization is intentional negative-control behavior.

## 23. Root completion

When the root procedure completes successfully, execution returns:

```python
ProcedureExecutionResult(
    execution_id: str,
    root_procedure_id: str,
    mode: ProcedureExecutionMode,
    state=ProcedureExecutionState.COMPLETED,
    step_results: tuple[StepExecutionResult, ...],
    interruption=None,
    final_world_state_ref: str | None,
    metrics: ProcedureExecutionMetrics,
)
```

Interrupted execution returns the same outer result type with:

- state = `INTERRUPTED`;
- non-null interruption;
- only actually executed step results;
- no hidden continuation.

## 24. Deterministic execution IDs

Portable and deterministic qualification runners use caller-supplied nonblank
execution IDs.

The core A008 runner does not generate random UUIDs.

Synthetic observation IDs are derived deterministically from:

- execution ID;
- call path;
- step ID;
- event type.

Identical input/library/executor state/execution ID produces identical logical
execution evidence.

## 25. Call path semantics

A call path is a tuple of procedure IDs from root to current procedure.

Example:

```text
("prepare-coffee", "heat-water", "check-kettle")
```

The current procedure ID is always the final path element.

Maximum runtime call-path length cannot exceed library `max_call_depth`.

## 26. Primitive step path

For audit/metrics, a primitive step path is represented deterministically as:

```text
procedure-a/procedure-b::step-3
```

or an equivalent frozen canonical encoding.

The frozen canonical encoding is:

```text
<procedure-id>/<procedure-id>/...::<step-id>
```

where the left side is the full call path and the right side is the originating
primitive step ID.

It must not depend on memory addresses or random IDs.

## 27. Flat expansion

A008 provides a deterministic flattening function:

```python
flatten_procedure(
    library: ProcedureLibrary,
    root_procedure_id: str,
) -> tuple[FlattenedPrimitiveStep, ...]
```

Each flattened step preserves:

- originating procedure ID;
- originating step ID;
- original call path;
- primitive action ref;
- original expected outcome;
- explanation-memory provenance.

CALL_PROCEDURE steps themselves are not primitive actions in FLAT mode.

Flattening performs no execution.

## 28. Semantic equivalence boundary

For a valid deterministic fixture with no injected failure:

FLAT and CHUNKED are expected to have the same:

- ordered primitive action refs;
- primitive action execution count;
- final simulated world state;
- primitive expected-outcome correctness.

They are not expected to have the same:

- parent-visible dispatch count;
- procedure-call count;
- call-stack evidence shape.

BLIND_CHUNKED is allowed to differ in failure localization but not in success
final-state correctness for a failure-free fixture.

## 29. Deliberative-dispatch definition

A008 does not claim to measure human deliberation or model reasoning.

It defines a software/control metric:

**parent-visible deliberative dispatch**

A dispatch visible to the immediate controller of the root procedure.

### FLAT

Each primitive action is one parent-visible dispatch.

### CHUNKED

At root level:

- root primitive ACTION = one dispatch;
- root CALL_PROCEDURE = one dispatch regardless of child primitive count.

Child internal dispatches remain recorded separately but are not counted as
root parent-visible dispatches.

### BLIND_CHUNKED

Uses the same parent-visible dispatch definition as CHUNKED.

## 30. ProcedureExecutionMetrics

A008 records at least:

```python
ProcedureExecutionMetrics(
    primitive_action_count: int,
    procedure_call_count: int,
    root_visible_dispatch_count: int,
    total_step_event_count: int,
    expected_outcome_check_count: int,
    suppressed_internal_check_count: int,
    max_runtime_call_depth: int,
)
```

All counts are nonnegative integers.

Mode-specific counting rules:

- FLAT `procedure_call_count = 0` because CALL_PROCEDURE steps are removed by
  flattening before execution;
- CHUNKED / BLIND_CHUNKED increment `procedure_call_count` once for every
  executed CALL_PROCEDURE step;
- completion-observer calls are verification events and do not increment
  `primitive_action_count`;
- root-visible dispatch count includes only ACTION/CALL dispatches issued by the
  root procedure controller, not child-internal dispatches and not completion
  probes;
- `total_step_event_count` counts executed ACTION and CALL_PROCEDURE step
  result records; completion observations are attached to CALL_PROCEDURE step
  results rather than counted as standalone procedure steps.

These are software/control-state measurements.

## 31. Deliberative compression ratio

For benchmark comparison only:

```text
deliberative_compression_ratio =
    FLAT.root_visible_dispatch_count
    / CHUNKED.root_visible_dispatch_count
```

The ratio is reported only when the CHUNKED denominator is > 0.

It means:

**reduction in root-controller-visible dispatches for the declared fixture.**

It does not mean:

- FLOP reduction;
- token reduction;
- wall-clock speedup;
- energy savings;
- parameter compression.

## 32. Chunk reuse definition

A chunk is genuinely reused when the same `procedure_id` is referenced by
CALL_PROCEDURE steps in at least two distinct parent procedure definitions.

A008 benchmark records:

- unique procedure definitions;
- total CALL_PROCEDURE uses;
- reused procedure IDs;
- reuse count per procedure.

Copying equivalent primitive steps into different procedures does not count as
reuse.

## 33. Simulator purpose

A008 includes a deterministic state-transition simulator for qualification.

It is not a production OS/tool executor.

Its purpose is to provide:

- reproducible action observations;
- reproducible world-state changes;
- injected action failures;
- final-state correctness checks.

## 34. Simulated world state

Conceptually:

```python
SimulatedWorldState(
    values: tuple[tuple[str, str], ...],
)
```

The canonical form is sorted by key and contains unique nonblank keys.

The simulator may expose a read-only mapping view internally, but persisted
qualification evidence uses deterministic tuple ordering.

## 35. Simulated action definition

Qualification uses generic declarative action effects conceptually equivalent
to:

```python
SimulatedActionDefinition(
    action_ref: str,
    writes: tuple[tuple[str, str], ...],
    observation_kind: ObservationKind,
    success_payload_ref: str,
)

SimulatedCompletionProbe(
    procedure_id: str,
    state_key: str,
    observation_kind: ObservationKind,
)
```

A completion probe reads the canonical current value of `state_key` and emits
that value as `payload_ref`. The corresponding ProcedureDefinition
`completion_outcome.expected_payload_ref` declares the required value.

A simulator completion probe is required for every procedure that is actually
invoked as a child in a qualification case. A root-only procedure does not
require a completion probe unless another procedure calls it.

This keeps procedure contracts domain-neutral.

Examples such as heating water or copying a document are fixture data, not
production opcodes.

## 36. Failure injection

The simulator accepts a frozen failure map keyed by canonical primitive step
path or action execution key.

A failure override can:

- replace the observation kind/payload;
- optionally suppress declared state writes.

Failure injection is deterministic.

It does not randomly fail actions.

## 37. Final world-state evidence

The simulator exposes a deterministic final-state digest/reference.

Qualification compares final world state against declared fixture
expectations.

The digest/reference is evidence of fixture correctness only.

It is not a persistent real-world state identifier.

## 38. Primary comparative modes

A008 primary experiment compares:

- `FLAT`
- `CHUNKED`
- `BLIND_CHUNKED`

CHUNKED is the primary experimental mode.

FLAT is the correctness/control-exposure baseline.

BLIND_CHUNKED is a negative control.

## 39. Portable engineering fixture

Portable tests must cover at least:

1. valid single primitive procedure;
2. reusable child procedure called by two different parents;
3. nested hierarchy depth > 2;
4. exact FLAT/CHUNKED primitive sequence equivalence;
5. FLAT/CHUNKED final-state equivalence;
6. root-visible dispatch reduction under CHUNKED;
7. primitive failure interrupted at exact failing step in FLAT;
8. same primitive failure interrupted at exact failing step in CHUNKED;
9. BLIND_CHUNKED failure localized only at chunk boundary;
10. explanation-memory provenance preservation;
11. no step executes after checked mismatch;
12. duplicate procedure ID failure;
13. duplicate step ID failure;
14. missing callee failure;
15. direct recursion failure;
16. indirect recursion failure;
17. static depth > 8 failure;
18. invalid CALL expectation failure;
19. deterministic repeated execution;
20. invalid simulator action ref failure.

## 40. Deterministic execution qualification fixture

The final deterministic experiment includes at least these scenario families:

- beverage preparation with shared `heat-water` chunk;
- second parent reusing the same `heat-water` chunk;
- document-backup procedure with nested verification;
- package-preparation procedure with reusable preparation chunk;
- injected primitive failure inside a reused chunk;
- nested chunk hierarchy;
- recursion/missing-callee invalid-library cases.

Fixture definitions are frozen before the final experiment outcome is
evaluated.

## 41. Primary research metrics

The deterministic experiment records:

- case count;
- successful case count by mode;
- final-state correctness by mode;
- primitive sequence equivalence FLAT vs CHUNKED;
- primitive action count by mode;
- procedure-call count by mode;
- root-visible dispatch count by mode;
- total step events by mode;
- expected-outcome checks by mode;
- suppressed internal checks in BLIND_CHUNKED;
- max runtime call depth;
- chunk reuse count;
- deliberative compression ratio;
- injected-failure count;
- correct failure localization count by mode;
- call-path correctness count;
- explanation-provenance correctness count;
- no-post-interruption-execution failures;
- deterministic-repeat match.

## 42. Primary hypothesis outcome

A008 deterministic qualification emits exactly one primary outcome:

- `SUPPORTED`
- `MIXED`
- `NOT_SUPPORTED`

These are research/mechanism outcomes, not execution-validity states.

### SUPPORTED

Require all:

- CHUNKED success/final-state correctness equals FLAT on all failure-free cases;
- CHUNKED ordered primitive action sequence equals FLAT on all equivalence cases;
- at least one declared reused chunk has reuse count >= 2;
- aggregate CHUNKED root-visible dispatch count < aggregate FLAT root-visible
  dispatch count;
- deliberative compression ratio > 1.0 on at least one declared chunking case;
- FLAT injected checked failures localize the exact primitive failing step;
- CHUNKED injected checked failures localize the exact primitive failing step;
- CHUNKED failure localization is not worse than FLAT for declared checked
  failure cases;
- explanation-memory provenance checks pass;
- no checked failure executes a later primitive;
- deterministic repeat passes.

### MIXED

Used when chunk reuse/dispatch reduction exists but one or more required
correctness/localization conditions fail.

Examples:

- reduced root-visible dispatches but CHUNKED loses final-state equivalence;
- chunk reuse works but some checked failure is localized incorrectly;
- correctness matches but no measurable root-visible dispatch reduction occurs
  for some required family while another family reduces.

### NOT_SUPPORTED

Used when:

- no declared root-visible dispatch reduction occurs; or
- reusable hierarchy provides no measurable chunk reuse; or
- CHUNKED fails to preserve the core execution-correctness objective strongly
  enough that the stated hypothesis is not demonstrated.

A valid negative outcome remains exit 0.

## 43. BLIND_CHUNKED interpretation

BLIND_CHUNKED does not determine whether the primary CHUNKED hypothesis is
SUPPORTED.

It is reported separately as a negative control.

Expected behavior in at least one injected-failure fixture:

- same primitive actions may execute;
- internal mismatch is not checked at the primitive;
- interruption is localized at a later chunk boundary;
- failure localization is therefore coarser than CHUNKED.

If BLIND_CHUNKED unexpectedly localizes as precisely as CHUNKED because a
fixture cannot distinguish them, that fixture does not qualify the intended
negative-control claim.

## 44. Execution validity vs hypothesis outcome

The deterministic qualification CLI exits nonzero only for invalid
execution/evidence such as:

- fixture fingerprint drift;
- duplicate fixture IDs;
- invalid procedure library that was expected to be valid;
- expected invalid-library case unexpectedly validates;
- nondeterministic logical replay;
- impossible metric-counter relationships;
- malformed result records;
- missing required scenario family;
- invalid primary outcome vocabulary;
- reported outcome inconsistent with frozen aggregate evidence.

A structurally valid `MIXED` or `NOT_SUPPORTED` outcome exits 0.

## 45. Determinism boundary

Identical:

- procedure library;
- simulator definition;
- initial world state;
- failure map;
- execution ID;
- mode;

must produce identical logical:

- primitive execution sequence;
- observations;
- verification records;
- call paths;
- interruption;
- final state;
- metrics;
- outcome classification.

No wall-clock timing is part of the determinism contract.

## 46. No automatic retry

A008 runner performs zero automatic retries.

After a checked mismatch:

- execution interrupts;
- runner returns evidence;
- caller decides what to do next.

Future A009 may combine that interruption with A007 expansion or model/tool
reasoning.

A008 itself does not.

## 47. No procedure retrieval/selection from natural language

A008 runner requires an explicit root procedure ID.

It does not select a procedure based on:

- natural-language similarity;
- A005 vector retrieval;
- Qwen model output;
- familiarity state.

Procedure selection belongs to the integrated A009 loop.

## 48. No graph semantics

Procedure call hierarchy is not an ASCA semantic relation graph.

A008 does not create or traverse:

- `AssociationEdge`;
- `RelationType`;
- identity links;
- causal graph paths;
- temporal graph paths.

A CALL_PROCEDURE edge exists only inside the validated procedure library and
has execution semantics, not general memory-graph semantics.

## 49. No generative-model dependency

A008 does not call `qwen3.5:4b` to:

- generate procedures;
- interpret actions;
- match expected outcomes;
- decide retries;
- select chunks;
- judge failure;
- explain interruptions.

No Ollama dependency is required for A008 qualification.

## 50. CI boundary

Because A008 qualification is deterministic and standard-library only, unlike
A005-A007 physical embedding experiments:

- portable unit tests run in GitHub CI;
- deterministic A008 qualification CLI also runs in GitHub CI;
- CI does not need Ollama;
- CI does not download model weights;
- CI does not call local OS/tool adapters.

This makes the A008 experiment itself reproducible in exact-commit CI.

## 51. Claims boundary

Permitted claims include:

- chunk reuse counts;
- exact primitive-sequence equivalence;
- exact final-state equivalence in declared fixtures;
- root-visible dispatch reduction;
- control-state compression ratio;
- exact expected-outcome verification;
- failure localization precision;
- interruption/call-path/provenance correctness.

A008 must not claim from those metrics alone:

- lower FLOPs;
- lower energy or power;
- faster real-world execution;
- fewer model tokens;
- human-like habits;
- biological procedural memory;
- general superiority over flat execution;
- real-world tool robustness.

## 52. FlyWireLLM boundary

FlyWireLLM remains paused and untouched.

A008 does not:

- restart training;
- use FlyWireLLM inference;
- mutate its repository;
- consume its holdout.

## 53. A007 boundary

A008 may produce real procedural mismatch evidence useful to a future surprise
controller, but A008 v0.1 does not automatically invoke A007.

A007 remains independently qualified.

A008 does not rewrite A007's `SUPPORTED` result.

## 54. Error handling

A008 fails closed on at least:

- blank procedure/action/step/expectation IDs;
- duplicate procedure IDs;
- duplicate step IDs in one procedure;
- missing callees;
- direct/indirect recursion;
- static call depth > max;
- invalid ACTION/CALL discriminated fields;
- CALL expectation inconsistent with callee ProcedureDefinition completion
  outcome;
- unknown root procedure ID;
- simulator missing action definition;
- simulator missing required child completion probe;
- malformed simulator state;
- invalid observation kind;
- impossible execution metrics;
- deterministic replay mismatch.

No malformed procedure is partially executed.

## 55. Portable qualification gates

Portable engineering qualification requires:

- all contract validations pass;
- all declared fail-closed cases fail as expected;
- FLAT/CHUNKED primitive sequence equivalence passes;
- FLAT/CHUNKED final-state equivalence passes;
- CHUNKED root-visible dispatch reduction demonstrated in declared fixture;
- chunk reuse demonstrated across distinct parents;
- FLAT/CHUNKED exact failure localization passes;
- BLIND_CHUNKED coarser localization demonstrated in a declared negative-control
  fixture;
- explanation provenance correct;
- no post-interruption primitive executes;
- deterministic repeat passes;
- no model/tool/graph dependency.

## 56. Deterministic qualification artifact

A008 qualification script emits UTF-8 JSON containing at least:

- qualification scope/version;
- fixture version/fingerprint;
- mode definitions;
- case IDs;
- library/profile constraints;
- per-case mode results;
- aggregate metrics;
- chunk reuse evidence;
- failure-localization evidence;
- deterministic-repeat evidence;
- primary hypothesis outcome;
- experiment-valid flag;
- errors.

Stdout bytes and optional `--output` bytes must be identical.

## 57. Qualification fixture freeze

Before the first final deterministic qualification run:

- fixture case IDs;
- procedures;
- step/action refs;
- simulator action transitions;
- simulator completion probes;
- failure map;
- expected final states;
- required comparison labels;
- outcome rules;

are frozen and fingerprinted.

After observing the final outcome, result chasing is forbidden.

A demonstrated fixture-validity defect may be corrected only under a new RED
regression test, with the correction documented.

## 58. Task/closure evidence

A008 closes only when:

- task/roadmap state is recoverable;
- contracts/library/verifier/runner/simulator are tested;
- FLAT/CHUNKED/BLIND_CHUNKED controls are qualified;
- deterministic qualification outcome is recorded;
- fixture fingerprint is frozen;
- exact branch CI passes including the A008 qualification script;
- whole-branch review resolves Critical/Important findings;
- post-review deterministic qualification reruns if semantics/validation change;
- post-review exact branch CI passes;
- fast-forward main integration succeeds;
- exact final-main CI passes;
- main is clean/synchronized 0/0;
- Issue #8 closes only after those gates;
- FlyWireLLM remains paused/untouched.

## 59. Non-goals

A008 v0.1 does not:

- execute real OS commands;
- call APIs;
- call LConnect/BConnect as procedural actions;
- use Qwen3.5:4b;
- use Ollama;
- generate procedures from language;
- learn new procedures;
- optimize procedures automatically;
- semantic-match observations;
- retry failed actions;
- recover automatically after interruption;
- call A007 automatically;
- infer causal truth;
- traverse a semantic graph;
- choose procedures from natural language;
- claim FLOP/energy savings.

## 60. Next milestone boundary

After A008 qualification, the next roadmap milestone remains:

`A009 — Integrated Cognitive Loop`

A009 may combine:

- A003 Familiarity;
- A005 Vector Retrieval;
- A006 Working Set;
- A007 Bounded Expansion;
- A008 Procedural Memory;
- A004 Model Adapter.

A009 is the appropriate place to test:

- procedure selection from retrieved context;
- real execution-mismatch-driven expansion;
- optional model reasoning;
- eventual real tool adapters.

A008 must not prematurely implement those integrations.

## 61. Success definition

A008 succeeds as an engineering milestone when FlyWireASCA can:

1. validate an immutable hierarchical procedure library;
2. reuse the same procedure chunk from multiple parents;
3. execute primitive actions through a deterministic abstract executor;
4. verify exact expected outcomes after checked steps;
5. interrupt immediately on checked mismatch;
6. preserve exact failing step, call path, expected/observed evidence, and
   explanation-memory references;
7. flatten the same hierarchy deterministically;
8. demonstrate FLAT/CHUNKED primitive and final-state equivalence on declared
   success fixtures;
9. reduce root-controller-visible dispatches in CHUNKED mode;
10. demonstrate that BLIND_CHUNKED trades failure localization for coarser
    chunk-boundary checking;
11. terminate deterministically without recursion/retry/tool/model dependencies.

The research/mechanism hypothesis is separately SUPPORTED only if the frozen
deterministic qualification satisfies the declared correctness, reuse,
dispatch-reduction, localization, provenance, and determinism conditions.

A negative research outcome remains valid evidence and must be recorded rather
than tuned away.