# A014 — Structural Need Inference / Query Intent Routing Gate

Date: 2026-10-11
Status: DONE
GitHub Issue: #18

## 1. Decision

A014 tested whether ordinary English/Thai query text can be converted into the
target-free `StructuralNeed` contract consumed by A013 without leaking expected
answer IDs, expected relation labels, benchmark labels, graph contents,
retrieval results, or evaluator correctness into runtime/model control.

The frozen physical architecture decision is:

`HYBRID_STRUCTURAL_ROUTING_JUSTIFIED`

for the declared A014 bilingual workload.

This conclusion is specific to structural-need routing. It does not claim that
every natural-language request can already execute through a single autonomous
ASCA runtime.

## 2. Compared routing policies

### RULE_ONLY

Conservative deterministic bilingual cues decide structural need. Unrecognized
queries abstain/fail closed.

### MODEL_ONLY

Every valid query is routed through the pinned model under a strict exact-JSON
contract.

### HYBRID_RULE_THEN_MODEL

Rules run first. Only rule abstentions invoke the model. Strong rule decisions
cannot be overridden by the model.

## 3. Frozen workload and identities

Frozen fixture:

- version: `a014-bilingual-v1`;
- valid cases: 32;
- derived from the 16 valid A013 cases in English and Thai;
- relation positives: 12;
- structural fail-closed/safety controls: 8;
- direct-vector/non-structural controls: 12;
- fixture SHA256:
  `c100f828265063c369d535f85db8166cbeaaba26943fbb6d276a24dc46018eca`.

Physical model:

- model: `qwen3.5:4b`;
- digest:
  `2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd`;
- backend: Ollama;
- temperature: 0;
- seed: 0;
- thinking: disabled;
- bounded output;
- prompt fingerprint:
  `b48568801f32579e36f2e633b740a3d6cc0a276ffa6dcaa05d035f790b5f6a8d`.

Source-bound implementation:

- implementation/source SHA:
  `e0e57e914b63f30bf6c360a49d56ebfbc1a22f83`;
- source manifest fingerprint:
  `a423296415b4e59ac2933c7c40900e3f9e74d832b554564b6b9ef66b7fbc9085`.

## 4. Physical routing result

| Metric | RULE_ONLY | MODEL_ONLY | HYBRID_RULE_THEN_MODEL |
| --- | ---: | ---: | ---: |
| Downstream success | 27/32 | 32/32 | 32/32 |
| Relation-positive success | 7/12 | 12/12 | 12/12 |
| Direct-control success | 12/12 | 12/12 | 12/12 |
| Structural-control success | 8/8 | 8/8 | 8/8 |
| False activations | 0 | 2 | 0 |
| Missed activations | 9 | 0 | 0 |
| Exact relation-set matches | 23/32 | 30/32 | 32/32 |
| Model invocations | 0 | 32 | 9 |
| Relation invocations | 11 | 22 | 20 |
| Scanned relation edges | not primary decision metric | not primary decision metric | not primary decision metric |

The hybrid policy preserves the 32/32 downstream success of model-only while:

- eliminating model-only's 2 false activations;
- reducing model calls from 32 to 9, a 71.875% reduction;
- achieving exact relation-set agreement on all 32 cases;
- retaining zero identity, provenance, budget, duplicate-visit, model-error, and
  invalid-model-output failures in the frozen physical evidence.

Compared with rule-only, hybrid recovers the five downstream failures while
removing all nine missed activations, at the cost of nine model calls.

## 5. What “performance” is established

A014 establishes a better routing trade-off on the frozen workload:

- correctness: hybrid matches model-only at 32/32 and exceeds rule-only at
  27/32;
- selectivity: hybrid invokes the model only 9/32 times instead of 32/32;
- routing integrity: hybrid has 0 false and 0 missed activations;
- relation-set precision: hybrid is exact on 32/32 versus model-only 30/32 and
  rule-only 23/32.

This is evidence of control-flow efficiency, not a general wall-clock or compute
benchmark. A014 does not establish lower FLOPs, lower energy, lower RAM, lower
token use overall, or lower end-to-end latency. Those require separately
designed measurements.

## 6. Runtime implementation

A014 adds:

`src/flywire_asca/structural_routing/`

with target-free request/result contracts, deterministic rules, strict model
routing, hybrid orchestration, frozen benchmark machinery, and downstream A013
evaluation.

Primary runtime entry point:

`run_structural_routing(request, policy=..., model_adapter=...)`

Input includes ordinary `query_text` plus request identity and optional language
hint. It does not receive expected targets or evaluator truth.

The qualified hybrid path produces an A013-compatible `StructuralNeed` and the
A014 evaluation path composes that result with A013
`SIGNAL_GATED_RELATION` recall.

## 7. End-to-end boundary

A014 does not modify the frozen A009 integrated cognitive loop. The current
qualified natural-language-to-structural-need path is composed with A013 inside
the A014 structural-routing/evaluation layer.

Therefore, after A014:

