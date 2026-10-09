# A008 Procedural Memory / Skill Chunking Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic hierarchical procedural-memory subsystem that reuses procedure chunks, verifies exact expected outcomes, interrupts on checked mismatches, and demonstrates reduced root-controller-visible dispatches without sacrificing CHUNKED correctness or failure localization relative to FLAT execution.

**Architecture:** A008 reuses A002 `ProcedureRef` and `Observation`, adds immutable procedure/step/execution records, validates an acyclic procedure library, and executes abstract actions through a deterministic simulator. FLAT expands to primitive actions, CHUNKED preserves hierarchy with primitive checkpoints, and BLIND_CHUNKED suppresses internal primitive checks while retaining child-completion boundary checks. The deterministic benchmark and qualification CLI use no Ollama or real tools and therefore run in GitHub CI.

**Tech Stack:** Python >=3.11 standard library only, frozen dataclasses, `Enum`, `Protocol`, hashlib/json for deterministic evidence, pytest, existing FlyWireASCA A002 contracts.

**Spec:** `docs/superpowers/specs/2026-10-09-a008-procedural-memory-design.md`

## Global Constraints

- Repository: public `funggier/FlyWireASCA`.
- Work branch: `research/a008-procedural-memory`.
- Base main: `d5342fbb74f7dc49e5fcc5472847495ba1212434`.
- Milestone: **A008 — Procedural Memory / Skill Chunking**.
- Reuse A002 `ProcedureRef` and `Observation`; do not create duplicate identity contracts.
- Procedure step kinds are exactly `ACTION` and `CALL_PROCEDURE`.
- Outcome matcher vocabulary is exactly `EXACT`.
- Execution modes are exactly `FLAT`, `CHUNKED`, `BLIND_CHUNKED`.
- Execution states are exactly `READY`, `RUNNING`, `COMPLETED`, `INTERRUPTED`, `FAILED_VALIDATION`.
- Every procedure has at least one step and an explicit `completion_outcome`.
- Every ACTION has a nonblank `action_ref` and no callee.
- Every CALL_PROCEDURE has a nonblank callee ID and no action ref.
- Every step has an explicit expected outcome.
- Every CALL_PROCEDURE expected outcome must match the callee's `completion_outcome` on observation kind, expected payload ref, and matcher; expectation IDs may differ.
- Procedure IDs are unique; step IDs are unique within a procedure.
- Direct and indirect recursion are forbidden.
- Primary `max_call_depth = 8`; depth counts root as 1.
- FLAT removes CALL_PROCEDURE steps by deterministic flattening and executes only primitive ACTION steps.
- CHUNKED preserves hierarchy, verifies every primitive ACTION and every CALL completion boundary.
- BLIND_CHUNKED suppresses ACTION verification below root only; root ACTION checks and every CALL completion-boundary check remain enabled.
- Checked mismatch interrupts immediately with zero automatic retries and no later primitive execution.
- Explanation-memory IDs are provenance only; no causal truth inference.
- Core runner receives caller-supplied nonblank execution IDs; no random UUIDs.
- Canonical primitive path is `<procedure-id>/<procedure-id>/...::<step-id>`.
- Completion observers do not count as primitive actions or standalone step events.
- FLAT `procedure_call_count = 0`.
- CHUNKED/BLIND_CHUNKED increment procedure-call count once per executed CALL_PROCEDURE.
- Root-visible dispatch count includes only root ACTION/CALL dispatches; child-internal dispatches and completion probes are excluded.
- No real OS/API/LConnect/BConnect execution.
- No Qwen3.5:4b, Ollama, embedding, semantic matcher, or graph traversal.
- A008 does not invoke A007 automatically.
- A007 final `SUPPORTED` outcome remains unchanged.
- FlyWireLLM remains paused and untouched.
- Deterministic A008 qualification script must run in GitHub CI.
- Primary outcome vocabulary is exactly `SUPPORTED`, `MIXED`, `NOT_SUPPORTED`.
- Valid `MIXED` or `NOT_SUPPORTED` qualification exits 0.
- Claims are limited to exact execution/dispatch/reuse/localization/control-state metrics; no FLOP, energy, token, or real-world speed claims.
- A009 remains PLANNED until A008 final-main CI and synchronization are GREEN.
- No reset/clean/rebase/force push.

## File Structure

