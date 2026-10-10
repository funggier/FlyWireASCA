# Current Development Task

Current task: A013
Status: ACTIVE
GitHub Issue: #16

## Current Action

A013 — Selective Relational Activation / Hybrid Recall Integration Gate is
active from verified base
`ff1f6e6b779a662f4a10aae955f8c7ce1a934b45`.

The implementation must remove the A012 benchmark-only target oracle from the
runtime relation path by introducing target-free bounded neighborhood
expansion. It will compare `VECTOR_ONLY`, `ALWAYS_RELATION`, and
`SIGNAL_GATED_RELATION` on a frozen mixed workload.

The signal-gated primary experiment uses an explicit typed structural-need
contract. It does not use an LLM or natural-language classifier to decide
whether relation traversal is required.

A005 remains `VECTOR_SUFFICIENT` for its qualified retrieval workload. A012
remains `EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED` for its frozen
relation-dependent workload. A011 remains historical frozen v0.x
`ENGINEERING_QUALIFIED`.

## Next Action

Implement target-free relation-expansion contracts and bounded expansion,
freeze the mixed A013 fixture and fingerprints, implement all three policies,
then run the portable qualifier and full local qualification before the first
feature push.

## Resume Rule

Read the A013 design, implementation plan, and task first. Then verify live
Git/GitHub/runtime state; live state overrides stale prose.

Do not reset/clean/rebase/force-push or modify A011-protected cognitive source
blobs. Keep FlyWireLLM untouched. No release/tag/version promotion is
authorized.
