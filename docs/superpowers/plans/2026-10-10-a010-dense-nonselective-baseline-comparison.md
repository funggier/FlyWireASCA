# A010 Dense / Non-selective Baseline Comparison Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a frozen, reproducible A010 comparison between the real A009 selective cognitive loop and a deliberately non-selective A005 + A006 exhaustive baseline, then qualify the result as `SUPPORTED`, `MIXED`, or `NOT_SUPPORTED` without rewriting earlier milestone outcomes.

**Architecture:** Keep A009 unchanged and call its public `run_cognitive_loop()` for `ASCA_PRIMARY`. Add a separate A010 comparison package whose dense path evaluates all declared A005 cue tiers with full-index top-k, merges the shared retrieval evidence through existing A006 `select_exhaustive()`, and executes the same explicit A008 root procedure once in `CHUNKED` mode. Normalize both paths into A010 evidence contracts, freeze a deterministic comparison fixture and classifier, then add a local-only physical comparison using the already-pinned Qwen embedding identity.

**Tech Stack:** Python 3.11+, standard library dataclasses/enums/hashlib/json, pytest 8+, existing FlyWireASCA A003/A005/A006/A007/A008/A009 packages, Git/GitHub Actions, local Ollama only for secondary physical qualification.

**Spec:** `docs/superpowers/specs/2026-10-10-a010-dense-nonselective-baseline-comparison-design.md`

## Global Constraints

- Live Git/GitHub/runtime state is authoritative before activation.
- Do not reset, clean, rebase, or force-push the repository.
- Do not create the A010 GitHub issue until Task 1 activation.
- Preserve A006 `NOT_SUPPORTED`, A007 `SUPPORTED`, A008 `SUPPORTED`, and A009 `SUPPORTED` exactly.
- A010 `ASCA_PRIMARY` must call the real A009 public controller; do not fork or mutate A009 primary semantics.
- A010 `DENSE_EXHAUSTIVE` must use the real A005 `ExactVectorMemoryIndex` and A006 `select_exhaustive()`.
- Primary procedure mode is A008 `CHUNKED`; no real OS/API/LConnect/BConnect side effects.
- Dense retrieval uses the same corpus, cue texts, embedding evidence, and minimum similarity threshold as ASCA; dense query `top_k = max(1, index.document_count)`.
- The portable classifier vocabulary is exactly `SUPPORTED`, `MIXED`, `NOT_SUPPORTED`.
- A valid `MIXED` or `NOT_SUPPORTED` outcome exits successfully; invalid evidence exits nonzero.
- Do not construct a synthetic scalar efficiency score.
- Logical query/vector-score/active-memory counts are not FLOPs, energy, RAM bytes, hardware bandwidth, or general latency.
- Physical A005 identity stays `qwen3-embedding:0.6b`, digest `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`, dimension `1024`, threshold `0.5037018224299838`.
- Any A004 terminal model diagnostic that remains in physical evidence stays `qwen3.5:4b`, digest `2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd`, and cannot control primary A010 success/classification.
- FlyWireLLM remains untouched.
- A011 remains PLANNED with no GitHub issue until A010 closes.
- Repair the stale README sentence that says A009 Issue #9 remains open during Task 1 activation; do not rewrite A009 result evidence.

## Review Focus

1. **Dense top-k accidentally remains selective:** a dense run with more above-threshold memories than A007's max top-k must still return every above-threshold document; Task 2 adds a test that asserts dense query `top_k == max(1, index.document_count)` and exhaustive selected IDs contain all positive candidates, including the zero-document edge case where the query contract still requires positive top-k.
2. **Hidden per-variant fixture drift:** ASCA and dense must not receive different corpora, cue texts, thresholds, procedures, requirements, or initial states; Task 4 adds a validator test that mutates one shared-input fingerprint field and requires qualification failure.
3. **Dense-only success suppressed by aggregation:** a valid dense-only success must remain visible and prevent `SUPPORTED`; Task 4 adds an explicit classifier test with `dense_only_success_count == 1`.
4. **Ablation leaks outside its declared axis:** no-structural-expansion and familiarity-disabled diagnostics must not change threshold/corpus/procedure inputs; Task 3 adds contract tests that compare frozen input identities and fail on off-axis mutation.
5. **Raw case evidence disagrees with aggregate metrics:** payload validation must derive all primary counts from raw case results and reject edited aggregate-only claims; Task 5 adds a payload-tampering test.

---

### Task 1: Activate A010 and add comparison contracts