- `src/flywire_asca/procedural_memory/__init__.py`: public A008 exports.
- `src/flywire_asca/procedural_memory/models.py`: enums and immutable procedure/execution evidence records.
- `src/flywire_asca/procedural_memory/library.py`: immutable `ProcedureLibrary`, hierarchy validation, static depth, deterministic flattening.
- `src/flywire_asca/procedural_memory/verifier.py`: exact expected-outcome verification and canonical provenance helpers.
- `src/flywire_asca/procedural_memory/simulator.py`: deterministic simulated world state, action effects, completion probes, failure injection, state digest.
- `src/flywire_asca/procedural_memory/runner.py`: executor protocol plus FLAT/CHUNKED/BLIND_CHUNKED execution and metrics.
- `src/flywire_asca/procedural_memory/benchmark.py`: deterministic fixture, comparative metrics, primary hypothesis classification.
- `scripts/qualify_procedural_memory_a008.py`: frozen UTF-8 deterministic qualification CLI.
- `tests/test_procedural_memory_models.py`: model/enumeration/invariant tests.
- `tests/test_procedural_memory_library.py`: registry/cycle/depth/callee/call-contract/flattening tests.
- `tests/test_procedural_memory_verifier.py`: exact matching/provenance tests.
- `tests/test_procedural_memory_simulator.py`: state transition/failure/probe/digest tests.
- `tests/test_procedural_memory_runner.py`: mode semantics, interruption, metrics, determinism.
- `tests/test_procedural_memory_benchmark.py`: portable research fixture/metrics/outcome tests.
- `tests/test_procedural_memory_qualification_cli.py`: fixture freeze, CLI validity, UTF-8, evidence/outcome drift tests.
- `tests/test_a008_task_ledger.py`: A008 live/closure state and evidence.
- `docs/development/tasks/A008-procedural-memory-skill-chunking.md`: recoverable task ledger.
- `docs/development/reports/ASCA-20261009-A008-procedural-memory-skill-chunking.md`: final qualification report.

## Review Focus

1. **BLIND_CHUNKED false success:** if internal primitive verification is suppressed but no state-based completion probe is checked, corrupted child state can look successful; Task 3 must prove BLIND localizes the injected failure at the nearest CALL boundary rather than silently completing.
2. **Flattened provenance loss:** flattening nested chunks can accidentally lose the originating call path, explanation IDs, or primitive expected outcome; Task 1 pins exact flattened records and canonical primitive paths.
3. **Post-interruption side effects:** a recursive/iterative runner can execute a later primitive after mismatch while returning INTERRUPTED correctly; Task 3 pins simulator execution logs and completed primitive paths to prove no later action runs.
4. **Metric double counting:** CALL completion observations or child-internal steps can inflate primitive/root-visible/step-event counts; Task 3 pins exact per-mode metrics on a known hierarchy.
5. **Qualification outcome drift:** the CLI can report a vocabulary-valid SUPPORTED/MIXED/NOT_SUPPORTED inconsistent with aggregate evidence; Task 4 must recompute and fail closed on outcome drift.

---

### Task 1: Add A008 procedure models, validated library, flattening, and task activation

**Files:**
- Create: `src/flywire_asca/procedural_memory/__init__.py`
- Create: `src/flywire_asca/procedural_memory/models.py`
- Create: `src/flywire_asca/procedural_memory/library.py`
- Create: `tests/test_procedural_memory_models.py`
- Create: `tests/test_procedural_memory_library.py`
- Create: `tests/test_a008_task_ledger.py`
- Create: `docs/development/tasks/A008-procedural-memory-skill-chunking.md`
- Modify: `docs/development/tasks/CURRENT.md`
- Modify: `docs/development/tasks/ROADMAP.md`
- Modify: `README.md`
- Modify: `tests/test_task_ledger.py`
- Modify historical milestone tests only when they incorrectly freeze live A008 state.

