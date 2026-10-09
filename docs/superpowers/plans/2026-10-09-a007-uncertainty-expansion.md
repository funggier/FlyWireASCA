# A007 Structural Uncertainty Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add deterministic structural-uncertainty assessment and a finite retrieval/working-set expansion controller that can stop early, widen through a frozen three-round scope ladder, or terminate explicitly as exhausted, then qualify whether SIGNAL_DRIVEN expansion recovers required memory more selectively than NO_EXPANSION and ALWAYS_EXPAND.

**Architecture:** A007 consumes A006 `SelectiveWorkingSetResult` values and derives typed structural triggers only from retrieval state, budget drops, and boundary ties. A pure controller produces STOP/EXPAND/EXHAUSTED assessments; a separate policy runner evaluates NO_EXPANSION, SIGNAL_DRIVEN, and ALWAYS_EXPAND so baseline policy termination cannot be confused with controller assessment. Physical qualification reuses A005 exact vector retrieval plus A006 `SINGLE_BEST`, keeps the A005 threshold fixed, and uses predeclared cue tiers rather than generative query reformulation.

**Tech Stack:** Python >=3.11 standard library only, frozen dataclasses, `Enum`, deterministic tuples, pytest, existing A005 vector-memory retrieval, existing A006 selective-activation contracts/baselines, local Ollama `qwen3-embedding:0.6b` only for physical qualification.

**Spec:** `docs/superpowers/specs/2026-10-09-a007-uncertainty-expansion-design.md`

## Global Constraints

- Repository: public `funggier/FlyWireASCA`.
- Work branch: `research/a007-uncertainty-expansion`.
- A007 title: **Surprise, Uncertainty & Expansion**.
- Base main: `8bdf87d19147cd30ccfbd8cd07238ab07c389dc0`.
- A006 engineering qualification remains GREEN.
- A006 frozen physical research outcome remains `NOT_SUPPORTED`; A007 must not rewrite or reinterpret it.
- Primary A007 physical selector is A006 `SINGLE_BEST`.
- A006 `SELECTIVE_CONVERGENCE` may appear only as a clearly secondary diagnostic and cannot determine the primary A007 research outcome.
- A007 v0.1 uses typed structural triggers only; it does not fabricate scalar surprise/uncertainty/risk values.
- Existing A002 `UncertaintySignal` remains unchanged and is not populated by A007 v0.1.
- Trigger order is exactly:
  1. `INSUFFICIENT_EVIDENCE`
  2. `MEMORY_BUDGET_TRUNCATED`
  3. `WORKING_SET_BUDGET_TRUNCATED`
  4. `MEMORY_BOUNDARY_TIE`
  5. `WORKING_SET_BOUNDARY_TIE`
- Decision kinds are exactly `STOP`, `EXPAND`, `EXHAUSTED`.
- Policy kinds are exactly `NO_EXPANSION`, `SIGNAL_DRIVEN`, `ALWAYS_EXPAND`.
- Policy termination reasons are exactly:
  - `CONTROLLER_STOP`
  - `CONTROLLER_EXHAUSTED`
  - `POLICY_NO_EXPANSION`
  - `POLICY_MAX_SCOPE`
- A007 supports A006 retrieval states `RECALLED`, `PARTIAL_RECALL`, and `INSUFFICIENT_EVIDENCE` only.
- A007 remains no-graph: every scope budget has `max_relation_hops = 0`.
- A007 owns expansion rounds itself, so every nested A006 scope budget has `max_expansions = 0`.
- A007 does not assemble model context, so every scope budget has `max_model_input_tokens = 0`.
- A007 physical threshold remains `0.5037018224299838`; threshold relaxation is out of scope.
- Frozen primary physical ladder:
  - round 0: 1 cue tier, top_k 12, max_memory_nodes 8, max_working_set_items 4;
  - round 1: 2 cue tiers, top_k 24, max_memory_nodes 12, max_working_set_items 8;
  - round 2: 3 cue tiers, top_k 32, max_memory_nodes 16, max_working_set_items 12.
