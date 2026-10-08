# A002 — ASCA Architecture Contract

Status: ACTIVE
GitHub Issue: #2
Branch: research/a002-architecture-contract

## Goal

Freeze ASCA contract version 0.1 as implementation-neutral typed interfaces,
invariants, deterministic serialization, and benchmark definitions without
implementing cognitive algorithms.

## Scope

In scope:

- typed cues, evidence, memories, and relations;
- explicit activation budgets and working-set contracts;
- uncertainty/surprise, procedure, and observation contracts;
- deterministic serialization/round-trip behavior;
- benchmark/baseline vocabulary;
- architecture invariants and audit;
- exact-commit CI qualification.

Out of scope:

- familiarity algorithm;
- associative retrieval/storage backend;
- selective routing policy;
- surprise-control behavior;
- procedural learning/chunking;
- FlyWireLLM integration or training.

## Phases

- Core memory/provenance contracts: DONE.
- Bounded control/procedure contracts: DONE.
- Serialization and benchmark definitions: DONE.
- Architecture audit/documentation: DONE.
- Exact qualification and closure: ACTIVE.

## Acceptance Criteria

- [ ] Public contracts are importable and immutable where practical.
- [ ] Required retrieval states and typed relation vocabulary are frozen.
- [ ] Confidence/proposition confidence are validated independently of activation strength.
- [ ] Activation/working-set budgets are explicit and validated.
- [ ] Supported contract records serialize deterministically and round-trip.
- [ ] Required non-selective/selective benchmark modes are defined.
- [ ] Architecture audit passes with no mandatory runtime dependency or FlyWireLLM import.
- [ ] Full local test suite passes on exact candidate.
- [ ] GitHub Actions passes on exact candidate and final closure commit.
- [ ] Branch/main synchronization evidence is recorded.
- [ ] FlyWireLLM training process and repository are not modified by A002.

## Evidence

Baseline at A002 start:

- base commit: `6f78b09ade14bec73b7689da3efa35016288c189`;
- baseline tests: `16 passed`;
- worktree: clean;
- FlyWireLLM training observed running separately and left untouched.

Further evidence is appended only after fresh verification.

## Current Action

Run Task 5 exact local qualification and push the A002 branch for exact CI.

## Next Action

After exact branch CI is GREEN, write A002 closure evidence, transition A003 to
PLANNED, qualify the closure commit, then fast-forward main without touching
FlyWireLLM training.
