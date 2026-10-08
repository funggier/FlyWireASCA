# A002 — ASCA Architecture Contract

Status: DONE
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
- Exact qualification and closure: DONE.

## Acceptance Criteria

- [x] Public contracts are importable and immutable where practical.
- [x] Required retrieval states and typed relation vocabulary are frozen.
- [x] Confidence/proposition confidence are validated independently of activation strength.
- [x] Activation/working-set budgets are explicit and validated.
- [x] Supported contract records serialize deterministically and round-trip.
- [x] Required non-selective/selective benchmark modes are defined.
- [x] Architecture audit passes with no mandatory runtime dependency or FlyWireLLM import.
- [x] Full local test suite passes on exact candidate.
- [x] GitHub Actions passes on exact candidate; final closure commit must pass before issue closure.
- [x] Branch candidate synchronization evidence is recorded; final main synchronization is an external closure gate.
- [x] FlyWireLLM training process and repository are not modified by A002.

## Evidence

Baseline at A002 start:

- base commit: `6f78b09ade14bec73b7689da3efa35016288c189`;
- baseline tests: `16 passed`;
- worktree: clean;
- FlyWireLLM training observed running separately and left untouched.

Exact implementation candidate: `c70e11f1af9cf652b8526f300a9c1d7317e5b6de`

- full pytest: 41 passed;
- architecture contract audit: PASS;
- repository qualifier: PASS;
- GitHub Actions run `37793506259`: success on exact candidate;
- closure report: `docs/development/reports/ASCA-20261008-A002-architecture-contract.md`.

## Current Action

A002 implementation and evidence are complete in the closure candidate.

## Next Action

Require CI on the closure commit, fast-forward `main`, verify exact main CI and
0/0 synchronization, then close GitHub Issue #2. A003 remains PLANNED.