- There are at most three evaluated rounds and at most two expansions.
- No Qwen3.5:4b generation, query generation, uncertainty scoring, memory selection, or expansion judgment occurs in A007.
- No typed graph is created or traversed.
- Physical embedding model remains `qwen3-embedding:0.6b`.
- Physical digest remains `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`.
- Expected embedding dimension remains 1024.
- Cue texts, fixture labels, profile, threshold, and ladder are frozen before the final physical run.
- A valid physical research result may be `SUPPORTED`, `MIXED`, or `NOT_SUPPORTED`; negative research evidence is not an execution error.
- Index-build embedding cost is fixed case-setup evidence and must be reported separately from per-policy query/expansion cost.
- Portable GitHub CI must not require Ollama or run the physical A007 qualification script.
- FlyWireLLM remains paused and untouched.
- Exact branch CI, physical qualification, whole-branch review, final main CI, and clean/synchronized main 0/0 are required before A007 closes.

## File Structure

- `src/flywire_asca/uncertainty_expansion/__init__.py`: public A007 exports.
- `src/flywire_asca/uncertainty_expansion/models.py`: trigger/decision/policy/termination enums and immutable scope/profile/decision/run records.
- `src/flywire_asca/uncertainty_expansion/controller.py`: structural-state validation, trigger derivation, STOP/EXPAND/EXHAUSTED assessment.
- `src/flywire_asca/uncertainty_expansion/runner.py`: bounded NO_EXPANSION / SIGNAL_DRIVEN / ALWAYS_EXPAND policy execution.
- `src/flywire_asca/uncertainty_expansion/benchmark.py`: portable synthetic fixture, policy comparison metrics, engineering qualifier.
- `scripts/qualify_uncertainty_expansion_a007.py`: frozen local A005+A006+A007 physical qualification CLI.
- `tests/test_uncertainty_expansion_models.py`: enum/model/profile validation.
- `tests/test_uncertainty_expansion_controller.py`: trigger ordering, state consistency, STOP/EXPAND/EXHAUSTED semantics.
- `tests/test_uncertainty_expansion_runner.py`: policy control flow, callback call counts, boundedness, termination reason semantics.
- `tests/test_uncertainty_expansion_benchmark.py`: portable recoveries/regressions/easy cases/exhaustion/determinism/gates.
- `tests/test_uncertainty_expansion_qualification_cli.py`: frozen physical profile/fixture, fake composition, UTF-8, fail-closed validation, metrics separation.
- `tests/test_a007_task_ledger.py`: task/roadmap/closure evidence.
- `docs/development/tasks/A007-surprise-uncertainty-expansion.md`: recoverable task ledger.
- `docs/development/reports/ASCA-20261009-A007-surprise-uncertainty-expansion.md`: final qualification report.

## Review Focus

1. **Control baseline contamination:** NO_EXPANSION must stop after round 0 even when assessment says EXPAND, while ALWAYS_EXPAND must evaluate every scope even when assessment says STOP; pin in Task 3.
2. **Structural-state contradictions:** impossible A006 combinations such as RECALLED with budget drops, PARTIAL_RECALL without drops, or ties without corresponding truncation must fail closed; pin in Task 2.
3. **No-op/invalid expansion profiles:** repeated identical scopes, shrinking limits, skipped round indices, or decreasing cue-tier/top_k scope can create loops or fake expansion; pin in Task 1.
4. **Shared setup cost contamination:** physical index-build embedding work must not be charged independently to every policy; snapshot counters and report setup vs per-policy deltas; pin in Task 5.
5. **Determinism vs backend timing:** repeated-controller equality must compare logical policy results and frozen evidence, not require backend timing counters to be byte-identical; pin in Tasks 3 and 5.

---

### Task 1: Add A007 contracts, frozen profile, and activate the task

**Files:**
- Create: `src/flywire_asca/uncertainty_expansion/__init__.py`
- Create: `src/flywire_asca/uncertainty_expansion/models.py`
- Create: `tests/test_uncertainty_expansion_models.py`
- Create: `tests/test_a007_task_ledger.py`
- Create: `docs/development/tasks/A007-surprise-uncertainty-expansion.md`
- Modify: `docs/development/tasks/CURRENT.md`
- Modify: `docs/development/tasks/ROADMAP.md`
- Modify: `README.md`
- Modify: `tests/test_task_ledger.py`
- Modify: historical A006 ledger tests only where they incorrectly freeze live A007 state.

