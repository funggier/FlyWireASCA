# A013 — Selective Relational Activation / Hybrid Recall Integration Gate

Status: ACTIVE
GitHub Issue: #16
Branch: research/a013-selective-relational-activation
Activation base: ff1f6e6b779a662f4a10aae955f8c7ce1a934b45

Approved design:
`docs/superpowers/specs/2026-10-11-a013-selective-relational-activation-design.md`

Approved implementation plan:
`docs/superpowers/plans/2026-10-11-a013-selective-relational-activation.md`

## Goal

Determine whether target-free bounded relation expansion should be always active
or selectively activated by an explicit structural-need contract on a mixed
recall workload, without leaking expected answer IDs into runtime control.

## Scope

- target-free bounded relation expansion;
- explicit typed `StructuralNeed` activation contract;
- `VECTOR_ONLY`, `ALWAYS_RELATION`, and `SIGNAL_GATED_RELATION` comparison;
- shared A005 vector retrieval;
- A012 ordering, relation, confidence, provenance, identity, and budget safety;
- frozen mixed portable workload and evidence-derived decision;
- portable CI qualification and evidence artifact;
- optional physical secondary replay only if it adds useful evidence.

## Non-scope

- expected-target IDs in runtime control;
- natural-language/LLM structural-intent classification;
- modifying A011-protected cognitive source blobs;
- changing A005/A006-A012 historical conclusions;
- full A009 cognitive-loop integration;
- persistent graph database;
- automatic relation learning;
- real tool/OS/API side effects;
- FlyWireLLM;
- release/tag/version promotion.

## Architecture decisions

A013 may conclude exactly one of:

- `SIGNAL_GATED_RELATION_JUSTIFIED`
- `ALWAYS_RELATION_PREFERRED`
- `RELATION_INTEGRATION_NOT_JUSTIFIED`
- `MIXED`

A valid negative or mixed research result does not make engineering
qualification fail.

## Acceptance Criteria

- [x] User explicitly authorized A013.
- [x] GitHub Issue #16 exists.
- [x] Activation base and clean worktree were verified from live Git.
- [ ] Design/plan/lifecycle activation committed.
- [ ] Runtime relation expansion accepts no expected target IDs.
- [ ] StructuralNeed is explicit, typed, deterministic, and target-free.
- [ ] Three policies share identical vector retrieval inputs.
- [ ] Relation expansion is directed, bounded, cycle-safe, deterministic, and provenance-preserving.
- [ ] Mixed portable fixture includes relation positives, structural negatives, and >=6 non-structural vector controls.
- [ ] Fixture and per-case fingerprints are frozen and validated.
- [ ] Decision is derived from predeclared rules.
- [ ] A011 protected source anchors remain unchanged.
- [ ] A012 portable qualifier remains unchanged and GREEN.
- [ ] Full tests/audit/repository qualification/whitespace pass.
- [ ] Exact feature/PR/main CI and artifact evidence recorded.
- [ ] FlyWireLLM remains untouched.

## Evidence

Activation preflight:

- local main HEAD: `ff1f6e6b779a662f4a10aae955f8c7ce1a934b45`;
- origin/main: same SHA;
- ahead/behind: 0/0;
- worktree: clean;
- exact closure CI run `38068100925`: success on the activation base;
- Issue #14: closed/completed;
- Issue #16: open.

## Current Action

Implement target-free relation-expansion contracts and tests in the isolated
A013 worktree.

## Next Action

Freeze the mixed benchmark, implement all three policies and the portable
qualifier, then run full local qualification before first feature push.
