# FlyWireASCA A002 Architecture Contract Qualification

Date: 2026-10-08
Task: A002 — ASCA Architecture Contract
GitHub Issue: #2
Branch: research/a002-architecture-contract

## Decision

A002 implementation candidate is GREEN on exact commit
`c70e11f1af9cf652b8526f300a9c1d7317e5b6de`.

This report and the task transition form the documentation closure layer.
The closure commit itself must also pass GitHub Actions before A002 is treated
as finally integrated on `main`.

## Contract delivered

ASCA Contract v0.1 now defines implementation-neutral public records for:

- evidence and cues;
- memory records;
- typed association relations;
- explicit activation budgets and activation state;
- bounded working sets;
- uncertainty, surprise, and risk signals;
- procedure references and observations;
- deterministic JSON round-trip serialization;
- baseline modes and evaluation metric vocabulary.

The contract intentionally does not implement familiarity scoring, associative
retrieval, routing policy, surprise-control behavior, procedural learning, a
storage backend, or a neural architecture.

## Exact implementation qualification

Qualified candidate commit:

`c70e11f1af9cf652b8526f300a9c1d7317e5b6de`

Fresh local evidence on that exact commit:

- `python -m pytest -q`: **41 passed**
- `python scripts/audit_architecture_contract.py`:
  **architecture_contract_audit=PASS**
- `python scripts/qualify_repository.py`:
  **repository_qualification=PASS**
- `git diff --check HEAD^ HEAD`: PASS
- worktree: clean

GitHub Actions branch evidence:

- workflow: CI
- run id: `37793506259`
- head SHA: `c70e11f1af9cf652b8526f300a9c1d7317e5b6de`
- event: push
- conclusion: **success**

## Contract invariants qualified

The tests and architecture audit verify:

- `same_person`, `same_name`, and `similar_to` are distinct relation
  types;
- activation weight is separate from proposition confidence;
- probability fields reject values outside [0, 1];
- working sets reject duplicate references and explicit budget overflow;
- activation budgets are explicit;
- required retrieval states are frozen;
- supported nested contract records serialize deterministically and round-trip;
- benchmark vocabulary includes dense/direct and the ASCA ablation modes;
- A002 adds no mandatory runtime dependency;
- ASCA source does not import `flywire_llm`;
- contract version is `0.1`.

## Qualification finding corrected

The first Task 5 local candidate at commit
`5dc98ebb53eb036ca9469eae67eb46bb30b67485` failed
`git diff --check` because two Markdown metadata lines in
`ASCA-CONTRACT-v0.1.md` had trailing spaces used as hard line breaks.

A regression test,
`test_contract_document_has_no_trailing_whitespace`, reproduced the finding
before the correction. The document was normalized without weakening CI.
The resulting candidate `c70e11f...` passed the full local gate and exact
branch CI.

## FlyWireLLM isolation evidence

FlyWireLLM remained a separate live workload throughout A002.

At branch qualification capture:

- repository:
  `T:\Space\Projects\ProjectsAI\FlyWireLLM`
- HEAD:
  `fc949583a7ecbbf3e717021efc9a3183295cb9e5`
- branch:
  `research/l004-base50m-pretraining`
- worktree: clean
- ahead/behind: 0/0
- training parent PID: 16328
- training child PID: 3868
- command:
  `scripts\run_pretraining_post_warmup_sustained_l004.py --external-root T:\Space\Projects\ProjectsAI\FlyWireLLM-data`
- child working set observed around 2.24 GB

A002 did not stop, restart, modify, import, or invoke the FlyWireLLM training
runtime. FlyWireLLM remains reserved as a future model-adapter candidate after
its training is independently complete and qualified.

## Deferred choices

A002 deliberately leaves open:

- graph/vector/embedded storage;
- familiarity implementation;
- activation score and decay formulas;
- memory consolidation;
- Transformer, SSM, MoE, or other model core;
- FlyWireLLM adapter design;
- autonomous learning policy;
- robotics/perception integration.

## Next milestone

A003 — Familiarity System.

A003 is **PLANNED** only. Closing A002 does not activate A003 automatically.