**Interfaces:**
- Produces `ExpansionTrigger(str, Enum)` with the five exact values from Global Constraints.
- Produces `ExpansionDecisionKind(str, Enum)`: STOP / EXPAND / EXHAUSTED.
- Produces `ExpansionPolicy(str, Enum)`: NO_EXPANSION / SIGNAL_DRIVEN / ALWAYS_EXPAND.
- Produces `ExpansionTerminationReason(str, Enum)`: CONTROLLER_STOP / CONTROLLER_EXHAUSTED / POLICY_NO_EXPANSION / POLICY_MAX_SCOPE.
- Produces immutable `ExpansionScope(round_index: int, enabled_cue_tier_count: int, top_k: int, budget: ActivationBudget)`.
- Produces immutable `ExpansionProfile(profile_name: str, scopes: tuple[ExpansionScope, ...])`.
- Produces immutable `ExpansionDecision(round_index: int, kind: ExpansionDecisionKind, triggers: tuple[ExpansionTrigger, ...], current_scope: ExpansionScope, next_scope: ExpansionScope | None)`.
- Produces `build_a007_primary_profile() -> ExpansionProfile` with the exact frozen three-round ladder.

- [ ] **Step 1: Write failing enum/scope/profile tests**

Pin:
- enum vocabularies and ordering exactly;
- scope requires round_index >= 0, cue-tier count > 0, top_k > 0;
- scope budget requires hops/expansions/model tokens = 0 and working-set <= memory budget;
- profile nonempty and profile_name nonblank;
- first scope round index = 0;
- round indices contiguous;
- cue-tier count/top_k/memory/working limits never decrease;
- every later scope changes at least one of cue-tier count/top_k/memory/working limits;
- duplicate scope round index fails;
- frozen primary profile equals exactly 1/12/8/4 -> 2/24/12/8 -> 3/32/16/12.

- [ ] **Step 2: Write failing decision-contract tests**

Pin:
- trigger tuples canonical in explicit enum order and unique;
- STOP requires no triggers and no next scope;
- EXPAND requires >=1 trigger, non-null next scope, and next round = current + 1;
- EXHAUSTED requires >=1 trigger and no next scope;
- decision round_index equals current_scope.round_index;
- EXPAND validates local adjacency only; full membership/order in an ExpansionProfile is owned by the runner.

- [ ] **Step 3: Run focused tests and verify RED**

Run:
```powershell
python -m pytest -q tests/test_uncertainty_expansion_models.py
```

Expected: collection/import FAIL because the A007 package does not exist.

- [ ] **Step 4: Implement model/profile contracts only**

Do not implement trigger derivation or runner control flow in Task 1.

- [ ] **Step 5: Write failing A007 live task/roadmap tests**

Pin:
- CURRENT A007 ACTIVE, Issue #7, branch `research/a007-uncertainty-expansion`;
- ROADMAP A007 ACTIVE;
- A008-A011 remain PLANNED;
- task ledger records A006 physical `NOT_SUPPORTED`, SINGLE_BEST primary policy, fixed threshold/ladder, no scalar surprise, no graph, no Qwen cue generation, FlyWireLLM paused;
- README current stage is A007;
- historical A006 report remains immutable closure evidence.

- [ ] **Step 6: Verify live-state tests RED**

Run:
```powershell
python -m pytest -q tests/test_a007_task_ledger.py tests/test_task_ledger.py
```

Expected: FAIL because A007 is still PLANNED and Issue #7 does not exist.

- [ ] **Step 7: Create GitHub Issue #7 and activate A007 docs**

Issue title:

`A007 — Surprise, Uncertainty & Expansion`

Do not create an A008 issue.

- [ ] **Step 8: Run Task 1 gates**

Run:
```powershell
python -m pytest -q tests/test_uncertainty_expansion_models.py tests/test_a007_task_ledger.py tests/test_task_ledger.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
git diff --check
```

Expected: all PASS.

- [ ] **Step 9: Commit Task 1**

Commit:

`Add A007 uncertainty expansion contracts and task activation`

### Task 2: Implement structural trigger derivation and controller assessment

**Files:**
- Create: `src/flywire_asca/uncertainty_expansion/controller.py`
- Create: `tests/test_uncertainty_expansion_controller.py`
- Modify: `src/flywire_asca/uncertainty_expansion/__init__.py`
- Modify: `docs/development/tasks/A007-surprise-uncertainty-expansion.md`

**Interfaces:**
- Consumes `SelectiveWorkingSetResult`, `ExpansionScope`, `ExpansionDecision`.
- Produces `derive_expansion_triggers(result: SelectiveWorkingSetResult) -> tuple[ExpansionTrigger, ...]`.
- Produces `assess_expansion(result: SelectiveWorkingSetResult, *, current_scope: ExpansionScope, next_scope: ExpansionScope | None) -> ExpansionDecision`.

- [ ] **Step 1: Write failing supported-state tests**

