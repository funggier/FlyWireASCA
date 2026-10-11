# A014 — Structural Need Inference / Query Intent Routing Gate Design

Date: 2026-10-11
Repository: `funggier/FlyWireASCA`
Milestone: A014
GitHub Issue: pending activation after design/plan approval
Design branch: `research/a014-structural-need-inference`
Activation base candidate: `4549951e3d2dbdbd877559d6b06ad501999e71f6`

## 1. Decision to make

A013 established that target-free relation expansion should be activated selectively
when an explicit typed `StructuralNeed` is already available. It deliberately did
not establish how that signal is obtained from ordinary user language.

A014 must answer the next upstream routing question:

> Given only ordinary English or Thai query text, with no benchmark labels,
> expected answer IDs, target memory IDs, or post-hoc retrieval correctness, can
> ASCA infer a safe `StructuralNeed` well enough to preserve downstream A013
> recall behavior, and which routing policy offers the best evidence-backed
> trade-off between correctness and model calls?

A014 compares three policies:

- `RULE_ONLY`
- `MODEL_ONLY`
- `HYBRID_RULE_THEN_MODEL`

The architecture decision is based on downstream recall and routing integrity,
not classification accuracy alone.

## 2. Preserved authority and historical outcomes

Live Git, GitHub, and runtime state remain authoritative over stale prose.

A014 preserves all historical conclusions:

- A005: `VECTOR_SUFFICIENT` for its qualified retrieval workload.
- A006: `NOT_SUPPORTED`.
- A007: `SUPPORTED`.
- A008: `SUPPORTED`.
- A009: `SUPPORTED`.
- A010: `NOT_SUPPORTED`.
- A011: historical frozen v0.x `ENGINEERING_QUALIFIED` on its exact protected source universe.
- A012: `EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED` for its frozen relation-dependent workload.
- A013: `SIGNAL_GATED_RELATION_JUSTIFIED` for its frozen mixed workload.

A014 is a post-A011 package. It must not edit any A011-protected cognitive source
blob and must not relabel post-A011 HEAD as A011-qualified.

FlyWireLLM remains out of scope.

## 3. Design baseline

The isolated A014 worktree was created from exact A013 closure main:

`4549951e3d2dbdbd877559d6b06ad501999e71f6`

Clean baseline verification before this design:

`1034 passed in 96.22s`

No A014 Issue, CURRENT activation, ROADMAP row, runtime source, or CI behavior is
created before the design and implementation-plan gates are approved.

## 4. Why A014 must be target-free

A014 sits upstream of A013. Its runtime inference request may contain only
information that is realistically available before recall:

- query/request identity;
- raw user query text;
- language hint only if explicitly supplied by the caller;
- fixed relation vocabulary/semantics owned by the router.

It must not receive or inspect:

- expected target memory IDs;
- benchmark labels;
- expected relation labels;
- vector retrieval results;
- relation graph contents;
- downstream success/failure;
- post-hoc evaluator feedback.

Benchmark expected labels and target IDs remain evaluator-only metadata.

This keeps A014 from converting the A013 target-free runtime path back into an
oracle-assisted controller.

## 5. Runtime contract

A014 adds a new post-A011 package:

`flywire_asca.structural_routing`

The core request is intentionally small:

- `request_id: str`
- `query_text: str`
- optional explicit `language_hint` restricted to `en`, `th`, or absent

The result records:

- routing policy;
- inference status;
- inferred `StructuralNeed`;
- inference source (`RULE`, `MODEL`, or `FAIL_CLOSED`);
- whether a model call occurred;
- parser/validation status;
- deterministic rule evidence identifiers, when rules decided the route;
- model identity fields when a model was used.

The runtime result contains no benchmark truth and no target IDs.

### 5.1 Inference status

A small explicit status vocabulary is used:

- `DECIDED_RELATIONAL`
- `DECIDED_NON_RELATIONAL`
- `ABSTAINED`
- `INVALID_MODEL_OUTPUT`
- `MODEL_ERROR`

`ABSTAINED`, `INVALID_MODEL_OUTPUT`, and `MODEL_ERROR` fail closed to `StructuralNeed()`
unless the selected policy has another permitted stage to consult.

No malformed model output may silently broaden relation scope.

## 6. Policy semantics

### 6.1 RULE_ONLY

A deterministic bilingual cue router examines only normalized query text.

Rules are intentionally conservative. They may emit:

- a strong positive decision with one or more explicit `RelationType` values;
- a strong non-relational decision for a narrowly defined direct-recall form;
- `ABSTAINED` when the text does not satisfy a strong rule.

