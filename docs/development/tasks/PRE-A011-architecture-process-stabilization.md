# PRE-A011 — Architecture & Process Consistency Stabilization

Status: ACTIVE
GitHub Issue: #11
Branch: maintenance/pre-a011-architecture-process-stabilization
Activation base: c8211fff43523b80c66fcfecff9088970d6c9981
Exact activation-base CI: 38020908291 — success
Baseline: 531 passed

Approved design:
`docs/superpowers/specs/2026-10-10-pre-a011-architecture-process-stabilization-design.md`

Approved implementation plan:
`docs/superpowers/plans/2026-10-10-pre-a011-architecture-process-stabilization.md`

## Goal

Make FlyWireASCA qualification-ready for A011 by removing architecture/process
inconsistency and justified maintenance debt while preserving cognitive behavior
and all frozen research evidence.

## Scope

- current architecture snapshot;
- qualification matrix;
- task-lifecycle ownership cleanup;
- stronger repository lifecycle qualification;
- package dependency/no-cycle auditing;
- CI/qualification consistency;
- stale documentation/formatting cleanup;
- bounded behavior-preserving maintainability cleanup.

## Non-scope

- A011 implementation or issue activation;
- A009/A010 retrieval optimization;
- benchmark retuning;
- frozen fixture/fingerprint/threshold/model identity changes;
- cognitive semantic changes;
- forced shared Ollama HTTP transport abstraction;
- benchmark splitting solely because files are large;
- FlyWireLLM changes.

## Behavior Freeze

Source cleanup is allowed only when characterization and regression evidence prove
that public behavior, serialized evidence, frozen fixtures/fingerprints,
thresholds, model identities, and historical outcomes are unchanged.

## Preserved Outcomes

- A006: `NOT_SUPPORTED`
- A007: `SUPPORTED`
- A008: `SUPPORTED`
- A009: `SUPPORTED`
- A010: `NOT_SUPPORTED`

A011 remains PLANNED with no GitHub issue.

FlyWireLLM remains untouched.

## Phases

- [x] Design approved.
- [x] Implementation plan approved.
- [x] PRE-A011 Issue #11 created.
- [x] Isolated maintenance worktree created.
- [x] Canonical architecture/qualification documentation published.
- [x] Historical lifecycle tests decoupled from mutable CURRENT/ROADMAP state.
- [x] Repository lifecycle qualifier hardened.
- [x] Package dependency direction/no-cycle audit enforced.
- [x] CI/qualification matrix aligned.
- [x] Justified maintainability cleanup completed.
- [x] Full portable and physical verification GREEN.
- [x] Whole-change review GREEN.
- [ ] Reviewed main integration and exact main CI GREEN.
- [ ] Issue #11 closed completed.
- [ ] CURRENT returned to A011 / PLANNED / no issue.

## Acceptance Criteria

- PRE-A011 never becomes an A-numbered ROADMAP milestone.
- A001-A010 remain DONE; A011 remains PLANNED until a later explicit gate.
- Historical outcomes remain unchanged.
- No cognitive semantic change is mixed into cleanup.
- Repository qualifier catches lifecycle/document inconsistency.
- Architecture audit catches undeclared package dependencies and cycles.
- Qualification matrix matches portable CI/local physical topology.
- Any source cleanup has characterization plus physical evidence.
- FlyWireLLM remains untouched.

## Maintainability Decisions

- Shared private JSON shape validation: **refactored** into
  `flywire_asca.contracts.validation` with caller-selected protocol exception
  types. Model/embedding HTTP transports, request payloads, timeouts, identity
  checks, and public adapter APIs remain separate and unchanged.
- Shared Ollama HTTP transport: **not refactored**. Model and embedding adapters
  intentionally retain distinct protocol/timeout/unavailable exception domains;
  forcing a common transport would add abstraction complexity beyond the
  duplication removed here.
- A009/A010 benchmark modules: **not split**. File size alone is not a sufficient
  cohesion boundary, and pre-A011 splitting would add regression surface without
  improving evidence validity.
- A009/A010 retrieval scheduling/cache behavior: **not changed**. Optimizing the
  A010 retrieval-work weakness would be a new research hypothesis, not
  maintenance cleanup.

## Qualification Evidence

Pre-review qualified behavior SHA:

`1c1f79a2213e248a0e1ea383943eee7281f1231a`

Fresh portable gate:
- qualified behavior suite: `552 passed`;
- closure-candidate local suite after report/tests: `556 passed`;
- architecture contract audit: PASS;
- repository qualification: PASS;
- A003/A008/A009/A010 portable qualification: PASS;
- A009 fingerprint:
  `2f92b5092de346f62879ac2cbb9f96d6de5d6f919e12d0693345c8228b01ab2a`;
- A010 fingerprint:
  `69d20542cd1e7e5c25a0fb61b9060f622379206b519da3cec7624e00bb6e5d4c`.

Fresh local physical matrix:
- A004: GREEN;
- A005: GREEN;
- A006: GREEN with `NOT_SUPPORTED`;
- A007: GREEN with `SUPPORTED`;
- A009: GREEN with portable outcome `SUPPORTED`;
- A010: GREEN with portable outcome `NOT_SUPPORTED`.

Qualification report:

`docs/development/reports/ASCA-20261010-PRE-A011-architecture-process-stabilization.md`

## Whole-change Review Evidence

Whole-change review: GREEN

Review method: **author self-review**. No independent reviewer/subagent mechanism
is available in this harness, so this is not described as independent reviewer
or peer-review evidence.

- Critical findings: 0
- Important findings: 3 — fixed
- Minor findings: 1 — fixed
- post-review local full suite: `561 passed`
- architecture contract audit: PASS
- repository qualification: PASS
- post-review portable A003/A008/A009/A010 qualification: PASS
- exact pre-review branch CI after whitespace-gate repair:
  `38022892597` — success
- earlier branch CI `38022744129`: failed only on trailing whitespace in a
  newly committed report; this exposed the missing staged local whitespace
  check and led to the `git diff --cached --check` workflow rule.

Important findings fixed:

1. lifecycle qualifier now rejects duplicate CURRENT fields, ACTIVE issue-number
   mismatch between CURRENT and its task file, and ambiguous active issue state;
2. architecture dependency audit now catches sibling relative imports such as
   `from .. import model`;
3. malformed A-numbered ROADMAP-like rows now fail closed instead of disappearing
   from parsing.

Minor finding fixed:

- whole-range trailing whitespace in the canonical pre-A011 snapshot and
  qualification matrix was removed.

No cognitive behavior, frozen fixture/fingerprint, model identity, threshold, or
historical research outcome changed during review fixes.

## Current Action

Task 8 — whole-change review GREEN; exact post-review branch CI pending.

## Next Action

Commit/push the review fixes, require exact post-review feature-branch CI, then
verify integration preconditions and fast-forward reviewed behavior to main.