**Interfaces:**
- Produces `ProcedureStepKind(str, Enum)`: ACTION, CALL_PROCEDURE.
- Produces `OutcomeMatcherKind(str, Enum)`: EXACT.
- Produces `ProcedureExecutionMode(str, Enum)`: FLAT, CHUNKED, BLIND_CHUNKED.
- Produces `ProcedureExecutionState(str, Enum)`: READY, RUNNING, COMPLETED, INTERRUPTED, FAILED_VALIDATION.
- Produces immutable `ExpectedOutcome(expectation_id: str, observation_kind: ObservationKind, expected_payload_ref: str, matcher: OutcomeMatcherKind = EXACT)`.
- Produces immutable `ProcedureStep(step_id: str, kind: ProcedureStepKind, expected_outcome: ExpectedOutcome, explanation_memory_ids: tuple[str, ...] = (), action_ref: str | None = None, callee_procedure_id: str | None = None)`.
- Produces immutable `ProcedureDefinition(procedure: ProcedureRef, steps: tuple[ProcedureStep, ...], completion_outcome: ExpectedOutcome)`.
- Produces immutable `FlattenedPrimitiveStep(procedure_id: str, step_id: str, call_path: tuple[str, ...], primitive_step_path: str, action_ref: str, expected_outcome: ExpectedOutcome, explanation_memory_ids: tuple[str, ...])`.
- Produces immutable `ProcedureLibrary(procedures: tuple[ProcedureDefinition, ...], max_call_depth: int = 8)` with deterministic `get(procedure_id: str) -> ProcedureDefinition`.
- Produces `flatten_procedure(library: ProcedureLibrary, root_procedure_id: str) -> tuple[FlattenedPrimitiveStep, ...]`.
- Produces `canonical_primitive_step_path(call_path: tuple[str, ...], step_id: str) -> str`.
- Produces `canonical_explanation_memory_ids(library: ProcedureLibrary, call_path: tuple[str, ...], step: ProcedureStep) -> tuple[str, ...]` for reuse by flattening, verifier evidence, and interruption construction.

- [ ] **Step 1: Write failing enum/model invariant tests**

Pin exact enum vocabularies; frozen dataclasses; nonblank IDs/payload refs; ACTION/CALL discriminated fields; required completion outcome; duplicate step IDs; unique nonblank explanation-memory IDs.

- [ ] **Step 2: Run model tests RED**

Run:
```powershell
python -m pytest -q tests/test_procedural_memory_models.py
```

Expected: import/collection FAIL because A008 package does not exist.

- [ ] **Step 3: Implement model contracts only**

Do not implement simulator/runner behavior.

- [ ] **Step 4: Write failing library validation tests**

Pin:
- duplicate procedure ID;
- missing callee;
- direct recursion;
- indirect recursion;
- root depth = 1;
- static depth exactly 8 allowed;
- static depth 9 rejected;
- CALL expected outcome kind/payload/matcher must equal the callee `completion_outcome`; parent/callee expectation IDs may differ;
- unknown lookup/root fails closed.

- [ ] **Step 5: Write failing flattening/provenance tests**

Use a root -> child -> grandchild fixture and require:
- ordered primitive action refs exactly match declaration expansion;
- CALL steps omitted from flattened primitive list;
- originating procedure/step IDs preserved;
- call paths preserved;
- canonical primitive path format is exactly `root/child/grandchild::step-id`;
- canonical explanation-memory union from `canonical_explanation_memory_ids(...)` preserves root-to-origin procedure refs then step refs, unique-first;
- repeated flatten returns identical tuple.

- [ ] **Step 6: Run library tests RED**

Run:
```powershell
python -m pytest -q tests/test_procedural_memory_library.py
```

Expected: FAIL because library APIs do not exist.

- [ ] **Step 7: Implement ProcedureLibrary and deterministic flattening**

Use DFS with explicit active-stack cycle detection and memoized static depth only if useful; no general graph contract/import.

- [ ] **Step 8: Write live A008 task/roadmap RED tests**

Require:
- CURRENT A008 ACTIVE, Issue #8, branch `research/a008-procedural-memory`;
- ROADMAP A008 ACTIVE;
- A009-A011 remain PLANNED;
- task ledger records no real tool/model/Ollama/graph/retry dependency;
- task ledger records FLAT/CHUNKED/BLIND_CHUNKED, max depth 8, exact matcher, FlyWireLLM paused;
- README current stage A008;
- A007 closure report remains historical evidence.

- [ ] **Step 9: Verify task-state RED**

Run:
```powershell
python -m pytest -q tests/test_a008_task_ledger.py tests/test_task_ledger.py
```

Expected: FAIL because A008 is still PLANNED and Issue #8 does not exist.

- [ ] **Step 10: Create GitHub Issue #8 and activate task docs**

Issue title:

`A008 — Procedural Memory / Skill Chunking`

Do not create A009 issue.

- [ ] **Step 11: Run Task 1 gates**

Run:
```powershell
python -m pytest -q tests/test_procedural_memory_models.py tests/test_procedural_memory_library.py tests/test_a008_task_ledger.py tests/test_task_ledger.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
git diff --check
```

Expected: all PASS.

- [ ] **Step 12: Commit Task 1**

Commit:

`Add A008 procedure library contracts and task activation`

### Task 2: Add exact verifier and deterministic simulator