Rule abstention fails closed in `RULE_ONLY`.

Rules must be stored independently from benchmark labels and may not branch on
case IDs, memory IDs, expected targets, or fixture fingerprints.

The rule layer is not intended to become a general natural-language parser. It
exists as a low-cost high-precision routing baseline.

### 6.2 MODEL_ONLY

A `ModelAdapter` is invoked for every valid routing request.

The model receives:

- the query text;
- a fixed description of the allowed relation vocabulary;
- a strict JSON response schema;
- an instruction to classify routing intent only.

The model does not receive memory contents, graph edges, target IDs, benchmark
labels, or expected answers.

Required JSON shape is logically equivalent to:

```json
{
  "requires_relation": true,
  "required_relations": ["works_at"],
  "requires_path_provenance": true
}
```

Validation rules:

- `requires_relation=false` requires an empty relation list and false provenance;
- `requires_relation=true` requires at least one known `RelationType`;
- unknown relation names are invalid;
- duplicate relation names are canonicalized only after validation;
- extra control fields that could carry targets/labels are rejected;
- malformed JSON or contradictory fields produce `INVALID_MODEL_OUTPUT`;
- invalid model output fails closed.

A model self-reported confidence score is not used to activate relation
traversal in A014.

### 6.3 HYBRID_RULE_THEN_MODEL

Hybrid uses the same deterministic rule router first.

- Strong rule-positive: return the rule decision without a model call.
- Strong rule-negative: return the rule decision without a model call.
- Rule abstention: invoke the same model router used by `MODEL_ONLY`.
- Invalid model output after fallback: fail closed.

The model may not override a strong deterministic rule in the primary A014
experiment. A future milestone may test arbitration if evidence requires it.

This policy isolates the intended question: can conservative deterministic cues
avoid unnecessary model calls while preserving the best observed downstream
routing correctness?

## 7. Relation vocabulary and safety

A014 may infer only relation types already defined by Contract v0.1.

The primary benchmark focuses on the relation semantics exercised by the
A012/A013 path:

- `WORKS_AT`
- `CAUSED_BY`
- `OCCURRED_BEFORE`
- `PART_OF`
- `USED_FOR`

`SAME_NAME`, `SAME_PERSON`, `SIMILAR_TO`, and `CO_OCCURS_WITH` remain valid
contract types but are not automatically promoted from vague lexical similarity.
Identity-sensitive relations require explicit evidence in a later dedicated
gate if they are to be inferred from natural language.

A014 must never translate `SAME_NAME` into `SAME_PERSON`.

## 8. Downstream evaluation path

A014 does not invent a new retrieval engine.

For each benchmark case:

1. the routing policy sees query text only;
2. the inferred `StructuralNeed` is passed into the existing A013
   `SIGNAL_GATED_RELATION` runtime path;
3. A013 performs the same A005 vector retrieval and target-free relation
   expansion semantics already qualified;
4. the benchmark evaluator, outside runtime control, checks expected routing and
   downstream task outcome.

This makes the principal measurement:

`natural-language query -> inferred StructuralNeed -> existing A013 recall`

rather than merely:

`natural-language query -> label`.

A014 must not modify the frozen A009 integrated loop.

## 9. Frozen bilingual workload

The A014 benchmark is frozen before router implementation is tuned.

The primary fixture is derived from the 16 valid A013 mixed-workload semantics
and supplies two natural-language renderings per semantic case:

- one English query;
- one Thai query.

This yields 32 valid routing cases while retaining the A013 downstream memory,
edge, vector, confidence, provenance, and expected-outcome semantics.

The 32 valid cases preserve the A013 category balance twice:

- 12 relation-dependent positive queries;
- 8 structural fail-closed/safety-control queries;
- 12 direct-vector/non-structural queries.

At least one additional invalid-contract case verifies request validation and is
excluded from valid success denominators.

The fixture freezes:

- case IDs and order;
- English/Thai query text;
- evaluator-only expected `StructuralNeed`;
- evaluator-only expected downstream target/outcome metadata;
- whole-fixture SHA256;
- per-case runtime-input SHA256;
- per-case evaluator-metadata SHA256.

Runtime-input fingerprints must exclude evaluator truth.

No rule may import benchmark fixture data.

## 10. Preventing benchmark overfitting

A014 explicitly separates fixture freezing from router implementation.

Before implementing routing behavior:

1. freeze all query texts and evaluator labels;
2. record whole-fixture and per-case fingerprints;
3. commit the frozen benchmark contract;
4. do not rewrite cases merely to improve a policy result.