**Files:**
- Create: `src/flywire_asca/baseline_comparison/__init__.py`
- Create: `src/flywire_asca/baseline_comparison/models.py`
- Create: `tests/test_baseline_comparison_models.py`
- Create: `tests/test_a010_task_ledger.py`
- Create: `docs/development/tasks/A010-dense-nonselective-baseline-comparison.md`
- Modify: `docs/development/tasks/CURRENT.md`
- Modify: `docs/development/tasks/ROADMAP.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: A009 `CognitiveLoopResult`, A008 `ProcedureExecutionResult`, A005 `VectorMemoryResult`, and stable string/memory IDs.
- Produces:
  - `ComparisonVariant(str, Enum)` with exact values `ASCA_PRIMARY`, `DENSE_EXHAUSTIVE`, `ASCA_ALWAYS_MAX_SCOPE`, `ASCA_NO_STRUCTURAL_EXPANSION`, `ASCA_FAMILIARITY_DISABLED`.
  - `ComparisonRunResult` immutable normalized evidence contract.
  - `ComparisonCaseResult` immutable paired-case evidence contract.
  - `BaselineComparisonReport` immutable aggregate report contract.

- [ ] **Step 1: Re-check activation preconditions and create isolated execution state**

Use the `superpowers:using-git-worktrees` skill before implementation.

Verify:

```text
main == origin/main
worktree clean
latest main CI success
Issue #9 closed/completed
no A010 issue exists
```

Then create `research/a010-dense-nonselective-baseline-comparison` in an isolated worktree from the exact reviewed plan commit. Do not reset/clean/rebase.

- [ ] **Step 2: Create the actual A010 GitHub issue**

Create the issue only now. Capture the actual returned issue number; do not assume it is `#10`.

The issue body must link the approved spec and plan and state:

```text
ASCA_PRIMARY = A009 MISMATCH_DRIVEN_RECOVERY / SINGLE_BEST / SIGNAL_DRIVEN / CHUNKED
DENSE_EXHAUSTIVE = same A005 evidence + all cue tiers + full-index top_k + select_exhaustive + one CHUNKED attempt
historical A006/A007/A008/A009 outcomes unchanged
FlyWireLLM untouched
no hardware/FLOP/energy/general-latency claim
```

- [ ] **Step 3: Write failing model and task-ledger tests**

In `tests/test_baseline_comparison_models.py`, pin:

```python
def test_comparison_variant_vocabulary_is_exact():
    assert tuple(item.value for item in ComparisonVariant) == (
        "ASCA_PRIMARY",
        "DENSE_EXHAUSTIVE",
        "ASCA_ALWAYS_MAX_SCOPE",
        "ASCA_NO_STRUCTURAL_EXPANSION",
        "ASCA_FAMILIARITY_DISABLED",
    )
```

Add fail-closed construction tests for blank IDs, duplicate execution IDs, negative counts, impossible selected/activated candidate relationships, and non-boolean success flags.

In `tests/test_a010_task_ledger.py`, require:

- CURRENT = A010 / ACTIVE / actual issue number;
- ROADMAP A010 = ACTIVE and A011 = PLANNED;
- task ledger links exact spec/plan;
- task ledger preserves all four historical outcomes;
- README no longer says A009 Issue #9 “remains open”;
- README states A010 ACTIVE and A009 SUPPORTED.

- [ ] **Step 4: Run the focused tests and verify RED**

Run:

```bash
python -m pytest -q tests/test_baseline_comparison_models.py tests/test_a010_task_ledger.py
```

Expected: FAIL because the A010 package/contracts/task ledger do not exist or status is still PLANNED.

- [ ] **Step 5: Implement minimal immutable comparison contracts**

In `models.py`, define:

```python
class ComparisonVariant(str, Enum): ...

@dataclass(frozen=True, slots=True)
class ComparisonRunResult:
    variant: ComparisonVariant
    case_id: str
    procedure_success: bool
    final_state_correct: bool
    final_world_state_ref: str | None
    evaluated_scope_indices: tuple[int, ...]
    query_count: int
    stored_count_sum: int
    metadata_eligible_count_sum: int
    scored_vector_count_sum: int
    above_threshold_count_sum: int
    returned_count_sum: int
    cumulative_unique_candidate_count: int
    cumulative_activated_candidate_count: int
    cumulative_selected_count: int
    peak_selected_count: int
    final_selected_memory_ids: tuple[str, ...]
    procedure_attempt_count: int
    execution_ids: tuple[str, ...]
    procedure_states: tuple[str, ...]
    mismatch_count: int
    forced_recovery_scope_count: int
    same_name_identity_preserved: bool
    trace_signature: tuple[tuple[str, tuple[str, ...]], ...]

@dataclass(frozen=True, slots=True)
class ComparisonCaseResult:
    case_id: str
    shared_input_fingerprint: str
    validation_error_observed: bool
    validation_error: str | None
    runs: tuple[ComparisonRunResult, ...]
    expected_primary_case: bool

@dataclass(frozen=True, slots=True)
class BaselineComparisonReport:
    case_results: tuple[ComparisonCaseResult, ...]
    case_count: int
    valid_case_count: int
    invalid_case_count: int
    primary_case_count: int
    asca_success_count: int
    dense_success_count: int
    shared_success_count: int
    dense_only_success_count: int
    asca_only_success_count: int
    asca_final_state_correct_count: int
    dense_final_state_correct_count: int
    asca_query_count: int
    dense_query_count: int
    asca_scored_vector_count: int
    dense_scored_vector_count: int
    asca_cumulative_selected_count: int
    dense_cumulative_selected_count: int
    asca_peak_selected_count: int
    dense_peak_selected_count: int
    asca_procedure_attempt_count: int
    dense_procedure_attempt_count: int
    identity_failure_count: int
    duplicate_execution_id_failure_count: int
    post_completion_extra_attempt_failure_count: int
    designated_parity_reduction_count: int
    asca_deterministic_repeat_match: bool
    dense_deterministic_repeat_match: bool
```

