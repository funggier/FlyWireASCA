# A014 — Structural Need Inference / Query Intent Routing Gate

Status: ACTIVE
GitHub Issue: #18
Branch: research/a014-structural-need-inference
Activation base: 4549951e3d2dbdbd877559d6b06ad501999e71f6

Approved design:
`docs/superpowers/specs/2026-10-11-a014-structural-need-inference-design.md`

Approved implementation plan:
`docs/superpowers/plans/2026-10-11-a014-structural-need-inference.md`

## Goal

Determine whether ordinary English and Thai query text can be converted into a
target-free A013-compatible `StructuralNeed` with sufficient downstream recall
correctness and routing integrity, and compare rule-only, model-only, and
hybrid rule-then-model routing.

## Scope

- `RULE_ONLY`, `MODEL_ONLY`, and `HYBRID_RULE_THEN_MODEL`;
- bilingual English/Thai frozen routing workload;
- strict target-free runtime request/result contracts;
- conservative deterministic routing cues;
- strict model JSON routing with fail-closed validation;
- downstream evaluation through the existing A013 `SIGNAL_GATED_RELATION` path;
- portable engineering/control-flow qualification;
- mandatory local physical qualification with pinned `qwen3.5:4b`;
- physical evidence bound to exact source, fixture, prompt, and model identity.

## Non-scope

- expected targets, expected relation labels, benchmark labels, graph contents,
  retrieval results, or post-hoc correctness in runtime/model routing;
- modifying A011-protected cognitive source blobs;
- changing A005-A013 historical conclusions;
- modifying the frozen A009 integrated loop;
- persistent graph database;
- autonomous relation learning;
- FlyWireLLM;
- release/tag/version promotion;
- automatic activation of A015.

## Architecture Decisions

A014 may conclude exactly one of:

- `HYBRID_STRUCTURAL_ROUTING_JUSTIFIED`
- `RULE_ROUTING_SUFFICIENT`
- `MODEL_ROUTING_PREFERRED`
- `STRUCTURAL_ROUTING_NOT_SUPPORTED`
- `MIXED`

A valid negative or mixed research result is not an engineering-process failure.

## Acceptance Criteria

- [x] User explicitly approved the A014 design.
- [x] User explicitly approved the A014 implementation plan.
- [x] GitHub Issue #18 exists.
- [x] Isolated branch/worktree exists from the exact A013 closure base.
- [x] Pre-A014 baseline: 1034 tests passed.
- [ ] A014 lifecycle metadata committed ACTIVE.
- [ ] Frozen bilingual benchmark committed before router tuning.
- [ ] Runtime routing APIs contain no target/expected-answer oracle.
- [ ] Rule, model, and hybrid policies implemented with TDD.
- [ ] Downstream A013 evaluation uses inferred `StructuralNeed` only.
- [ ] Portable qualification passes.
- [ ] Mandatory pinned-model physical qualification completes.
- [ ] Physical evidence is source/fixture/prompt/model bound.
- [ ] Exact feature CI is GREEN.
- [ ] PR CI and normal main integration CI are GREEN.
- [ ] Closure metadata receives exact main CI GREEN.
- [ ] Issue #18 closes only after exact closure evidence.
- [ ] FlyWireLLM remains untouched.
- [ ] A015 remains inactive.

## Evidence

Activation evidence will accumulate here as Task 1 onward completes.

Initial anchors:

- activation base: `4549951e3d2dbdbd877559d6b06ad501999e71f6`;
- design commit: `3361a2d8ffef34b235e58d141f5b994817b49ed7`;
- plan commit: `f58ea5fd89af5339162cd5d1489b438ded2a8c42`;
- GitHub Issue: #18;
- baseline: `1034 passed in 96.22s`.

## Current Action

Activate lifecycle metadata, then freeze the bilingual benchmark and proceed
task-by-task under the approved TDD plan.

## Next Action

Task 2 defines target-free structural-routing contracts. Task 3 freezes the
bilingual benchmark before any routing-policy tuning.
