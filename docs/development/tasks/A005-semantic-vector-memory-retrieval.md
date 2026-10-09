# A005 — Semantic Vector Memory Retrieval

Status: DONE
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
- Portable benchmark/calibration/decision evaluator: DONE.
- Local physical embedding qualification: DONE.
- Exact qualification, decision report, and closure: DONE.

## Acceptance Criteria

- [x] Generic embedding contracts are backend-neutral.
- [x] Zero/non-finite/wrong-dimension vectors fail closed.
- [x] Ollama embedding adapter is portable-testable through fake transport.
- [x] Exact cosine index is deterministic.
- [x] Metadata filters run before scoring.
- [x] Similarity remains separate from proposition confidence.
- [x] Same-name ambiguity is preserved unless explicit metadata constrains it.
- [x] Portable calibration and qualification fixtures are disjoint.
- [x] Physical calibration and physical qualification fixtures are disjoint.
- [x] qwen3-embedding:0.6b physical qualification passes or records a valid negative result.
- [x] Full embedding model digest and frozen physical threshold are recorded.
- [x] A003 and A004 qualification evidence remain intact.
- [x] FlyWireLLM remains paused and untouched.
- [x] Exact branch candidate CI passes; final-main CI remains an external integration gate.
- [x] Final main synchronization/cleanliness remains an external integration gate before Issue #5 closure.
- [x] Closure records exactly one controlled-fixture graph decision outcome.

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

Portable benchmark evidence:

- full suite after Task 4: 144 passed;
- portable calibration threshold: `0.5`;
- threshold origin: `portable_fake_geometry_only`;
- this threshold tests calibration logic only and is **not** the physical Qwen threshold;
- portable qualification includes 12 cases and 256 distractors;
- graph decision evaluator exercises all three outcomes synthetically.

Physical development-calibration evidence:

- Ollama runtime: `0.32.15`;
- embedding model: `qwen3-embedding:0.6b`;
- full digest: `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`;
- architecture: `qwen3`;
- exact parameter count: `595,776,512`;
- reported parameter size: `595.78M`;
- quantization: `Q8_0`;
- embedding dimension: `1024`;
- vector-health probes: 16/16 finite, nonzero, unit-normalized;
- physical development threshold: `0.5037018224299838`;
- threshold origin: `physical_development_fixture_v1`;
- calibration case IDs: `physical-cal-bike`, `physical-cal-cat`;
- final physical qualification fixture is separate and has now been run with the frozen threshold.

Physical final-qualification evidence:

- implementation/pin commit: `7dfd4b0f477128007eae4c14c7e8948d610c18f3`;
- experiment validity: PASS;
- retrieval qualification: PASS;
- initial physical qualification: 6/6 passed on pin commit `7dfd4b0f477128007eae4c14c7e8948d610c18f3`;
- final review identified missing physical no-hit and relation/multi-memory challenge coverage;
- reviewed implementation: `e5536d983b45e241dda2e9d740cdc792adbd9ae7`;
- post-review physical qualification: **8/8 passed** with the same frozen threshold;
- Recall@1: `1.0` on cases where Recall@1 is declared;
- Recall@K: `1.0`;
- mean reciprocal rank: `1.0`;
- measured physical no-hit correctness: `1.0`;
- metadata-filter correctness: `1.0`;
- false retrieval count: `0`;
- ambiguity failure count: `0`;
- relation-semantic failure count: `0`;
- scalability warning count: `0` on the declared eight-document fixture;
- embedding request count: `9`;
- embedding input count: `16`;
- stored memory count: `8`;
- vector-scored total: `57`;
- vector health: 16/16 finite, nonzero, dimension 1024, unit-normalized;
- post-review branch CI run `37907918470`: success;
- graph decision: `VECTOR_SUFFICIENT` for A005 **retrieval scope**.

The reviewed physical fixture now exercises both no-hit behavior and a
multi-memory relation-evidence challenge. The relation challenge proves that
both required memories can be retrieved; it does not claim that vector
similarity performs downstream relational inference.

## Current Action

A005 implementation, physical qualification, exact candidate CI, and initial controlled-fixture decision evidence are complete in the closure candidate.

## Next Action

Require exact closure-branch CI, perform whole-branch methodological/code review and one fix pass for Critical/Important findings, then fast-forward `main`, require exact main CI and sync 0/0, and close Issue #5. A006 remains PLANNED.
