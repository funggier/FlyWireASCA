# A001 — Repository & Research Foundation

Status: ACTIVE
GitHub Issue: pending creation

## Goal

Create the independent public `funggier/FlyWireASCA` repository and a
reproducible engineering/research foundation for later ASCA work.

## Scope

In scope:

- MIT-licensed Python package foundation;
- project README and claims boundary;
- task-driven/evidence-driven workflow;
- local tests and repository qualification;
- GitHub Actions CI;
- public GitHub repository and issue tracking;
- exact-commit evidence and synchronization.

Out of scope:

- Familiarity Field implementation;
- associative memory implementation;
- database/backend selection;
- FlyWireLLM integration;
- model training;
- ASCA performance claims.

## Phases

- Foundation skeleton: DONE locally at initial commit.
- Task ledger: ACTIVE.
- CI and repository qualifier: PLANNED.
- GitHub publication/synchronization: PLANNED.
- Exact qualification and closure evidence: PLANNED.

## Acceptance Criteria

- [ ] Public GitHub repository `funggier/FlyWireASCA` exists.
- [x] MIT License exists locally.
- [ ] Full local test suite passes on final candidate.
- [ ] Repository qualifier passes.
- [ ] GitHub Actions CI passes on the exact qualified commit.
- [ ] Local and remote `main` are synchronized 0/0.
- [ ] A001 evidence report is committed.
- [ ] Final worktree is clean.
- [ ] No FlyWireLLM training file or process was modified by A001.

## Evidence

Initial local foundation commit:

`b7e2df48b8f0d376a81e01da015aab896cf63529`

Repository-contract test at that checkpoint:

`4 passed`

Further evidence is appended only after fresh verification.

## Current Action

Implement and verify the persistent task ledger.

## Next Action

Add repository qualification tooling and CI under TDD, then create the public
GitHub repository only after local qualification is green.