Validate all integer counts as nonnegative; require unique nonblank IDs; reject impossible `peak_selected_count > cumulative_selected_count`; reject `procedure_attempt_count != len(execution_ids)`; reject duplicate execution IDs.

- [ ] **Step 6: Activate repository docs and repair stale A009 prose**

Write the A010 task ledger with the returned issue number, branch, spec, plan, constraints, phases, acceptance criteria, current/next action.

Set A010 ACTIVE in CURRENT/ROADMAP. Keep A011 PLANNED/no issue.

Replace only the stale README A009 issue sentence; preserve A009 metrics/outcomes.

- [ ] **Step 7: Run focused and ledger regressions**

Run:

```bash
python -m pytest -q tests/test_baseline_comparison_models.py tests/test_a010_task_ledger.py tests/test_a009_task_ledger.py tests/test_a008_task_ledger.py
python scripts/qualify_integrated_loop_a009.py
git diff --check
```

Expected: PASS; A009 qualifier remains valid and unchanged.

- [ ] **Step 8: Commit Task 1**

```bash
git add src/flywire_asca/baseline_comparison tests/test_baseline_comparison_models.py tests/test_a010_task_ledger.py docs/development/tasks/A010-dense-nonselective-baseline-comparison.md docs/development/tasks/CURRENT.md docs/development/tasks/ROADMAP.md README.md
git commit -m "Activate A010 baseline comparison contracts"
```

---

### Task 2: Implement the dense exhaustive runner

**Files:**
- Create: `src/flywire_asca/baseline_comparison/dense.py`
- Create: `tests/test_baseline_comparison_dense.py`
- Modify: `src/flywire_asca/baseline_comparison/__init__.py`

**Interfaces:**
- Consumes:
  - `IntegratedRetrievalContext`
  - `ProcedureLibrary`
  - `ContextBoundProcedureExecutorFactory`
  - A006 `SelectiveRetrievalEvidence` and `select_exhaustive(evidence)`
  - A008 `run_procedure(..., mode=ProcedureExecutionMode.CHUNKED, ...)`
- Produces:
  - `evaluate_dense_exhaustive(context: IntegratedRetrievalContext) -> DenseRetrievalEvaluation`
  - `run_dense_exhaustive(*, case_id: str, root_procedure_id: str, retrieval_context: IntegratedRetrievalContext, procedure_library: ProcedureLibrary, procedure_executor_factory: ContextBoundProcedureExecutorFactory, same_name_expected_ids: tuple[str, ...] = ()) -> ComparisonRunResult`

- [ ] **Step 1: Write failing dense retrieval tests**

Pin that `evaluate_dense_exhaustive()`:

- evaluates every cue from every declared tier exactly once;
- uses `top_k == max(1, context.index.document_count)`;
- preserves `minimum_similarity`;
- uses `top_k == 1` for an empty index and produces a valid empty exhaustive working set;
- passes every returned result into A006 `select_exhaustive()`;
- keeps every positive candidate, even when candidate count exceeds A007 maximum working-set budget;
- preserves two same-display-name memory IDs as two IDs.

Include a corpus with at least 40 positive candidates so a hidden `top_k=32` regression fails visibly.

- [ ] **Step 2: Run dense retrieval tests and verify RED**

Run:

```bash
python -m pytest -q tests/test_baseline_comparison_dense.py
```

Expected: FAIL because `dense.py` does not exist.

- [ ] **Step 3: Implement dense evidence evaluation**

Define:

```python
@dataclass(frozen=True, slots=True)
class DenseRetrievalEvaluation:
    retrieval_results: tuple[VectorMemoryResult, ...]
    working_set_result: SelectiveWorkingSetResult
```