- yes: ordinary English/Thai text can be used to infer whether bounded relation
  expansion is needed, without manually supplying the structural relation
  signal;
- yes: the qualified path can drive A013 relation-aware recall on the frozen
  evaluation topology;
- no: there is not yet one production-style public API where arbitrary ordinary
  text automatically flows through routing, recall, A009 cognition, procedure
  execution, model fallback, and real tool/action side effects until task
  completion.

That missing end-to-end integration is a distinct future research/engineering
gate and must not be claimed as completed by A014.

## 8. Physical evidence

Committed evidence:

`docs/development/qualification/a014-structural-routing-physical-v1.json`

Evidence-declared SHA256:

`a7fd02566917f3051a4e40881bce976933ea6e604a7558d510a8720ce89f3dcf`

Committed evidence file SHA256:

`53d5afe65027e0fc992cdd379debef263911fd9e93bb9f977500e755c1ec9d47`

The verifier reconstructs and validates source identity, fixture/prompt/model
identity, raw invoked model outputs, policy metrics, and derived decision.

Raw model outputs are retained for all 41 physical model invocations across
MODEL_ONLY and HYBRID.

## 9. Verification and repair history

A014 retained failure evidence rather than hiding it.

### Architecture/CI integration repair

Task 10 first exposed missing architecture-auditor support for the new package
and stale CI/matrix expectations. A temporary editing defect also wrote literal
`\n` text into three files. The defect was identified as serialization/editing,
not architecture, then repaired and requalified.

### Physical verifier hardening

Review found that the verifier did not originally validate its own evidence SHA
and trusted some raw-case semantic fields too directly. The verifier was
hardened in commit:

`0246a061787d9043e26baea1611a85e0fcbc58d4`

After that change the physical-contract suite passed 7/7 and the full suite
passed 1162/1162.

### Shallow-history CI repair

An initial feature CI run failed because `actions/checkout` used shallow history
and could not inspect the source-bound implementation commit. This was a CI
checkout defect, not a physical-evidence mismatch. Commit:

`37e1cf36078d525123ea64d99134b701f79a4653`

changed the required checkout history so the exact verifier could inspect its
bound source.

## 10. Exact Git/GitHub evidence

Final feature head:

`37e1cf36078d525123ea64d99134b701f79a4653`

Exact feature CI:

- run: `38116882068`;
- result: GREEN;
- A014 artifact:
  `a014-structural-routing-38116882068-1`;
- digest:
  `sha256:1f8eb913b1f04b6fe0c522affe9135be02d8c904dc9ca6eaacf1a798e19cbd2a`.

Integration choice:

The user selected option 1 from the required finishing menu:
local merge back to `main`. Because the feature branch was a direct descendant
of the current main base, Git performed a fast-forward integration. PR
integration was not selected, so there is intentionally no A014 PR or PR-CI
record.

Merged/main implementation SHA:

`37e1cf36078d525123ea64d99134b701f79a4653`

Merged-main local verification:

`1162 passed in 98.61s`

Exact integration/main CI:

- run: `38152301384`;
- result: GREEN;
- exact head:
  `37e1cf36078d525123ea64d99134b701f79a4653`;
- A014 artifact:
  `a014-structural-routing-38152301384-1`;
- digest:
  `sha256:d37c4cfa6ab28d2f2ff3d5f3f25c6387245ec322b923578d22be2bdaa6a3f604`.

## 11. Historical conclusions preserved

A014 does not rewrite prior evidence:

- A005: `VECTOR_SUFFICIENT` for A005's qualified scope;
- A006: `NOT_SUPPORTED`;
- A007: `SUPPORTED`;
- A008: `SUPPORTED`;
- A009: `SUPPORTED`;
- A010: `NOT_SUPPORTED`;
- A011 frozen v0.x: `ENGINEERING_QUALIFIED`;
- A012: `EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED`;
- A013: `SIGNAL_GATED_RELATION_JUSTIFIED`;
- A014: `HYBRID_STRUCTURAL_ROUTING_JUSTIFIED`.

A011 frozen anchors remain:

- profile SHA256:
  `add06f285bf6decc7d492b987d3769dc64db4cb3d0177c8c6586d50ee5f6d46d`;
- protected paths: 67;
- protected mode/path/blob SHA256:
  `8df49f05fe54de43667ab2f8ef5de2caae9376ffedf2cb8f8d26f0e4abcca6b6`.

## 12. Claims boundary

A014 does not establish:

- universal natural-language intent understanding;
- arbitrary end-to-end autonomous task completion;
- safe real-world tool/OS/API side effects;
- autonomous relation learning;
- persistent graph-database necessity;
- graph-first superiority;
- lower FLOPs, energy, RAM, tokens, or wall-clock latency;
- production safety;
- AGI, consciousness, or biological equivalence.

## 13. Closure state

A014 implementation and integration are complete. Closure metadata is committed
separately on main and Issue #18 is closed only after that exact closure commit
receives GREEN CI.

No A015 milestone is activated automatically.

FlyWireLLM was not modified.

No release, tag, or version promotion was performed.
