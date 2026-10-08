# ASCA Contract v0.1

Status: A002 architecture contract  
Project: FlyWireASCA  
Contract version: 0.1

## Purpose

ASCA Contract v0.1 freezes the minimum public vocabulary and record boundaries
needed for later experiments without freezing the algorithms that will use
them. It is deliberately implementation-neutral: storage, neural architecture,
retrieval scoring, consolidation, model provider, and action policy remain open
research choices.

## Core invariants

### Familiarity and activation are not truth

A cue may be familiar or strongly activated without being identical, factual,
or relevant. Identity-like relations therefore remain typed. In particular,
`same_person`, `same_name`, and `similar_to` are different relation types
and consumers must not collapse one into another.

### Activation is separate from proposition confidence

`AssociationEdge.activation_weight` is a finite routing/activation quantity.
It may be positive or negative and is not a probability.

`AssociationEdge.proposition_confidence` is a probability in [0, 1] about
the proposition represented by the edge. High activation must never be treated
as high proposition confidence merely because both happen to be numerically
large.

### Provenance is explicit

`EvidenceRef`, `evidence_ids`, and source references keep evidence attached
to cues, memories, relations, and observations. A002 defines references, not a
particular evidence database.

### Activation is bounded

`ActivationBudget` makes limits explicit:

- maximum memory nodes;
- maximum relation hops;
- maximum working-set items;
- maximum model-input tokens;
- maximum expansion count.

The contract does not decide how budgets are chosen. Later tasks may adapt them
from familiarity, uncertainty, surprise, risk, or empirical cost.

### Working state is explicit

`WorkingSet` is an explicit bounded collection rather than hidden prompt-only
state. Duplicate references and budget overflow are invalid at the contract
boundary.

### Retrieval state is explicit

Contract v0.1 defines:

- UNFAMILIAR
- FAMILIAR
- KNOWN_BUT_NOT_RECALLED
- PARTIAL_RECALL
- RECALLED
- CONFLICTING_RECALL
- INSUFFICIENT_EVIDENCE

These states do not imply that a neural network must produce them.

### Procedures remain interruptible

`ProcedureRef` represents a reusable procedure by identity/version and can
carry lazy links to explanatory memories. `Observation.expected_match` gives
later control logic an explicit place to represent whether an outcome matched
expectation. A002 does not implement automatic execution or interruption.

## Public record groups

### Memory and association

- `EvidenceRef`
- `Cue`
- `MemoryRecord`
- `AssociationEdge`

### Control and working state

- `ActivationBudget`
- `ActivationState`
- `WorkingSetEntry`
- `WorkingSet`
- `UncertaintySignal`

### Procedure and observation

- `ProcedureRef`
- `Observation`

### Evaluation

- `BaselineMode`
- `EvaluationMetric`
- `BenchmarkDefinition`
- `REQUIRED_BASELINE_MODES`

## Serialization contract

`dumps_contract` produces deterministic JSON for supported dataclass records.
`loads_contract` reconstructs a requested record type from that JSON using its
type hints. Nested dataclasses, enums, tuples, and optional values used by
contract v0.1 must round-trip without semantic loss.

Serialization is an interchange/testing boundary, not a storage-engine choice.

## Baseline contract

At minimum ASCA research keeps vocabulary for:

1. dense/direct processing;
2. ASCA selective processing;
3. ASCA with surprise-driven expansion disabled;
4. ASCA with familiarity disabled.

Individual benchmark cases may select the modes that are meaningful for that
case. Later qualification must not report a single efficiency score in place
of the underlying correctness, recall, activation, token, compute, latency,
memory-I/O, procedural-reuse, surprise, and recovery measurements.

## Compatibility expectations

Contract version 0.1 is pre-1.0 research infrastructure. Additive documentation
or internal implementation changes do not require a version bump when public
behavior is unchanged.

A breaking change to a public field name/type, enum meaning, serialization
shape, or invariant requires a contract-version change and a migration note.
Consumers should record which ASCA contract version produced persisted
artifacts or benchmark evidence.

## Deliberately deferred choices

Contract v0.1 does not freeze:

- graph database vs embedded/local storage;
- vector index or embedding model;
- neural vs symbolic/hybrid familiarity;
- activation scoring or decay formula;
- memory consolidation policy;
- selective neural compute / MoE / SSM / Transformer choice;
- autonomous learning policy;
- robotics or perception stack;
- long-term self-modification.

These choices require evidence from later milestones.

## FlyWireLLM boundary

FlyWireLLM is not a dependency of ASCA Contract v0.1 and A002 does not import or
run it. FlyWireLLM may later become one model behind a model adapter after its
training is complete and separately qualified.

That future adapter must translate between the model-facing representation and
ASCA contracts without making FlyWireLLM the definition of ASCA itself. Other
models and deterministic test cores must remain possible.

## Claims boundary

This contract defines software interfaces. It does not establish biological
fidelity, human cognitive equivalence, consciousness, AGI, production safety,
or superiority over dense language models.