**Files:**
- Create: `src/flywire_asca/procedural_memory/verifier.py`
- Create: `src/flywire_asca/procedural_memory/simulator.py`
- Create: `tests/test_procedural_memory_verifier.py`
- Create: `tests/test_procedural_memory_simulator.py`
- Modify: `src/flywire_asca/procedural_memory/models.py`
- Modify: `src/flywire_asca/procedural_memory/__init__.py`
- Modify: `docs/development/tasks/A008-procedural-memory-skill-chunking.md`

**Interfaces:**
- Produces immutable `OutcomeVerification(expectation_id: str, observation_id: str, matched: bool)`.
- Produces `verify_outcome(expected: ExpectedOutcome, observed: Observation) -> OutcomeVerification`.
- Consumes `canonical_explanation_memory_ids(...)` from Task 1; verifier does not define a second provenance implementation.
- Produces immutable `SimulatedWorldState(values: tuple[tuple[str, str], ...])` with sorted unique nonblank keys and deterministic `get(key: str) -> str | None`.
- Produces immutable `SimulatedActionDefinition(action_ref: str, writes: tuple[tuple[str, str], ...], observation_kind: ObservationKind, success_payload_ref: str)`.
- Produces immutable `SimulatedCompletionProbe(procedure_id: str, state_key: str, observation_kind: ObservationKind)`.
- Produces immutable `SimulatedFailureOverride(primitive_step_path: str, observation_kind: ObservationKind, payload_ref: str, suppress_writes: bool = True)`.
- Produces mutable execution-scoped `DeterministicProcedureSimulator(action_definitions: tuple[SimulatedActionDefinition, ...], completion_probes: tuple[SimulatedCompletionProbe, ...], initial_state: SimulatedWorldState, failure_overrides: tuple[SimulatedFailureOverride, ...] = ())`.
- Simulator methods:
  - `execute_action(*, action_ref: str, execution_id: str, call_path: tuple[str, ...], step_id: str) -> Observation`
  - `observe_procedure_completion(*, procedure_id: str, execution_id: str, call_path: tuple[str, ...]) -> Observation`
  - `world_state() -> SimulatedWorldState`
  - `world_state_ref() -> str`
  - `executed_primitive_step_paths() -> tuple[str, ...]`.

- [ ] **Step 1: Write failing exact-verifier tests**

Pin kind mismatch => `matched=False`; payload mismatch => false; exact kind/payload => true; executor-provided `Observation.expected_match` is ignored; observation object remains unchanged.

- [ ] **Step 2: Write failing explanation-provenance tests**

For root -> child -> grandchild failing step require canonical unique-first union:
root ProcedureRef explanation IDs -> child -> grandchild -> failing step IDs.

Reject call path that does not resolve exactly through library CALL relationships.

- [ ] **Step 3: Verify verifier RED**

Run:
```powershell
python -m pytest -q tests/test_procedural_memory_verifier.py
```

Expected: FAIL because verifier APIs do not exist.

- [ ] **Step 4: Implement verifier/provenance helpers minimally**

No semantic matching or causal inference.

- [ ] **Step 5: Write failing simulator model/state tests**

Pin:
- world-state tuples sorted by key;
- duplicate/blank keys rejected;
- duplicate/blank action refs rejected by simulator registry;
- duplicate completion-probe procedure IDs rejected;
- duplicate write keys inside one action definition are rejected so action effects are unambiguous;
- state writes apply deterministically with unique final keys;
- unknown action ref fails closed before mutation;
- missing completion probe fails closed;
- completion probe emits current state-key value;
- missing probed state key fails closed.

- [ ] **Step 6: Write failing deterministic failure-injection tests**

Require:
- failure override keyed by exact canonical primitive path;
- replacement observation kind/payload applied;
- `suppress_writes=True` preserves pre-action state;
- `suppress_writes=False` applies writes but still emits override observation;
- executed primitive path log records exactly one entry per action call;
- observation IDs deterministic from execution ID/path/step/event;
- same initial state/inputs/execution ID => equal observations/state/ref/log.

- [ ] **Step 7: Verify simulator RED**

Run:
```powershell
python -m pytest -q tests/test_procedural_memory_simulator.py
```

Expected: FAIL because simulator does not exist.

- [ ] **Step 8: Implement deterministic simulator**

Use canonical JSON + SHA-256 for `world_state_ref`; no timestamps/randomness.

- [ ] **Step 9: Run Task 2 gates**

Run:
```powershell
python -m pytest -q tests/test_procedural_memory_verifier.py tests/test_procedural_memory_simulator.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
git diff --check
```

