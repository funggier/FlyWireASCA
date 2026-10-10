# A012 — Relational Reasoning / Structure Decision Gate Final Evidence

Date: 2026-10-10
Milestone: A012
Repository: `funggier/FlyWireASCA`
Status: DONE
Primary architecture decision: `EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED`

## 1. Question answered

A012 tested a narrower question than A005:

> When a controlled task requires an explicitly stored typed relation or bounded
> relation path, does bounded relation traversal recover correct evidence that
> the qualified A005 Vector + Metadata retrieval primitive does not reliably
> recover?

The result does **not** revoke A005's `VECTOR_SUFFICIENT` conclusion for the
A005 retrieval workload. It establishes that explicit typed structure is
justified for the declared A012 relation-dependent workload.

## 2. Frozen portable experiment

Fixture version: `a012-deterministic-v1`

Fixture SHA256:

`dcabd86117f22e35c18fe605c8411da143962f112645a78c9124ec5987179aea`

Workload:

- 6 relation-dependent positive cases:
  - ownership / `WORKS_AT`;
  - causal / `CAUSED_BY`;
  - temporal / `OCCURRED_BEFORE`;
  - two-hop `PART_OF`;
  - `USED_FOR`;
  - same-name disambiguated ownership;
- 1 direct-vector control;
- 4 fail-closed controls:
  - cycle;
  - low-confidence edge;
  - relation allowlist;
  - missing target;
- 1 invalid-contract control.

Both primary variants use the real A005 `ExactVectorMemoryIndex`,
`VectorMemoryDocument`, and `VectorMemoryQuery` primitives on shared frozen
inputs.

### Portable metrics

| Metric | Result |
| --- | ---: |
| Cases | 12 |
| Valid / invalid-contract | 11 / 1 |
| Primary relation-dependent cases | 6 |
| Vector + Metadata successes | 5 |
| Bounded-relation successes | 11 |
| Shared successes | 5 |
| Relation-only recoveries | 6 |
| Vector-only successes | 0 |
| Regressions | 0 |
| Identity failures | 0 |
| Provenance failures | 0 |
| Budget violations | 0 |
| Duplicate-visit failures | 0 |
| Vector queries | 11 |
| Vector scored items | 27 |
| Relation edge scans | 11 |
| Deterministic repeat | true |

Portable decision:

`EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED`

This decision is derived from frozen case evidence and literal fixture/shared
input fingerprints; it is not hard-coded from the project name.

## 3. Bounded relation semantics

A012 implements a deterministic in-memory control, not a persistent graph
database.

The relation path is:

- directed;
- relation-allowlisted;
- confidence-thresholded;
- bounded to maximum 3 hops, 8 visited nodes, and 32 scanned edges;
- cycle-suppressed;
- deterministic by activation weight, proposition confidence, then edge ID;
- provenance-preserving through exact edge/evidence IDs;
- identity-safe: `SAME_NAME` is never promoted to `SAME_PERSON`;
- LLM-free for traversal decisions;
- side-effect-free.

Architecture audit permits `relational_reasoning` to depend only on
`contracts`, `embedding`, and `vector_memory`.

## 4. Physical secondary replay

Physical replay is secondary evidence and cannot rewrite the portable primary
decision.

Pinned runtime:

- Ollama model: `qwen3-embedding:0.6b`
- model digest:
  `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`
- embedding dimension: 1024
- frozen A005 physical threshold: `0.5037018224299838`
- keep-alive requested by runner: `6h`

Exact-clean replay was rerun on final feature head:

`0728ddab442b774dcedb60a3fb7870444a95ffcb`

Observed physical result:

- experiment valid: true;
- observed decision: `EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED`;
- agrees with portable decision: true;
- Vector successes: 2 / 11;
- relation-aware successes: 6 / 11;
- relation-only recoveries: 4;
- regressions: 0;
- identity failures: 0;
- provenance failures: 0;
- budget violations: 0;
- duplicate-visit failures: 0;
- deterministic repeat: true.

Physical evidence JSON SHA256:

`35cbe908737f259f917d20bc67c779dbb7107df1393488cedd08899bbe441455`

Some negative controls are retrieved directly by the physical embedder at the
frozen threshold. Therefore physical case counts are descriptive
embedding-specific evidence rather than a replacement portable fixture.

## 5. A011 frozen qualification boundary

A011 remains historical qualification of its exact frozen v0.x source universe.
A012 did not weaken the production A011 provenance guard.

