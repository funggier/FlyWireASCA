# A013 — Selective Relational Activation / Hybrid Recall Integration Gate Plan

Date: 2026-10-11
Issue: #16
Activation base: `ff1f6e6b779a662f4a10aae955f8c7ce1a934b45`

Approved design:
`docs/superpowers/specs/2026-10-11-a013-selective-relational-activation-design.md`

## Task 1 — Activate lifecycle and freeze design

- Record A013 in CURRENT/ROADMAP.
- Create A013 task ledger as ACTIVE.
- Record branch/worktree and activation base.
- Add lifecycle tests.
- Commit design/plan/activation metadata before implementation.

## Task 2 — Define target-free contracts

Add `src/flywire_asca/relational_activation/` with:

- policy enum:
  - `VECTOR_ONLY`
  - `ALWAYS_RELATION`
  - `SIGNAL_GATED_RELATION`
- architecture-decision enum;
- `StructuralNeed`;
- target-free expansion request/result/path evidence;
- hybrid recall result with separate vector and relation provenance.

Tests must prove no target/expected-answer field exists in runtime request types.

## Task 3 — Implement target-free bounded expansion

Implement deterministic directed expansion using A012 safety semantics:

- relation allowlist;
- confidence threshold;
- A012 ordering;
- max 3 hops / 8 visited nodes / 32 edge scans;
- cycle suppression;
- exact path/evidence provenance;
- no invented seed;
- fail closed on empty vector retrieval.

Unit tests cover ordering, cycles, low confidence, allowlist, node/edge/hop
budgets, provenance, same-name identity separation, and deterministic replay.

## Task 4 — Implement hybrid recall policies

Create a runner that:

1. performs the same A005 vector query for every policy;
2. derives relation seeds only from returned vector memory IDs;
3. applies the policy using only `StructuralNeed`;
4. never consumes expected target IDs;
5. merges reached IDs without identity collapse;
6. records vector query/scoring and relation work separately.

Add policy tests including explicit false/missed activation accounting.

## Task 5 — Freeze mixed portable benchmark

Build a literal deterministic fixture containing:

- 6 relation-dependent positives;
- 4 structural fail-closed controls;
- >=6 direct-vector non-structural controls;
- 1 invalid-contract control.

Expected answers stay in benchmark metadata only.

Freeze:

- case IDs;
- whole fixture SHA256;
- per-case shared input SHA256 values.

Add tamper tests.

## Task 6 — Implement portable qualifier

Add `scripts/qualify_relational_activation_a013.py`.

Qualifier must:

- rerun deterministically;
- validate literal fingerprints;
- validate raw case evidence and aggregates;
- derive one of the four predeclared decisions;
- treat valid negative/mixed decisions as process PASS;
- optionally write canonical JSON evidence.

## Task 7 — Architecture and CI integration

Update architecture audit to permit only:

`relational_activation -> {contracts, embedding, vector_memory, relational_reasoning}`

Add negative tests for forbidden dependency directions/cycles.

Update qualification matrix and CI:

- keep A012 portable qualification;
- keep physical runners out of CI;
- add A013 portable qualification and artifact upload.

Do not edit A011-protected cognitive source blobs.

## Task 8 — Development qualification

Run:

- focused A013 tests;
- full pytest;
- architecture audit;
- repository qualifier;
- A003/A008/A009/A010 portable qualifiers;
- A011 preservation;
- A012 portable qualifier;
- A013 portable qualifier;
- compile checks;
- `git diff --check`.

Record exact counts, fixture hash, result metrics, and local HEAD.

## Task 9 — Exact GitHub qualification

- push feature branch;
- require exact feature CI GREEN;
- create PR;
- require exact PR CI GREEN;
- review whole change;
- normal merge only;
- require exact integration/main CI GREEN;
- verify A013 artifact hash.

No reset/clean/rebase/force-push.

## Task 10 — Closure

Write final evidence report and full-session handoff.

Update:

- A013 task -> DONE;
- CURRENT -> A013 DONE;
- ROADMAP -> A013 DONE;
- README current stage.

Commit closure metadata on main, require exact main CI GREEN, comment exact
evidence to Issue #16, then close Issue #16 as completed.

Do not auto-activate A014. No release/tag/version promotion.
