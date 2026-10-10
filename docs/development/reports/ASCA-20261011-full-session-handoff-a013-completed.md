# Full Session Handoff — A013 Completed

Date: 2026-10-11
Repository: `funggier/FlyWireASCA`
Milestone: A013 — Selective Relational Activation / Hybrid Recall Integration Gate
Status: DONE

## Resume authority

On any later session, verify live Git, GitHub, and runtime state first. Live
state overrides stale prose. Do not reset, clean, rebase, force-push, or remove
evidence worktrees/branches unless explicitly authorized.

FlyWireLLM is a separate project and was not touched.

## Final A013 conclusion

Frozen primary decision:

`SIGNAL_GATED_RELATION_JUSTIFIED`

Scope: the frozen A013 mixed portable workload using an explicit typed
`StructuralNeed` contract and target-free bounded relation expansion.

The result does not claim natural-language structural-need inference or general
graph superiority.

## Why A013 exists

A012 justified explicit bounded typed relation traversal for its
relation-dependent benchmark. A013 tested the next integration question:
whether that traversal should be invoked for all valid recalls or selectively.

A design review discovered that the A012 controlled benchmark request included
expected target memory IDs. This is acceptable benchmark instrumentation but
would be an oracle leak if reused as a general runtime recall API.

A013 therefore introduced a target-free post-A011 integration layer.

## Frozen benchmark result

Fixture SHA256:

`fcd805a5229bfad43f8eed6999be37ae61168dda1a8560f04370b3df0262baa5`

17 cases total:

- 16 valid;
- 1 invalid contract;
- 6 relation-dependent positives;
- 4 structural fail-closed controls;
- 6 non-structural direct-vector controls.

Results:

- vector-only success: 10/16;
- always-relation success: 16/16;
- signal-gated success: 16/16;
- relation-only recoveries: 6 for always and 6 for signal;
- regressions: 0;
- relation invocations: signal 10 vs always 16;
- scanned edges: signal 11 vs always 16;
- visited relation nodes: signal 18 vs always 29;
- false activations: 0;
- missed activations: 0;
- identity/provenance/budget/duplicate-visit failures: 0;
- deterministic repeat: true.

## Implementation

New package:

`src/flywire_asca/relational_activation`

Runtime request contracts are target-free.

Allowed architecture dependency:

`relational_activation -> {contracts, embedding, vector_memory, relational_reasoning}`

The A011-protected A009 integrated loop was not modified.

## A011 historical fixture hardening

A013 exposed a weakness in historical A011 **test-fixture construction**, not
the production A011 guard.

Old fixture logic hard-coded the post-A011 package that must be removed from a
synthetic frozen-A011 candidate. A013 generalized the fixture to reconstruct
the exact cognitive source set from the immutable A011 profile. This allows
future post-A011 packages without weakening the strict source-universe guard.

Production A011 anchors remain:

- profile:
  `add06f285bf6decc7d492b987d3769dc64db4cb3d0177c8c6586d50ee5f6d46d`;
- protected paths: 67;
- protected mode/path/blob:
  `8df49f05fe54de43667ab2f8ef5de2caae9376ffedf2cb8f8d26f0e4abcca6b6`.

## Development and repair history

Activation commit:

`bfebc8dbb824a13c2e2312a9a18e144f1fe72668`

Activation CI:

`38087294056` — failed 1 historical A012 mutable-ledger ownership test.

Initial implementation candidate:

`1ad2f606de8efcf7aa9d20cf65e095830061d829`

Implementation CI:

`38088167589` — failed 31 A011 historical qualification tests because the
synthetic frozen candidate retained newly committed A013 cognitive source.

Final feature repair/head:

`1dcb0d243ad82cfa53faff2279bc667119faf77c`

Clean local final suite:

`1033 passed in 81.63s`

Targeted historical qualification after generic A011 fixture repair:

`386 passed in 83.41s`

## Exact GitHub chain

Final feature CI:

- run: `38088579496`;
- head: `1dcb0d243ad82cfa53faff2279bc667119faf77c`;
- result: GREEN;
- A013 artifact digest:
  `sha256:4c406ddfc95408f832d3c89dea667f9cc93a035feb9a05a96734ea0fb770fb4c`.

PR #17:

- exact PR CI: `38088663875`;
- same head: `1dcb0d243ad82cfa53faff2279bc667119faf77c`;
- result: GREEN;
- A013 artifact digest:
  `sha256:a3b5fe924033492b6828a7c0e7364ae3348dcddf4d37a0177f41518df8d11245`.

Normal merge:

`92f534a25771ffabf06f4076bc6b7deb27bd80b5`

Exact integration/main CI:

- run: `38088760197`;
- head: `92f534a25771ffabf06f4076bc6b7deb27bd80b5`;
- result: GREEN;
- A013 artifact digest:
  `sha256:7cde5442f4d905a42d312e4a11e0707d9c82c610ba489f0af185cf9f666f0b1d`.

Canonical local A013 evidence JSON SHA256 observed during development:

`2cf1f5183f40f2c68c5c73c6968f464955f03aceddc9fbd860c65fa35f6ba722`

## Historical research outcomes after A013

- A006: `NOT_SUPPORTED`
- A007: `SUPPORTED`
- A008: `SUPPORTED`
- A009: `SUPPORTED`
- A010: `NOT_SUPPORTED`
- A011 frozen v0.x: `ENGINEERING_QUALIFIED`
- A012: `EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED` for A012 scope
- A013: `SIGNAL_GATED_RELATION_JUSTIFIED` for A013 scope

A005 remains `VECTOR_SUFFICIENT` for the A005 retrieval workload.

## Claims limits

Do not turn A013 into claims that:

- an LLM can infer structural need correctly;
- a persistent graph DB is now required;
- graph-first architecture is generally superior;
- A013 proves lower FLOPs, energy, RAM, tokens, or latency;
- relation learning is autonomous;
- real tool side effects are safe;
- ASCA is AGI, conscious, or biologically equivalent.

## Repository state rule after closure

A013 closure metadata should leave:

- A013 task: DONE;
- CURRENT: A013 DONE;
- ROADMAP: A013 DONE;
- no A014 automatically activated;
- PR #17 merged;
- Issue #16 closed as completed only after exact closure-main CI is GREEN;
- local main equal to origin/main and clean;
- no release/tag/version promotion.

The closure metadata commit itself must receive exact main CI before Issue #16
is closed.
