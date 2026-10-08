# A003 Familiarity System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement and qualify a deterministic exact Familiarity System baseline that recognizes previously encountered typed cue surfaces and narrows opaque candidate regions without performing recall, identity resolution, or semantic inference.

**Architecture:** Add a focused `flywire_asca.familiarity` package that consumes ASCA Contract v0.1 `Cue`/`CueKind` records. `ExactFamiliarityIndex` uses a typed normalized key for one-probe lookup, while `ExhaustiveFamiliarityBaseline` preserves identical observable semantics by scanning every trace; a deterministic benchmark compares correctness, ambiguity preservation, candidate narrowing, and logical work.

**Tech Stack:** Python >=3.11 standard library only, ASCA Contract v0.1, frozen dataclasses, Unicode `unicodedata.normalize`, pytest, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-10-08-a003-familiarity-system-design.md`

## Global Constraints

- Task: A003 — Familiarity System; GitHub Issue #3.
- Branch: `research/a003-familiarity-system`.
- Base contract: ASCA Contract v0.1.
- No mandatory runtime dependency may be added.
- No FlyWireLLM import, model call, checkpoint access, process stop/restart, training command, or training-file mutation.
- No associative recollection, graph spreading activation, identity resolution, working-set routing, surprise policy, or procedural learning is implemented in A003.
- Exact typed key is `(CueKind, normalized_surface_value)`.
- Normalization is exactly NFKC -> strip -> collapse Unicode whitespace runs to one ASCII space -> Unicode `casefold()`.
- Normalization performs no stemming, transliteration, typo correction, translation, token similarity, embedding lookup, or semantic inference.
- Same surface under different `CueKind` values must remain different keys.
- Same-name ambiguity must return every matching candidate region; no identity winner or `same_person` conclusion is produced.
- Exact familiarity score is binary: exactly `1.0` for a matching bucket and `0.0` for no bucket.
- Result region IDs and trace IDs are deduplicated/sorted deterministically.
- Exact lookup logical probes equal 1 for every valid cue; exhaustive lookup logical probes equal the total trace count.
- Logical probe counts are not FLOP or hardware-energy claims.
- No online trace mutation API is added in A003 v0.1.
- Controlled benchmark data is synthetic/declared and requires no external dataset.
- A004 remains PLANNED when A003 closes.

## File Structure

- `src/flywire_asca/familiarity/__init__.py`: public A003 exports only.
- `src/flywire_asca/familiarity/models.py`: immutable trace/result/cost/benchmark record types and validation.
- `src/flywire_asca/familiarity/normalization.py`: conservative deterministic surface normalization and typed-key construction.
- `src/flywire_asca/familiarity/exact.py`: `ExactFamiliarityIndex` and `ExhaustiveFamiliarityBaseline`.
- `src/flywire_asca/familiarity/benchmark.py`: deterministic controlled benchmark evaluation and qualification logic.
- `scripts/run_familiarity_benchmark_a003.py`: machine-readable CLI benchmark/qualification entry point.
- `tests/test_familiarity_models.py`: immutable model validation.
- `tests/test_familiarity_normalization.py`: Unicode/type-key normalization behavior.
- `tests/test_familiarity_exact.py`: exact/exhaustive semantic equivalence and ambiguity behavior.
- `tests/test_familiarity_benchmark.py`: fixture metrics, deterministic report, and qualification acceptance.
- `docs/development/tasks/A003-familiarity-system.md`: recoverable task ledger.
- `docs/development/reports/ASCA-20261008-A003-familiarity-system.md`: final exact evidence.

## Review Focus

1. **Unicode whitespace/case normalization:** non-ASCII whitespace, compatibility characters, and Thai text must normalize deterministically without English-only tokenization; pin in Task 1 normalization tests.
2. **Cross-kind collision:** identical normalized surface under `CueKind.TEXT` and `CueKind.ENTITY` must not share familiarity; pin in Task 2 exact-index tests.
3. **Ambiguous same-name input:** multiple matching regions must all survive and no winner field may exist; pin in Task 2 public-result/ambiguity tests.
4. **Duplicate traces/regions:** duplicate `trace_id` must fail closed while different traces pointing to the same region must deduplicate only the region output, not matched trace IDs; pin in Tasks 1–2.
5. **Cost/benchmark overclaim:** exact and exhaustive outputs must match while logical probe counts differ; benchmark JSON must not label those counts as FLOPs, energy, or hardware compute; pin in Task 3 benchmark/CLI tests.

---

### Task 1: Activate A003 and define familiarity records plus normalization

**Files:**
- Create: `src/flywire_asca/familiarity/__init__.py`
- Create: `src/flywire_asca/familiarity/models.py`
- Create: `src/flywire_asca/familiarity/normalization.py`
- Create: `tests/test_familiarity_models.py`
- Create: `tests/test_familiarity_normalization.py`
- Create: `docs/development/tasks/A003-familiarity-system.md`
- Modify: `docs/development/tasks/CURRENT.md`
- Modify: `docs/development/tasks/ROADMAP.md`
- Modify: `tests/test_task_ledger.py`

**Interfaces:**
- Consumes: `flywire_asca.contracts.Cue`, `CueKind`, `RetrievalState`, and existing validation semantics.
- Produces:
  - `FamiliarityTrace(trace_id: str, cue_kind: CueKind, surface_value: str, region_id: str, evidence_ids: tuple[str, ...] = ())`
  - `FamiliarityCost(index_probes: int, matched_trace_count: int, total_trace_count: int)`
  - `FamiliarityResult(cue_id: str, retrieval_state: RetrievalState, familiarity_score: float, candidate_region_ids: tuple[str, ...], matched_trace_ids: tuple[str, ...], cost: FamiliarityCost)`
  - `normalize_surface(value: str) -> str`
  - `familiarity_key(kind: CueKind, surface_value: str) -> tuple[CueKind, str]`

- [ ] **Step 1: Write failing model tests**

Add tests asserting:
- all three public records are frozen dataclasses;
- blank `trace_id` and blank `region_id` raise `ValueError`;
- empty-after-normalization `surface_value` is invalid;
- duplicate `evidence_ids` are invalid;
- `FamiliarityCost` fields are integers >= 0 and `matched_trace_count <= total_trace_count`;
- `FamiliarityResult` permits only `FAMILIAR` with score `1.0` or `UNFAMILIAR` with score `0.0`;
- `FAMILIAR` requires at least one matched trace and candidate region;
- `UNFAMILIAR` requires empty matched/candidate tuples;
- `candidate_region_ids` and `matched_trace_ids` must each already equal `tuple(sorted(set(values)))`; non-canonical result construction raises `ValueError`;
- `cost.matched_trace_count == len(matched_trace_ids)` and `cost.total_trace_count >= cost.matched_trace_count`.

- [ ] **Step 2: Write failing normalization tests**

Pin exact values:
- `normalize_surface("  Alice  ") == "alice"`;
- `normalize_surface("ＡＬＩＣＥ") == "alice"` through NFKC;
- `normalize_surface("สวัสดี\u00a0  โลก") == "สวัสดี โลก"`;
- whitespace-only input raises `ValueError`;
- `familiarity_key(CueKind.ENTITY, " A ") != familiarity_key(CueKind.TEXT, " A ")`;
- repeated calls produce identical values.

- [ ] **Step 3: Run focused tests and verify RED**

Run:
```powershell
python -m pytest -q tests/test_familiarity_models.py tests/test_familiarity_normalization.py
```

Expected: collection/import failure because `flywire_asca.familiarity` does not exist.

- [ ] **Step 4: Implement minimal records and normalization**

Use frozen/slotted dataclasses. `FamiliarityTrace.__post_init__` validates the original surface by calling `normalize_surface` but preserves the original `surface_value`; the normalized form is derived, not duplicated in storage.

`normalize_surface(value: str) -> str` uses:
```text
unicodedata.normalize("NFKC", value)
-> split on Unicode whitespace
-> join with " "
-> casefold
```

- [ ] **Step 5: Activate the A003 task ledger**

Create `A003-familiarity-system.md` with Status ACTIVE, Issue #3, branch, Goal, Scope, Phases, Acceptance Criteria, Evidence, Current Action, Next Action.

Update:
- `CURRENT.md`: A003 / ACTIVE / Issue #3 / branch;
- `ROADMAP.md`: A003 ACTIVE;
- task-ledger tests: A003 is the single ACTIVE task.

Do not modify A002 DONE evidence.

- [ ] **Step 6: Run focused tests and full regression**

Run:
```powershell
python -m pytest -q tests/test_familiarity_models.py tests/test_familiarity_normalization.py tests/test_task_ledger.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
git diff --check
```

Expected: all commands PASS.

- [ ] **Step 7: Commit Task 1**

Commit:
```text
Add A003 familiarity records and normalization
```

### Task 2: Implement exact and exhaustive familiarity engines

**Files:**
- Create: `src/flywire_asca/familiarity/exact.py`
- Create: `tests/test_familiarity_exact.py`
- Modify: `src/flywire_asca/familiarity/__init__.py`
- Modify: `docs/development/tasks/A003-familiarity-system.md`

**Interfaces:**
- Consumes: Task 1 `FamiliarityTrace`, `FamiliarityResult`, `FamiliarityCost`, `familiarity_key`; A002 `Cue`.
- Produces:
  - `ExactFamiliarityIndex(traces: Iterable[FamiliarityTrace])`
  - `ExactFamiliarityIndex.assess(cue: Cue) -> FamiliarityResult`
  - `ExhaustiveFamiliarityBaseline(traces: Iterable[FamiliarityTrace])`
  - `ExhaustiveFamiliarityBaseline.assess(cue: Cue) -> FamiliarityResult`
- Construction materializes the finite input iterable once and rejects duplicate `trace_id`.

- [ ] **Step 1: Write failing known/unknown semantic-equivalence tests**

Use declared traces:
- ENTITY `Alice` -> `person-alice`;
- lookup ENTITY `" alice "` => FAMILIAR, score 1.0, region `("person-alice",)`;
- lookup ENTITY `"Bob"` => UNFAMILIAR, score 0.0, empty outputs;
- exact and exhaustive observable fields are equal except `cost.index_probes`.

- [ ] **Step 2: Write failing cue-kind and ambiguity tests**

Pin:
- ENTITY `"A"` familiar does not make TEXT `"A"` familiar;
- two ENTITY `"A"` traces in `person-a-primary` and `person-a-neighbor` return both regions sorted;
- `FamiliarityResult` has no `identity_id`, `winner_id`, or `same_person` field;
- two different matching trace IDs pointing to the same region return one candidate region but both trace IDs.

- [ ] **Step 3: Write failing construction/cost/determinism tests**

Assert:
- duplicate trace IDs raise `ValueError`;
- generator input works after one construction materialization;
- exact valid lookup always reports `index_probes == 1`;
- exhaustive lookup reports `index_probes == total_trace_count`;
- both report the same `matched_trace_count` and `total_trace_count`;
- trace/region ordering is independent of construction order.

- [ ] **Step 4: Run focused tests and verify RED**

Run:
```powershell
python -m pytest -q tests/test_familiarity_exact.py
```

Expected: FAIL because engines do not exist.

- [ ] **Step 5: Implement `ExactFamiliarityIndex`**

Store:
- immutable tuple of all traces;
- dict keyed by `tuple[CueKind, str]` to tuple of traces.

`assess` performs exactly one dict `.get()` typed-key probe and builds deterministic sorted IDs. It returns all regions; it never calls memory/relation/LLM APIs.

- [ ] **Step 6: Implement `ExhaustiveFamiliarityBaseline`**

Materialize the same trace representation but scan every trace on each valid cue. Matching uses the same `familiarity_key` function as the exact index.

Use `cost.index_probes = total_trace_count` to represent logical records examined; document that this field is a logical-work counter despite its historical name.

- [ ] **Step 7: Run focused tests and full regression**

Run:
```powershell
python -m pytest -q tests/test_familiarity_exact.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
git diff --check
```

Expected: all PASS.

- [ ] **Step 8: Update A003 resume pointer and commit**

Mark engine implementation DONE and benchmark qualification ACTIVE in A003 task phases.

Commit:
```text
Add exact familiarity index baseline
```

### Task 3: Add deterministic benchmark evaluator and CI qualification gate

**Files:**
- Create: `src/flywire_asca/familiarity/benchmark.py`
- Create: `tests/test_familiarity_benchmark.py`
- Create: `scripts/run_familiarity_benchmark_a003.py`
- Modify: `src/flywire_asca/familiarity/__init__.py`
- Modify: `.github/workflows/ci.yml`
- Modify: `tests/test_ci_contract.py`
- Modify: `docs/development/tasks/A003-familiarity-system.md`

**Interfaces:**
- Consumes: exact/exhaustive engines and A002 `Cue`/`RetrievalState`.
- Produces:
  - `FamiliarityBenchmarkCase(case_id: str, cue: Cue, expected_state: RetrievalState, expected_region_ids: tuple[str, ...], universe_region_count: int | None = None, ambiguity_expected: bool = False)`;
  - `FamiliarityBenchmarkCaseResult(case_id: str, expected_state: RetrievalState, actual_state: RetrievalState, expected_region_ids: tuple[str, ...], actual_region_ids: tuple[str, ...], classification_correct: bool, regions_correct: bool, ambiguity_preserved: bool, candidate_region_count: int, candidate_region_fraction: float | None, matched_trace_count: int, exact_logical_probes: int, exhaustive_logical_probes: int, semantic_equivalent: bool)`;
  - `FamiliarityBenchmarkReport(scope: str, total_trace_count: int, case_results: tuple[FamiliarityBenchmarkCaseResult, ...], case_count: int, correct_classification_count: int, classification_accuracy: float, false_familiarity_count: int, false_unfamiliar_count: int, ambiguity_failure_count: int, semantic_mismatch_count: int, exact_logical_probes: int, exhaustive_logical_probes: int)`;
  - `build_a003_qualification_fixture() -> tuple[tuple[FamiliarityTrace, ...], tuple[FamiliarityBenchmarkCase, ...]]`;
  - `run_familiarity_benchmark(traces: Iterable[FamiliarityTrace], cases: Iterable[FamiliarityBenchmarkCase]) -> FamiliarityBenchmarkReport`;
  - `benchmark_report_payload(report: FamiliarityBenchmarkReport) -> dict[str, object]`;
  - `qualify_a003_report(report: FamiliarityBenchmarkReport) -> list[str]`.
- CLI:
  - `python scripts/run_familiarity_benchmark_a003.py` prints one deterministic JSON report;
  - `--qualify` additionally applies A003 acceptance and exits 0/1.

- [ ] **Step 1: Write failing benchmark-model validation tests**

Assert:
- case IDs are nonblank and unique when evaluated;
- expected state is only FAMILIAR/UNFAMILIAR;
- `expected_region_ids` must already equal `tuple(sorted(set(expected_region_ids)))`; non-canonical input raises `ValueError`;
- `universe_region_count`, when present, is positive and >= the number of expected regions;
- `ambiguity_expected=True` requires at least two expected regions.

- [ ] **Step 2: Write failing qualification-fixture tests**

Fixture must include:
1. unique known cue;
2. unknown cue;
3. normalization-equivalent cue;
4. cross-`CueKind` negative;
5. same-name two-region ambiguity;
6. duplicate traces to one region;
7. Thai/Unicode normalization case;
8. a synthetic distractor population of at least 256 distinct traces/regions used by one known and one unknown query.

Expected controlled qualification:
- classification accuracy = 1.0;
- false familiarity count = 0;
- false unfamiliar count = 0;
- ambiguity failures = 0;
- semantic mismatches between exact/exhaustive = 0;
- every exact valid case contributes exactly 1 logical probe;
- exhaustive logical probes = `case_count * total_trace_count`;
- each case result records `candidate_region_count`; `candidate_region_fraction` is `count / universe_region_count` when declared and `None` otherwise;
- report `scope == "controlled_fixture_only"`.

- [ ] **Step 3: Write failing deterministic CLI/overclaim tests**

Assert:
- two CLI runs from the same fixture produce byte-identical stdout JSON;
- JSON keys are sorted/deterministic;
- output includes the literal qualification scope `"controlled_fixture_only"`;
- output contains no keys/labels containing `flop`, `energy`, or `hardware_compute_reduction`;
- `--qualify` returns exit 0 for the built-in fixture.

- [ ] **Step 4: Run focused tests and verify RED**

Run:
```powershell
python -m pytest -q tests/test_familiarity_benchmark.py
```

Expected: FAIL because benchmark module/script do not exist.

- [ ] **Step 5: Implement benchmark evaluator**

Compute integer counts first, then deterministic rates from those counts. Compare exact/exhaustive results excluding only `cost.index_probes`; any state, score, candidate-region, matched-trace, matched-count, or total-trace mismatch increments `semantic_mismatch_count`.

`ambiguity_preserved` is true for non-ambiguity cases and, for `ambiguity_expected=True`, only when all expected regions are returned with no selected identity field. `ambiguity_failure_count` counts false values only for ambiguity-expected cases.

Do not record wall-clock time in the deterministic qualification JSON.

- [ ] **Step 6: Implement qualification fixture and CLI**

Use only synthetic/declared data. CLI serializes a plain dict via:
```python
json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
```

`qualify_a003_report` returns an empty list only when:
- `scope == "controlled_fixture_only"`;
- `case_count > 0`;
- `classification_accuracy == 1.0`;
- false familiarity/unfamiliar counts are 0;
- ambiguity failure count is 0;
- semantic mismatch count is 0;
- `exact_logical_probes == case_count`;
- `exhaustive_logical_probes == case_count * total_trace_count`.

Otherwise it returns deterministic human-readable error strings.

- [ ] **Step 7: Add explicit CI benchmark gate**

Add GitHub Actions step:
```yaml
- name: Qualify A003 familiarity benchmark
  run: python scripts/run_familiarity_benchmark_a003.py --qualify