Expected: all PASS.

- [ ] **Step 10: Commit Task 2**

Commit:

`Add A008 exact verifier and deterministic simulator`

### Task 3: Implement FLAT, CHUNKED, and BLIND_CHUNKED execution

**Files:**
- Create: `src/flywire_asca/procedural_memory/runner.py`
- Create: `tests/test_procedural_memory_runner.py`
- Modify: `src/flywire_asca/procedural_memory/models.py`
- Modify: `src/flywire_asca/procedural_memory/__init__.py`
- Modify: `docs/development/tasks/A008-procedural-memory-skill-chunking.md`

**Interfaces:**
- Produces `ProcedureExecutor(Protocol)` with the two executor methods from Task 2.
- Produces immutable `ProcedureExecutionMetrics(primitive_action_count: int, procedure_call_count: int, root_visible_dispatch_count: int, total_step_event_count: int, expected_outcome_check_count: int, suppressed_internal_check_count: int, max_runtime_call_depth: int)`.
- Produces immutable `StepExecutionResult(procedure_id: str, step_id: str, call_path: tuple[str, ...], kind: ProcedureStepKind, observation: Observation, expected_outcome: ExpectedOutcome, verification: OutcomeVerification | None, primitive_action_executed: bool)`.
- Produces immutable `ProcedureInterruption(root_procedure_id: str, failing_procedure_id: str, failing_step_id: str, call_path: tuple[str, ...], expected_outcome: ExpectedOutcome, observed: Observation, explanation_memory_ids: tuple[str, ...], completed_primitive_step_paths: tuple[str, ...])`.
- Produces immutable `ProcedureExecutionResult(execution_id: str, root_procedure_id: str, mode: ProcedureExecutionMode, state: ProcedureExecutionState, step_results: tuple[StepExecutionResult, ...], interruption: ProcedureInterruption | None, final_world_state_ref: str | None, metrics: ProcedureExecutionMetrics)`.
- Produces `run_procedure(library: ProcedureLibrary, *, root_procedure_id: str, mode: ProcedureExecutionMode, executor: ProcedureExecutor, execution_id: str) -> ProcedureExecutionResult`.

- [ ] **Step 1: Write failing FLAT execution tests**

Use hierarchy root -> shared-child -> nested-child. Pin:
- primitive execution order equals `flatten_procedure`;
- no CALL step result records;
- `procedure_call_count == 0`;
- primitive count == total step-event count;
- root-visible dispatch count == primitive count;
- every primitive check verified;
- max runtime depth reflects original flattened call path, not 1;
- success state COMPLETED and no interruption.

- [ ] **Step 2: Write failing CHUNKED success/metrics tests**

Pin exact known hierarchy:
- root ACTION counts root-visible 1;
- root CALL counts root-visible +1 and procedure_call +1;
- child primitive ACTIONs do not increase root-visible dispatch;
- nested CALL increments procedure-call count;
- completion probes create CALL step result records but not primitive actions;
- total step events = ACTION result records + CALL result records;
- expected-outcome checks include checked ACTIONs + CALL boundaries;
- suppressed count = 0;
- ordered primitive action refs/final state equal FLAT.

- [ ] **Step 3: Write failing immediate-interruption tests for FLAT and CHUNKED**

Inject failure at a nested primitive and require:
- state INTERRUPTED;
- failing procedure/step/call path exact;
- expected/observed exact;
- canonical explanation-memory provenance exact;
- completed primitive path tuple excludes failing primitive if its verification fails after execution? **Ruling:** it includes the failing primitive because the action executed, but no later primitive path;
- simulator execution log proves no later primitive executes;
- parent completion observer is not called after a checked child primitive mismatch and no parent CALL StepExecutionResult is emitted for the unfinished call;
- zero automatic retries.

- [ ] **Step 4: Write failing BLIND_CHUNKED negative-control tests**

Inject a nested primitive failure with suppressed state write. Require:
- internal primitive ACTION result has `verification=None`;
- `suppressed_internal_check_count` increments;
- child completion probe observes wrong/missing expected state;
- interruption attributed to the nearest parent CALL_PROCEDURE step;
- BLIND interruption provenance uses the parent call path + CALL step references, not the undetected primitive step references;
- no primitive-level interruption is emitted;
- no later root action executes after CALL-boundary mismatch;
- failure-free BLIND final state equals FLAT/CHUNKED.

- [ ] **Step 5: Write failing runner input/record validation tests**

