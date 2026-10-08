# A001 Repository & Research Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the independent public `funggier/FlyWireASCA` repository and a reproducible, task-driven, evidence-driven Python foundation without implementing ASCA cognitive algorithms yet.

**Architecture:** A001 creates only the engineering/research shell: repository metadata, MIT licensing, Python package skeleton, test harness, CI, development task ledger, and qualification evidence. Cognitive interfaces and algorithms begin in A002 or later so the repository foundation does not prematurely freeze ASCA implementation choices.

**Tech Stack:** Python >=3.11, standard library runtime, pytest development tests, Git, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-10-08-asca-architecture-design.md`

## Global Constraints

- GitHub repository: `funggier/FlyWireASCA`.
- Initial visibility: public.
- Local project root: `T:\Space\Projects\ProjectsAI\FlyWireASCA`.
- Repository source license: MIT.
- ASCA is independent from `funggier/FlyWireLLM`.
- A001 must not modify or depend on the active FlyWireLLM training runtime.
- Python-first; no mandatory cloud dependency; no mandatory external LLM.
- No cognitive algorithm, database choice, model integration, or large-model training is part of A001.
- Task-driven development is mandatory: task status, current action, next action, acceptance criteria, and evidence must be recoverable from repository files.
- Git/GitHub/runtime state is authoritative over stale documentation.
- No task may be marked DONE solely because code exists; fresh verification evidence is required.

## Review Focus

1. Existing non-empty local directory: initialization must preserve the approved spec and plan rather than overwrite them.
2. GitHub repository name collision or pre-existing remote: creation must fail closed and inspect the existing repository rather than silently reuse an unknown repository.
3. Package import from a clean checkout: `flywire_asca` must import without machine-local paths or external services.
4. Task recovery after interruption: `CURRENT.md` and A001 task file must identify one unambiguous current/next action.
5. License/claims drift: repository metadata and README must continue to state MIT for repository source and must not imply that external data/model artifacts are MIT or that ASCA has proven cognitive/biological claims.

---

### Task 1: Bootstrap the local Python repository without losing design artifacts

**Files:**
- Preserve: `docs/superpowers/specs/2026-10-08-asca-architecture-design.md`
- Preserve: `docs/superpowers/plans/2026-10-08-a001-repository-foundation.md`
- Create: `.gitignore`
- Create: `pyproject.toml`
- Create: `src/flywire_asca/__init__.py`
- Create: `tests/test_repository_contract.py`

**Interfaces:**
- Consumes: approved ASCA design spec.
- Produces: importable `flywire_asca` package; project metadata declaring `FlyWireASCA`, Python >=3.11, and MIT license.

- [ ] **Step 1: Initialize Git in the existing project directory without deleting or relocating approved design artifacts**

Run:
```powershell
git init -b main
git status --short --branch
```

Expected: repository initialized on `main`; existing spec/plan remain visible as untracked files.

- [ ] **Step 2: Create the failing repository contract test**

Create `tests/test_repository_contract.py` with tests that assert:
- importing `flywire_asca` succeeds;
- project metadata name is `FlyWireASCA`;
- `requires-python` is at least 3.11;
- project license metadata declares MIT;
- `LICENSE` contains the MIT grant phrase;
- `README.md` contains `Associative Selective Cognition Architecture`, `task-driven`, and the explicit FlyWireLLM independence boundary.

- [ ] **Step 3: Run the focused test and verify RED**

Run:
```powershell
python -m pytest -q tests/test_repository_contract.py
```

Expected: FAIL because package/metadata/LICENSE/README are not all present yet.

- [ ] **Step 4: Create minimal package and project metadata**

Create:
- `pyproject.toml` using setuptools build backend, package discovery under `src`, version `0.1.0.dev0`, Python `>=3.11`, no runtime dependencies, `pytest` in the `dev` optional dependency, and MIT license metadata;
- `src/flywire_asca/__init__.py` exporting `__version__ = "0.1.0.dev0"`;
- `.gitignore` covering Python caches, virtual environments, build artifacts, test caches, local secrets, checkpoints, datasets, and large runtime artifacts without ignoring tracked docs/results metadata.

- [ ] **Step 5: Add MIT License and project README**

Create `LICENSE` using the standard MIT License text with `Copyright (c) 2026 funggier`.

Create `README.md` that states:
- project name and ASCA expansion;
- ASCA is a flexible research direction, not a requirement that every component be associative/selective;
- repository is independent from FlyWireLLM;
- task/evidence-driven workflow;
- claims boundary: no human-equivalence, AGI, biological fidelity, or superiority claims without evidence;
- link to the architecture spec and development task ledger.

- [ ] **Step 6: Run focused test and verify GREEN**

Run:
```powershell
python -m pytest -q tests/test_repository_contract.py
```

Expected: all repository contract tests PASS.

- [ ] **Step 7: Commit foundation skeleton**

Run:
```powershell
git add .gitignore pyproject.toml LICENSE README.md src tests docs/superpowers
git commit -m "Initialize FlyWireASCA research foundation"
```

Expected: clean commit containing the approved design, plan, and minimal Python foundation.

### Task 2: Add recoverable task-driven development ledger

**Files:**
- Create: `docs/development/tasks/README.md`
- Create: `docs/development/tasks/CURRENT.md`
- Create: `docs/development/tasks/A001-repository-research-foundation.md`
- Create: `docs/development/tasks/ROADMAP.md`
- Create: `tests/test_task_ledger.py`

**Interfaces:**
- Consumes: repository metadata from Task 1.
- Produces: canonical local task ledger contract and A001/A002-A010 roadmap.

- [ ] **Step 1: Write failing task-ledger tests**

Tests must assert:
- `CURRENT.md` names exactly one current task, A001;
- A001 file contains `Status: ACTIVE`, Goal, Scope, Acceptance Criteria, Evidence, Current Action, and Next Action sections;
- ROADMAP lists A001 through A010 exactly once;
- allowed task states are documented as `PLANNED / ACTIVE / BLOCKED / DONE`;
- the task README states Git/GitHub/runtime overrides stale prose.

- [ ] **Step 2: Run focused tests and verify RED**

Run:
```powershell
python -m pytest -q tests/test_task_ledger.py
```

Expected: FAIL because ledger files do not exist.

- [ ] **Step 3: Implement the task ledger**

Create the four documentation files.

A001 acceptance criteria must include:
- public GitHub repo created;
- MIT license present;
- local tests PASS;
- CI PASS on exact pushed commit;
- local/remote synchronization verified;
- A001 evidence report committed;
- A001 status moved to DONE only after all gates pass.

ROADMAP must record:
- A001 Repository & Research Foundation;
- A002 ASCA Architecture Contract;
- A003 Familiarity System;
- A004 Associative Memory & Recall;
- A005 Working Set / Selective Activation;
- A006 Surprise, Uncertainty & Expansion;
- A007 Procedural Memory / Skill Chunking;
- A008 Integrated Cognitive Loop;
- A009 Dense/Non-selective Baseline Comparison;
- A010 ASCA v0.x Qualification.

- [ ] **Step 4: Run task-ledger tests and full regression**

Run:
```powershell
python -m pytest -q tests/test_task_ledger.py
python -m pytest -q
```

Expected: all tests PASS.

- [ ] **Step 5: Commit task system**

Run:
```powershell
git add docs/development/tasks tests/test_task_ledger.py
git commit -m "Add ASCA task-driven development ledger"
```

### Task 3: Add continuous integration and repository qualification checks

**Files:**
- Create: `.github/workflows/ci.yml`
- Create: `scripts/qualify_repository.py`
- Create: `tests/test_repository_qualification.py`

**Interfaces:**
- Consumes: package metadata and task ledger.
- Produces: `python scripts/qualify_repository.py` with exit code 0 only when repository-level invariants pass.

- [ ] **Step 1: Write failing qualification tests**

Tests must exercise `qualify_repository(root: Path) -> list[str]` and assert:
- valid repository returns an empty error list;
- missing LICENSE is reported;
- missing CURRENT task pointer is reported;
- README missing the FlyWireLLM independence boundary is reported;
- a machine-local absolute path inside package source is reported.

- [ ] **Step 2: Run focused tests and verify RED**

Run:
```powershell
python -m pytest -q tests/test_repository_qualification.py
```

Expected: FAIL because the qualifier does not exist.

- [ ] **Step 3: Implement repository qualifier**

Create `scripts/qualify_repository.py` with:
- `qualify_repository(root: Path) -> list[str]`;
- CLI exit 0 when no errors, exit 1 otherwise;
- checks limited to A001 invariants, not cognitive architecture behavior.

- [ ] **Step 4: Add GitHub Actions CI**

Create `.github/workflows/ci.yml` triggered on push and pull_request:
- Python 3.11;
- install `.[dev]`;
- run `python -m pytest -q`;
- run `python scripts/qualify_repository.py`;
- run a whitespace/diff-equivalent source check where supported without adding unnecessary dependencies.

- [ ] **Step 5: Run focused and full local verification**

Run:
```powershell
python -m pytest -q tests/test_repository_qualification.py
python -m pytest -q
python scripts/qualify_repository.py
git diff --check
```

Expected: all commands exit 0.

- [ ] **Step 6: Commit CI and qualification tooling**

Run:
```powershell
git add .github scripts tests/test_repository_qualification.py
git commit -m "Add A001 CI and repository qualification"
```

### Task 4: Create public GitHub repository, activate GitHub task, and synchronize exact commit

**Files:**
- Modify: `docs/development/tasks/A001-repository-research-foundation.md`
- Modify: `docs/development/tasks/CURRENT.md`

**Interfaces:**
- Consumes: clean local `main` commit from Task 3.
- Produces: public `funggier/FlyWireASCA`, `origin` remote, GitHub A001 issue, exact local/remote synchronization.

- [ ] **Step 1: Verify repository does not already exist or inspect it if it does**

Expected: create a new repo only if `funggier/FlyWireASCA` is absent. If it exists unexpectedly, stop mutation and reconcile ownership/history first.

- [ ] **Step 2: Create public GitHub repository**

Run with the authenticated GitHub CLI:
```powershell
gh repo create funggier/FlyWireASCA --public --source . --remote origin --description "Research and engineering for Associative Selective Cognition Architecture (ASCA)"
```

Do not pass `--add-readme`, `--license`, or `--gitignore`; local history is authoritative.

- [ ] **Step 3: Push `main` without force**

Run:
```powershell
git push -u origin main
```

Verify the pushed remote commit equals local HEAD.

- [ ] **Step 4: Create GitHub Issue for A001**

Issue title:
`A001 — Repository & Research Foundation`

Issue body must mirror goal, scope, acceptance criteria, and current status from the local A001 task ledger.

Record the issue number in A001 and CURRENT.md.

- [ ] **Step 5: Commit task metadata update and push**

Run full tests and repository qualifier before commit, then commit the issue-link/status update and push normally.

### Task 5: Exact-commit qualification and A001 closure evidence

**Files:**
- Create: `docs/development/reports/ASCA-20261008-A001-repository-foundation.md`
- Modify: `docs/development/tasks/A001-repository-research-foundation.md`
- Modify: `docs/development/tasks/CURRENT.md`
- Modify: `docs/development/tasks/ROADMAP.md`

**Interfaces:**
- Consumes: synchronized GitHub repository and CI status.
- Produces: exact A001 qualification report and transition pointer to A002.

- [ ] **Step 1: Run fresh local qualification on the exact candidate commit**

Run:
```powershell
python -m pytest -q
python scripts/qualify_repository.py
git diff --check
git status --short --branch
git rev-parse HEAD
```

Expected:
- tests PASS;
- qualifier PASS;
- diff check PASS;
- worktree clean;
- exact candidate SHA recorded.

- [ ] **Step 2: Verify GitHub Actions for that exact SHA**

Expected: CI completed successfully for the same commit, not merely a later/earlier commit.

- [ ] **Step 3: Fetch and verify synchronization**

Run non-destructive fetch and verify:
- `HEAD == origin/main`;
- ahead/behind = `0 / 0`;
- no force push used.

- [ ] **Step 4: Write A001 evidence report**

Report:
- repository URL/name and public visibility;
- local workspace;
- MIT license;
- exact qualified commit SHA;
- local test count/result;
- repository qualification result;
- CI run result for exact SHA;
- local/remote synchronization;
- worktree state;
- GitHub A001 issue;
- no FlyWireLLM files/processes modified;
- claims boundary;
- next task A002.

- [ ] **Step 5: Close A001 task and point CURRENT to A002**

Update:
- A001 `Status: DONE`;
- ROADMAP A001 DONE, A002 PLANNED;
- CURRENT.md states there is no active implementation task until A002 is activated, or points to A002 as the next planned task without falsely marking it ACTIVE.

- [ ] **Step 6: Commit closure evidence**

Run tests/qualifier/diff check again, then commit:
```powershell
git add docs/development
git commit -m "Qualify A001 repository foundation"
```

- [ ] **Step 7: Push, fetch, and verify final A001 exact state**

Expected:
- `HEAD == origin/main`;
- ahead/behind `0 / 0`;
- final worktree clean;
- CI PASS on closure commit or, if the evidence report explicitly separates candidate qualification from documentation-only closure, CI PASS on the closure commit before declaring final GREEN.

- [ ] **Step 8: Update/close GitHub A001 issue only after final GREEN evidence**

Expected: issue records final qualified SHA and evidence summary.

## A001 Non-Goals

A001 must not:
- implement Familiarity Field;
- implement Associative Memory Fabric;
- choose a graph/vector/database backend;
- integrate FlyWireLLM;
- train or download an LLM;
- introduce cloud-service requirements;
- claim ASCA performance or biological fidelity.

## Execution Order

Execute Tasks 1 through 5 sequentially. Do not activate A002 until A001 closure evidence is GREEN and synchronized.
