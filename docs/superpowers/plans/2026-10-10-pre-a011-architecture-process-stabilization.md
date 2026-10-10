# PRE-A011 Architecture & Process Consistency Stabilization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make FlyWireASCA qualification-ready for A011 by hardening architecture/lifecycle/qualification contracts, cleaning justified maintenance debt, and proving A003-A010 behavior and research outcomes remain unchanged.

**Architecture:** Treat PRE-A011 as a maintenance gate outside the A-numbered research roadmap. Centralize mutable lifecycle ownership, strengthen repository and package-layer audits, publish a canonical architecture/qualification snapshot, and perform one bounded source refactor that deduplicates Ollama JSON shape validation while preserving all adapter semantics. A011 remains PLANNED with no issue throughout PRE-A011.

**Tech Stack:** Python 3.11+, stdlib `ast`/`dataclasses`/`pathlib`/`re`, pytest 8+, Git/GitHub Actions, existing local Ollama physical qualifiers.

**Spec:** `docs/superpowers/specs/2026-10-10-pre-a011-architecture-process-stabilization-design.md`

## Global Constraints

- Live Git/GitHub/runtime state is authoritative over stale prose.
- Never reset, clean, rebase, or force-push.
- PRE-A011 is a maintenance gate, not a new A-numbered research milestone.
- Do not create the A011 GitHub issue.
- During PRE-A011, ROADMAP keeps A001-A010 DONE and A011 PLANNED; CURRENT may point to PRE-A011/ACTIVE if the maintenance task document exists.
- Preserve historical research outcomes exactly: A006 `NOT_SUPPORTED`; A007 `SUPPORTED`; A008 `SUPPORTED`; A009 `SUPPORTED`; A010 `NOT_SUPPORTED`.
- Do not change frozen fixtures, fingerprints, thresholds, selectors, expansion policies, procedure modes, model tags/digests, or research classifiers.
- Do not optimize A009/A010 retrieval or modify cognitive semantics to improve A010.
- Source cleanup must be behavior-preserving and justified by concrete maintenance debt.
- Do not force a shared Ollama HTTP transport abstraction in PRE-A011.
- Do not split large benchmark modules solely because they are large.
- GitHub CI remains portable and Ollama-free.
- Physical qualifiers remain local-only secondary evidence where the milestone defines a portable primary outcome.
- FlyWireLLM remains untouched.
- A valid historical `NOT_SUPPORTED` outcome remains a successful qualification result.
- Evidence terminology distinguishes activation base, qualified behavior SHA, reviewed behavior SHA, integration SHA, closure metadata commit, and live repository closure state.

## File Structure

New documentation:
- `docs/architecture/ASCA-PRE-A011-SNAPSHOT.md` — canonical implemented architecture/outcome snapshot consumed by A011.
- `docs/development/QUALIFICATION-MATRIX.md` — canonical portable/physical qualification topology.
- `docs/development/tasks/PRE-A011-architecture-process-stabilization.md` — maintenance task ledger created only at activation.
- `docs/development/reports/ASCA-20261010-PRE-A011-architecture-process-stabilization.md` — final stabilization evidence.

Process/audit ownership:
- `scripts/qualify_repository.py` — repository lifecycle/document coherence.
- `scripts/audit_architecture_contract.py` — contract + package dependency direction/cycle audit.
- `tests/test_task_ledger.py` — sole owner of mutable CURRENT/ROADMAP state.
- historical `tests/test_a004_task_ledger.py` through `tests/test_a010_task_ledger.py` — milestone-local immutable evidence only.
- `tests/test_repository_qualification.py` and `tests/test_architecture_audit.py` — RED→GREEN infrastructure tests.
- `tests/test_ci_contract.py` — portable CI and qualification-matrix contract.

Bounded source cleanup:
- `src/flywire_asca/contracts/validation.py` — shared generic JSON-shape validation helpers with caller-selected exception type.
- `src/flywire_asca/model/ollama.py` — consume shared validation helpers; keep model transport/errors/public API unchanged.
- `src/flywire_asca/embedding/ollama.py` — consume shared validation helpers; keep embedding transport/errors/public API unchanged.
- `tests/test_contract_validation.py` — new shared-helper characterization.
- existing `tests/test_ollama_adapter.py` and `tests/test_ollama_embedding_adapter.py` — adapter behavior regression.

