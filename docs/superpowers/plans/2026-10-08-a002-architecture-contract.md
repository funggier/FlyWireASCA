# A002 ASCA Architecture Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Freeze ASCA contract version 0.1 as implementation-neutral typed Python interfaces, invariants, deterministic serialization, and benchmark definitions without implementing cognitive algorithms.

**Architecture:** A002 adds immutable standard-library data contracts under `flywire_asca.contracts`. The contracts separate routing/activation strength from proposition confidence, keep retrieval budgets explicit, preserve provenance, and define benchmark/control vocabulary while deliberately leaving storage engines, neural mechanisms, scoring formulas, and FlyWireLLM integration unfrozen.

**Tech Stack:** Python >=3.11 standard library, frozen dataclasses, `Enum`, `Protocol` only where required, JSON serialization, pytest, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-10-08-asca-architecture-design.md`

## Global Constraints

- Repository: public `funggier/FlyWireASCA`.
- Task: A002 — ASCA Architecture Contract, GitHub Issue #2.
- Work branch: `research/a002-architecture-contract`.
- ASCA contract version: `0.1`.
- No runtime dependency may be added.
- No FlyWireLLM import, checkpoint, model call, training command, or training-file mutation.
- No database/storage backend is selected.
- No familiarity, recall, routing, surprise-control, or skill-learning algorithm is implemented.
- Association activation strength and proposition confidence remain separate fields.
- Retrieval/working-set expansion is explicitly budgeted.
- Public contract records are immutable dataclasses where practical.
- Serialization must be deterministic and round-trip the supported contract records.
- Git/GitHub/runtime state overrides stale prose.
- Exact-commit CI and synchronization evidence are required before A002 closes.

## Review Focus

1. Same-name/similarity relations must remain typed and must not imply identity.
2. Confidence fields must reject values outside [0, 1] while activation weights remain a separate finite quantity.
3. Working sets must reject duplicate references and entries beyond their explicit budget.
4. Serialization must preserve enums, nested dataclasses, tuples, and optional values deterministically.
5. Architecture audit must fail if a mandatory runtime dependency or FlyWireLLM source import is introduced.

---

### Task 1: Activate A002 and define core memory/provenance contracts

**Files:**
- Create: `docs/development/tasks/A002-asca-architecture-contract.md`
- Modify: `docs/development/tasks/CURRENT.md`
- Modify: `docs/development/tasks/ROADMAP.md`
- Create: `src/flywire_asca/contracts/__init__.py`
- Create: `src/flywire_asca/contracts/enums.py`
- Create: `src/flywire_asca/contracts/validation.py`
- Create: `src/flywire_asca/contracts/memory.py`
- Create: `tests/test_contract_memory.py`

**Interfaces:**
- Produces enums: `CueKind`, `MemoryKind`, `RelationType`, `RetrievalState`.
- Produces records: `EvidenceRef`, `Cue`, `MemoryRecord`, `AssociationEdge`.
- All public records are frozen dataclasses.

- [ ] Write failing tests for exact enum members, probability validation, typed relations, nonempty IDs, and separation of `activation_weight` from `proposition_confidence`.
- [ ] Run focused tests and verify RED because `flywire_asca.contracts` does not exist.
- [ ] Implement minimal enums/validation/memory records.
- [ ] Update task ledger so A002 is the single ACTIVE task and Issue #2 is recorded.
- [ ] Run focused tests plus full suite; expect GREEN.
- [ ] Commit: `Add A002 core architecture contracts`.

### Task 2: Add bounded activation, working-set, procedure, and observation contracts

**Files:**
- Create: `src/flywire_asca/contracts/control.py`
- Create: `src/flywire_asca/contracts/procedure.py`
- Create: `tests/test_contract_control.py`
- Create: `tests/test_contract_procedure.py`

**Interfaces:**
- Produces `ActivationBudget(max_memory_nodes, max_relation_hops, max_working_set_items, max_model_input_tokens, max_expansions)`.
- Produces `ActivationState(node_id, activation, hop, source_cue_ids)`.
- Produces `WorkingSetEntry(ref_id, kind, activation, reason)`, `WorkingSet(entries, retrieval_state, budget)`.
- Produces `UncertaintySignal(uncertainty, surprise, risk, reasons)`.
- Produces `ProcedureRef` and `Observation`.

- [ ] Write failing tests for positive/nonnegative budgets, finite activation, duplicate working-set refs, budget overflow, retrieval states, uncertainty range, and procedure/observation identity fields.
- [ ] Verify RED.
- [ ] Implement minimal immutable records and validation.
- [ ] Run focused tests and full suite; expect GREEN.
- [ ] Commit: `Add bounded ASCA control contracts`.

### Task 3: Add deterministic contract serialization and baseline benchmark definitions

**Files:**
- Create: `src/flywire_asca/contracts/codec.py`
- Create: `src/flywire_asca/contracts/benchmark.py`
- Create: `tests/test_contract_codec.py`
- Create: `tests/test_contract_benchmark.py`

**Interfaces:**
- Produces `dumps_contract(record) -> str`.
- Produces `loads_contract(record_type, payload) -> record_type`.
- Produces `BaselineMode`, `EvaluationMetric`, `BenchmarkDefinition`.
- Required baselines: dense/direct, ASCA selective, ASCA without surprise expansion, ASCA without familiarity.

- [ ] Write failing nested round-trip/determinism tests for memory/control/procedure records.
- [ ] Verify RED.
- [ ] Implement recursive dataclass/enum/tuple/optional codec using standard library only.
- [ ] Write failing benchmark-definition tests for required baseline modes and evaluation metric vocabulary.
- [ ] Implement benchmark contracts.
- [ ] Run focused tests and full suite; expect GREEN.
- [ ] Commit: `Add ASCA contract serialization and benchmarks`.

### Task 4: Document invariants and add architecture audit

**Files:**
- Create: `docs/architecture/ASCA-CONTRACT-v0.1.md`
- Create: `scripts/audit_architecture_contract.py`
- Create: `tests/test_architecture_audit.py`
- Modify: `src/flywire_asca/contracts/__init__.py`

**Interfaces:**
- Produces `CONTRACT_VERSION = "0.1"`.
- Produces `audit_architecture_contract(root: Path) -> list[str]`.
- Audit must verify no required runtime dependencies, no `flywire_llm` source import, expected retrieval states/baselines, contract doc/version presence, and the activation/confidence field separation.

- [ ] Write failing audit tests including injected dependency and injected FlyWireLLM import fixtures.
- [ ] Verify RED.
- [ ] Implement minimal audit script.
- [ ] Write contract document covering invariants, deferred choices, compatibility expectations, and FlyWireLLM future-adapter boundary.
- [ ] Export public contract names/version.
- [ ] Run focused tests, full suite, repository qualifier, architecture audit, and `git diff --check`.
- [ ] Commit: `Document and audit ASCA contract v0.1`.

### Task 5: Exact qualification, branch CI, merge, and A002 closure

**Files:**
- Create: `docs/development/reports/ASCA-20261008-A002-architecture-contract.md`
- Modify: `docs/development/tasks/A002-asca-architecture-contract.md`
- Modify: `docs/development/tasks/CURRENT.md`
- Modify: `docs/development/tasks/ROADMAP.md`

**Interfaces:**
- Consumes all A002 deliverables.
- Produces exact qualification evidence and transitions A003 to PLANNED without activating it.

- [ ] Run fresh local full suite, repository qualifier, architecture audit, and diff check on candidate branch commit.
- [ ] Push branch and verify GitHub Actions success for exact branch SHA.
- [ ] Write evidence report with exact SHA, test count, audit, CI run, and explicit proof that FlyWireLLM training was not modified.
- [ ] Transition A002 to DONE and A003 to PLANNED; CURRENT points to A003 PLANNED.
- [ ] Re-run full local verification and commit closure.
- [ ] Push closure commit and require exact CI success.
- [ ] Fast-forward local `main` only after branch closure is GREEN, push `main`, fetch, and verify 0/0 synchronization.
- [ ] Close GitHub Issue #2 with final exact main SHA and evidence.
- [ ] Remove the isolated worktree only after the integrated main is verified clean.

## A002 Non-Goals

A002 must not choose an embedding model, graph database, vector database, neural familiarity estimator, activation scoring formula, memory decay formula, Transformer/SSM/MoE core, or FlyWireLLM integration path.

## Execution Order

Execute Tasks 1–5 sequentially. Negative or failed qualification evidence must be recorded and corrected before advancing. A003 remains PLANNED until A002 is fully GREEN.
