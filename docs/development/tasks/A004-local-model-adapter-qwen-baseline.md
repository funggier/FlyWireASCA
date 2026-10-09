# A004 — Local Model Adapter & Qwen3.5:4B Baseline

Status: ACTIVE
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
- Qwen-only baseline and portable CI: ACTIVE.
- Local physical Qwen qualification: PLANNED.
- Exact qualification and closure: PLANNED.

## Acceptance Criteria

- [ ] Generic model contracts are independent from Ollama/Qwen.
- [ ] Ollama adapter unit tests run with fake transport.
- [ ] Thinking-off requests explicitly send JSON boolean `think: false`.
- [ ] Strict digest mismatch fails closed.
- [ ] Portable GitHub CI does not download or run Qwen/Ollama.
- [ ] Local physical qualification passes for pinned `qwen3.5:4b` digest.
- [ ] Six-case Thai/English controlled Qwen-only baseline passes.
- [ ] Token/timing/model metadata is captured without FLOP/energy overclaim.
- [ ] Full local regression, architecture audit, repository qualifier, and A003 benchmark remain GREEN.
- [ ] Exact branch and final main CI pass.
- [ ] FlyWireLLM remains paused and untouched.
- [ ] Final main synchronizes 0/0 and is clean.

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

Further evidence is appended only after fresh verification.

## Current Action

Implement Task 3 Qwen-only controlled baseline scoring and portable CI coverage under TDD.

## Next Action

After portable baseline software is GREEN and committed, implement the local physical Qwen qualification runner.