## Review Focus

1. **PRE maintenance task falsely required in ROADMAP:** repository qualifier must accept PRE-A011/ACTIVE outside the A-numbered roadmap only when its own task document exists and status matches.
2. **Historical tests still depend on mutable CURRENT/ROADMAP:** a meta-test must fail if A004-A010 milestone tests reference those files after decoupling.
3. **Dependency audit misses indirect cycle:** inject a reverse `contracts -> model` import while `model -> contracts` exists and require an explicit cycle error.
4. **Shared JSON validation changes exception domain:** model malformed payloads must still raise `ModelProtocolError`, embedding malformed payloads must still raise `EmbeddingProtocolError`, with existing message fragments preserved.
5. **Qualification matrix and CI drift apart:** tests must verify all portable commands listed as CI gates exist in workflow and every physical-only command remains absent.

---

### Task 1: Activate PRE-A011 maintenance gate

**Files:**
- Create: `docs/development/tasks/PRE-A011-architecture-process-stabilization.md`
- Create: `tests/test_pre_a011_task_ledger.py`
- Modify: `docs/development/tasks/CURRENT.md`
- Test: `tests/test_task_ledger.py`

**Interfaces:**
- Consumes: approved PRE-A011 spec and plan; live main/GitHub/CI.
- Produces: actual PRE-A011 issue number, isolated branch/worktree, ACTIVE maintenance ledger, CURRENT=PRE-A011/ACTIVE while ROADMAP remains unchanged.

- [ ] **Step 1: Re-check activation preconditions**

Use `superpowers:using-git-worktrees`.

Require:

```text
main == origin/main
main clean
latest exact plan-commit CI = success
Issues #1-#10 closed/completed
A011 title search = no issue
A001-A010 ROADMAP = DONE
A011 ROADMAP = PLANNED
```

- [ ] **Step 2: Create isolated worktree**

Create branch:

`maintenance/pre-a011-architecture-process-stabilization`

from the exact approved plan commit in an isolated worktree.

- [ ] **Step 3: Create PRE-A011 GitHub issue**

Title exactly:

`PRE-A011 — Architecture & Process Consistency Stabilization`

Issue body must state:

- maintenance gate, not A011;
- A011 remains PLANNED/no issue;
- exact preserved A006-A010 outcomes;
- behavior freeze with bounded cleanup;
- no retrieval optimization;
- FlyWireLLM untouched;
- links to approved spec/plan;
- activation-base SHA and CI.

Capture the actual returned issue number; do not guess it.

- [ ] **Step 4: Write failing maintenance-ledger tests**

In `tests/test_pre_a011_task_ledger.py`, require:

```python
def test_pre_a011_is_active_without_mutating_research_roadmap():
    current = read(TASKS / "CURRENT.md")
    roadmap = read(TASKS / "ROADMAP.md")
    task = read(TASKS / "PRE-A011-architecture-process-stabilization.md")
    assert "Current task: PRE-A011" in current
    assert "Status: ACTIVE" in current
    assert "A011" in roadmap and "PLANNED" in roadmap
    assert "PRE-A011" not in roadmap
    assert "Status: ACTIVE" in task
```

Also require the actual PRE-A011 issue number and approved spec/plan paths in the task ledger.

- [ ] **Step 5: Verify RED**

Run:

`python -m pytest -q tests/test_pre_a011_task_ledger.py`

Expected: FAIL because PRE-A011 task/CURRENT activation do not yet exist.

- [ ] **Step 6: Create maintenance task ledger and activate CURRENT**

Write task sections:

- Goal
- Scope / non-scope
- behavior-freeze rules
- accepted cleanup candidates
- preserved outcomes
- activation base/CI
- phases
- acceptance criteria
- current action
- next action

Set CURRENT to PRE-A011 / ACTIVE / actual issue number.

Do **not** add PRE-A011 to the A-numbered ROADMAP.