Frozen A011 anchors preserved on post-A011 heads:

- profile SHA256:
  `add06f285bf6decc7d492b987d3769dc64db4cb3d0177c8c6586d50ee5f6d46d`;
- protected path count: 67;
- protected Git mode/path/blob SHA256:
  `8df49f05fe54de43667ab2f8ef5de2caae9376ffedf2cb8f8d26f0e4abcca6b6`.

Because A011 requires the complete non-qualification cognitive Python source
universe to equal those 67 paths, any post-A011 cognitive package is
intentionally outside the A011 profile. CI therefore checks preservation rather
than falsely relabelling the A012 head as A011-qualified.

Historical A011 tests now create a synthetic frozen-A011 candidate in their
temporary clone by removing only the post-A011 `relational_reasoning` package.
The production source guard is unchanged.

## 6. Review and repair evidence

Whole-change review found no remaining Critical or Important issue after these
evidence-driven repairs:

1. post-A011 CI topology was changed from live-head A011 requalification to
   literal frozen-profile/blob preservation;
2. empty physical retrieval seeds were classified as valid retrieval misses
   rather than invalid relation contracts;
3. historical README assertions were updated without rewriting A008-A010
   outcomes;
4. historical A011 tests were isolated from the post-A011 cognitive source
   universe;
5. Linux `core.autocrlf=true` fixture cleanup was made robust with forced
   removal inside the temporary synthetic test clone only.

Local full repository suite after the A011 test-isolation repair:

`994 passed in 89.41s`

Architecture audit, repository qualification, A003/A008/A009/A010 portable
gates, A011 preservation, A012 portable qualification, compile checks, and
`git diff --check` were GREEN.

## 7. Exact Git / GitHub evidence

Activation base:

`23b96f4502b81cddb9563b55c26fdd0adc731265`

Planning commit:

`f5a6542b84f72c85a4f87267196665b4bfdfd410`

Activation commit:

`544a15926ee905d28d9dd634b0753d9b71b23738`

Initial implementation candidate:

`a5151694ba01bea66efe2c8fdc177c25d1a9f144`

Historical A011 fixture-isolation repair:

`89e4a6009a38e05a3a0fedbaae5aeae783d3675f`

Final feature head:

`0728ddab442b774dcedb60a3fb7870444a95ffcb`

Exact feature push CI:

- run: `38067495867`
- result: GREEN
- portable artifact SHA256:
  `760cad31a867c6f52613d1e3c5aa7a879528ac386dcbb570cb5cd9c587c86340`

Pull request:

- PR: #15
- head: `0728ddab442b774dcedb60a3fb7870444a95ffcb`
- base: `23b96f4502b81cddb9563b55c26fdd0adc731265`
- exact PR CI run: `38067628031`
- result: GREEN

Normal merge integration:

`48dfc64bca60d62528787b57d04a01df04fac30d`

Exact integration/main CI:

- run: `38067737917`
- result: GREEN
- all CI gates including A011 preservation and A012 portable qualification:
  PASS
- integration portable artifact SHA256:
  `760cad31a867c6f52613d1e3c5aa7a879528ac386dcbb570cb5cd9c587c86340`

## 8. Preserved historical outcomes

A012 does not rewrite prior research conclusions:

- A006: `NOT_SUPPORTED`
- A007: `SUPPORTED`
- A008: `SUPPORTED`
- A009: `SUPPORTED`
- A010: `NOT_SUPPORTED`
- A011: frozen v0.x `ENGINEERING_QUALIFIED` on its historical exact
  qualification source

A005 remains `VECTOR_SUFFICIENT` for its qualified retrieval workload.

FlyWireLLM was not modified.

## 9. Claims boundary

A012 does not establish:

- general graph superiority;
- a requirement for a persistent graph database;
- lower FLOPs, energy, RAM use, hardware bandwidth, or general latency;
- automatic relation learning;
- autonomous self-modification;
- safe real-world side-effect execution;
- biological or human-cognition equivalence;
- AGI or consciousness.

The justified change is narrower: for the frozen A012 relation-dependent
workload, explicit bounded typed relation traversal provides reproducible
correct recoveries beyond Vector + Metadata alone.

## 10. Closure

A012 implementation, review, feature qualification, PR qualification, normal
merge integration, and integration/main qualification are complete.

The repository closure metadata commit containing this report must receive its
own exact main CI before GitHub Issue #14 is closed. No A013 milestone is
activated by A012 closure.