`evaluate_dense_exhaustive()` must build one `VectorMemoryQuery` per declared cue using the same query text and threshold, with:

```python
top_k = max(1, context.index.document_count)
```

Then convert each result to `SelectiveRetrievalEvidence` and call the existing `select_exhaustive()`.

Do not reproduce A006 ranking/activation internals.

- [ ] **Step 4: Write failing one-attempt procedure tests**

Assert `run_dense_exhaustive()`:

- creates exactly one execution ID: `f"a010:{case_id}:dense:procedure-attempt:0"`;
- creates the executor from the factory's immutable snapshot;
- passes every exhaustive selected memory ID to the executor;
- calls `run_procedure(... CHUNKED ...)` exactly once;
- reports no forced recovery scope;
- records success/failure and final state without a replay;
- reports `evaluated_scope_indices == (2,)` as the normalized “all declared tiers available” logical scope marker;
- fails closed on unknown root procedure or malformed context.

- [ ] **Step 5: Implement `run_dense_exhaustive()`**

Use:

```python
executor = procedure_executor_factory.create(
    available_memory_ids=selected_ids,
    execution_id=execution_id,
)
execution = run_procedure(
    procedure_library,
    root_procedure_id=root_procedure_id,
    mode=ProcedureExecutionMode.CHUNKED,
    executor=executor,
    execution_id=execution_id,
)
```

Normalize the raw A005/A006/A008 evidence into `ComparisonRunResult`.

- [ ] **Step 6: Run Task 2 tests and full A006/A009 regressions**

Run:

```bash
python -m pytest -q tests/test_baseline_comparison_dense.py tests/test_selective_activation_baselines.py tests/test_integrated_loop_controller.py
python scripts/qualify_integrated_loop_a009.py
git diff --check
```

Expected: PASS.

- [ ] **Step 7: Commit Task 2**

```bash
git add src/flywire_asca/baseline_comparison/dense.py src/flywire_asca/baseline_comparison/__init__.py tests/test_baseline_comparison_dense.py
git commit -m "Add A010 dense exhaustive runner"
```

---

### Task 3: Add ASCA normalization and benchmark-only ablations

**Files:**
- Create: `src/flywire_asca/baseline_comparison/ablations.py`
- Create: `tests/test_baseline_comparison_ablations.py`
- Modify: `src/flywire_asca/baseline_comparison/__init__.py`

**Interfaces:**
- Consumes:
  - A009 `run_cognitive_loop()`
  - A009 `CognitiveLoopRequest`
  - A009 `LoopPolicy.MISMATCH_DRIVEN_RECOVERY` and `ALWAYS_MAX_SCOPE`
  - A007 `run_initial_integrated_expansion(..., policy=ExpansionPolicy.NO_EXPANSION)` for the structural ablation
  - A009 `evaluate_integrated_scope()`, `ContextBoundProcedureExecutorFactory`, and A008 `run_procedure()` for benchmark-only bounded replay
- Produces:
  - `normalize_a009_result(case_id: str, variant: ComparisonVariant, result: CognitiveLoopResult, *, same_name_expected_ids: tuple[str, ...] = ()) -> ComparisonRunResult`
  - `run_asca_primary(...) -> ComparisonRunResult`
  - `run_asca_always_max_scope(...) -> ComparisonRunResult`
  - `run_no_structural_expansion_ablation(...) -> ComparisonRunResult`
  - `run_familiarity_disabled_ablation(...) -> ComparisonRunResult`

- [ ] **Step 1: Write failing proof that ASCA_PRIMARY delegates to A009**

Use a spy/monkeypatch around `flywire_asca.integrated_loop.controller.run_cognitive_loop` (or import through a module reference that can be patched) and assert:

- exactly one call;
- request policy = `MISMATCH_DRIVEN_RECOVERY`;
- no A010 copy of A009 controller logic executes for primary;
- normalized counts equal the raw A009 evidence.

- [ ] **Step 2: Implement A009 normalization and primary/always-max wrappers**

`run_asca_primary()` must call the real A009 public controller with the frozen primary policy.

`run_asca_always_max_scope()` must call the same controller with `LoopPolicy.ALWAYS_MAX_SCOPE`.

`normalize_a009_result()` derives:

- retrieval query/count sums from `scope_evaluations`;
- cumulative candidate/activated/selected counts from each scope's `working_set_result`;
- peak/final selected counts;
- procedure attempts/execution IDs/states;
- mismatch count;
- forced recovery scope count from A009 trace/attempt structure;
- logical trace signature.

- [ ] **Step 3: Write failing structural-ablation tests**

Pin these semantics:

- initial retrieval uses A007 `NO_EXPANSION`, so only scope 0 is initially evaluated;
- A009-level procedure mismatch recovery remains bounded and may advance scope exactly +1;
- max attempts = 3;
- each replay uses a fresh execution ID and the same immutable initial snapshot;
- A005 threshold, cue texts, procedure library, requirements, and initial state fingerprint equal ASCA_PRIMARY inputs;
- only initial A007 expansion policy differs.

- [ ] **Step 4: Implement `run_no_structural_expansion_ablation()` without modifying A009**

Compose public A007/A009/A008 primitives in A010 only:

1. evaluate initial A007 `NO_EXPANSION`;
2. run one CHUNKED procedure attempt;
3. on mismatch, evaluate exactly the next frozen A007 scope;
4. replay from a fresh executor using the same factory snapshot;
5. stop at success or scope 2 / three attempts.

Do not add a new A009 `LoopPolicy`.

- [ ] **Step 5: Write failing familiarity-disabled tests**

Run the same A009 primary request twice:

- normal: the case's exact familiarity index;
- disabled diagnostic: an empty `ExactFamiliarityIndex(())`.

Assert retrieval/procedure normalized evidence is identical except familiarity evidence itself is omitted from the A010 diagnostic signature. Any procedure-success, scope, working-set, or final-state difference is an error.

- [ ] **Step 6: Implement `run_familiarity_disabled_ablation()`**

Call the real A009 controller with an empty familiarity index and normalize only control/retrieval/procedure evidence. Label the variant `ASCA_FAMILIARITY_DISABLED`.

- [ ] **Step 7: Run Task 3 tests and A009 regressions**

Run:

```bash
python -m pytest -q tests/test_baseline_comparison_ablations.py tests/test_integrated_loop_controller.py tests/test_integrated_loop_retrieval.py
python scripts/qualify_integrated_loop_a009.py
git diff --check
```

Expected: PASS; A009 frozen qualifier remains unchanged.

- [ ] **Step 8: Commit Task 3**

```bash
git add src/flywire_asca/baseline_comparison/ablations.py src/flywire_asca/baseline_comparison/__init__.py tests/test_baseline_comparison_ablations.py
git commit -m "Add A010 ASCA comparison ablations"
```

---

### Task 4: Freeze deterministic comparison fixture and classifier

**Files:**
- Create: `src/flywire_asca/baseline_comparison/benchmark.py`
- Create: `tests/test_baseline_comparison_benchmark.py`
- Modify: `src/flywire_asca/baseline_comparison/__init__.py`

**Interfaces:**
- Consumes: Task 1 contracts, Task 2 dense runner, Task 3 ASCA wrappers/ablations, existing A003/A005/A008 fixture-building primitives.
- Produces:
  - `BaselineComparisonCase`
  - `build_a010_deterministic_fixture() -> tuple[BaselineComparisonCase, ...]`
  - `a010_fixture_fingerprint(cases: Iterable[BaselineComparisonCase]) -> str`
  - `run_a010_benchmark(cases: Iterable[BaselineComparisonCase]) -> BaselineComparisonReport`
  - `classify_a010_hypothesis(report: BaselineComparisonReport) -> str`
  - `qualify_a010_report(report: BaselineComparisonReport) -> list[str]`

- [ ] **Step 1: Write the frozen case-family tests**

Require the ordered IDs exactly:

```python
EXPECTED_CASE_IDS = (
    "easy-local-many-distractors",
    "unfamiliar-semantic-many-distractors",
    "structural-expansion-required",
    "procedure-recovery-one-scope",
    "procedure-recovery-two-scopes",
    "persistent-missing-memory",
    "selective-routing-miss-sentinel",
    "same-name-identity",
    "tie-heavy-distractors",
    "structural-expansion-ablation",
    "familiarity-disabled-equivalence",
    "invalid-contract",
)
```

Pin deterministic corpus-size classes to `16`, `64`, and `256` where declared by each case.

The routing-miss sentinel must be capable of producing a dense-only success if SINGLE_BEST/budget drops required evidence. Do not require ASCA to win this case in the fixture-construction test.

- [ ] **Step 2: Implement deterministic fixture builders**

Define a canonical immutable `BaselineComparisonCase` with all shared inputs needed by both variants, including:

- case ID;
- goal/familiarity cue;
- root procedure;
- deterministic memory specs/vectors;
- cue tiers;
- minimum similarity;
- procedure/action definitions;
- memory requirements;
- initial state;
- expected same-name IDs;
- flags identifying primary/ablation/invalid cases;
- whether the case is designated for parity-with-reduction evidence.

Generate distractors deterministically from case ID + integer index; no randomness.

- [ ] **Step 3: Add shared-input fingerprint tests**

`shared_input_fingerprint(case)` must hash the canonical shared corpus/query/procedure/threshold/state inputs.