- [ ] **Step 7: Run activation regressions**

Run:

```bash
python -m pytest -q tests/test_pre_a011_task_ledger.py tests/test_task_ledger.py
git diff --check
```

Expected: PASS.

- [ ] **Step 8: Commit Task 1**

```bash
git add docs/development/tasks/CURRENT.md docs/development/tasks/PRE-A011-architecture-process-stabilization.md tests/test_pre_a011_task_ledger.py tests/test_task_ledger.py
git commit -m "Activate pre-A011 stabilization gate"
```

---

### Task 2: Publish the canonical pre-A011 architecture and qualification truth

**Files:**
- Create: `docs/architecture/ASCA-PRE-A011-SNAPSHOT.md`
- Create: `docs/development/QUALIFICATION-MATRIX.md`
- Create: `tests/test_pre_a011_documentation.py`
- Modify: `docs/superpowers/specs/2026-10-08-asca-architecture-design.md`
- Modify: `docs/development/tasks/README.md`
- Modify: `docs/development/tasks/A009-integrated-cognitive-loop.md`
- Modify: `docs/development/reports/ASCA-20261010-A010-dense-nonselective-baseline-comparison.md`

**Interfaces:**
- Produces: canonical architecture snapshot and qualification matrix for A011 and later process tests.
- Preserves: original design body, roadmap migration, all historical numeric evidence/outcomes.

- [ ] **Step 1: Write failing documentation contract tests**

Require:

- architecture snapshot exists;
- snapshot lists A002-A010 implemented roles;
- exact outcomes A006-A010 appear;
- snapshot distinguishes implemented versus deferred concepts;
- snapshot links roadmap migration;
- original architecture design contains an archival notice but still contains its original old A004/A010 roadmap text;
- qualification matrix lists A003-A010;
- physical scripts A004-A007/A009/A010 are labeled local-only;
- A009 task no longer says Issue #9/final evidence remains pending;
- A010 report no longer has bullet-list rows inside the physical evidence Markdown table;
- task workflow README defines CURRENT as current task state, not only active task;
- evidence-role terminology contains all six terms from Global Constraints.

- [ ] **Step 2: Verify RED**

Run:

`python -m pytest -q tests/test_pre_a011_documentation.py`

Expected: FAIL on missing snapshot/matrix and stale docs.

- [ ] **Step 3: Write `ASCA-PRE-A011-SNAPSHOT.md`**

Record exactly:

- current package layering;
- A002-A010 implemented components;
- implemented/deferred initial concepts;
- exact A006-A010 outcomes;
- A010 7/8 vs 8/8 success and logical-work implication with claims boundary;
- no generalized performance claim;
- A011 remains PLANNED.

- [ ] **Step 4: Add archival notice to initial architecture design**

Add only a notice near the top. Do not renumber/rewrite the historical body.

- [ ] **Step 5: Write `QUALIFICATION-MATRIX.md`**

List exact commands:

Portable CI:
- `python -m pytest -q`
- `python scripts/audit_architecture_contract.py`
- `python scripts/qualify_repository.py`
- `python scripts/run_familiarity_benchmark_a003.py --qualify`
- `python scripts/qualify_procedural_memory_a008.py`
- `python scripts/qualify_integrated_loop_a009.py`
- `python scripts/qualify_baseline_comparison_a010.py`

Local physical:
- `python scripts/qualify_qwen_a004.py`
- `python scripts/qualify_vector_memory_a005.py`
- `python scripts/qualify_selective_activation_a006.py`
- `python scripts/qualify_uncertainty_expansion_a007.py`
- `python scripts/qualify_integrated_loop_a009_physical.py --portable-primary-outcome SUPPORTED`
- `python scripts/qualify_baseline_comparison_a010_physical.py --portable-primary-outcome NOT_SUPPORTED`

Record pinned Qwen model/digests and that negative research outcomes can be valid qualified outcomes.

- [ ] **Step 6: Repair stale workflow/docs**

Update task workflow README with evidence-role definitions.

Repair A009 stale pending closure prose without deleting historical intermediate evidence.

Fix only A010 physical Markdown table formatting; do not alter values.