Pin:
- blank execution ID rejected before executor call;
- unknown root rejected;
- invalid mode rejected;
- executor missing required callable methods rejected;
- result state/interrupt consistency;
- nonnegative metrics;
- max runtime call depth <= library max;
- deterministic repeated execution with fresh equivalent simulators.

- [ ] **Step 6: Verify runner RED**

Run:
```powershell
python -m pytest -q tests/test_procedural_memory_runner.py
```

Expected: FAIL because runner/results do not exist.

- [ ] **Step 7: Implement shared execution engine**

Use one hierarchy walker for CHUNKED/BLIND and one flattened iterator for FLAT. Keep mode-specific verification/root-dispatch counting explicit; do not duplicate action execution logic.

- [ ] **Step 8: Run Task 3 gates**

Run:
```powershell
python -m pytest -q tests/test_procedural_memory_runner.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
git diff --check
```

Expected: all PASS.

- [ ] **Step 9: Commit Task 3**

Commit:

`Add A008 hierarchical procedural runner`

### Task 4: Add deterministic benchmark and exact qualification CLI in CI

**Files:**
- Create: `src/flywire_asca/procedural_memory/benchmark.py`
- Create: `scripts/qualify_procedural_memory_a008.py`
- Create: `tests/test_procedural_memory_benchmark.py`
- Create: `tests/test_procedural_memory_qualification_cli.py`
- Modify: `.github/workflows/ci.yml`
- Modify: `tests/test_ci_contract.py`
- Modify: `docs/development/tasks/A008-procedural-memory-skill-chunking.md`

**Benchmark records/interfaces:**
- Produces immutable `ProceduralBenchmarkCase` containing library, root ID, initial world state, action definitions, completion probes, failure overrides, expected final state/ref, labels for success/failure/reuse/localization.
- Produces immutable `ProceduralModeCaseResult`.
- Produces immutable `ProceduralBenchmarkCaseResult`.
- Produces immutable `ProceduralBenchmarkReport`.
- Produces `build_a008_fixture() -> tuple[ProceduralBenchmarkCase, ...]`.
- Produces `run_a008_benchmark(cases: Iterable[ProceduralBenchmarkCase]) -> ProceduralBenchmarkReport`.
- Produces `classify_a008_hypothesis(report: ProceduralBenchmarkReport) -> str`.
- Produces `qualify_a008_report(report: ProceduralBenchmarkReport) -> list[str]`.

**Frozen fixture families:**
- tea preparation using shared `heat-water`;
- coffee preparation reusing the exact same `heat-water` procedure ID;
- document backup with nested verification;
- package preparation with reusable preparation chunk;
- injected primitive failure inside reused chunk;
- depth >2 success hierarchy;
- direct recursion expected invalid;
- indirect recursion expected invalid;
- missing callee expected invalid;
- depth 9 expected invalid.

- [ ] **Step 1: Write failing fixture/reuse tests**

Pin:
- unique case IDs;
- same `heat-water` procedure ID referenced from at least two distinct parent definitions;
- at least one valid hierarchy depth >2;
- all required scenario families present;
- invalid-library cases declare their expected validation substring.

- [ ] **Step 2: Write failing comparative metric tests**

For valid success cases require:
- FLAT/CHUNKED ordered primitive sequence equivalence;
- FLAT/CHUNKED final-state equivalence;
- BLIND final-state equivalence when no failure injected;
- aggregate CHUNKED root-visible dispatch < FLAT;
- at least one compression ratio >1.0;
- reused chunk count >=2 parent uses;
- mode-specific metric invariants from spec.

- [ ] **Step 3: Write failing failure-localization tests**

Require:
- FLAT and CHUNKED exact failing primitive localization on checked failure fixture;
- BLIND localization at declared nearest CALL boundary;
- explanation provenance correct;
- no post-interruption execution;
- call-path correctness.

- [ ] **Step 4: Write failing invalid-library and deterministic-repeat tests**

Expected invalid cases must fail before execution and are excluded from success/final-state/root-visible-dispatch denominators. Valid benchmark repeated twice must produce a byte/logically equal report because A008 records no timing.

- [ ] **Step 5: Write failing primary-outcome classification tests**

Pin exact rules:
- SUPPORTED only when correctness/equivalence/reuse/aggregate dispatch reduction/compression/localization/provenance/no-post-failure/determinism conditions all hold;
- MIXED when reuse/reduction exists but a correctness/localization condition fails;
- NOT_SUPPORTED when no declared dispatch reduction, no measurable chunk reuse, or core CHUNKED correctness objective is not demonstrated.

- [ ] **Step 6: Verify benchmark RED**

