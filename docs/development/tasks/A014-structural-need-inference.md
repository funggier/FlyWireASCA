# A014 — Structural Need Inference / Query Intent Routing Gate

Status: DONE
GitHub Issue: #18
Historical branch: research/a014-structural-need-inference
Activation base: 4549951e3d2dbdbd877559d6b06ad501999e71f6

Approved design:
`docs/superpowers/specs/2026-10-11-a014-structural-need-inference-design.md`

Approved implementation plan:
`docs/superpowers/plans/2026-10-11-a014-structural-need-inference.md`

## Goal

Determine whether ordinary English and Thai query text can be converted into a
target-free A013-compatible `StructuralNeed` with sufficient downstream recall
correctness and routing integrity, comparing rule-only, model-only, and hybrid
rule-then-model routing.

## Scope

- `RULE_ONLY`, `MODEL_ONLY`, and `HYBRID_RULE_THEN_MODEL`;
- frozen bilingual English/Thai routing workload;
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
- production-ready end-to-end natural-language agent execution;
- FlyWireLLM;
- release/tag/version promotion;
- automatic activation of A015.

## Architecture Decision

Frozen physical decision:

`HYBRID_STRUCTURAL_ROUTING_JUSTIFIED`

Physical 32-case result:

- `RULE_ONLY`: 27/32 downstream success, 0 false activations, 9 missed
  activations, 0 model calls;
- `MODEL_ONLY`: 32/32 downstream success, 2 false activations, 0 missed
  activations, 32 model calls;
- `HYBRID_RULE_THEN_MODEL`: 32/32 downstream success, 0 false activations,
  0 missed activations, 9 model calls.

The hybrid policy therefore preserved the model-only downstream success while
removing the two model-only false activations and reducing model invocations
from 32 to 9.

## Acceptance Criteria

- [x] User explicitly approved the A014 design.
- [x] User explicitly approved the A014 implementation plan.
- [x] GitHub Issue #18 exists.
- [x] Isolated branch/worktree was created from the exact A013 closure base.
- [x] Pre-A014 baseline: 1034 tests passed.
- [x] A014 lifecycle metadata was committed ACTIVE before implementation.
- [x] Frozen bilingual benchmark was committed before router tuning.
- [x] Runtime routing APIs contain no target/expected-answer oracle.
- [x] Rule, model, and hybrid policies were implemented with TDD.
- [x] Downstream A013 evaluation uses inferred `StructuralNeed` only.
- [x] Portable qualification passes.
- [x] Mandatory pinned-model physical qualification completed.
- [x] Physical evidence is source/fixture/prompt/model bound.
- [x] Exact feature CI is GREEN.
- [x] User-selected local-main integration completed and exact main CI is GREEN.
- [x] Closure metadata records the absence of PR/PR-CI because PR integration
  was not selected.
- [x] FlyWireLLM remained untouched.
- [x] A015 remains inactive.

## Evidence

- activation base:
  `4549951e3d2dbdbd877559d6b06ad501999e71f6`;
- design commit:
  `3361a2d8ffef34b235e58d141f5b994817b49ed7`;
- plan commit:
  `f58ea5fd89af5339162cd5d1489b438ded2a8c42`;
- implementation/source-bound physical SHA:
  `e0e57e914b63f30bf6c360a49d56ebfbc1a22f83`;
- final feature head:
  `37e1cf36078d525123ea64d99134b701f79a4653`;
- exact feature CI:
  run `38116882068`, GREEN;
- feature A014 artifact digest:
  `sha256:1f8eb913b1f04b6fe0c522affe9135be02d8c904dc9ca6eaacf1a798e19cbd2a`;
- user-selected local fast-forward integration to main:
  `37e1cf36078d525123ea64d99134b701f79a4653`;
- exact integration/main CI:
  run `38152301384`, GREEN;
- integration A014 artifact digest:
  `sha256:d37c4cfa6ab28d2f2ff3d5f3f25c6387245ec322b923578d22be2bdaa6a3f604`;
- merged-main local verification:
  `1162 passed in 98.61s`;
- physical decision:
  `HYBRID_STRUCTURAL_ROUTING_JUSTIFIED`;
- physical evidence SHA256:
  `a7fd02566917f3051a4e40881bce976933ea6e604a7558d510a8720ce89f3dcf`;
- committed evidence file SHA256:
  `53d5afe65027e0fc992cdd379debef263911fd9e93bb9f977500e755c1ec9d47`;
- frozen fixture SHA256:
  `c100f828265063c369d535f85db8166cbeaaba26943fbb6d276a24dc46018eca`;
- prompt fingerprint:
  `b48568801f32579e36f2e633b740a3d6cc0a276ffa6dcaa05d035f790b5f6a8d`;
- source manifest fingerprint:
  `a423296415b4e59ac2933c7c40900e3f9e74d832b554564b6b9ef66b7fbc9085`;
- model:
  `qwen3.5:4b`;
- model digest:
  `2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd`.

## Current Action

A014 implementation and main integration are complete. Closure metadata is
being committed and qualified on exact main before Issue #18 is closed.

## Next Action

After the closure metadata commit receives exact main CI GREEN, post the final
evidence summary to Issue #18 and close it as completed.

Do not activate A015 automatically.