- [ ] **Step 7: Run documentation tests**

Run:

```bash
python -m pytest -q tests/test_pre_a011_documentation.py
git diff --check
```

Expected: PASS. Repository-wide relative-link validation is owned by Task 4 and is not duplicated here.

- [ ] **Step 8: Commit Task 2**

```bash
git add docs/architecture/ASCA-PRE-A011-SNAPSHOT.md docs/development/QUALIFICATION-MATRIX.md docs/superpowers/specs/2026-10-08-asca-architecture-design.md docs/development/tasks/README.md docs/development/tasks/A009-integrated-cognitive-loop.md docs/development/reports/ASCA-20261010-A010-dense-nonselective-baseline-comparison.md tests/test_pre_a011_documentation.py
git commit -m "Document pre-A011 architecture qualification truth"
```

---

### Task 3: Decouple historical milestone tests from mutable lifecycle state

**Files:**
- Modify: `tests/test_task_ledger.py`
- Modify: `tests/test_a004_task_ledger.py`
- Modify: `tests/test_a005_task_ledger.py`
- Modify: `tests/test_a006_task_ledger.py`
- Modify: `tests/test_a007_task_ledger.py`
- Modify: `tests/test_a008_task_ledger.py`
- Modify: `tests/test_a009_task_ledger.py`
- Modify: `tests/test_a010_task_ledger.py`

**Interfaces:**
- Produces: one canonical mutable-lifecycle test owner (`test_task_ledger.py`).
- Historical tests continue validating only their milestone-local task/report/evidence.

- [ ] **Step 1: Add a failing ownership test**

In `tests/test_task_ledger.py`, scan A004-A010 ledger test source and assert none contains:

```text
CURRENT.md
ROADMAP.md
```

Also assert the central test itself validates current PRE-A011 task state plus unchanged A001-A011 research roadmap.

- [ ] **Step 2: Verify RED**

Run:

`python -m pytest -q tests/test_task_ledger.py`

Expected: FAIL because A004-A010 historical tests still reference CURRENT/ROADMAP.

- [ ] **Step 3: Remove mutable-state assertions from A004-A010 tests**

Delete only assertions whose truth changes when a later milestone activates.

Retain:

- historical task status/evidence;
- issue identity/closure;
- historical CI/SHA where recorded;
- frozen outcome/fingerprint;
- milestone-specific report assertions.

Do not weaken historical evidence tests.

- [ ] **Step 4: Centralize mutable lifecycle assertions**

`tests/test_task_ledger.py` must parse current task and ROADMAP and assert:

- PRE-A011 is CURRENT/ACTIVE while maintenance gate executes;
- PRE-A011 task document exists and matches status;
- PRE-A011 is not added to A-roadmap;
- A001-A010 rows are DONE;
- A011 row is PLANNED;
- A-numbered IDs are unique/monotonic;
- no A011 issue number is recorded.

- [ ] **Step 5: Run all ledger tests**

Run:

`python -m pytest -q tests/test_task_ledger.py tests/test_a004_task_ledger.py tests/test_a005_task_ledger.py tests/test_a006_task_ledger.py tests/test_a007_task_ledger.py tests/test_a008_task_ledger.py tests/test_a009_task_ledger.py tests/test_a010_task_ledger.py tests/test_pre_a011_task_ledger.py`

Expected: PASS.

- [ ] **Step 6: Commit Task 3**

```bash
git add tests/test_task_ledger.py tests/test_a004_task_ledger.py tests/test_a005_task_ledger.py tests/test_a006_task_ledger.py tests/test_a007_task_ledger.py tests/test_a008_task_ledger.py tests/test_a009_task_ledger.py tests/test_a010_task_ledger.py
git commit -m "Centralize mutable task lifecycle tests"
```

---

### Task 4: Harden repository lifecycle qualification

**Files:**
- Modify: `scripts/qualify_repository.py`
- Modify: `tests/test_repository_qualification.py`

**Interfaces:**
- Preserve: `qualify_repository(root: Path) -> list[str]`.
- Add internal immutable parse records:
  - `RoadmapEntry(task_id: str, milestone: str, status: str)`
  - `CurrentTaskState(task_id: str, status: str, github_issue: str)`