Run:
```powershell
python -m pytest -q tests/test_procedural_memory_benchmark.py
```

Expected: FAIL because benchmark does not exist.

- [ ] **Step 7: Implement benchmark and qualifier**

Keep BLIND metrics separate from the primary CHUNKED hypothesis decision except for the required negative-control localization evidence.

- [ ] **Step 8: Write failing CLI freeze/validity tests**

Pin:
- qualification scope/version;
- fixture version/fingerprint literal;
- case ID set;
- mode definitions;
- max depth 8;
- no model/tool/Ollama fields;
- output includes per-case results, aggregate metrics, reuse/localization evidence, experiment_valid, errors, primary outcome;
- stdout UTF-8 bytes equal `--output` bytes;
- valid MIXED/NOT_SUPPORTED exits 0;
- invalid evidence exits nonzero;
- validator recomputes expected outcome and rejects outcome drift;
- impossible metric relationships fail closed.

- [ ] **Step 9: Implement qualification CLI and freeze fixture fingerprint before first final run**

The CLI runs the deterministic benchmark directly; it does not shell to pytest or depend on external services.

- [ ] **Step 10: Add A008 deterministic qualification to GitHub CI**

Modify `.github/workflows/ci.yml` to run:

```powershell
python scripts/qualify_procedural_memory_a008.py
```

Keep all A004-A007 physical Ollama scripts local-only.

- [ ] **Step 11: Extend CI contract tests**

Pin that:
- A008 qualification script is present in workflow;
- no Ollama/local HTTP command appears;
- prior physical scripts remain absent;
- full pytest, architecture audit, A003 benchmark, repository qualifier remain present.

- [ ] **Step 12: Run Task 4 gates including final deterministic qualification**

Run:
```powershell
python -m pytest -q tests/test_procedural_memory_benchmark.py tests/test_procedural_memory_qualification_cli.py tests/test_ci_contract.py
python scripts/qualify_procedural_memory_a008.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
git diff --check
```

Expected: all engineering gates PASS. Qualification may validly report SUPPORTED/MIXED/NOT_SUPPORTED.

- [ ] **Step 13: Commit Task 4**

Commit:

`Add A008 deterministic procedural qualification`

### Task 5: Exact branch qualification, report, and closure transition

**Files:**
- Create: `docs/development/reports/ASCA-20261009-A008-procedural-memory-skill-chunking.md`
- Modify: `docs/development/tasks/A008-procedural-memory-skill-chunking.md`
- Modify: `docs/development/tasks/CURRENT.md`
- Modify: `docs/development/tasks/ROADMAP.md`
- Modify: `README.md`
- Modify: `tests/test_a008_task_ledger.py`
- Modify: `tests/test_task_ledger.py`

- [ ] **Step 1: Run fresh deterministic qualification and repository gate**

Run from clean branch candidate:

```powershell
python scripts/qualify_procedural_memory_a008.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
git diff --check
git status --short --branch
git rev-parse HEAD
```

Record exact output/metrics/outcome.

- [ ] **Step 2: Verify isolation read-only**

Confirm:
- A002 `ProcedureRef` / `Observation` unchanged;
- A007 closure/result remains `SUPPORTED`;
- A005/A006 retrieval/selection semantics unchanged;
- A004 model path untouched;
- no real tool/OS/API invocation introduced;
- FlyWireLLM clean/paused with no training runner.

- [ ] **Step 3: Push branch and require exact CI**

Because A008 deterministic qualification is now in workflow, exact branch CI must prove both portable tests and the frozen A008 experiment.

- [ ] **Step 4: Write A008 qualification report**

Record:
- exact branch SHA and CI run ID;
- test count and audit/qualifier/A003 results;
- fixture version/fingerprint/case IDs;
- max depth and mode definitions;
- primary SUPPORTED/MIXED/NOT_SUPPORTED outcome;
- success/final-state/primitive-sequence equivalence;
- root-visible dispatch counts and compression ratios;
- primitive/procedure-call/check/suppressed-check metrics;
- shared chunk reuse evidence;
- exact FLAT/CHUNKED failure localization;
- BLIND chunk-boundary localization;
- call-path/provenance/no-post-interruption evidence;
- deterministic repeat;
- claims boundary;
- no model/Ollama/tool/graph/retry dependency;
- A007 `SUPPORTED` preserved;
- FlyWireLLM paused/untouched.

- [ ] **Step 5: Write failing closure-transition tests**

