# A012 — Relational Reasoning / Structure Decision Gate

Status: DONE
GitHub Issue: #14
Branch: research/a012-relational-structure-decision
Activation base: 23b96f4502b81cddb9563b55c26fdd0adc731265

Approved design:
`docs/superpowers/specs/2026-10-10-a012-relational-reasoning-structure-decision-design.md`

Approved implementation plan:
`docs/superpowers/plans/2026-10-10-a012-relational-reasoning-structure-decision.md`

## Goal

Test whether bounded explicit typed relation traversal is justified for
relation-dependent reasoning workloads beyond A005's qualified Vector + Metadata
retrieval scope.

A005's `VECTOR_SUFFICIENT` result remains valid for A005 retrieval scope.
A012 does not pre-decide that a graph is required.

## Scope

- real A005 Vector + Metadata comparison baseline;
- deterministic bounded traversal over existing Contract v0.1
  `AssociationEdge` records;
- causal, temporal, ownership, part-of, used-for, path, identity, cycle and
  negative controls;
- explicit provenance and search-budget accounting;
- portable primary architecture decision;
- optional local physical embedding replay as secondary evidence;
- CI and architecture-audit integration without changing the A011 frozen
  protected source set.

## Non-scope

- persistent graph database;
- automatic relation/edge learning;
- A005 threshold retuning;
- A006-A010 fixture/outcome changes;
- integration into the A009 cognitive loop during this milestone;
- real tool/OS/API side effects;
- memory consolidation or autonomous learning;
- FlyWireLLM;
- release/tag/version promotion.

## Architecture decisions

A012 may conclude exactly one of:

- `EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED`
- `VECTOR_METADATA_REMAINS_SUFFICIENT`
- `MIXED`

A valid negative/mixed research result does not make engineering qualification
fail.

## Acceptance Criteria

- [x] A012 lifecycle is activated with a real GitHub issue.
- [x] Both variants share the real A005 retrieval primitive and frozen shared inputs.
- [x] Explicit traversal is directed, deterministic, bounded and cycle-safe.
- [x] Relation and identity semantics are not inferred beyond explicit evidence.
- [x] Edge/evidence provenance is retained for accepted paths.
- [x] Frozen portable workload includes positive, negative and vector-direct controls.
- [x] Fixture/shared-input fingerprints are stable and validated.
- [x] Architecture decision is evidence-derived.
- [x] Portable qualifier is Ollama-free and prepared for CI.
- [x] Physical secondary replay is local-only and development replay is GREEN.
- [x] A011 frozen profile/67 protected-source identities remain guarded by a
  preservation check; the post-A011 HEAD is not relabelled A011-qualified.
- [x] Full tests, architecture audit, repository qualifier and whitespace check pass.
- [x] Exact feature/main CI and final evidence are recorded before closure.
- [x] FlyWireLLM remains untouched.

## Evidence

Development evidence before the exact candidate commit:

- Full repository test suite: `994 passed in 81.97s`.
- Architecture audit: PASS.
- Repository qualification: PASS.
- A003/A008/A009/A010 portable gates: PASS.
- A011 frozen-profile preservation: profile SHA256
  `add06f285bf6decc7d492b987d3769dc64db4cb3d0177c8c6586d50ee5f6d46d`,
  67 protected paths, protected SHA256
  `8df49f05fe54de43667ab2f8ef5de2caae9376ffedf2cb8f8d26f0e4abcca6b6`.
- A012 portable fixture SHA256:
  `dcabd86117f22e35c18fe605c8411da143962f112645a78c9124ec5987179aea`.
- A012 portable result: `EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED`; Vector +
  Metadata success 5/11, bounded-relation success 11/11, relation-only
  recoveries 6, regressions/identity/provenance/budget/duplicate-visit failures 0.
- Development physical replay on local `qwen3-embedding:0.6b`, digest
  `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`,
  dimension 1024, frozen threshold `0.5037018224299838`: experiment valid,
  observed decision `EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED`, Vector success
  2/11, relation-aware success 6/11, relation-only recoveries 4, deterministic
  repeat, zero regression/identity/provenance/budget/duplicate-visit failures.
- Whole-change review: no Critical/Important finding remains after TDD repairs
  for post-A011 CI topology, empty physical seed handling, and historical README
  compatibility.
- `git diff --check`: PASS.
- FlyWireLLM: untouched.
- Final feature head: `0728ddab442b774dcedb60a3fb7870444a95ffcb`.
- Exact feature push CI `38067495867`: GREEN.
- PR #15 exact CI `38067628031`: GREEN.
- Normal merge integration:
  `48dfc64bca60d62528787b57d04a01df04fac30d`.
- Exact integration/main CI `38067737917`: GREEN.
- Portable CI artifact SHA256 on feature/main:
  `760cad31a867c6f52613d1e3c5aa7a879528ac386dcbb570cb5cd9c587c86340`.
- Exact-clean final-head physical evidence SHA256:
  `35cbe908737f259f917d20bc67c779dbb7107df1393488cedd08899bbe441455`.

Historical authority:

- A005 final graph decision: `VECTOR_SUFFICIENT` for retrieval scope.
- A005 report explicitly allows a later relation/path reasoning experiment.
- A011 full-system v0.x qualification is complete and remains a frozen profile.

## Current Action

A012 implementation and integration are complete. Exact feature push CI
`38067495867`, PR #15 CI `38067628031`, and integration/main CI `38067737917`
are GREEN. Normal merge integration is
`48dfc64bca60d62528787b57d04a01df04fac30d`.

Final evidence report:
`docs/development/reports/ASCA-20261010-A012-relational-reasoning-structure-decision.md`.

## Next Action

Require exact main CI GREEN for the closure metadata commit containing this
task/report/handoff, then close GitHub Issue #14 as completed. Do not activate
A013 automatically.