- Add internal parsers:
  - `_parse_roadmap(text: str) -> tuple[RoadmapEntry, ...]`
  - `_parse_current(text: str) -> CurrentTaskState`
- Add internal validators:
  - `_validate_lifecycle(root: Path) -> list[str]`
  - `_validate_markdown_links(root: Path) -> list[str]`

- [ ] **Step 1: Expand the temporary repository fixture**

Update `_fixture_root()` to include:

- ROADMAP with A001 DONE and A002 PLANNED;
- A001 task file with checked acceptance;
- CURRENT A002/PLANNED/no issue;
- minimal required workflow README if qualifier requires it.

- [ ] **Step 2: Write failing lifecycle tests**

Add tests for:

1. duplicate ROADMAP task ID;
2. non-monotonic A-numbered IDs;
3. invalid status vocabulary;
4. A-numbered CURRENT status mismatch with ROADMAP;
5. PRE-A011 CURRENT accepted when matching maintenance task exists;
6. PRE-A011 CURRENT rejected when maintenance task is missing;
7. PLANNED current task rejected if numeric issue is guessed;
8. ACTIVE current task rejected if own task file lacks numeric issue;
9. DONE task rejected if unchecked `- [ ]` acceptance remains;
10. DONE task filename/heading ID mismatch;
11. broken repository-relative Markdown link.

- [ ] **Step 3: Verify RED**

Run:

`python -m pytest -q tests/test_repository_qualification.py`

Expected: new tests FAIL.

- [ ] **Step 4: Implement roadmap/current parsers**

Parsers fail closed by returning qualification errors rather than throwing uncontrolled exceptions from `qualify_repository()`.

Allowed statuses exactly:

`PLANNED / ACTIVE / BLOCKED / DONE`.

- [ ] **Step 5: Implement lifecycle validator**

Special PRE-* rule:

```text
PRE current -> matching PRE task file/status required; no ROADMAP row required
A### current -> matching ROADMAP row/status required
```

For DONE task hygiene, inspect the structured task file itself rather than globally banning the English word "pending".

- [ ] **Step 6: Implement local Markdown link validation**

Validate only repository-relative links. Ignore:

- `http://`
- `https://`
- `mailto:`
- same-document `#anchor`

Strip anchors before path resolution.

- [ ] **Step 7: Run qualifier tests and live qualifier**

Run:

```bash
python -m pytest -q tests/test_repository_qualification.py
python scripts/qualify_repository.py
```

Expected: PASS / `repository_qualification=PASS`.

- [ ] **Step 8: Commit Task 4**

```bash
git add scripts/qualify_repository.py tests/test_repository_qualification.py
git commit -m "Harden repository lifecycle qualification"
```

---

### Task 5: Enforce package dependency direction and cycle freedom

**Files:**
- Modify: `scripts/audit_architecture_contract.py`
- Modify: `tests/test_architecture_audit.py`

**Interfaces:**
- Preserve: `audit_architecture_contract(root: Path) -> list[str]`.
- Add constant:
  - `ALLOWED_PACKAGE_DEPENDENCIES: dict[str, frozenset[str]]`
- Add:
  - `_package_dependencies(root: Path) -> dict[str, set[str]]`
  - `_dependency_errors(graph: dict[str, set[str]]) -> list[str]`

- [ ] **Step 1: Write failing forbidden-dependency test**

Copy fixture then inject into `src/flywire_asca/vector_memory/bad.py`:

`from flywire_asca.integrated_loop import run_cognitive_loop`

Require an error mentioning undeclared dependency `vector_memory -> integrated_loop`.

- [ ] **Step 2: Write failing cycle test**

Inject:

`from flywire_asca.model import OllamaModelAdapter`

into a new `contracts/bad.py`.

Because model already depends on contracts, require explicit cycle detection mentioning `contracts` and `model`.

- [ ] **Step 3: Verify RED**

Run:

`python -m pytest -q tests/test_architecture_audit.py`

Expected: new dependency/cycle tests FAIL.