If a fixture defect is discovered later, the change must be documented as a
benchmark revision and all policy evidence rerun. Silent query or label edits are
qualification failures.

Rules are reviewed for generic cue semantics, not case-ID matching.

## 11. Portable versus physical evidence

A014 separates engineering qualification from actual local-model capability.

### 11.1 Portable CI evidence

GitHub CI remains network-free and Ollama-free.

Portable tests/qualification verify:

- runtime request/result contracts;
- target/label leakage prevention;
- deterministic bilingual rule behavior;
- strict model JSON parsing and fail-closed semantics;
- model-call accounting using a scripted/fake adapter;
- hybrid control flow;
- frozen fixture fingerprints;
- downstream A013 integration with evaluator truth kept outside runtime;
- architecture dependency rules;
- exact decision-derivation code against supplied evidence.

A fake/scripted adapter is engineering evidence only. It must never be cited as
proof that a real model can infer structural need.

### 11.2 Mandatory local physical evidence

A014 cannot close its research question using fake model output.

A mandatory local physical qualifier compares all three policies using the pinned
A004 terminal model:

- model tag: `qwen3.5:4b`;
- digest:
  `2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd`.

The physical runner verifies model identity before scoring and uses deterministic
request settings where supported:

- temperature 0;
- seed 0;
- thinking disabled;
- bounded output;
- fixed router system prompt.

Physical evidence records raw model output for every model invocation, parsed
routing result, model identity, token/timing metadata when available, and
downstream A013 outcome.

Physical evidence is descriptive for timing/token fields. A014 does not claim
general speed, token, energy, FLOP, or RAM superiority.

## 12. Binding physical evidence to source

Because GitHub CI cannot rerun Ollama, committed physical evidence must be bound
to the exact A014 cognitive source that produced it.

The physical evidence records:

- exact implementation Git commit;
- A014 source-file manifest;
- source mode/path/blob fingerprint;
- frozen fixture fingerprint;
- router prompt fingerprint;
- model tag/digest;
- raw case evidence;
- derived aggregate metrics;
- derived architecture decision.

A portable verification script recomputes the A014 source and fixture
fingerprints on later doc-only closure commits. Any A014 cognitive source,
fixture, prompt, or decision-logic drift invalidates the physical evidence and
requires a fresh physical run.

The production A011 preservation guard remains unchanged.

## 13. Primary metrics

Metrics are reported separately for `RULE_ONLY`, `MODEL_ONLY`, and
`HYBRID_RULE_THEN_MODEL`.

Routing metrics:

- valid case count;
- structural activation true positives;
- structural activation true negatives;
- false activations;
- missed activations;
- exact relation-set matches;
- relation-set over-selection count;
- relation-set under-selection count;
- invalid model-output count;
- model transport/runtime error count;
- abstention count.

Downstream metrics:

- downstream task success count;
- relation-dependent positive success count;
- direct-vector/non-structural success count;
- structural fail-closed control success count;
- regressions relative to the evaluator-provided A013 oracle `StructuralNeed`
  path.

Cost/control metrics:

- model invocation count;
- relation invocation count;
- scanned relation-edge count;
- relation visited-node count;
- prompt/generated token counts when physically available.

Integrity metrics:

- target/label leakage failures;
- identity failures;
- provenance failures;
- budget violations;
- duplicate-visit failures;
- deterministic portable repeat.

No opaque aggregate intelligence score is introduced.

## 14. Predeclared architecture decisions

A014 may conclude exactly one of:

- `HYBRID_STRUCTURAL_ROUTING_JUSTIFIED`
- `RULE_ROUTING_SUFFICIENT`
- `MODEL_ROUTING_PREFERRED`
- `STRUCTURAL_ROUTING_NOT_SUPPORTED`
- `MIXED`

### 14.1 HYBRID_STRUCTURAL_ROUTING_JUSTIFIED

Requires all of:

- hybrid downstream success equals the best observed valid policy;
- hybrid relation-positive success equals the best observed valid policy;
- hybrid direct-vector success is not below the best observed valid policy;
- hybrid has no more missed activations than model-only;
- hybrid has no more false activations than model-only;
- hybrid exact relation-set matches are not below model-only;
- hybrid uses strictly fewer model calls than model-only;
- hybrid introduces zero new identity, provenance, budget, duplicate-visit, or
  leakage failures;
- physical evidence is bound to exact source/model/fixture identities.

### 14.2 RULE_ROUTING_SUFFICIENT

Requires rule-only to match the best downstream and routing correctness without
model calls and without integrity failures.