Pin:
- RECALLED with no drops/ties -> empty trigger tuple -> STOP;
- INSUFFICIENT_EVIDENCE -> INSUFFICIENT_EVIDENCE trigger;
- PARTIAL_RECALL + memory drop -> MEMORY_BUDGET_TRUNCATED;
- PARTIAL_RECALL + working-set drop -> WORKING_SET_BUDGET_TRUNCATED;
- boundary ties add their matching tie trigger after truncation triggers;
- multiple triggers preserve exact enum order independent of input construction.

- [ ] **Step 2: Write failing structural-consistency tests**

Pin fail-closed behavior for:
- unsupported retrieval states;
- RECALLED with memory or working-set drops;
- PARTIAL_RECALL with zero total drops;
- INSUFFICIENT_EVIDENCE with selected entries;
- INSUFFICIENT_EVIDENCE with positive candidate/active/selected counts inconsistent with A006 meaning;
- memory boundary tie without memory drop;
- working-set boundary tie without working-set drop.

- [ ] **Step 3: Write failing assessment tests**

Pin:
- no triggers => STOP and next_scope must be discarded/None in returned decision;
- triggers + next scope => EXPAND;
- triggers + no next scope => EXHAUSTED;
- decision round_index must equal current_scope.round_index;
- next scope must be exactly current round + 1 and must not be a no-op relative to current scope;
- result object is not mutated.

- [ ] **Step 4: Verify RED**

Run:
```powershell
python -m pytest -q tests/test_uncertainty_expansion_controller.py
```

Expected: FAIL because controller functions do not exist.

- [ ] **Step 5: Implement validation, trigger derivation, and assessment minimally**

Do not add scalar uncertainty values and do not import graph/model-generation code.

- [ ] **Step 6: Run focused/full gates**

Run:
```powershell
python -m pytest -q tests/test_uncertainty_expansion_controller.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
git diff --check
```

Expected: all PASS.

- [ ] **Step 7: Commit Task 2**

Commit:

`Add A007 structural expansion controller`

### Task 3: Implement bounded policy runner and control baselines

**Files:**
- Create: `src/flywire_asca/uncertainty_expansion/runner.py`
- Create: `tests/test_uncertainty_expansion_runner.py`
- Modify: `src/flywire_asca/uncertainty_expansion/models.py`
- Modify: `src/flywire_asca/uncertainty_expansion/__init__.py`
- Modify: `docs/development/tasks/A007-surprise-uncertainty-expansion.md`

**Interfaces:**
- Produces immutable `ExpansionRoundResult(scope: ExpansionScope, working_set_result: SelectiveWorkingSetResult, assessment: ExpansionDecision)`.
- Produces immutable `ExpansionRunResult(policy: ExpansionPolicy, rounds: tuple[ExpansionRoundResult, ...], final_result: SelectiveWorkingSetResult, final_assessment: ExpansionDecision, termination_reason: ExpansionTerminationReason)`.
- Produces `run_expansion_policy(profile: ExpansionProfile, *, policy: ExpansionPolicy, evaluate_scope: Callable[[ExpansionScope], SelectiveWorkingSetResult]) -> ExpansionRunResult`.
- Optional thin wrappers may expose `run_signal_driven_expansion`, `run_no_expansion`, and `run_always_expand`, but all must delegate to the same policy runner.

- [ ] **Step 1: Write failing SIGNAL_DRIVEN control-flow tests**

Pin:
- STOP at round 0 -> callback called once, CONTROLLER_STOP;
- EXPAND round 0 then STOP round 1 -> callback scopes [0,1], CONTROLLER_STOP;
- EXPAND at rounds 0 and 1 then triggers remain at round 2 -> scopes [0,1,2], final assessment EXHAUSTED, CONTROLLER_EXHAUSTED;
- no fourth round;
- each evaluated scope callback invoked exactly once.

- [ ] **Step 2: Write failing NO_EXPANSION baseline tests**

Pin:
- evaluates round 0 exactly once;
- returns POLICY_NO_EXPANSION even if round-0 assessment is EXPAND;
- final_assessment still preserves EXPAND for audit;
- never calls a later scope.

- [ ] **Step 3: Write failing ALWAYS_EXPAND baseline tests**

Pin:
- evaluates every scope exactly once in profile order;
- continues after STOP assessments;
- final termination is POLICY_MAX_SCOPE;
- final_assessment is the actual structural assessment of max scope, not rewritten to fit policy termination.

