# A003 — Familiarity System

Status: DONE
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
- Exact qualification and closure: DONE.

## Acceptance Criteria

- [x] Familiarity records are immutable and validated.
- [x] Normalization is NFKC + whitespace collapse + casefold.
- [x] CueKind remains part of the familiarity key.
- [x] Exact and exhaustive engines are semantically equivalent.
- [x] Same-name ambiguity preserves all candidate regions without identity inference.
- [x] Exact valid lookup reports one logical probe.
- [x] Exhaustive lookup reports scanning the full trace set.
- [x] Controlled fixture classification accuracy is 1.0.
- [x] False familiarity/unfamiliar counts are 0 on the controlled fixture.
- [x] Benchmark qualification is an explicit GitHub Actions gate.
- [x] Full local regression, architecture audit, repository qualifier, and diff check pass.
- [x] Exact branch candidate CI passes; closure/main CI remain external closure gates.
- [x] FlyWireLLM training repository/process remain untouched.

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

Exact implementation candidate: `6c9534cb743123c60184e9e00244f836c3e901e1`

- full pytest: 66 passed;
- benchmark qualification: PASS;
- classification accuracy: 1.0;
- exact/exhaustive semantic mismatch count: 0;
- initial branch CI run `37803237340`: success on exact candidate;
- whole-branch review fix commit: `3a70afa07475d86ea523d0dfe1433c2006bb683f`;
- post-review full pytest: 68 passed;
- post-review branch CI run `37804356820`: success;
- closure report: `docs/development/reports/ASCA-20261008-A003-familiarity-system.md`.

## Current Action

A003 implementation and candidate evidence are complete in the closure candidate.

## Next Action

Require exact closure-branch CI, fast-forward `main`, verify merged result and exact main CI, then close Issue #3. A004 remains PLANNED.
