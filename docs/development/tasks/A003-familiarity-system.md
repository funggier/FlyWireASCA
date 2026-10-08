# A003 — Familiarity System

Status: ACTIVE
GitHub Issue: #3
Branch: research/a003-familiarity-system

## Goal

Implement and qualify the first model-independent familiarity subsystem for
FlyWireASCA using a deterministic exact typed familiarity baseline.

## Scope

In scope:

- immutable familiarity trace/result/cost records;
- conservative Unicode normalization;
- exact typed familiarity index;
- exhaustive semantic-equivalent baseline;
- deterministic controlled benchmark;
- logical cost accounting;
- exact branch/main CI qualification.

Out of scope:

- fuzzy or approximate matching;
- embeddings or neural familiarity;
- associative recall;
- identity resolution;
- working-set routing;
- surprise-driven expansion;
- FlyWireLLM integration or training.

## Phases

- Records and normalization: DONE.
- Exact/exhaustive engines: DONE.
- Benchmark and CI qualification: DONE.
- Exact qualification and closure: ACTIVE.

## Acceptance Criteria

- [ ] Familiarity records are immutable and validated.
- [ ] Normalization is NFKC + whitespace collapse + casefold.
- [ ] CueKind remains part of the familiarity key.
- [ ] Exact and exhaustive engines are semantically equivalent.
- [ ] Same-name ambiguity preserves all candidate regions without identity inference.
- [ ] Exact valid lookup reports one logical probe.
- [ ] Exhaustive lookup reports scanning the full trace set.
- [ ] Controlled fixture classification accuracy is 1.0.
- [ ] False familiarity/unfamiliar counts are 0 on the controlled fixture.
- [ ] Benchmark qualification is an explicit GitHub Actions gate.
- [ ] Full local regression, architecture audit, repository qualifier, and diff check pass.
- [ ] Exact branch and final main CI pass.
- [ ] FlyWireLLM training repository/process remain untouched.

## Evidence

A003 design spec:

`docs/superpowers/specs/2026-10-08-a003-familiarity-system-design.md`

A003 implementation plan:

`docs/superpowers/plans/2026-10-08-a003-familiarity-system.md`

Baseline before implementation:

- base commit: `33dfeba3b88631acd772c39f5208be8f70176f28`;
- baseline full tests: `42 passed`;
- branch: `research/a003-familiarity-system`;
- worktree started clean.

Further evidence is appended only after fresh verification.

## Current Action

Run Task 4 exact local qualification and publish the A003 branch for exact CI.

## Next Action

After exact branch CI is GREEN, write closure evidence, transition A004 to PLANNED, qualify the closure commit, then fast-forward main.