- [ ] **Step 4: Write failing run-record validation/determinism tests**

Pin:
- rounds nonempty, contiguous, unique, and in profile order;
- final_result equals last round result;
- final_assessment equals last round assessment;
- policy/termination combinations are valid;
- repeated execution against a deterministic fake evaluator yields logically identical ExpansionRunResult;
- fake evaluator call log confirms no speculative calls.

- [ ] **Step 5: Verify RED**

Run:
```powershell
python -m pytest -q tests/test_uncertainty_expansion_runner.py
```

Expected: FAIL because runner/run records do not exist.

- [ ] **Step 6: Implement one shared policy runner**

Keep policy-specific behavior as explicit branches over the same validated profile and assessment function; do not duplicate retrieval logic.

- [ ] **Step 7: Run focused/full gates**

Run:
```powershell
python -m pytest -q tests/test_uncertainty_expansion_runner.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
git diff --check
```

Expected: all PASS.

- [ ] **Step 8: Commit Task 3**

Commit:

`Add A007 bounded expansion policy runner`

### Task 4: Add portable A007 benchmark and engineering qualification

**Files:**
- Create: `src/flywire_asca/uncertainty_expansion/benchmark.py`
- Create: `tests/test_uncertainty_expansion_benchmark.py`
- Modify: `tests/test_ci_contract.py`
- Modify: `docs/development/tasks/A007-surprise-uncertainty-expansion.md`

**Interfaces:**
- Produces immutable `UncertaintyExpansionBenchmarkCase`.
- Produces immutable `UncertaintyExpansionCaseResult`.
- Produces immutable `UncertaintyExpansionBenchmarkReport`.
- Produces `build_a007_portable_fixture() -> tuple[UncertaintyExpansionBenchmarkCase, ...]`.
- Produces `run_a007_benchmark(cases: Iterable[UncertaintyExpansionBenchmarkCase]) -> UncertaintyExpansionBenchmarkReport`.
- Produces `qualify_a007_report(report: UncertaintyExpansionBenchmarkReport) -> list[str]`.

**Portable metrics include:**
- case count;
- total declared required-memory IDs across cases with nonempty required sets;
- coverage denominator excludes cases with an empty required-memory tuple rather than treating them as automatic recoveries;
- required-memory coverage for NO_EXPANSION / SIGNAL_DRIVEN / ALWAYS_EXPAND;
- SIGNAL_DRIVEN recovery count;
- SIGNAL_DRIVEN regression count;
- easy-case unnecessary expansion count;
- persistent-insufficient exhausted count;
- ambiguity failure count;
- structural validation failure count;
- max SIGNAL_DRIVEN rounds;
- total rounds by policy;
- total scope evaluations by policy;
- STOP / EXHAUSTED / policy termination counts;
- deterministic-repeat result.

Recovery/regression metrics compare only cases with nonempty declared
`required_memory_ids`. Persistent-insufficient and pure budget/tie engineering
cases with no required IDs contribute to boundedness/trigger metrics, not
required-memory coverage.

- [ ] **Step 1: Write failing fixture-coverage tests**

Require cases for:
- easy STOP round 0;
- recover at round 1;
- recover at round 2;
- memory-budget truncation;
- working-set truncation;
- memory boundary tie;
- working-set boundary tie;
- persistent insufficient -> EXHAUSTED;
- same-name ambiguity;
- initially sufficient no-regression;
- unsupported retrieval-state failure;
- inconsistent structural-state failure;
- deterministic repeat;
- all three policy comparisons.

- [ ] **Step 2: Write failing metric/gate tests**

Pin:
- portable required-memory recovery cases succeed;
- SIGNAL_DRIVEN regression count = 0;
- easy unnecessary expansion count = 0;
- persistent-insufficient case ends EXHAUSTED;
- max SIGNAL_DRIVEN rounds <= 3;
- ALWAYS_EXPAND evaluates exactly all profile scopes;
- NO_EXPANSION evaluates exactly one scope per valid case;
- ambiguity/validation failures = 0;
- qualifier returns no errors for frozen portable fixture.

- [ ] **Step 3: Write failing research/engineering separation tests**

Pin that portable qualification:
- is an engineering correctness gate;
- does not emit the primary physical SUPPORTED/MIXED/NOT_SUPPORTED outcome;
- contains no scalar surprise/uncertainty calibration metric;
- contains no FLOP/energy/power claim.

- [ ] **Step 4: Write deterministic-repeat tests**

