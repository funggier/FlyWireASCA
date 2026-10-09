# A004 — Local Model Adapter & Qwen3.5:4B Baseline

Status: DONE
GitHub Issue: #4
Branch: research/a004-qwen-adapter

## Goal

Add a model-agnostic model adapter boundary to FlyWireASCA, implement a local
Ollama adapter, and qualify `qwen3.5:4b` as the first reproducible Qwen-only
model-under-test baseline.

## Scope

In scope:

- backend-neutral model request/response/descriptor contracts;
- `ModelAdapter` protocol and adapter error model;
- local Ollama JSON HTTP adapter;
- strict Qwen tag/digest qualification;
- thinking-off text-only Qwen baseline;
- portable CI with fake transport/model tests only;
- local physical Qwen qualification;
- roadmap migration from future A004-A010 to A005-A011;
- exact branch/main evidence.

Out of scope:

- Qwen training/fine-tuning or weight changes;
- tools or vision;
- thinking-enabled qualification;
- ASCA familiarity/recall integration into prompts;
- FlyWireLLM training restart;
- ASCA improvement claims;
- FLOP/energy claims.

## Phases

- Generic model contracts and roadmap migration: DONE.
- Ollama transport and adapter: DONE.
- Qwen-only baseline and portable CI: DONE.
- Local physical Qwen qualification: DONE.
- Exact qualification and closure: DONE.

## Acceptance Criteria

- [x] Generic model contracts are independent from Ollama/Qwen.
- [x] Ollama adapter unit tests run with fake transport.
- [x] Thinking-off requests explicitly send JSON boolean `think: false`.
- [x] Strict digest mismatch fails closed.
- [x] Portable GitHub CI does not download or run Qwen/Ollama.
- [x] Local physical qualification passes for pinned `qwen3.5:4b` digest.
- [x] Six-case Thai/English controlled Qwen-only baseline passes.
- [x] Token/timing/model metadata is captured without FLOP/energy overclaim.
- [x] Full local regression, architecture audit, repository qualifier, and A003 benchmark remain GREEN.
- [x] Exact branch candidate CI passes; final main CI remains an external integration gate.
- [x] FlyWireLLM remains paused and untouched.
- [x] Final main synchronization/cleanliness remains an external integration gate before Issue #4 closure.

## Evidence

A004 design spec:

`docs/superpowers/specs/2026-10-09-a004-qwen-adapter-design.md`

A004 implementation plan:

`docs/superpowers/plans/2026-10-09-a004-qwen-adapter.md`

Baseline before implementation:

- base main: `1079e8eb6c11027e83de2e96547e1ac094fc9e16`;
- branch: `research/a004-qwen-adapter`;
- baseline full tests: `68 passed`;
- worktree: clean;
- GitHub Issue: #4;
- observed Ollama runtime: `0.32.15`;
- target model tag: `qwen3.5:4b`;
- target full digest:
  `2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd`.

Physical qualification on implementation commit `3b8cdbb03db8cd959ce52639316a36e978d1e8f4`:

- local qualification: PASS;
- Ollama runtime: `0.32.15`;
- model: `qwen3.5:4b`;
- full digest: `2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd`;
- architecture: `qwen35`;
- exact parameter count: `4,659,865,088`;
- quantization: `Q4_K_M`;
- generation profile: thinking off, tools off, vision off, context 8192, max output 256, temperature 0, seed 0;
- controlled Qwen-only baseline: 6/6 passed, pass rate 1.0;
- prompt tokens total: 293;
- generated tokens total: 16;
- total duration: 2,509,991,400 ns;
- prompt-eval duration total: 1,739,271,000 ns;
- generation eval duration total: 586,869,000 ns;
- load-duration aggregate is intentionally `None` because Ollama omitted that field on some individual responses;
- local evidence JSON remains scratch-only and is not committed.

## Current Action

A004 implementation, physical qualification, and branch-candidate evidence are complete in the closure candidate.

## Next Action

Require exact closure-branch CI, perform whole-branch review/fix pass, fast-forward `main`, require exact main CI and sync 0/0, then close Issue #4. A005 remains PLANNED.