- [ ] **Step 4: Implement AST dependency extraction**

Track only package names declared in `ALLOWED_PACKAGE_DEPENDENCIES`.

Ignore:

- stdlib/external imports;
- intra-package imports;
- root helper modules not represented as architecture packages.

Continue detecting FlyWireLLM imports independently.

- [ ] **Step 5: Implement undeclared-edge and cycle validation**

Use deterministic DFS/Tarjan-style cycle reporting.

The current live graph must pass exactly as declared in the spec.

- [ ] **Step 6: Run architecture tests and live audit**

Run:

```bash
python -m pytest -q tests/test_architecture_audit.py
python scripts/audit_architecture_contract.py
```

Expected: PASS / `architecture_contract_audit=PASS`.

- [ ] **Step 7: Commit Task 5**

```bash
git add scripts/audit_architecture_contract.py tests/test_architecture_audit.py
git commit -m "Enforce ASCA package dependency contract"
```

---

### Task 6: Align qualification matrix with portable CI

**Files:**
- Modify: `tests/test_ci_contract.py`
- Modify: `.github/workflows/ci.yml` only if an explicit label/comment improves clarity without changing command topology.
- Test/consume: `docs/development/QUALIFICATION-MATRIX.md`

**Interfaces:**
- The qualification matrix is the human-readable source of qualification topology.
- CI remains the executable portable gate.

- [ ] **Step 1: Write failing matrix/workflow cross-check tests**

Parse matrix text and assert every portable command listed in Task 2 is present in `ci.yml`.

Assert every physical command/script is absent.

Also require matrix contains:

- A006 `NOT_SUPPORTED`;
- A007/A008/A009 `SUPPORTED`;
- A010 `NOT_SUPPORTED`;
- local-only wording;
- valid negative-outcome wording.

- [ ] **Step 2: Verify RED**

Run:

`python -m pytest -q tests/test_ci_contract.py`

Expected: FAIL until matrix-aware assertions/docs are aligned.

- [ ] **Step 3: Align CI labels/comments only if needed**

Do not add Ollama or physical scripts.

Do not create a portable orchestration script unless the existing explicit command list becomes genuinely simpler by doing so; default is no new orchestrator.

- [ ] **Step 4: Run CI contract tests**

Run:

`python -m pytest -q tests/test_ci_contract.py`

Expected: PASS.

- [ ] **Step 5: Commit Task 6**

```bash
git add tests/test_ci_contract.py .github/workflows/ci.yml
git commit -m "Align CI with qualification matrix"
```

If workflow content does not need modification, do not stage it.

---

### Task 7: Consolidate duplicated Ollama JSON shape validation

**Files:**
- Modify: `src/flywire_asca/contracts/validation.py`
- Modify: `src/flywire_asca/model/ollama.py`
- Modify: `src/flywire_asca/embedding/ollama.py`
- Create: `tests/test_contract_validation.py`
- Modify only if needed for characterization: `tests/test_ollama_adapter.py`
- Modify only if needed for characterization: `tests/test_ollama_embedding_adapter.py`

**Interfaces:**
- Add to `flywire_asca.contracts.validation`:
  - `require_mapping(name: str, value: object, *, error_type: type[Exception] = ValueError) -> dict[str, object]`
  - `require_list(name: str, value: object, *, error_type: type[Exception] = ValueError) -> list[object]`
  - `require_string(name: str, value: object, *, error_type: type[Exception] = ValueError) -> str`
  - `optional_string(name: str, value: object, *, error_type: type[Exception] = ValueError) -> str | None`
  - `optional_nonnegative_int(name: str, value: object, *, error_type: type[Exception] = ValueError) -> int | None`
- Existing `require_nonempty`, `require_probability`, `require_finite`, and `require_unique_nonempty` signatures remain unchanged.
- Model adapter keeps `ModelProtocolError`.
- Embedding adapter keeps `EmbeddingProtocolError`.
- Public Ollama adapter constructors, payloads, timeout handling, transport classes, identity validation, and response contracts remain unchanged.

- [ ] **Step 1: Write shared-helper RED tests**