Run the same fixture twice and require equality of logical report payload.

- [ ] **Step 5: Verify RED**

Run:
```powershell
python -m pytest -q tests/test_uncertainty_expansion_benchmark.py
```

Expected: FAIL because benchmark module does not exist.

- [ ] **Step 6: Implement portable fixture/report/qualifier**

Use fake scope evaluators; do not call Ollama or embedding APIs.

- [ ] **Step 7: Extend CI boundary tests**

Pin that GitHub workflow:
- runs full pytest and existing portable gates;
- does not execute `qualify_uncertainty_expansion_a007.py`;
- does not call Ollama/local HTTP;
- keeps prior physical qualification scripts local-only.

- [ ] **Step 8: Run Task 4 gates**

Run:
```powershell
python -m pytest -q tests/test_uncertainty_expansion_benchmark.py tests/test_ci_contract.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
git diff --check
```

Expected: all PASS.

- [ ] **Step 9: Commit Task 4**

Commit:

`Add A007 uncertainty expansion benchmark`

### Task 5: Implement and run frozen physical A005+A006+A007 qualification

**Files:**
- Create: `scripts/qualify_uncertainty_expansion_a007.py`
- Create: `tests/test_uncertainty_expansion_qualification_cli.py`
- Modify: `docs/development/tasks/A007-surprise-uncertainty-expansion.md`

**Frozen physical constants:**
- model: `qwen3-embedding:0.6b`
- digest: `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`
- dimension: 1024
- threshold: `0.5037018224299838`
- selector: `SINGLE_BEST`
- profile name: `a007-structural-expansion-v1`
- round 0: tier 1 / top_k 12 / memory 8 / working 4
- round 1: tier 2 / top_k 24 / memory 12 / working 8
- round 2: tier 3 / top_k 32 / memory 16 / working 12

**Physical helper records/interfaces:**
- immutable `PhysicalExpansionCue(source_cue_id: str, query_id: str, query_text: str)`.
- immutable `PhysicalExpansionCueTier(tier_index: int, cues: tuple[PhysicalExpansionCue, ...])`.
- immutable `PhysicalExpansionCase(case_id: str, documents: tuple[VectorMemoryDocument, ...], cue_tiers: tuple[PhysicalExpansionCueTier, ...], required_memory_ids: tuple[str, ...], initially_sufficient: bool = False, ambiguity_expected: bool = False, persistent_insufficient: bool = False)`.
- Produces `build_physical_fixture() -> tuple[PhysicalExpansionCase, ...]`.
- Produces `run_physical_case(adapter, case, *, profile, threshold, embedding_profile) -> dict[str, object]`.
- Produces `classify_hypothesis_outcome(...) -> str`.
- Produces `validate_physical_experiment(payload: dict[str, object]) -> list[str]`.

- [ ] **Step 1: Write failing frozen-profile and fixture-structure tests**

Pin exact model/digest/dimension/threshold/selector/profile/three scopes.

Fixture must include:
- English easy;
- Thai easy;
- English later-tier recovery;
- Thai later-tier recovery;
- cross-lingual recovery;
- budget-truncation;
- same-name ambiguity;
- persistent insufficient.

Require exactly three cue tiers per physical case, unique source cue/query IDs across each case, and frozen fixture version/fingerprint constants before final live run.

- [ ] **Step 2: Write failing fake A005+A006+A007 composition tests**

With a deterministic fake embedding adapter:
- build one `ExactVectorMemoryIndex` per case;
- use `select_single_best` at every scope;
- round N searches all cues in enabled tiers under that round's top_k;
- SIGNAL_DRIVEN can recover at later tier;
- NO_EXPANSION remains round 0;
- ALWAYS_EXPAND evaluates all three rounds;
- shared index-build occurs once.

- [ ] **Step 3: Write failing setup-vs-policy metrics tests**

Pin a recording adapter/counter snapshot API so:
- index build metrics are captured once as `setup_embedding_metrics`;
- each policy records counter deltas from immediately before to immediately after that policy;
- sum of policy query inputs excludes document-index inputs;
- token/timing fields preserve backend values when available;
- logical determinism comparisons exclude timing-duration equality and cumulative
  recorder counters; compare policy/round/decision/selected-memory payloads
  under the same retrieved evidence instead.

- [ ] **Step 4: Write failing physical engineering-validation tests**

