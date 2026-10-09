# A005 — Semantic Vector Memory Retrieval

Status: ACTIVE
GitHub Issue: #5
Branch: research/a005-vector-memory

## Goal

Build and qualify a safe multilingual Vector + Metadata memory retriever, then
use measured evidence to decide whether a typed graph is actually necessary.

## Scope

In scope:

- backend-neutral embedding contracts and adapter boundary;
- local Ollama embedding adapter;
- exact in-memory cosine retrieval;
- explicit memory metadata filters;
- portable fake-vector benchmark;
- separate threshold calibration and qualification fixtures;
- physical `qwen3-embedding:0.6b` qualification;
- evidence-based graph decision gate.

Out of scope:

- typed graph construction/traversal;
- multi-hop relation reasoning;
- ANN/vector-database acceleration;
- Qwen3.5:4b generative reranking;
- vector similarity as identity/truth;
- FlyWireLLM restart/training.

A typed graph is deferred until A005 evidence justifies it.

## Phases

- Generic embedding contracts and A005 activation: DONE.
- Ollama embedding adapter: DONE.
- Exact Vector + Metadata index: DONE.
- Portable benchmark/calibration/decision evaluator: ACTIVE.
- Local physical embedding qualification: PLANNED.
- Exact qualification, decision report, and closure: PLANNED.

## Acceptance Criteria

- [ ] Generic embedding contracts are backend-neutral.
- [ ] Zero/non-finite/wrong-dimension vectors fail closed.
- [ ] Ollama embedding adapter is portable-testable through fake transport.
- [ ] Exact cosine index is deterministic.
- [ ] Metadata filters run before scoring.
- [ ] Similarity remains separate from proposition confidence.
- [ ] Same-name ambiguity is preserved unless explicit metadata constrains it.
- [ ] Portable calibration and qualification fixtures are disjoint.
- [ ] Physical calibration and physical qualification fixtures are disjoint.
- [ ] qwen3-embedding:0.6b physical qualification passes or records a valid negative result.
- [ ] Full embedding model digest and frozen physical threshold are recorded.
- [ ] A003 and A004 qualification evidence remain intact.
- [ ] FlyWireLLM remains paused and untouched.
- [ ] Exact branch/final-main CI pass.
- [ ] Main synchronizes 0/0 and is clean.
- [ ] Closure records exactly one graph decision outcome.

## Decision Gate

A005 closure must record exactly one:

- `VECTOR_SUFFICIENT`
- `VECTOR_NEEDS_INDEX_OR_METADATA`
- `GRAPH_JUSTIFIED`

No graph task is created automatically.

## Evidence

Approved A005 spec:

`docs/superpowers/specs/2026-10-09-a005-vector-memory-design.md`

Approved A005 implementation plan:

`docs/superpowers/plans/2026-10-09-a005-vector-memory.md`

Baseline:

- base main: `230280bf633d20631a0da38d55bdfd7716758734`;
- branch: `research/a005-vector-memory`;
- baseline tests: 107 passed;
- GitHub Issue: #5;
- worktree initially clean.

## Current Action

Implement Task 4 portable benchmark, separate threshold calibration/qualification fixtures, and graph-decision evaluator under TDD.

## Next Action

After portable benchmark qualification is GREEN and committed, implement the local physical embedding/vector-memory qualification runner.
