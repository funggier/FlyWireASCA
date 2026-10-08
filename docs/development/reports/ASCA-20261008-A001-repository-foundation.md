# FlyWireASCA A001 Repository Foundation Qualification

Date: 2026-10-08
Task: A001 — Repository & Research Foundation
GitHub Issue: #1

## Decision

**A001 CLOSURE CANDIDATE GREEN**

The engineering foundation is qualified on exact implementation commit
`08868b099da4ae2bd31154201dd3ac9d0568fe5d`. The task transition and this
report are a documentation closure layer on top of that exact-qualified
implementation. The commit containing this report must also pass CI before
A001 is externally claimed final GREEN.

Closure-transition local verification before committing this report:

- `python -m pytest -q`: **15 passed**
- `python scripts/qualify_repository.py`: **repository_qualification=PASS**
- `git diff --check`: PASS

## Repository

- GitHub: `funggier/FlyWireASCA`
- visibility: **PUBLIC**
- local workspace: `T:\Space\Projects\ProjectsAI\FlyWireASCA`
- default branch: `main`
- source license: MIT
- GitHub Issue: #1

## Exact implementation qualification

Qualified implementation commit:

`08868b099da4ae2bd31154201dd3ac9d0568fe5d`

Fresh local evidence on that exact commit:

- `python -m pytest -q`: **14 passed**
- `python scripts/qualify_repository.py`: **repository_qualification=PASS**
- `git diff --check HEAD^ HEAD`: PASS
- worktree: clean
- local `main` vs exact remote `refs/heads/main`: ahead 0 / behind 0
- exact remote SHA matched local HEAD

GitHub Actions exact-commit evidence:

- workflow: CI
- run id: `37759237750`
- exact head SHA:
  `08868b099da4ae2bd31154201dd3ac9d0568fe5d`
- conclusion: **success**
- event: push

## CI failure found and corrected

The preceding commit `4a836ed01bc2106cbc97ec662a949302acd76e1c`
failed only at the CI whitespace step.

Root cause:

- `actions/checkout` used its default shallow history;
- only HEAD was fetched;
- the workflow called `git diff --check HEAD^ HEAD`;
- `HEAD^` therefore did not exist inside the runner checkout.

The failure was reproduced with a regression test,
`test_ci_fetches_parent_commit_for_diff_check`, which failed before the fix.
The workflow now pins `fetch-depth: 2`; the regression test passed, the full
suite passed 14/14, and exact GitHub Actions run `37759237750` passed.

## Closure-report whitespace correction

The first closure-report commit
`e0b5f5a5e4a424f7d0daca5fd1690f2561c6c75f` failed only the CI whitespace
step because two Markdown header lines intentionally used two trailing spaces
for hard line breaks. The repository CI contract rejects trailing whitespace,
so the report was normalized instead of weakening CI. Regression test
`test_a001_closure_report_has_no_trailing_whitespace` reproduced the two bad
lines before the fix.

## A001 deliverables

Qualified foundation includes:

- Python package `flywire_asca`;
- `pyproject.toml` with Python >=3.11 and MIT metadata;
- standard MIT `LICENSE`;
- README with ASCA scope and claims boundary;
- architecture design spec;
- A001 implementation plan;
- task ledger with `CURRENT.md` and A001-A010 roadmap;
- repository qualifier;
- GitHub Actions CI;
- public GitHub repository;
- GitHub Issue #1.

No Familiarity, associative-memory, working-set, surprise, procedural-memory,
or other cognitive algorithm is implemented by A001.

## FlyWireLLM isolation evidence

A001 did not modify the active FlyWireLLM training repository or process.

At closure evidence capture:

- FlyWireLLM HEAD:
  `46761af6112a9b7ab0376b940c9235670e8d3355`
- branch: `research/l004-base50m-pretraining`
- worktree: clean
- ahead/behind: 0/0
- active production session:
  `proc-1791449373566-361`
- session remained running;
- live training had progressed through optimizer step 497;
- stderr was empty.

The only requested GitHub-side change to FlyWireLLM was repository visibility:
`funggier/FlyWireLLM` is now **PUBLIC**. Before changing visibility, current
tracked files, Git history, and historical large blobs were scanned for common
secret patterns; the only secret-like strings found were deliberate fake
`api_key=abcdefghijklmnopqrstuvwxyz012345` screening fixtures in tests. No
large tracked/history blobs were found. Existing release assets were also
reviewed; v0.2.0 contains release/document ZIPs and checksums, while v0.1.0
contains the blank random smoke checkpoint and release/document assets.

## Claims boundary

A001 does not claim:

- human cognitive equivalence;
- biological fidelity;
- consciousness or AGI;
- superior efficiency to dense LLMs;
- production safety;
- validated ASCA cognitive performance.

Those require later controlled experiments.

## Next milestone

A002 — ASCA Architecture Contract.

A002 remains **PLANNED**. It is not activated by closing A001.
