# A013 — Selective Relational Activation / Hybrid Recall Integration Gate Design

Date: 2026-10-11
Repository: `funggier/FlyWireASCA`
Milestone: A013
GitHub Issue: #16
Activation base: `ff1f6e6b779a662f4a10aae955f8c7ce1a934b45`

## 1. Decision to make

A012 established that bounded explicit typed relation traversal is justified for
its frozen relation-dependent workload. It did not establish how relation
traversal should be activated in a mixed recall workload, and its experimental
`TraversalRequest` contains expected target IDs so that the A012 benchmark can
terminate as soon as its controlled target is found.

A013 must answer a narrower integration question without leaking benchmark
answers into runtime control:

> Can target-free bounded relation expansion, activated only by an explicit
> structural-need signal, preserve relation-dependent correctness and exact
> provenance while reducing unnecessary relation work compared with always-on
> relation expansion?

A013 compares three policies:

- `VECTOR_ONLY`
- `ALWAYS_RELATION`
- `SIGNAL_GATED_RELATION`

The benchmark evaluator may know expected targets. Runtime retrieval and
relation-expansion code must not receive expected target IDs.

## 2. Preserved authority and historical outcomes

Live Git/GitHub/runtime state is authoritative over stale prose.

A013 preserves these conclusions:

- A005: `VECTOR_SUFFICIENT` for the qualified A005 retrieval workload.
- A006: `NOT_SUPPORTED`.
- A007: `SUPPORTED`.
- A008: `SUPPORTED`.
- A009: `SUPPORTED`.
- A010: `NOT_SUPPORTED`.
- A011: historical frozen v0.x `ENGINEERING_QUALIFIED` on its exact source profile.
- A012: `EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED` for the frozen A012
  relation-dependent workload.

A013 does not edit A011-protected cognitive source blobs. It adds a post-A011
layer and may reuse post-A011 A012 primitives without relabelling the new HEAD
as A011-qualified.

## 3. Why target-free expansion is required

A012's target-aware traversal is a valid controlled experiment: expected target
IDs are part of the benchmark contract and allow exact measurement of path
recovery and early termination.

That API is not a valid general recall controller because a production recall
request normally does not know the answer memory ID in advance. Reusing it
unchanged would create an oracle channel.

A013 therefore introduces a target-free relation-expansion primitive. It takes:

- seed memory IDs;
- allowed relation types;
- the A012 confidence threshold semantics;
- maximum hops;
- maximum visited nodes;
- maximum scanned edges.

It returns a bounded deterministic neighborhood with exact path provenance for
every newly reached memory. It never accepts an expected target ID.

The benchmark separately evaluates whether expected targets are present in the
returned vector or relation evidence.

## 4. Structural-need signal

The primary portable experiment does not use an LLM or natural-language
classifier to decide whether relation traversal is needed.

A `StructuralNeed` contract declares the relation semantics the upstream task
requires:

- `required_relations: tuple[RelationType, ...]`
- `requires_path_provenance: bool`

Canonical semantics:

- empty `required_relations` and false provenance requirement means no
  structural activation request;
- a non-empty required relation set activates the structural path;
- path provenance is evidence-only and cannot create a relation not present in
  stored edges;
- the signal never contains expected answer IDs.

This deliberately separates two questions:

1. A013: given an explicit structural requirement, should relation expansion be
   selectively activated?
2. A future milestone: how should an upstream system infer or obtain that
   requirement from unconstrained language/tasks?

A013 must not smuggle the second question into the first.

## 5. Runtime policy semantics

### 5.1 VECTOR_ONLY

1. Run the real A005 `ExactVectorMemoryIndex`.
2. Return vector evidence only.
3. Do not invoke relation expansion.

### 5.2 ALWAYS_RELATION

1. Run the same vector retrieval.
2. Use returned memory IDs as relation seeds.
3. Run target-free bounded expansion for every valid benchmark case.
4. Merge vector IDs and reached relation IDs without changing identity.
5. Preserve vector evidence and relation path provenance separately.

If vector retrieval returns no seed, relation expansion is skipped as a
fail-closed retrieval miss; no seed may be invented.

### 5.3 SIGNAL_GATED_RELATION

1. Run the same vector retrieval.
2. Inspect only `StructuralNeed`.
3. If structural activation is not requested, return vector evidence directly.
4. If requested and vector seeds exist, run the same target-free bounded
   expansion used by `ALWAYS_RELATION`.
5. If requested but no seed exists, fail closed with no invented seed.

The signal policy cannot inspect expected target IDs, benchmark labels, or
post-hoc correctness.

## 6. Deterministic relation expansion

A013 relation expansion preserves A012 ordering and safety semantics:

1. descending `activation_weight`;
2. descending `proposition_confidence`;
3. lexical `edge_id`.

Bounds remain no larger than A012:

- max hops: 3;
- max visited nodes: 8;
- max scanned edges: 32.

Additional rules:

- directed edges only;
- explicit relation allowlist;
- proposition-confidence threshold;
- cycle suppression;
- no duplicate visited memory IDs;
- no implicit inverse edges;
- no `SAME_NAME` to `SAME_PERSON` promotion;
- no LLM decision in traversal;
- no persistent graph database;
- no external side effects.