Assert all primary variant runs for one case carry the same fingerprint.

Mutating only a variant label must not change shared-input fingerprint.

Mutating corpus, cue text, threshold, procedure requirement, or initial state must change it.

- [ ] **Step 4: Write failing benchmark evidence tests**

For every valid primary case require exactly one `ASCA_PRIMARY` and one `DENSE_EXHAUSTIVE` result.

Also run declared secondary controls only where the fixture flags them.

Assert raw metrics include:

- success/final-state evidence;
- A005 query/scored/returned counts;
- cumulative/peak selected counts;
- procedure attempts/mismatches/recovery;
- identity preservation;
- deterministic repeat status.

Run each primary variant twice and compare normalized logical results exactly.

- [ ] **Step 5: Implement `run_a010_benchmark()`**

Aggregate integer counts from raw case evidence only.

Derive:

```text
shared_success_count
dense_only_success_count
asca_only_success_count
ASCA/DENSE query_count
ASCA/DENSE scored_vector_count
ASCA/DENSE cumulative_selected_count
ASCA/DENSE peak_selected_count
ASCA/DENSE procedure_attempt_count
designated_parity_reduction_count
identity/duplicate-ID/post-completion failures
repeat-match booleans
```

Do not build a weighted efficiency score.

- [ ] **Step 6: Write classifier RED tests**

Pin classification:

```python
def test_dense_only_success_prevents_supported(): ...
def test_supported_requires_equal_success_and_strict_three_dimension_reduction(): ...
def test_not_supported_when_no_declared_selective_reduction_exists(): ...
def test_mixed_when_reduction_exists_but_dense_has_additional_success(): ...
```

Exact `SUPPORTED` requirements:

- `dense_only_success_count == 0`;
- ASCA success count == dense success count;
- every shared success final-state-correct for both;
- identity failures = 0;
- ASCA query count < dense;
- ASCA scored-vector count < dense;
- ASCA cumulative selected count < dense;
- `designated_parity_reduction_count >= 1`;
- max A009 attempts <= 3 / no scope > 2;
- duplicate execution ID failures = 0;
- post-completion extra-attempt failures = 0;
- both repeat-match booleans true;
- no fixture/fairness drift.

Use `MIXED` when meaningful selective reduction exists but a SUPPORTED condition fails; use `NOT_SUPPORTED` when no useful selective reduction exists on valid frozen evidence.

- [ ] **Step 7: Implement classifier and fail-closed report validator**

`qualify_a010_report()` must reject impossible relationships and compare aggregate metrics against values re-derived from raw `case_results`.

Dense-only success is evidence, never a validation error by itself.

- [ ] **Step 8: Freeze fixture fingerprint only after fixture tests are stable**

Compute the canonical SHA-256 once the ordered fixture and shared inputs are finalized. Record it in the later qualification CLI test; after this step do not retune targets/distractors/thresholds based on outcome.

- [ ] **Step 9: Run Task 4 tests and full portable suite**

Run:

```bash
python -m pytest -q tests/test_baseline_comparison_benchmark.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
python scripts/qualify_procedural_memory_a008.py
python scripts/qualify_integrated_loop_a009.py
git diff --check
```

Expected: PASS before accepting any A010 outcome.

- [ ] **Step 10: Commit Task 4**

```bash
git add src/flywire_asca/baseline_comparison/benchmark.py src/flywire_asca/baseline_comparison/__init__.py tests/test_baseline_comparison_benchmark.py
git commit -m "Add A010 deterministic baseline benchmark"
```

---

### Task 5: Add portable qualification, local physical comparison, and CI

**Files:**
- Create: `scripts/qualify_baseline_comparison_a010.py`
- Create: `scripts/qualify_baseline_comparison_a010_physical.py`
- Create: `tests/test_baseline_comparison_qualification_cli.py`
- Create: `tests/test_baseline_comparison_physical.py`
- Modify: `.github/workflows/ci.yml`
- Modify: `tests/test_ci_contract.py`

**Interfaces:**
- Consumes: frozen Task 4 fixture/report/classifier.
- Produces:
  - portable UTF-8 JSON qualification payload;
  - `validate_qualification_payload(payload) -> list[str]`;
  - local-only physical JSON payload using pinned Qwen embedding identity;
  - exact CI step `python scripts/qualify_baseline_comparison_a010.py`.

- [ ] **Step 1: Write portable CLI RED tests**

Require payload fields:

```text
qualification_scope = deterministic_dense_nonselective_baseline_a010
fixture_version = a010-deterministic-v1
fixture_fingerprint = <Task 4 frozen SHA-256>
case_ids = exact ordered fixture IDs
variants = exact declared primary/diagnostic variant names
primary_hypothesis_outcome in SUPPORTED/MIXED/NOT_SUPPORTED
experiment_valid = true/false
aggregate_metrics
cases
claims_boundary
```

