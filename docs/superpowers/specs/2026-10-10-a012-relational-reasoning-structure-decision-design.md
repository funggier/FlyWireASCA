# A012 — Relational Reasoning / Structure Decision Gate Design

Date: 2026-10-10
Status: APPROVED FOR IMPLEMENTATION
Repository: `funggier/FlyWireASCA`
Activation base: `23b96f4502b81cddb9563b55c26fdd0adc731265`

## 1. Purpose

A012 tests whether FlyWireASCA now has reproducible evidence that explicit typed
relation traversal is useful beyond the already-qualified A005 Vector + Metadata
retrieval scope.

A005 concluded `VECTOR_SUFFICIENT` for its retrieval workload. That result is
preserved. Its own final report explicitly left open a later reasoning experiment
for causal, temporal, ownership, and path-dependent failures. A012 is that
decision gate.

A012 does **not** assume that a graph is desirable because ASCA contains the word
"Associative". It compares the current retrieval primitive against a bounded
relation-aware experimental control and lets measured task evidence determine
whether explicit relation structure is justified.

## 2. Approval and authority

The user explicitly authorized creating the next milestone and continuing the
work in this session: "อนุมัตให้สร้างและทำต่อได้เลยครับ".

Live Git/GitHub/runtime state overrides historical prose. A011 is complete and
`ENGINEERING_QUALIFIED` for its frozen v0.x profile. A012 is a new research
milestone outside that frozen cognitive profile.

Historical outcomes remain unchanged:

- A006: `NOT_SUPPORTED`
- A007: `SUPPORTED`
- A008: `SUPPORTED`
- A009: `SUPPORTED`
- A010: `NOT_SUPPORTED`
- A011: engineering-qualified frozen v0.x profile

FlyWireLLM remains independent and untouched.

## 3. Research question

> On controlled tasks where the answer depends on an explicit typed
> relationship or bounded relation path, does bounded relation traversal recover
> correct evidence that the current Vector + Metadata retrieval primitive does
> not reliably recover, without introducing identity collapse, unbounded search,
> hidden inference, or provenance loss?

This is a structure-decision experiment. It is not a general claim that graph
reasoning is superior to vector retrieval.

## 4. Compared variants

### 4.1 VECTOR_METADATA

The control uses the real A005 primitives:

- `ExactVectorMemoryIndex`
- `VectorMemoryDocument`
- `VectorMemoryQuery`
- explicit metadata filters where the fixture declares them

It receives the same memory corpus, query text, deterministic embedding evidence,
threshold, and initial retrieval budget as the relation-aware variant.

The control performs no typed-edge traversal and cannot infer relation paths that
are not represented in its retrieved evidence.

### 4.2 BOUNDED_RELATION

The experimental variant starts from the exact same A005 retrieval result, then
may traverse explicit `AssociationEdge` records from ASCA Contract v0.1.

It may use only:

- explicitly stored directed edges;
- relation types already defined by `RelationType`;
- a case-declared relation allowlist;
- bounded hop/node/edge budgets;
- explicit proposition-confidence checks;
- deterministic priority ordering;
- visited-node/cycle suppression;
- recorded edge/evidence provenance.

It must not:

- create implicit inverse edges;
- invent transitive facts that are not represented by an explicit path;
- collapse `SAME_NAME` into `SAME_PERSON`;
- let vector similarity become identity/truth;
- call an LLM to decide traversal;
- execute real tools or side effects.

## 5. Traversal semantics

The first implementation is an in-memory deterministic relation layer, not a
persistent graph database.

A traversal request contains:

- seed memory IDs from A005 retrieval;
- allowed relation types;
- maximum hops;
- maximum visited nodes;
- maximum scanned edges;
- minimum proposition confidence.

Traversal is breadth-first by hop count. Within one frontier, eligible outgoing
edges are ordered deterministically by:

1. descending `activation_weight`;
2. descending `proposition_confidence`;
3. `edge_id` lexical order.

`activation_weight` and `proposition_confidence` remain separate semantics.
The former prioritizes exploration; the latter is an evidence acceptance bound.

The traversal result records:

- visited memory IDs;
- discovered target IDs;
- exact edge IDs used by each accepted path;
- evidence IDs carried by those edges;
- hop count;
- scanned-edge count;
- termination reason.

No recursion or hidden retry is permitted.

## 6. Boundedness defaults

Portable primary defaults:

- max hops: 3
- max visited nodes: 8
- max scanned edges: 32
- minimum proposition confidence: 0.50

A benchmark case may choose a stricter bound but not exceed the fixture maxima.

Termination reasons are explicit:

- `TARGET_FOUND`
- `FRONTIER_EXHAUSTED`
- `HOP_BUDGET_EXHAUSTED`
- `NODE_BUDGET_EXHAUSTED`
- `EDGE_BUDGET_EXHAUSTED`

## 7. Frozen portable workload

The deterministic fixture must include both positive and negative controls.

Primary relation-dependent cases:

1. **ownership/workplace one-hop** — retrieve a person anchor, answer through
   explicit `WORKS_AT`.
2. **causal one-hop** — retrieve an observed event, answer through
   `CAUSED_BY`.