```

Extend `tests/test_ci_contract.py` to pin this command.

- [ ] **Step 8: Run benchmark and full gates**

Run:
```powershell
python -m pytest -q tests/test_familiarity_benchmark.py tests/test_ci_contract.py
python scripts/run_familiarity_benchmark_a003.py --qualify
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
git diff --check
```

Expected:
- benchmark CLI exits 0;
- controlled fixture satisfies all A003 acceptance values;
- full suite/audits PASS.

- [ ] **Step 9: Update task resume pointer and commit**

Mark Tasks 1–3 DONE and exact qualification ACTIVE.

Commit:
```text
Add A003 familiarity benchmark qualification
```

### Task 4: Exact branch qualification, closure evidence, and fast-forward integration

**Files:**
- Create: `docs/development/reports/ASCA-20261008-A003-familiarity-system.md`
- Modify: `docs/development/tasks/A003-familiarity-system.md`
- Modify: `docs/development/tasks/CURRENT.md`
- Modify: `docs/development/tasks/ROADMAP.md`
- Modify: `tests/test_task_ledger.py`

**Interfaces:**
- Consumes: all A003 implementation/benchmark artifacts.
- Produces: exact qualification evidence, A003 DONE state, and A004 PLANNED pointer.

- [ ] **Step 1: Run fresh exact local candidate gate**

Run on a clean branch HEAD:
```powershell
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
git diff --check HEAD^ HEAD
git status --short --branch
git rev-parse HEAD
```

Expected: every command PASS/clean; record exact SHA and test count.

- [ ] **Step 2: Verify FlyWireLLM isolation before publication**

Read-only evidence:
- FlyWireLLM repository branch/HEAD;
- clean/ahead/behind state;
- Windows process command line for the active L004 training runner if still present.

Do not stop, restart, signal, import, or inspect training checkpoints.

- [ ] **Step 3: Push A003 branch and require exact branch CI**

Push without force. Verify GitHub Actions success for the exact candidate SHA and record run ID.

- [ ] **Step 4: Write A003 evidence report**

Report:
- candidate SHA;
- local test count;
- benchmark deterministic JSON/acceptance summary;
- audit/qualifier/diff results;
- exact branch CI run;
- exact vs exhaustive semantic equivalence;
- logical-probe comparison with explicit non-FLOP disclaimer;
- same-name ambiguity evidence;
- FlyWireLLM isolation evidence;
- deferred fuzzy/neural/recall scope.

- [ ] **Step 5: Write failing closure-transition tests**

Pin:
- A003 Status DONE;
- CURRENT points to A004 / PLANNED / no issue yet;
- ROADMAP marks A003 DONE and A004 PLANNED;
- closure report contains candidate SHA, test count, benchmark qualification, CI run ID, and FlyWireLLM isolation.

Run focused test and verify RED before changing ledger state.

- [ ] **Step 6: Transition A003 to DONE and A004 to PLANNED**

Update task/report pointers only after branch candidate CI is GREEN.

Run:
```powershell
python -m pytest -q tests/test_task_ledger.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
git diff --check
```

Expected: all PASS.

- [ ] **Step 7: Commit closure and require exact closure-branch CI**

Commit:
```text
Qualify A003 familiarity system
```

Push branch and require CI success on that exact closure SHA.

- [ ] **Step 8: Fast-forward local main only**

Preconditions:
- local main clean;
- `origin/main` fetched and equals local main;
- A003 closure branch is a descendant of main;
- no force/rebase/reset/clean.

Run:
```powershell
git merge --ff-only research/a003-familiarity-system
```

- [ ] **Step 9: Verify merged result before public main push**

Run:
```powershell
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
git diff --check origin/main..HEAD
```

Expected: all PASS.

- [ ] **Step 10: Push main and require exact main CI**

Push without force. Require GitHub Actions success on the same final SHA from the `main` push.

- [ ] **Step 11: Fetch and verify final synchronization**

Require:
- `HEAD == origin/main`;
- ahead/behind = 0/0;
- worktree clean.

- [ ] **Step 12: Close Issue #3 and remove clean A003 worktree**

Issue closure comment records:
- final main SHA;
- local/full test result;
- benchmark qualification summary;
- branch and main CI run IDs;
- sync 0/0;
- FlyWireLLM untouched/still separate;
- A004 PLANNED.

Remove the worktree without deleting branch/history only after final GREEN evidence.

## A003 Non-Goals

A003 must not add:
- fuzzy or approximate lexical matching;
- embeddings/vector search;
- neural familiarity estimation;
- recency or usage-strength learning;
- cross-modal familiarity;
- semantic/associative recall;
- identity resolution;
- graph traversal;
- working-set selection policy;
- surprise-driven expansion;
- FlyWireLLM adapter/model invocation;
- hardware-compute/energy claims from logical probe counts.

## Execution Order

Execute Tasks 1–4 sequentially. Every task uses RED -> GREEN -> full regression -> commit. Do not activate A004 until A003 final main CI and synchronization are GREEN.
