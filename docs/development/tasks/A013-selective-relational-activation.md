# A013 — Selective Relational Activation / Hybrid Recall Integration Gate

Status: DONE
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
- [x] Design/plan/lifecycle activation committed.
- [x] Runtime relation expansion accepts no expected target IDs.
- [x] StructuralNeed is explicit, typed, deterministic, and target-free.
- [x] Three policies share identical vector retrieval inputs.
- [x] Relation expansion is directed, bounded, cycle-safe, deterministic, and provenance-preserving.
- [x] Mixed portable fixture includes relation positives, structural negatives, and >=6 non-structural vector controls.
- [x] Fixture and per-case fingerprints are frozen and validated.
- [x] Decision is derived from predeclared rules.
- [x] A011 protected source anchors remain unchanged.
- [x] A012 portable qualifier remains unchanged and GREEN.
- [x] Full tests/audit/repository qualification/whitespace pass.
- [x] Exact feature/PR/main CI and artifact evidence recorded.
- [x] FlyWireLLM remains untouched.

## Evidence

Activation preflight:

- local main HEAD: `ff1f6e6b779a662f4a10aae955f8c7ce1a934b45`;
- origin/main: same SHA;
- ahead/behind: 0/0;
- worktree: clean;
- exact closure CI run `38068100925`: success on the activation base;
- Issue #14: closed/completed;
- Issue #16: open;
- activation commit: `bfebc8dbb824a13c2e2312a9a18e144f1fe72668`;
- activation push CI run `38087294056`: failed only because historical A012 ledger test still owned mutable `CURRENT.md`; Linux result was 997 passed / 1 failed;
- A012 ledger ownership repaired so historical A012 tests no longer assert the mutable current milestone;
- clean local full suite after repair: `1033 passed in 90.32s`;
- architecture audit: PASS;
- repository qualification: PASS;
- A003/A008/A009/A010 portable gates: PASS;
- A011 preservation: PASS, 67 protected paths with profile/protected anchors unchanged;
- A012 portable decision remains `EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED`;
- A013 frozen fixture SHA256: `fcd805a5229bfad43f8eed6999be37ae61168dda1a8560f04370b3df0262baa5`;
- A013 portable decision: `SIGNAL_GATED_RELATION_JUSTIFIED`;
- A013 valid successes (vector/always/signal): `10/16/16`;
- A013 relation invocations (signal/always): `10/16`;
- A013 scanned edges (signal/always): `11/16`;
- regressions, false/missed activation, identity, provenance, budget, and duplicate-visit failures: 0;
- compile and `git diff --check`: PASS.

## Current Action

A013 is integrated and complete. Frozen primary result:
`SIGNAL_GATED_RELATION_JUSTIFIED`.

Exact GitHub chain:

- final feature head: `1dcb0d243ad82cfa53faff2279bc667119faf77c`;
- feature CI `38088579496`: GREEN;
- feature A013 artifact digest:
  `sha256:4c406ddfc95408f832d3c89dea667f9cc93a035feb9a05a96734ea0fb770fb4c`;
- PR #17 exact CI `38088663875`: GREEN;
- PR A013 artifact digest:
  `sha256:a3b5fe924033492b6828a7c0e7364ae3348dcddf4d37a0177f41518df8d11245`;
- normal merge commit:
  `92f534a25771ffabf06f4076bc6b7deb27bd80b5`;
- exact integration/main CI `38088760197`: GREEN;
- integration A013 artifact digest:
  `sha256:7cde5442f4d905a42d312e4a11e0707d9c82c610ba489f0af185cf9f666f0b1d`.

Final report:
`docs/development/reports/ASCA-20261011-A013-selective-relational-activation.md`

Full-session handoff:
`docs/development/reports/ASCA-20261011-full-session-handoff-a013-completed.md`

## Next Action

No A014 milestone is activated automatically.

Issue #16 may be closed as completed only after the A013 closure-metadata commit
on main receives exact CI GREEN. Future work must start from a separately scoped
milestone and live-state verification.