3. **temporal one-hop** — follow an explicit `OCCURRED_BEFORE` edge in its
   stored direction.
4. **part-of two-hop** — component -> subsystem -> system using explicit
   `PART_OF` edges.
5. **used-for one-hop** — tool/object -> purpose using `USED_FOR`.
6. **same-name disambiguated ownership** — two same-name entities remain
   distinct; metadata selects the intended seed and traversal must not cross to
   the other identity.

Required controls:

7. **vector-direct control** — the current vector retriever should succeed
   without relation traversal.
8. **cycle control** — an explicit cycle must terminate without duplicate-node
   growth.
9. **low-confidence edge control** — an edge below the confidence threshold
   must not be accepted.
10. **relation allowlist control** — an otherwise reachable target through a
    non-allowed relation must not be followed.
11. **missing-target control** — neither mode may fabricate an answer.
12. **invalid-contract control** — malformed or inconsistent benchmark input
    must fail validation rather than silently normalizing itself.

The fixture and shared-input representation receive stable SHA-256 fingerprints.

## 8. Fairness and measurements

Both variants share the same:

- memory records and retrieval texts;
- embedding vectors / physical embedding model;
- query text;
- metadata filters;
- initial top-k and threshold;
- target definition.

Measurements are reported separately, not collapsed into one score:

- task success;
- vector query count;
- vector scored count;
- initially retrieved count;
- final selected/discovered count;
- relation edge scans;
- relation hops;
- identity failures;
- provenance failures;
- budget violations;
- cycle/duplicate-visit failures;
- relation-only recoveries;
- vector-only successes;
- shared successes.

Logical counts are not hardware FLOPs, RAM bytes, energy, or general latency.

## 9. Decision rule

A012 produces one architecture decision:

### `EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED`

Required when all of the following hold on the frozen portable primary workload:

- at least three primary relation-dependent cases are relation-only recoveries;
- relation-aware success is strictly greater than VECTOR_METADATA success;
- zero VECTOR_METADATA successes regress under BOUNDED_RELATION;
- zero identity/provenance/budget/cycle failures;
- all deterministic repeat and fixture-integrity checks pass.

### `VECTOR_METADATA_REMAINS_SUFFICIENT`

Used when explicit traversal produces no genuine relation-only recovery and the
vector control covers every declared relation-dependent case.

### `MIXED`

Used for any valid experiment between those two outcomes, including gains with
regressions or insufficient evidence for architectural promotion.

A valid negative or mixed result is research evidence, not an engineering test
failure.

## 10. Physical secondary evidence

A local physical replay may replace deterministic embedding vectors with the
pinned `qwen3-embedding:0.6b` adapter while preserving the same documents,
queries, metadata, explicit edges, target definitions, and traversal bounds.

Physical evidence is secondary. It may expose embedding-specific behavior but
must not rewrite the frozen portable primary decision.

No terminal `qwen3.5:4b` generation is needed for A012.

## 11. Package and dependency boundary

A012 adds a new package:

`flywire_asca.relational_reasoning`

Allowed direct dependencies:

- `contracts`
- `embedding`
- `vector_memory`

The package must not depend on:

- `integrated_loop`
- `baseline_comparison`
- `qualification`
- `model`
- FlyWireLLM

A012 does not modify A005-A010 cognitive implementations. Existing A011
`protected_source.paths` and frozen profile bytes remain unchanged.

The architecture audit may be extended to recognize the new package and enforce
the dependency direction. This does not redefine the A011 frozen profile.

## 12. Qualification topology

Portable CI must add an explicit A012 qualifier after the existing A010 gate and
before/alongside A011 portable profile qualification.

A011 remains a qualification of the declared frozen v0.x profile. A012 is a new
experimental layer and must carry its own evidence. Passing A011 on a later
repository SHA must not be described as qualifying A012.

The A012 portable qualifier must be network/Ollama-free.

Physical A012 qualification is local-only and must not appear in GitHub CI.

## 13. Non-scope

A012 does not:

- create a persistent graph database;
- replace Vector + Metadata retrieval;
- modify the A005 frozen threshold;
- retune A006-A010 fixtures or outcomes;
- add relation learning or automatic edge creation;
- add memory consolidation;
- add autonomous self-modification;
- integrate real OS/API/LConnect/BConnect actions into the cognitive loop;
- add external web/tool retrieval;
- change Contract v0.1 public field meanings;
- change package version from `0.1.0.dev0`;
- create a release/tag;
- touch FlyWireLLM.

## 14. Acceptance

A012 implementation is acceptable only when:

- the real A005 vector primitives are used by both variants;
- relation traversal is explicit, deterministic, bounded, cycle-safe and
  provenance-preserving;
- same-name identity remains distinct;
- the fixture has stable fingerprints and declared positive/negative controls;
- the architecture decision is derived from report evidence, not hard-coded;
- portable qualification and full pytest pass;
- architecture and repository qualifiers pass;
- exact branch CI is green;
- local physical secondary replay is recorded if runtime prerequisites remain
  available;
- review findings are resolved or explicitly deferred by severity;
- integration preserves A011 frozen protected source identities;
- exact main CI is green before closure.