In `tests/test_contract_validation.py` require:

- valid mapping/list/string pass through;
- blank string fails;
- optional None passes;
- bool is rejected as nonnegative integer;
- custom error type is raised exactly with the existing message shape.

Example:

```python
class MarkerError(Exception):
    pass

with pytest.raises(MarkerError, match="field must be an object"):
    require_mapping("field", [], error_type=MarkerError)
```

- [ ] **Step 2: Add adapter characterization before refactor**

Ensure existing adapter tests explicitly pin:

```text
model malformed object -> ModelProtocolError
embedding malformed object -> EmbeddingProtocolError
model invalid JSON -> ModelProtocolError
embedding invalid JSON -> EmbeddingProtocolError
```

Do not change expected message fragments.

- [ ] **Step 3: Verify RED for shared helpers and GREEN for current adapters**

Run:

```bash
python -m pytest -q tests/test_contract_validation.py
python -m pytest -q tests/test_ollama_adapter.py tests/test_ollama_embedding_adapter.py
```

Expected: new helper tests FAIL; existing adapter tests PASS.

- [ ] **Step 4: Implement generic validation helpers**

Use `error_type(message)` only for type/shape validation.

Do not move HTTP request code or adapter-specific model/embedding semantic checks.

- [ ] **Step 5: Replace duplicated private validators mechanically**

In both Ollama modules, bind the shared validators with the adapter-specific protocol error type while preserving existing call sites and messages.

A reasonable implementation is module-local `functools.partial` bindings; do not introduce a new HTTP abstraction.

- [ ] **Step 6: Run focused characterization**

Run:

```bash
python -m pytest -q tests/test_contract_validation.py tests/test_ollama_adapter.py tests/test_ollama_embedding_adapter.py tests/test_model_contracts.py tests/test_embedding_contracts.py
```

Expected: PASS.

- [ ] **Step 7: Run physical A004 and A005 qualification immediately**

Run:

```bash
python scripts/qualify_qwen_a004.py
python scripts/qualify_vector_memory_a005.py
```

Expected: pinned model/digest identities and historical qualified behavior remain valid.

- [ ] **Step 8: Record explicit no-refactor decisions**

In PRE-A011 task ledger record:

- shared HTTP transport: not refactored; exception-domain separation makes forced abstraction unjustified;
- A009/A010 benchmark modules: not split; no sufficiently strong cohesion boundary to justify pre-A011 regression surface.

- [ ] **Step 9: Commit Task 7**

```bash
git add src/flywire_asca/contracts/validation.py src/flywire_asca/model/ollama.py src/flywire_asca/embedding/ollama.py tests/test_contract_validation.py tests/test_ollama_adapter.py tests/test_ollama_embedding_adapter.py docs/development/tasks/PRE-A011-architecture-process-stabilization.md
git commit -m "Deduplicate Ollama JSON validation"
```

Stage only adapter tests actually changed.

---

### Task 8: Full pre-A011 qualification, review, integration, and closure

**Files:**
- Create: `docs/development/reports/ASCA-20261010-PRE-A011-architecture-process-stabilization.md`
- Modify: `docs/development/tasks/PRE-A011-architecture-process-stabilization.md`
- Modify: `docs/development/tasks/CURRENT.md`
- Modify: `tests/test_pre_a011_task_ledger.py`
- Modify: `tests/test_task_ledger.py`

**Interfaces:**
- Consumes: Tasks 1-7.
- Produces: reviewed maintenance branch, final main integration, PRE-A011 DONE, CURRENT=A011/PLANNED/no issue.

- [ ] **Step 1: Run complete portable verification**

Run:

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

Record exact full-test count.

- [ ] **Step 2: Run complete local physical verification**

Run:

```bash
python scripts/qualify_qwen_a004.py
python scripts/qualify_vector_memory_a005.py
python scripts/qualify_selective_activation_a006.py
python scripts/qualify_uncertainty_expansion_a007.py
python scripts/qualify_integrated_loop_a009_physical.py --portable-primary-outcome SUPPORTED
python scripts/qualify_baseline_comparison_a010_physical.py --portable-primary-outcome NOT_SUPPORTED
```

