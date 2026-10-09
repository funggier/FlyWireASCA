# A008 — Procedural Memory / Skill Chunking

Status: DONE
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
- Deterministic benchmark / qualification CLI / CI: DONE.
- Exact branch qualification / report / closure transition: DONE.
- Whole-branch review / integration: ACTIVE.

## Acceptance Criteria

- [x] Immutable models/library and deterministic flattening validated.
- [x] Direct/indirect recursion and depth >8 fail closed.
- [x] CALL completion contracts validated by kind/payload/matcher.
- [x] Exact verifier ignores executor-supplied expected_match.
- [x] Deterministic simulator supports state, probes, and failure injection.
- [x] FLAT/CHUNKED success semantics equivalent on declared fixtures.
- [x] CHUNKED reduces root-visible dispatches in declared chunking fixtures.
- [x] CHUNKED localizes checked primitive failure exactly.
- [x] BLIND_CHUNKED demonstrates coarser CALL-boundary localization.
- [x] No primitive executes after checked interruption.
- [x] No automatic retry/recovery occurs.
- [x] Deterministic qualification runs in GitHub CI.
- [x] Valid primary outcome is exactly SUPPORTED/MIXED/NOT_SUPPORTED.
- [x] No real tool/model/Ollama/graph dependency is introduced.
- [x] FlyWireLLM remains paused/untouched.
- [x] Whole-branch review Critical/Important findings resolved.
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

Post-review behavior candidate:

`b0ad2f1abed08683ea8218861c97f3c2d47384d3`

Post-review exact branch CI:

`37959983484` — success

Merged main behavior/evidence SHA:

`0142973814fb67dd28a54fa454f25fa88f7dfcd9`

First final-main CI: DONE

- exact CI: `37961029994` — success;
- merged-main local suite: `383 passed`;
- deterministic A008 outcome: `SUPPORTED`.

Whole-branch review resolved three Important findings: max_call_depth cap
enforcement, invalid-library reuse-metric contamination, and impossible
count/reuse qualification payload relationships. The required post-review
deterministic qualification remained `SUPPORTED` with fixture fingerprint
unchanged and FLAT / CHUNKED root-visible dispatches 13 / 8.

Exact branch qualification evidence:


- candidate SHA: `0bfee1dfc424934ed783150f6c4d86140c6502d2`;
- branch CI: `37956221852` — success;
- full suite: `370 passed`;
- fixture fingerprint:
  `f52fbd4ab018386ff3cbfb62a68cc44a4b40e54ec4fd9a3b2e885dd2c5663fc6`;
- primary outcome: `SUPPORTED`;
- FLAT / CHUNKED root-visible dispatches: 13 / 8;
- maximum compression ratio: 2.0;
- shared `heat-water` parent reuse count: 2;
- checked failure localization FLAT/CHUNKED/BLIND: 1/1, 1/1, 1/1.

## Current Action

A008 review, post-review qualification, fast-forward main integration,
merged-main local gates, and first final-main CI are GREEN. Prepare the
main integration-evidence commit and exact CI.

## Next Action

A009 — Integrated Cognitive Loop remains PLANNED with no issue. Do not start it
until A008 integration-evidence CI, final ledger CI, Issue #8 closure, and synchronization are GREEN.

A009 — Integrated Cognitive Loop remains PLANNED with no issue.