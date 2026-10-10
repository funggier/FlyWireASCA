# A013 — Selective Relational Activation / Hybrid Recall Integration Gate

Date: 2026-10-11
Status: DONE
GitHub Issue: #16
Pull Request: #17

## 1. Decision

A013 answers whether bounded explicit relation traversal, once justified by A012
for relation-dependent workloads, should run for every valid recall request or
only when an explicit structural-need contract requests it.

The frozen portable result is:

`SIGNAL_GATED_RELATION_JUSTIFIED`

for the declared A013 mixed workload.

This result does not replace A005 or A012. A005 remains `VECTOR_SUFFICIENT`
for its qualified retrieval workload. A012 remains
`EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED` for its frozen relation-dependent
workload.

## 2. Oracle boundary discovered during design

A012's controlled benchmark accepts expected target memory IDs so it can measure
path recovery and terminate as soon as a known benchmark target is found. That
is valid for A012 measurement but is not a suitable production-style recall
control contract because a runtime request normally does not know the answer ID
in advance.

A013 therefore introduces target-free bounded relation expansion:

- runtime expansion receives vector-derived seed memory IDs;
- runtime expansion receives an explicit relation allowlist;
- runtime expansion receives only bounded traversal controls;
- expected answer IDs remain benchmark evaluator metadata;
- runtime request dataclasses contain no expected-target or answer field.

This avoids carrying the A012 benchmark oracle into the post-A012 integration
layer.

## 3. Compared policies

All three variants use the same A005 `ExactVectorMemoryIndex` query input.

### VECTOR_ONLY

Return vector retrieval evidence only. Do not invoke relation expansion.

### ALWAYS_RELATION

Use returned vector memory IDs as seeds and invoke target-free bounded relation
expansion for every valid case that has a vector seed.

### SIGNAL_GATED_RELATION

Use the same vector retrieval, but invoke target-free bounded relation expansion
only when an explicit typed `StructuralNeed` contains required relation
semantics.

The primary A013 experiment deliberately does not use an LLM or unconstrained
natural-language classifier to infer structural need.

## 4. Runtime implementation

A013 adds:

`src/flywire_asca/relational_activation/`

with:

- `models.py`
- `index.py`
- `runner.py`
- `benchmark.py`
- `__init__.py`

Important contracts include:

- `RelationalActivationPolicy`
- `RelationalActivationDecision`
- `StructuralNeed`
- `ExpansionRequest`
- `ExpansionPathEvidence`
- `ExpansionResult`
- `HybridRecallRequest`
- `HybridRecallResult`
- `TargetFreeRelationIndex`
- `run_hybrid_recall`

The architecture audit allows only:

`relational_activation -> {contracts, embedding, vector_memory, relational_reasoning}`

A013 does not modify the frozen A009 integrated loop or other A011-protected
cognitive source blobs.

## 5. Traversal safety contract

A013 preserves A012 traversal semantics while removing target awareness:

- directed edges only;
- explicit typed relation allowlist;
- proposition-confidence threshold;
- deterministic edge order:
  1. activation weight descending;
  2. proposition confidence descending;
  3. edge ID lexical;
- maximum 3 hops;
- maximum 8 visited nodes;
- maximum 32 scanned edges;
- cycle suppression;
- no duplicate visited nodes;
- no implicit inverse relation;
- no `SAME_NAME` to `SAME_PERSON` promotion;
- exact edge/evidence path provenance;
- no invented seed if vector retrieval returns none;
- no LLM traversal decision;
- no persistent graph database;
- no real tool or side-effect execution.

## 6. Frozen workload

Frozen A013 fixture SHA256:

`fcd805a5229bfad43f8eed6999be37ae61168dda1a8560f04370b3df0262baa5`

The fixture contains 17 cases:

- 16 valid;
- 1 invalid-contract control;
- 6 relation-dependent positives;
- 4 structural fail-closed controls;
- 6 direct-vector/non-structural controls.

Relation-dependent positives cover:

- ownership/workplace;
- causal;
- temporal;
- two-hop part-of;
- used-for;
- same-name disambiguated ownership.

Structural controls cover:

- cycle suppression;
- low-confidence edge rejection;
- relation allowlist;
- missing target.

The whole fixture and every shared case input have literal SHA256 anchors in
source. The qualifier rejects silent fixture drift.

## 7. Frozen portable evidence

Valid-case correctness:

| Metric | Vector only | Always relation | Signal gated |
| --- | ---: | ---: | ---: |
| Successes | 10/16 | 16/16 | 16/16 |
| Relation-positive successes | 0/6 | 6/6 | 6/6 |
| Direct-vector successes | 6/6 | 6/6 | 6/6 |
| Relation-only recoveries | — | 6 | 6 |
| Regressions vs vector-only | — | 0 | 0 |

Relation work:

| Metric | Always relation | Signal gated |
| --- | ---: | ---: |
| Relation invocations | 16 | 10 |
| Scanned edges | 16 | 11 |
| Relation visited nodes | 29 | 18 |

Safety/integrity:

- false signal activations: 0;
- missed signal activations: 0;
- identity failures: 0;
- provenance failures: 0;
- budget violations: 0;
- duplicate-visit failures: 0;
- deterministic repeat: true.

The predeclared decision rules therefore derive:

`SIGNAL_GATED_RELATION_JUSTIFIED`

The claim is only that the explicit typed signal preserved the always-on
relation correctness on this frozen mixed workload while avoiding unnecessary
relation work on non-structural controls.

## 8. Qualification topology

Primary qualifier:

`scripts/qualify_relational_activation_a013.py`

It is deterministic, network-free, and Ollama-free. It validates:

- fixture SHA;
- case IDs and ordering;
- per-case shared-input SHAs;
- raw policy evidence;
- aggregate counts;
- safety metrics;
- decision vocabulary and decision derivation.

No mandatory A013 physical replay was added. The primary variable in A013 is
the deterministic activation policy after a vector seed, not embedding quality.
A012 remains the physical relation-retrieval evidence boundary.

Local canonical A013 JSON SHA256 observed during development:

`2cf1f5183f40f2c68c5c73c6968f464955f03aceddc9fbd860c65fa35f6ba722`

## 9. CI repair evidence retained

A013 intentionally preserves two failed-run diagnostics rather than hiding
them.

### 9.1 Activation lifecycle failure

Activation commit:

`bfebc8dbb824a13c2e2312a9a18e144f1fe72668`

CI run:

`38087294056`

Result:

- 997 passed;
- 1 failed.

Cause: the historical A012 ledger test still asserted ownership of mutable
`CURRENT.md` after A013 activation.

Repair: A012 historical tests now validate A012's immutable historical
artifacts, while the generic current-ledger test owns mutable CURRENT/ROADMAP
state.

### 9.2 Linux synthetic A011 fixture failure

Initial implementation commit:

`1ad2f606de8efcf7aa9d20cf65e095830061d829`

CI run:

`38088167589`

Result:

- 1002 passed;
- 31 failed.

Cause: historical A011 qualification tests reconstructed a frozen A011
candidate by hard-coding removal of only the A012 `relational_reasoning`
package. Once committed A013 source existed in Git HEAD, the synthetic clone
retained `relational_activation`, and the unchanged strict production A011
source-universe guard correctly rejected the candidate.

Repair commit:

`1dcb0d243ad82cfa53faff2279bc667119faf77c`

The test fixture now:

1. reads the immutable frozen A011 profile;
2. derives the exact protected cognitive Python source set;
3. derives the current Git-tree cognitive source set using the same scope;
4. removes only post-A011 extras inside the synthetic test clone;
5. fails if any protected path is missing;
6. verifies the reconstructed set exactly equals the frozen profile.

The production A011 guard was not weakened.

Targeted historical qualification after the generic repair:

`386 passed in 83.41s`

A011 frozen anchors remained unchanged.

## 10. Local final development qualification

After the generic A011 fixture repair:

- full pytest: `1033 passed in 81.63s`;
- architecture audit: PASS;
- repository qualifier: PASS;
- A003 portable: PASS;
- A008 portable: PASS;
- A009 portable: PASS;
- A010 portable: PASS;
- A011 frozen preservation: PASS;
- A012 portable: PASS;
- A013 portable: PASS;
- compile: PASS;
- `git diff --check`: PASS.

## 11. Exact GitHub evidence

Final feature head:

`1dcb0d243ad82cfa53faff2279bc667119faf77c`

Exact feature push CI:

- run `38088579496`;
- result: GREEN;
- A013 artifact:
  `a013-relational-activation-38088579496-1`;
- GitHub artifact digest:
  `sha256:4c406ddfc95408f832d3c89dea667f9cc93a035feb9a05a96734ea0fb770fb4c`.

Pull Request:

- PR #17;
- head: `1dcb0d243ad82cfa53faff2279bc667119faf77c`;
- base: `ff1f6e6b779a662f4a10aae955f8c7ce1a934b45`;
- exact PR CI run `38088663875`: GREEN;
- PR A013 artifact:
  `a013-relational-activation-38088663875-1`;
- GitHub artifact digest:
  `sha256:a3b5fe924033492b6828a7c0e7364ae3348dcddf4d37a0177f41518df8d11245`.

Normal merge commit:

`92f534a25771ffabf06f4076bc6b7deb27bd80b5`

Exact integration/main CI:

- run `38088760197`;
- result: GREEN;
- exact head:
  `92f534a25771ffabf06f4076bc6b7deb27bd80b5`;
- A013 artifact:
  `a013-relational-activation-38088760197-1`;
- GitHub artifact digest:
  `sha256:7cde5442f4d905a42d312e4a11e0707d9c82c610ba489f0af185cf9f666f0b1d`.

## 12. Historical conclusions preserved

A013 does not rewrite prior evidence:

- A005: `VECTOR_SUFFICIENT` for A005's qualified scope;
- A006: `NOT_SUPPORTED`;
- A007: `SUPPORTED`;
- A008: `SUPPORTED`;
- A009: `SUPPORTED`;
- A010: `NOT_SUPPORTED`;
- A011 frozen v0.x: `ENGINEERING_QUALIFIED`;
- A012: `EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED` for A012's frozen scope;
- A013: `SIGNAL_GATED_RELATION_JUSTIFIED` for A013's frozen mixed scope.

A011's frozen profile SHA256 remains:

`add06f285bf6decc7d492b987d3769dc64db4cb3d0177c8c6586d50ee5f6d46d`

with 67 protected paths and protected Git mode/path/blob SHA256:

`8df49f05fe54de43667ab2f8ef5de2caae9376ffedf2cb8f8d26f0e4abcca6b6`

## 13. Claims boundary

A013 does not establish:

- that a model can infer `StructuralNeed` correctly from unconstrained text;
- that relation traversal should always be disabled without an explicit signal
  in every future architecture;
- that a persistent graph database is required;
- general graph superiority;
- lower FLOPs, energy, RAM, tokens, or wall-clock latency;
- autonomous relation learning;
- production safety;
- safe real-world side effects;
- AGI, consciousness, or biological equivalence.

## 14. Closure state

A013 is complete after exact feature, PR, and integration qualification.

No A014 milestone is activated by this closure.

FlyWireLLM was not modified.

No release, tag, or version promotion was performed.
