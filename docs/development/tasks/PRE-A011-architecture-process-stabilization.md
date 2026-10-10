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
- [ ] Canonical architecture/qualification documentation published.
- [ ] Historical lifecycle tests decoupled from mutable CURRENT/ROADMAP state.
- [ ] Repository lifecycle qualifier hardened.
- [ ] Package dependency direction/no-cycle audit enforced.
- [ ] CI/qualification matrix aligned.
- [ ] Justified maintainability cleanup completed.
- [ ] Full portable and physical verification GREEN.
- [ ] Whole-change review GREEN.
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

## Current Action

Task 1 — activate PRE-A011 maintenance gate.

## Next Action

Publish canonical architecture and qualification truth, then continue through the
approved implementation plan.