Require:
- A008 task Status DONE;
- ROADMAP A008 DONE;
- CURRENT A009 PLANNED/no issue;
- README current stage reflects A008 result;
- report exact SHA/CI/fingerprint/outcome;
- exactly one primary outcome;
- A009 issue not created;
- no real tool/model execution claim.

Verify RED before edits.

- [ ] **Step 6: Transition task/roadmap/README and run closure gate**

Run:
```powershell
python -m pytest -q tests/test_a008_task_ledger.py tests/test_task_ledger.py
python scripts/qualify_procedural_memory_a008.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
git diff --check
```

Expected: all PASS.

- [ ] **Step 7: Commit closure candidate and require exact closure-branch CI**

Commit:

`Qualify A008 procedural memory skill chunking`

Push normally and require exact SHA CI.

### Task 6: Whole-branch review, post-review qualification, and main integration

**Files:**
- Modify Task 5 report/task/tests only when review or integration evidence requires it.

- [ ] **Step 1: Perform whole-branch review**

Review base:

`d5342fbb74f7dc49e5fcc5472847495ba1212434..closure-head`

Prioritize:
- BLIND false success / missing completion probe;
- flatten provenance/call-path loss;
- post-interruption execution;
- metric double counting;
- recursion/depth off-by-one;
- CALL expected-outcome vs callee completion contract drift;
- executor `Observation.expected_match` accidentally trusted;
- qualification outcome drift;
- invalid-library case treated as runtime success;
- hidden model/tool/graph/retry dependency;
- control-state reduction overclaimed as compute/energy reduction.

- [ ] **Step 2: Fix Critical/Important findings with RED -> GREEN tests**

If runner/library/simulator/benchmark/qualification semantics change, rerun the deterministic A008 qualification before accepting the fix.

- [ ] **Step 3: Run post-review full branch gate**

Run:
```powershell
python scripts/qualify_procedural_memory_a008.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
git diff --check
```

- [ ] **Step 4: Commit review evidence/fixes and require exact post-review branch CI**

Record reviewer limitation honestly if no fresh reviewer/subagent is available.

- [ ] **Step 5: Verify main integration preconditions**

Require:
- main clean;
- main == origin/main before merge;
- branch HEAD descends from A008 base/main;
- branch worktree clean;
- Issue #8 still open.

- [ ] **Step 6: Fast-forward local main only**

Run:

```powershell
git merge --ff-only research/a008-procedural-memory
```

No merge commit, rebase, reset, clean, or force push.

- [ ] **Step 7: Verify merged main before push**

Run:
```powershell
python scripts/qualify_procedural_memory_a008.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
git diff --check origin/main..HEAD
```

- [ ] **Step 8: Push main and require exact final-main CI**

Do not close Issue #8 until exact merged-main CI succeeds.

- [ ] **Step 9: Record main integration evidence with tested documentation-only commits**

Follow the A006/A007 closure discipline: any main commit that records a prior CI run must itself pass fresh local gates and exact-main CI before Issue #8 closes.

- [ ] **Step 10: Final synchronization and Issue #8 closure**

Require:
- final HEAD == origin/main;
- ahead/behind 0/0;
- main clean;
- exact final-main CI success;
- A009 still PLANNED/no issue;
- FlyWireLLM paused/untouched.

Close Issue #8 with final SHA/CI/test count/deterministic outcome/fixture fingerprint/key comparative metrics.

- [ ] **Step 11: Cleanup**

Remove clean A008 worktree and delete local `research/a008-procedural-memory` branch non-force. Preserve remote branch/history unless explicitly requested otherwise.

## A008 Non-Goals

A008 must not:
- execute real OS commands, APIs, LConnect, or BConnect as procedure actions;
- use Qwen3.5:4b or Ollama;
- generate or learn procedures;
- select a procedure from natural language;
- use semantic expected-outcome matching;
- retry or recover automatically after interruption;
- invoke A007 automatically;
- infer causal truth from explanation-memory IDs;
- build/traverse an ASCA semantic graph;
- claim lower FLOPs, energy, tokens, or real-world latency from fewer root-visible dispatches.

## Execution Order

Execute Tasks 1-6 sequentially with RED -> GREEN -> fresh regression -> commit at each checkpoint. Freeze the deterministic fixture and fingerprint before the first final qualification outcome is evaluated. Because A008 has no external model/tool dependency, the exact deterministic qualification CLI is part of GitHub CI. Keep experiment validity separate from the SUPPORTED/MIXED/NOT_SUPPORTED mechanism outcome. A009 remains PLANNED until A008 final main CI, Issue #8 closure, and synchronization are GREEN.