### 14.3 MODEL_ROUTING_PREFERRED

Requires model-only to provide strictly better downstream correctness than
hybrid and rule-only, with no integrity failure that invalidates the result.

### 14.4 STRUCTURAL_ROUTING_NOT_SUPPORTED

Applies when no tested inferred-routing policy preserves an acceptable A013
downstream path over the frozen workload, or when the experiment cannot satisfy
the no-leakage/integrity contract.

All other valid evidence yields `MIXED`.

A negative or mixed research result is not an engineering-process failure.

## 15. Architecture boundary

Allowed package dependency:

`structural_routing -> {contracts, model, relational_activation}`

The runtime package must not depend directly on:

- `integrated_loop`;
- `baseline_comparison`;
- `qualification`;
- A014 benchmark evaluator modules from runtime routing modules;
- FlyWireLLM.

Existing lower layers must not gain reverse dependencies on
`structural_routing`.

The A014 benchmark may compose lower-layer benchmark fixtures, but runtime
modules must remain evaluator-independent.

## 16. Error handling and fail-closed rules

A014 fails closed on:

- empty/invalid query text;
- unsupported language hint;
- rule ambiguity under `RULE_ONLY`;
- model transport error;
- malformed JSON;
- unknown relation name;
- contradictory model fields;
- unexpected target/label-like control fields;
- model response request-ID mismatch;
- model identity mismatch in physical qualification.

A fail-closed routing result carries no relation types and cannot cause
unbounded relation expansion.

Transport/runtime failure produces `MODEL_ERROR` and is recorded distinctly from a legitimate
non-relational decision.

## 17. Test strategy

Implementation follows TDD.

Required test families:

- request/result contract validation;
- target/expected-answer field rejection;
- English and Thai normalization;
- conservative rule-positive cases;
- conservative rule-negative cases;
- rule abstention;
- strict model parser acceptance/rejection;
- model request prompt contains only allowed runtime inputs;
- MODEL_ONLY invokes exactly once per valid request;
- HYBRID invokes model only after abstention;
- model transport failure fails closed;
- downstream A013 wiring uses inferred need only;
- benchmark truth never enters runtime dataclasses or model prompt;
- fixture and per-case tamper detection;
- architecture audit accepts only declared dependencies;
- reverse-dependency/cycle rejection;
- physical evidence source/model/fixture binding;
- portable decision derivation;
- historical A011/A012/A013 preservation.

## 18. Qualification topology

Portable CI after A014 activation is expected to include:

- full pytest;
- architecture audit;
- repository qualifier;
- existing A003/A008/A009/A010 gates;
- A011 frozen preservation;
- A012 portable qualifier;
- A013 portable qualifier;
- A014 portable router qualifier;
- A014 committed-physical-evidence integrity verifier after physical evidence
  exists;
- whitespace check.

The physical A014 runner remains local-only and is never invoked by GitHub CI.

A014 cannot be declared DONE until the mandatory physical comparison completes,
its evidence is source-bound, exact feature CI is GREEN, PR CI is GREEN, normal
main integration CI is GREEN, and closure metadata receives exact main CI.

## 19. Claims boundary

A014 does not establish:

- general natural-language understanding;
- correctness outside the frozen English/Thai routing workload;
- that `qwen3.5:4b` is generally the best router model;
- safe inference of identity-sensitive relations from names alone;
- a need for a persistent graph database;
- autonomous relation learning;
- general latency, FLOP, energy, RAM, bandwidth, or token superiority;
- production safety or safe real-world side effects;
- AGI, consciousness, or biological equivalence.

The intended claim is limited to whether the tested routing policies can derive
A013-compatible `StructuralNeed` from the frozen bilingual workload under the
declared safety and evidence contract.

## 20. Acceptance boundary

A014 may be activated only after this design and its implementation plan are
approved.

After activation, A014 can close only when:

- task/Issue lifecycle is ACTIVE and evidence-bound;
- frozen bilingual benchmark is committed before policy tuning;
- runtime routing APIs contain no target/expected-answer oracle;
- portable engineering qualification passes;
- mandatory pinned-model physical comparison completes;
- physical evidence is bound to unchanged A014 source/fixture/prompt identities;
- one predeclared decision is derived from raw evidence;
- exact feature, PR, integration/main, and closure CI gates are GREEN;
- final report and full-session handoff preserve all limitations and exact evidence;
- FlyWireLLM remains untouched;
- no release/tag/version promotion occurs unless separately authorized.

No A015 milestone is activated automatically by A014 closure.