CLI must exit nonzero for:
- model/digest/dimension mismatch;
- fixture version/fingerprint/case-set drift;
- physical profile drift;
- duplicate cue/query identity;
- ambiguity-preservation failure;
- persistent-insufficient case not ending CONTROLLER_EXHAUSTED under SIGNAL_DRIVEN;
- controller nondeterminism;
- malformed cost counters.

A valid `MIXED` or `NOT_SUPPORTED` outcome must still exit 0.

- [ ] **Step 5: Write failing hypothesis-classification tests**

Frozen primary rules:
- SUPPORTED only if recovery >= 1, regression = 0, SIGNAL_DRIVEN coverage == ALWAYS_EXPAND coverage, easy unnecessary expansion = 0, all persistent-insufficient cases exhaust, and SIGNAL_DRIVEN total rounds < ALWAYS_EXPAND total rounds;
- MIXED if recovery >= 1 but one or more SUPPORTED conditions fail;
- NOT_SUPPORTED if recovery = 0 or no valid recovery objective improvement is demonstrated.

- [ ] **Step 6: Write failing UTF-8/output tests**

Pin:
- Thai payload works with simulated cp1252 console;
- stdout bytes == `--output` bytes;
- payload has no Qwen3.5:4b generation field/call;
- payload has no graph or threshold-relaxation field;
- payload calls request/round reductions by their measured names, not FLOP/energy savings.

- [ ] **Step 7: Verify RED**

Run:
```powershell
python -m pytest -q tests/test_uncertainty_expansion_qualification_cli.py
```

Expected: FAIL because physical script does not exist.

- [ ] **Step 8: Implement physical runner and freeze fixture identity**

Before the first final live run:
- finalize texts/labels;
- compute fixture fingerprint;
- pin version/fingerprint/case IDs in tests and script;
- commit the runner and fixture.

After observing final physical outcomes, do not edit threshold/ladder/text/labels unless a fixture-validity defect is demonstrated with a new RED regression test.

- [ ] **Step 9: Run portable gates before live inference**

Run:
```powershell
python -m pytest -q tests/test_uncertainty_expansion_qualification_cli.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
git diff --check
```

Expected: all PASS.

- [ ] **Step 10: Commit physical tooling**

Commit:

`Add A007 physical uncertainty expansion qualification`

- [ ] **Step 11: Verify local embedding identity read-only**

Require exact tag/digest/dimension. Do not repull or update a correct installed model.

- [ ] **Step 12: Run live physical qualification**

Use a managed process and scratch JSON evidence.

Require structurally valid execution:
- frozen identity/profile/fixture;
- primary selector SINGLE_BEST;
- all three policies reported;
- policy runs use the same immutable index and documents but independent
  counter snapshots; no policy reuses another policy's query results;
- persistent-insufficient bounded termination;
- ambiguity preserved;
- deterministic controller result;
- setup/per-policy counters valid;
- exactly one research outcome SUPPORTED/MIXED/NOT_SUPPORTED.

A valid negative outcome remains exit 0 and is recorded without result chasing.

- [ ] **Step 13: Record physical evidence in task ledger**

Include raw outcome metrics and explicit statement that setup cost is separated from policy execution cost. Keep scratch JSON ignored.

### Task 6: Exact qualification, closure report, review, integration

**Files:**
- Create: `docs/development/reports/ASCA-20261009-A007-surprise-uncertainty-expansion.md`
- Modify: `docs/development/tasks/A007-surprise-uncertainty-expansion.md`
- Modify: `docs/development/tasks/CURRENT.md`
- Modify: `docs/development/tasks/ROADMAP.md`
- Modify: `README.md`
- Modify: `tests/test_a007_task_ledger.py`
- Modify: `tests/test_task_ledger.py`

- [ ] **Step 1: Run fresh exact branch gate**

Run:
```powershell
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
git diff --check HEAD^ HEAD
git status --short --branch
git rev-parse HEAD
```

If controller, policy runner, fixture, or physical cost behavior changed after the last physical run, rerun physical qualification.

- [ ] **Step 2: Verify isolation read-only**

Confirm:
- A005 digest/threshold/vector semantics unchanged;
- A006 selector/baseline semantics and physical `NOT_SUPPORTED` report unchanged;
- A004 generative model path untouched;
- FlyWireLLM has no active training runner and is not modified.

- [ ] **Step 3: Push branch and require exact portable CI**

Push normally without force. Record exact branch SHA and CI run ID.

- [ ] **Step 4: Write A007 qualification report**

