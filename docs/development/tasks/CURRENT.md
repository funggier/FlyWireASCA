# Current Development Task

Current task: A014
Status: ACTIVE
GitHub Issue: #18

## Current Action

A014 — Structural Need Inference / Query Intent Routing Gate is active.

The approved design asks whether ordinary English/Thai query text can be
converted into the target-free `StructuralNeed` contract already consumed by
A013, comparing:

- `RULE_ONLY`;
- `MODEL_ONLY`;
- `HYBRID_RULE_THEN_MODEL`.

The primary decision is based on downstream A013 recall and routing integrity,
not classifier accuracy alone.

Implementation order is evidence-sensitive:

1. define target-free routing contracts;
2. freeze the bilingual benchmark before router tuning;
3. implement deterministic, model-only, and hybrid routing under TDD;
4. evaluate inferred need through the existing A013 signal-gated path;
5. run portable engineering qualification;
6. run mandatory pinned `qwen3.5:4b` physical qualification and bind evidence
   to exact source/fixture/prompt/model identities.

## Preserved Boundaries

- A011 remains historical qualification of its exact frozen v0.x source profile.
- A012 remains `EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED` for its frozen workload.
- A013 remains `SIGNAL_GATED_RELATION_JUSTIFIED` for its frozen workload.
- A014 must not modify A011-protected cognitive source blobs.
- FlyWireLLM remains untouched.
- No release/tag/version promotion is authorized.
- A015 is not activated automatically.

## Resume Rule

Read:

- `docs/development/tasks/A014-structural-need-inference.md`;
- `docs/superpowers/specs/2026-10-11-a014-structural-need-inference-design.md`;
- `docs/superpowers/plans/2026-10-11-a014-structural-need-inference.md`;
- `docs/development/QUALIFICATION-MATRIX.md`;
- the latest A014 execution ledger under `.superpowers/sdd/`.

Then verify live Git/GitHub/runtime state. Live state overrides stale prose.

Do not reset/clean/rebase/force-push or modify A011-protected cognitive source
blobs.
