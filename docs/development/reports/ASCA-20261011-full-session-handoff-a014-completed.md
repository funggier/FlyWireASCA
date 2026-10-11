# Full Session Handoff — A014 Completed

Date: 2026-10-11
Repository: `funggier/FlyWireASCA`
Milestone: A014 — Structural Need Inference / Query Intent Routing Gate
Status: DONE

## Resume authority

On any later session, verify live Git, GitHub, and runtime state first. Live
state overrides stale prose. Do not reset, clean, rebase, or force-push.

FlyWireLLM is a separate project and was not touched.

## Final A014 conclusion

Frozen physical decision:

`HYBRID_STRUCTURAL_ROUTING_JUSTIFIED`

A014 demonstrates, on its frozen bilingual workload, that ordinary English/Thai
query text can be converted into an A013-compatible target-free
`StructuralNeed` without manually supplying expected relation truth.

## Physical result

32 valid bilingual cases:

- `RULE_ONLY`: 27/32 downstream success, 9 missed activations, 0 false
  activations, 0 model calls;
- `MODEL_ONLY`: 32/32 downstream success, 0 missed activations, 2 false
  activations, 32 model calls;
- `HYBRID_RULE_THEN_MODEL`: 32/32 downstream success, 0 missed activations,
  0 false activations, 9 model calls.

Hybrid therefore matches model-only correctness while reducing model calls by
23/32, or 71.875%, and improves routing integrity from 30/32 exact relation-set
matches to 32/32.

## Frozen identities

- fixture:
  `c100f828265063c369d535f85db8166cbeaaba26943fbb6d276a24dc46018eca`;
- prompt:
  `b48568801f32579e36f2e633b740a3d6cc0a276ffa6dcaa05d035f790b5f6a8d`;
- model:
  `qwen3.5:4b`;
- model digest:
  `2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd`;
- source implementation:
  `e0e57e914b63f30bf6c360a49d56ebfbc1a22f83`;
- source manifest:
  `a423296415b4e59ac2933c7c40900e3f9e74d832b554564b6b9ef66b7fbc9085`;
- physical evidence:
  `a7fd02566917f3051a4e40881bce976933ea6e604a7558d510a8720ce89f3dcf`.

## Runtime boundary

Important: A014 is not yet a complete conversational/autonomous runtime.

Current qualified flow:

ordinary English/Thai query text
→ A014 structural routing
→ inferred `StructuralNeed`
→ A013 signal-gated relation-aware recall

The A014 evaluation layer proves that composition against the frozen workload.

The frozen A009 integrated cognitive loop remains unchanged. There is no single
production-style entry point yet that accepts arbitrary ordinary text and
automatically composes A014 routing + A013 recall + A009 cognitive loop +
procedure execution + real external side effects until completion.

Do not state otherwise in future sessions.

## Exact GitHub chain

Final feature head:

`37e1cf36078d525123ea64d99134b701f79a4653`

Feature CI:

- run `38116882068`;
- GREEN;
- A014 artifact digest:
  `sha256:1f8eb913b1f04b6fe0c522affe9135be02d8c904dc9ca6eaacf1a798e19cbd2a`.

The user selected finishing option 1, local-main integration. The merge was a
fast-forward to the same SHA. No PR was created and there is no PR-CI evidence.

Merged-main local suite:

`1162 passed in 98.61s`

Integration/main CI:

- run `38152301384`;
- GREEN;
- head:
  `37e1cf36078d525123ea64d99134b701f79a4653`;
- A014 artifact digest:
  `sha256:d37c4cfa6ab28d2f2ff3d5f3f25c6387245ec322b923578d22be2bdaa6a3f604`.

## Historical research outcomes after A014

- A005: `VECTOR_SUFFICIENT`
- A006: `NOT_SUPPORTED`
- A007: `SUPPORTED`
- A008: `SUPPORTED`
- A009: `SUPPORTED`
- A010: `NOT_SUPPORTED`
- A011 frozen v0.x: `ENGINEERING_QUALIFIED`
- A012: `EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED`
- A013: `SIGNAL_GATED_RELATION_JUSTIFIED`
- A014: `HYBRID_STRUCTURAL_ROUTING_JUSTIFIED`

## A011 preservation

Frozen A011 profile SHA256:

`add06f285bf6decc7d492b987d3769dc64db4cb3d0177c8c6586d50ee5f6d46d`

Protected paths: 67.

Protected mode/path/blob SHA256:

`8df49f05fe54de43667ab2f8ef5de2caae9376ffedf2cb8f8d26f0e4abcca6b6`.

## Next milestone rule

No A015 is activated automatically.

If future work aims for “type ordinary text and let ASCA carry it through
automatically”, define a separate end-to-end integration gate. That gate should
measure both completion correctness and execution cost/latency, and must
preserve A011 source history and A014 target-free routing boundaries.

## Closure rule

Issue #18 is closed only after the closure-metadata commit on main receives exact
GREEN CI. At final closure verify:

- local main equals origin/main;
- ahead/behind 0/0;
- worktree clean;
- Issue #18 closed;
- CURRENT says A014 DONE;
- ROADMAP says A014 DONE;
- no A015 active;
- no release/tag/version promotion.