Report:
- exact candidate SHA/test count/audits/A003/diff;
- portable engineering metrics;
- frozen profile/fixture fingerprint;
- physical model identity;
- per-policy coverage/recovery/regression;
- easy-case unnecessary expansion;
- persistent-insufficient exhaustion;
- rounds executed per policy;
- setup embedding metrics;
- per-policy embedding/query/input/token/timing counter deltas;
- primary research outcome;
- any secondary SELECTIVE_CONVERGENCE diagnostic clearly separated;
- non-FLOP/non-energy claims boundary;
- A006 `NOT_SUPPORTED` preserved;
- FlyWireLLM paused/untouched;
- exact branch CI.

- [ ] **Step 5: Write failing closure-transition tests**

Pin:
- A007 Status DONE;
- CURRENT -> A008 PLANNED / no issue;
- ROADMAP A007 DONE, A008 PLANNED;
- closure report exact SHA/CI/profile/fingerprint/outcome/cost evidence;
- report has exactly one primary SUPPORTED/MIXED/NOT_SUPPORTED outcome;
- no prediction-surprise qualification claim;
- no graph milestone or A008 issue auto-created.

Verify RED before state edits.

- [ ] **Step 6: Transition A007 DONE / A008 PLANNED and run closure gate**

Run:
```powershell
python -m pytest -q tests/test_a007_task_ledger.py tests/test_task_ledger.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
git diff --check
```

Expected: all PASS.

- [ ] **Step 7: Commit closure and require exact closure-branch CI**

Commit:

`Qualify A007 surprise uncertainty expansion`

Push and require exact SHA CI.

- [ ] **Step 8: Whole-branch review and one Critical/Important fix pass**

Review base `8bdf87d19147cd30ccfbd8cd07238ab07c389dc0..closure-head`, prioritizing:
- baseline policy/controller-assessment conflation;
- contradictory structural-state acceptance;
- hidden extra rounds or speculative callback evaluation;
- threshold/profile/fixture drift;
- setup-vs-policy cost contamination;
- timing included in determinism equality;
- hidden Qwen/graph dependencies;
- research outcome treated as execution validity;
- overclaim of request/round savings as compute/energy savings.

Fix Critical/Important findings with RED->GREEN tests. Rerun physical qualification whenever controller, policy, fixture, cost accounting, or validation behavior changes.

- [ ] **Step 9: Require post-review exact branch CI**

Push reviewed branch and require exact SHA CI before integration.

- [ ] **Step 10: Fast-forward local main only**

Require main clean/synchronized and ancestry from base, then:

```powershell
git merge --ff-only research/a007-uncertainty-expansion
```

No rebase/reset/force push.

- [ ] **Step 11: Verify merged main before push**

Run:
```powershell
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
git diff --check origin/main..HEAD
```

- [ ] **Step 12: Push main and require exact final-main CI**

Do not close Issue #7 until exact main SHA CI succeeds.

- [ ] **Step 13: Record main integration evidence with tested closure commits**

If recording CI evidence requires a documentation-only commit on main, verify that commit locally and through exact-main CI before issue closure, following the A006 closure discipline.

- [ ] **Step 14: Final synchronization, Issue #7 closure, cleanup**

Require:
- HEAD == origin/main;
- ahead/behind 0/0;
- main clean;
- Issue #7 still open until this point;
- FlyWireLLM paused/untouched.

Close Issue #7 with final SHA/CI/portable/physical outcome/cost evidence.

Remove the clean A007 worktree and delete the local feature branch non-force. Preserve remote/history unless explicitly requested otherwise.

## A007 Non-Goals

A007 must not:
- qualify true prediction surprise;
- populate scalar `UncertaintySignal` with invented values;
- lower A005 threshold;
- generate query cues with Qwen3.5:4b;
- ask Qwen3.5:4b to judge uncertainty/expansion;
- build/traverse a typed graph;
- change A005 vector retrieval semantics;
- change A006 SINGLE_BEST semantics;
- rewrite A006 physical `NOT_SUPPORTED`;
- detect contradiction;
- execute/learn procedures;
- assemble final model prompts;
- claim fewer rounds/requests equal lower FLOPs, power, or energy.

## Execution Order

Execute Tasks 1-6 sequentially with RED -> GREEN -> fresh regression -> commit at each checkpoint. Keep portable CI independent of Ollama. Freeze physical fixture/profile before the final live run. Keep structural experiment validity separate from the SUPPORTED/MIXED/NOT_SUPPORTED research outcome. A008 remains PLANNED until A007 final main CI and synchronization are GREEN.