The result records, for each reached non-seed memory:

- reached memory ID;
- full memory path;
- edge IDs;
- evidence IDs;
- hop count.

Termination records one of:

- `FRONTIER_EXHAUSTED`
- `HOP_BUDGET_EXHAUSTED`
- `NODE_BUDGET_EXHAUSTED`
- `EDGE_BUDGET_EXHAUSTED`

There is no target-found termination because the primitive has no target.

## 7. Package boundary

A013 adds:

`flywire_asca.relational_activation`

Allowed dependencies:

- `contracts`
- `embedding`
- `vector_memory`
- `relational_reasoning`

It must not depend on:

- `integrated_loop`
- `baseline_comparison`
- `qualification`
- `model`
- FlyWireLLM.

The existing A009 integrated loop remains frozen by history and is not modified
during A013. Full cognitive-loop integration is a later decision after this
target-free activation gate has evidence.

## 8. Frozen portable mixed workload

The portable fixture must contain both structural and non-structural recall.

Minimum valid cases:

- the six A012 relation-dependent positive semantics:
  ownership/workplace, causal, temporal, two-hop part-of, used-for, and
  same-name disambiguated ownership;
- the four A012 structural fail-closed controls:
  cycle, low-confidence edge, relation allowlist, and missing target;
- at least six direct-vector/non-structural controls with no structural need;
- one invalid-contract control excluded from success denominators.

The fixture must be literal and fingerprinted. Shared case inputs must also have
stable per-case fingerprints so the qualifier cannot bless silent fixture
rewrites.

Expected target IDs remain in benchmark case metadata only. Tests must prove the
runtime policy/expansion request types have no target field.

## 9. Primary metrics

For each policy and in aggregate record:

- valid success count;
- relation-dependent positive success count;
- direct-vector control success count;
- relation-only recoveries over `VECTOR_ONLY`;
- regressions relative to `VECTOR_ONLY`;
- relation invocation count;
- scanned edge count;
- visited relation-node count;
- structural false-activation count;
- structural missed-activation count;
- identity failures;
- provenance failures;
- budget violations;
- duplicate-visit failures;
- deterministic repeat.

Do not collapse these measurements into one opaque scalar.

## 10. Predeclared architecture decision

A013 may conclude exactly one of:

- `SIGNAL_GATED_RELATION_JUSTIFIED`
- `ALWAYS_RELATION_PREFERRED`
- `RELATION_INTEGRATION_NOT_JUSTIFIED`
- `MIXED`

`SIGNAL_GATED_RELATION_JUSTIFIED` requires all of:

- signal-gated relation-dependent success equals always-relation success;
- signal-gated direct-vector success is not below vector-only;
- signal-gated relation invocations are fewer than always-relation;
- signal-gated scanned edges are no greater than always-relation and at least
  one relation scan is avoided;
- false activation and missed activation are zero for the frozen explicit
  `StructuralNeed` contract;
- identity/provenance/budget/duplicate-visit failures are zero;
- deterministic repeat is true.

`ALWAYS_RELATION_PREFERRED` requires always-on relation to achieve strictly
better correctness than signal-gated under the frozen signal contract without
structural safety failure.

`RELATION_INTEGRATION_NOT_JUSTIFIED` applies when neither relation policy
produces a useful relation-dependent correctness gain over vector-only or when
the relation integration cannot satisfy the frozen safety/provenance contract.

All other valid evidence yields `MIXED`.

A valid negative or mixed architecture result is not an engineering
qualification failure.

## 11. Qualification topology

Portable CI:

- full pytest;
- architecture audit;
- existing historical portable gates;
- A011 frozen-source preservation;
- A012 portable qualifier unchanged;
- A013 portable qualifier with JSON evidence artifact;
- whitespace check.

A013 primary qualification is deterministic and Ollama-free.

A local physical replay may be added only as secondary evidence using the pinned
A005/A012 embedding model identity. Physical evidence cannot rewrite the
portable primary decision.

## 12. Claims boundary

A013 does not establish:

- that an LLM can infer structural need correctly;
- that always-on relation traversal is generally bad;
- that a persistent graph database is required;
- general latency, FLOP, energy, RAM, or token superiority;
- autonomous relation learning or memory consolidation;
- production safety;
- AGI, consciousness, or biological equivalence.

The intended claim is only about bounded target-free relation activation on the
frozen mixed A013 workload.

## 13. Acceptance boundary

A013 can close only after:

- design and plan are committed;
- Issue #16 and task ledger are ACTIVE;
- runtime types prove expected targets cannot enter the activation request;
- portable fixture and fingerprints are frozen;
- all three policies run on shared inputs;
- decision is evidence-derived from predeclared rules;
- exact feature CI is GREEN;
- PR exact CI is GREEN;
- normal merge to main is GREEN;
- closure metadata commit receives exact main CI;
- final report/handoff records exact SHAs, runs, artifact hashes, and claim
  boundaries;
- FlyWireLLM remains untouched.