Require stdout bytes equal `--output` file bytes exactly.

- [ ] **Step 2: Implement portable qualification CLI**

Follow the A009 qualification style:

- canonical compact JSON;
- sorted keys;
- UTF-8 + trailing newline;
- valid negative research outcome returns exit code 0;
- invalid payload/evidence returns nonzero.

- [ ] **Step 3: Add raw-evidence tamper tests**

Take a valid payload and prove the validator rejects:

- edited aggregate query count;
- edited aggregate dense-only success count;
- changed shared-input fingerprint;
- dense top-k/fairness marker drift;
- duplicate execution ID;
- impossible selected-count relation;
- case order/ID drift;
- invalid outcome vocabulary;
- outcome inconsistent with raw evidence.

This is the Review Focus raw-vs-aggregate gate.

- [ ] **Step 4: Write physical prerequisite and comparison tests**

Pin constants:

```python
EMBEDDING_MODEL = "qwen3-embedding:0.6b"
EMBEDDING_DIGEST = "ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d"
EMBEDDING_DIMENSION = 1024
MINIMUM_SIMILARITY = 0.5037018224299838
PHYSICAL_FIXTURE_VERSION = "a010-physical-v1"
```

Use fake adapters in portable tests to verify descriptor mismatch fails closed.

Physical result must record, separately for ASCA and dense:

- procedure success;
- query count;
- scored-vector count;
- final/cumulative selected counts;
- procedure attempts;
- observed runner duration if measured;
- embedding descriptor identity.

Timing remains descriptive secondary metadata.

- [ ] **Step 5: Implement the local physical script**

Build the same physical documents/query texts for both variants, use `OllamaEmbeddingAdapter` with exact expected digest/dimension and `keep_alive="6h"`.

Do not retune the threshold or documents after observing final results.

If a terminal model diagnostic is retained, pin the A004 model digest and keep it outside the primary classifier.

- [ ] **Step 6: Add CI contract tests first**

Require:

```text
python scripts/qualify_baseline_comparison_a010.py
```

and forbid:

```text
qualify_baseline_comparison_a010_physical.py
ollama pull
ollama run
127.0.0.1:11434
localhost
```

- [ ] **Step 7: Update GitHub Actions CI**

Add:

```yaml
- name: Qualify A010 dense non-selective baseline
  run: python scripts/qualify_baseline_comparison_a010.py
```

Do not add physical Ollama work to CI.

- [ ] **Step 8: Run Task 5 portable verification**

Run:

```bash
python -m pytest -q tests/test_baseline_comparison_qualification_cli.py tests/test_baseline_comparison_physical.py tests/test_ci_contract.py
python scripts/qualify_baseline_comparison_a010.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
python scripts/qualify_procedural_memory_a008.py
python scripts/qualify_integrated_loop_a009.py
git diff --check
```

Expected: all PASS.

- [ ] **Step 9: Run local physical qualification**

Run:

```bash
python scripts/qualify_baseline_comparison_a010_physical.py --portable-primary-outcome <ACTUAL_PORTABLE_OUTCOME>
```

Record exact model descriptor evidence and raw ASCA/dense physical metrics. If the physical prerequisites are unavailable, record the exact blocker; do not alter portable outcome.

- [ ] **Step 10: Commit Task 5**

```bash
git add scripts/qualify_baseline_comparison_a010.py scripts/qualify_baseline_comparison_a010_physical.py tests/test_baseline_comparison_qualification_cli.py tests/test_baseline_comparison_physical.py tests/test_ci_contract.py .github/workflows/ci.yml
git commit -m "Add A010 baseline qualification"
```

Push the feature branch and require exact-commit branch CI success before Task 6.

---

### Task 6: Qualification report, whole-branch review, integration, and closure

**Files:**
- Create: `docs/development/reports/ASCA-20261010-A010-dense-nonselective-baseline-comparison.md`
- Modify: `docs/development/tasks/A010-dense-nonselective-baseline-comparison.md`
- Modify: `docs/development/tasks/CURRENT.md`
- Modify: `docs/development/tasks/ROADMAP.md`
- Modify: `README.md`
- Modify: `tests/test_a010_task_ledger.py`

**Interfaces:**
- Consumes: exact portable qualification payload, local physical payload when available, exact feature-branch CI, whole-branch review findings.
- Produces: one authoritative A010 report, reviewed main integration, final-main CI evidence, A010 issue closure, A011 PLANNED/no issue.

- [ ] **Step 1: Freeze and record the first final A010 result**

Run the complete verification gate from Task 5 on the candidate commit.

Record exactly one primary outcome declaration:

```text
Primary A010 hypothesis outcome: `SUPPORTED`
```

or `MIXED` or `NOT_SUPPORTED`, exactly matching the frozen classifier.

Record raw integer metrics before ratios and explicitly state the claims boundary.

- [ ] **Step 2: Write closure-candidate ledger/report tests RED**

Require the report/task ledger to include:

- exact fixture version/fingerprint;
- exact primary outcome;
- raw ASCA/dense success counts;
- dense-only/ASCA-only counts;
- query/scored-vector/cumulative-selected counts;
- procedure attempts;
- identity/repeat/fairness validity;
- physical evidence or exact physical blocker;
- preserved historical A006/A007/A008/A009 outcomes;
- FlyWireLLM untouched;
- exact candidate SHA and CI run.

Set A011 as next PLANNED task with no issue.

- [ ] **Step 3: Write the qualification report and closure candidate docs**

Keep A010 ACTIVE until whole-branch review and reviewed main integration are complete.

- [ ] **Step 4: Commit closure candidate and obtain exact branch CI**

Commit:

```bash
git add docs/development/reports/ASCA-20261010-A010-dense-nonselective-baseline-comparison.md docs/development/tasks/A010-dense-nonselective-baseline-comparison.md docs/development/tasks/CURRENT.md docs/development/tasks/ROADMAP.md README.md tests/test_a010_task_ledger.py
git commit -m "Qualify A010 dense non-selective baseline comparison"
```

Push and require exact SHA CI success.

- [ ] **Step 5: Request whole-branch review**

Use `superpowers:requesting-code-review`.

Review range:

```text
activation-base-plan-commit..A010-closure-candidate
```

Review specifically:

- fairness of shared inputs;
- dense `select_exhaustive()` proof;
- ASCA primary delegation to A009;
- routing-miss sentinel honesty;
- classifier `SUPPORTED/MIXED/NOT_SUPPORTED` logic;
- raw-to-aggregate validation;
- bounded procedure replay;
- identity preservation;
- physical/portable claims separation;
- no A009 semantic mutation;
- no FlyWireLLM change.

If no independent reviewer mechanism exists, record the limitation explicitly as author self-review; do not call it independent review.

- [ ] **Step 6: Fix every Critical/Important finding with RED→GREEN tests**

Use `superpowers:receiving-code-review` before applying review findings.

After fixes, rerun:

```bash
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
python scripts/qualify_procedural_memory_a008.py
python scripts/qualify_integrated_loop_a009.py
python scripts/qualify_baseline_comparison_a010.py
git diff --check
```

Rerun physical A010 qualification if a review fix affects physical evidence/identity/normalization.

Require exact post-review branch CI.

- [ ] **Step 7: Verify integration preconditions**

Before main integration require:

```text
main clean and synchronized with origin/main
feature branch clean and synchronized
feature branch descends activation base
A010 issue open
A011 issue absent
exact reviewed feature SHA CI = success
```

- [ ] **Step 8: Integrate reviewed behavior without rewriting history**

Use the branch-finishing workflow and prefer fast-forward-only integration when the branch topology permits it.

Do not reset/rebase/force-push to manufacture a fast-forward.

Run the full gate on merged main before push, then push main.

- [ ] **Step 9: Require exact reviewed-main CI**

Capture exact main SHA and exact GitHub Actions run ID/conclusion.

If CI fails, keep A010 issue open and repair through normal commits/tests.

- [ ] **Step 10: Finalize repository closure state**

Only after exact final-main evidence is GREEN:

- A010 task status = DONE;
- ROADMAP A010 = DONE;
- CURRENT = A011 / PLANNED / no issue;
- README current stage records A010 outcome and A011 planned;
- report says A010 repository state DONE;
- preserve historical A006/A007/A008/A009 results exactly.

Add a final closure-state test proving no stale “A010 remains open/pending” prose.

- [ ] **Step 11: Commit/push final closure evidence and require exact final CI**

Run full local gate, commit closure state, push main, and require exact final-main CI success.

- [ ] **Step 12: Close the A010 issue and clean temporary local execution state**

Post the final evidence comment with:

- final main SHA;
- exact final CI run;
- full local test count;
- frozen fixture fingerprint;
- primary outcome;
- key ASCA/dense raw metrics;
- physical evidence status;
- review finding counts;
- historical outcome preservation;
- FlyWireLLM untouched;
- A011 PLANNED/no issue.

Then close the issue as `completed`.

Remove only the clean isolated A010 worktree and delete only the clean local feature branch non-force. Preserve remote feature history unless explicitly requested otherwise.

Final authoritative check:

```text
main == origin/main
ahead/behind = 0/0
worktree clean
A010 issue closed/completed
A011 no issue
```
