# A008 — Procedural Memory / Skill Chunking

Status: ACTIVE
GitHub Issue: #8
Branch: research/a008-procedural-memory

## Goal

Build deterministic reusable hierarchical procedural memory and qualify whether
CHUNKED execution reduces root-controller-visible dispatches while preserving
primitive correctness and exact failure localization relative to FLAT.

## Scope

Primary architecture: hierarchical CHUNKED procedures with explicit step-level
checkpoints (architecture option 1).

Controls:

- FLAT;
- CHUNKED;
- BLIND_CHUNKED.

A008 uses exact (`EXACT`) outcome matching, forbids recursion, uses
`max_call_depth = 8`, and performs zero automatic retry/recovery.

A008 does not execute a real tool, OS command, API, LConnect, or BConnect action.
It does not use `qwen3.5:4b`, Ollama, embeddings, or a typed/semantic graph.
FlyWireLLM remains paused and untouched.

## Phases

- Models / ProcedureLibrary / flattening / activation: DONE.
- Exact verifier / deterministic simulator: DONE.
- FLAT / CHUNKED / BLIND_CHUNKED runner: DONE.
- Deterministic benchmark / qualification CLI / CI: ACTIVE.
- Exact branch qualification / report / closure transition: PLANNED.
- Whole-branch review / integration: PLANNED.

## Acceptance Criteria

- [ ] Immutable models/library and deterministic flattening validated.
- [ ] Direct/indirect recursion and depth >8 fail closed.
- [ ] CALL completion contracts validated by kind/payload/matcher.
- [ ] Exact verifier ignores executor-supplied expected_match.
- [ ] Deterministic simulator supports state, probes, and failure injection.
- [ ] FLAT/CHUNKED success semantics equivalent on declared fixtures.
- [ ] CHUNKED reduces root-visible dispatches in declared chunking fixtures.
- [ ] CHUNKED localizes checked primitive failure exactly.
- [ ] BLIND_CHUNKED demonstrates coarser CALL-boundary localization.
- [ ] No primitive executes after checked interruption.
- [ ] No automatic retry/recovery occurs.
- [ ] Deterministic qualification runs in GitHub CI.
- [ ] Valid primary outcome is exactly SUPPORTED/MIXED/NOT_SUPPORTED.
- [ ] No real tool/model/Ollama/graph dependency is introduced.
- [ ] FlyWireLLM remains paused/untouched.
- [ ] Exact branch/review/final-main CI and synchronization gates pass.

## Evidence

Approved design:

`docs/superpowers/specs/2026-10-09-a008-procedural-memory-design.md`

Approved Native implementation plan:

`docs/superpowers/plans/2026-10-09-a008-procedural-memory.md`

Activation base:

- main: `d5342fbb74f7dc49e5fcc5472847495ba1212434`;
- issue: #8;
- branch: `research/a008-procedural-memory`;
- A007 historical outcome: `SUPPORTED`.

## Current Action

Implement Task 4 frozen deterministic benchmark, qualification CLI, and CI
gate under TDD.

## Next Action

After deterministic qualification is GREEN, write exact branch evidence and
A008 closure report.

A009 — Integrated Cognitive Loop remains PLANNED with no issue.