Require historical outcomes/identities unchanged.

- [ ] **Step 3: Prove frozen research identity**

Record and compare:

- A006 outcome;
- A007 outcome;
- A009 portable fixture fingerprint/outcome;
- A010 portable fixture fingerprint/outcome;
- A005 threshold;
- embedding model/digest/dimension;
- terminal model/digest;
- no A011 issue.

Any drift blocks closure.

- [ ] **Step 4: Classify source diff**

Run:

`git diff <activation-base>..HEAD -- src/flywire_asca`

Expected source diff is limited to:

- `contracts/validation.py`;
- `model/ollama.py`;
- `embedding/ollama.py`.

The report must explain why each is behavior-preserving and cite focused + physical evidence.

Any cognitive package diff is a blocker.

- [ ] **Step 5: Write PRE-A011 report and closure-candidate tests**

Report:

- problems found and repaired;
- architecture graph and no-cycle evidence;
- lifecycle ownership change;
- qualifier hardening;
- qualification matrix;
- JSON validator deduplication;
- explicit deferred cleanup decisions;
- portable/physical results;
- exact preserved outcomes;
- claims boundary;
- FlyWireLLM untouched.

Keep PRE-A011 ACTIVE until reviewed main is GREEN.

- [ ] **Step 6: Commit closure candidate and require exact feature-branch CI**

Commit report/task evidence, push feature branch, require exact SHA CI success.

- [ ] **Step 7: Whole-change review**

Use `superpowers:requesting-code-review`.

Review range:

`activation-base..closure-candidate`

Focus on:

- no cognitive semantic drift;
- lifecycle qualifier false positives/false negatives;
- PRE-* exception to ROADMAP rules;
- dependency graph completeness/cycle detection;
- adapter exception behavior;
- qualification matrix/CI truth;
- preserved research fingerprints/outcomes;
- no hidden A011 activation.

If no independent reviewer mechanism is available, record author self-review explicitly.

- [ ] **Step 8: Fix every Critical/Important finding with RED→GREEN evidence**

Use `superpowers:receiving-code-review`.

Rerun all affected focused tests plus the complete portable gate. Rerun affected physical qualifiers if any source/qualification semantics changed.

Require exact post-review branch CI.

- [ ] **Step 9: Integrate reviewed branch**

Verify:

```text
main clean/sync
feature clean/sync
PRE-A011 issue open
A011 issue absent
exact reviewed branch CI success
```

Use fast-forward-only integration when topology permits. Do not rewrite history.

Run full portable gate on merged main before push, push main, then require exact main CI success.

- [ ] **Step 10: Close PRE-A011 issue after main evidence**

Post final evidence comment containing:

- reviewed/integration SHA;
- exact main CI;
- test count;
- architecture/repository audit results;
- physical gate results;
- preserved outcomes/fingerprints;
- source cleanup classification;
- review findings;
- A011 still PLANNED/no issue.

Close PRE-A011 issue as completed.

- [ ] **Step 11: Return CURRENT to A011/PLANNED**

Set:

```text
Current task: A011
Status: PLANNED
GitHub Issue: not created
```

PRE-A011 task = DONE / issue closed completed.

ROADMAP remains unchanged: A001-A010 DONE, A011 PLANNED.

Update central lifecycle tests for this final state; historical milestone tests must require no edits.

- [ ] **Step 12: Final closure commit and exact CI**

Run complete portable gate, commit closure metadata, push main, require exact closure CI success.

Do not require the closure metadata commit to record its own SHA.

- [ ] **Step 13: Cleanup local execution state**

Remove only the clean isolated PRE-A011 worktree and local feature branch non-force.

Preserve remote feature history unless explicitly requested otherwise.

Final authoritative check:

```text
main == origin/main
ahead/behind = 0/0
main clean
PRE-A011 issue closed/completed
CURRENT = A011/PLANNED/no issue
A011 title search = no issue
A006 NOT_SUPPORTED
A007 SUPPORTED
A008 SUPPORTED
A009 SUPPORTED
A010 NOT_SUPPORTED
```
