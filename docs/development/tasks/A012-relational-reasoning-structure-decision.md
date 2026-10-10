# A012 — Relational Reasoning / Structure Decision Gate

Status: ACTIVE
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
- [ ] Both variants share the real A005 retrieval primitive and frozen shared inputs.
- [ ] Explicit traversal is directed, deterministic, bounded and cycle-safe.
- [ ] Relation and identity semantics are not inferred beyond explicit evidence.
- [ ] Edge/evidence provenance is retained for accepted paths.
- [ ] Frozen portable workload includes positive, negative and vector-direct controls.
- [ ] Fixture/shared-input fingerprints are stable and validated.
- [ ] Architecture decision is evidence-derived.
- [ ] Portable qualifier is Ollama-free and present in CI.
- [ ] Physical secondary replay is local-only.
- [ ] A011 frozen protected-source identities remain unchanged.
- [ ] Full tests, architecture audit, repository qualifier and whitespace check pass.
- [ ] Exact feature/main CI and final evidence are recorded before closure.
- [ ] FlyWireLLM remains untouched.

## Evidence

Activation and implementation evidence will be appended after the task becomes
ACTIVE. Historical authority:

- A005 final graph decision: `VECTOR_SUFFICIENT` for retrieval scope.
- A005 report explicitly allows a later relation/path reasoning experiment.
- A011 full-system v0.x qualification is complete and remains a frozen profile.

## Current Action

A012 is ACTIVE on GitHub Issue #14. Begin TDD implementation of strict records
and bounded explicit relation traversal.

## Next Action

Implement Task 2 records/models RED -> GREEN, then Task 3 bounded traversal.
