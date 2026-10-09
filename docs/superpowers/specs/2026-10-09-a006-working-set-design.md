# A006 Working Set / Selective Activation Design Specification

Date: 2026-10-09
Status: DESIGN FOR USER REVIEW
Planned task: A006 — Working Set / Selective Activation
Branch: research/a006-working-set
Base: ASCA main at 6147b9a6f6bc8c27b66735812e54c0050f13df36

## 1. Purpose

A006 adds an explicit bounded active-state layer on top of A005 semantic
Vector + Metadata retrieval.

A005 answered:

> Can semantic vector retrieval surface useful multilingual memory evidence
> without requiring a typed graph?

Its controlled-fixture verdict was `VECTOR_SUFFICIENT` for retrieval scope.

A006 asks the next question:

> Given memory evidence from one or more cues/queries, can FlyWireASCA keep a
> much smaller deterministic working set while preserving the memories needed
> for the task, and can multiple independent cues converge on the same memory
> without turning activation into truth?

A006 tests selective active-state management. It does not yet generate a final
natural-language answer.

## 2. Architectural decision

A006 uses **multi-query convergence + bounded working set**.

The core flow is:

```text
Cue A -> A005 VectorMemoryResult ----+
Cue B -> A005 VectorMemoryResult ----+--> validate/merge by memory_id
Cue C -> A005 VectorMemoryResult ----+              |
                                                    v
                                       per-memory support evidence
                                                    |
                                                    v
                                      bounded activation aggregation
                                                    |
                                                    v
                                        max_memory_nodes budget
                                                    |
                                                    v
                                      max_working_set_items budget
                                                    |
                                                    v
                                            WorkingSet
```

Normative boundary: **A006 does not build or traverse a typed graph.**

A006 does not:

- build or traverse a typed graph;
- rescore memories with Qwen3.5:4b;
- infer identity from convergence;
- modify proposition confidence;
- claim retrieval compute was reduced merely because the active set is smaller.

## 3. Relationship to A005

A005 remains the retrieval layer.

A006 consumes already-produced `VectorMemoryResult` objects and does not
re-embed or re-search memory itself.

This separation is intentional:

- A005 decides which memories are semantically retrievable.
- A006 decides which retrieved memories remain active under an explicit budget.

The A006 implementation must not import Ollama-specific embedding code into the
selection algorithm.

Physical qualification may compose the existing A005 local
`qwen3-embedding:0.6b` retriever with A006, but the portable A006 selector is
fully testable with synthetic `VectorMemoryResult` values.

## 4. Relationship to A003 Familiarity

A003 Familiarity is not required as a gate in A006 v0.1.

A later integrated controller may use familiarity to determine whether to
retrieve at all, but A006 isolates active-state selection after retrieval.

This keeps the experiment attributable:

```text
retrieval quality       -> A005
active-state selection  -> A006
```

## 5. Relationship to the typed graph decision

A005 concluded `VECTOR_SUFFICIENT` only for retrieval scope.

A006 therefore continues without graph traversal.

A006 must not reinterpret multi-query convergence as a relation path. If two
cues support the same memory, the only conclusion is that the memory has
multiple retrieval supports.

No `AssociationEdge`, `RelationType`, causal path, temporal path, ownership
path, or `SAME_PERSON` relation is created from convergence.

If a later benchmark demonstrates that correct active-state selection requires
explicit path semantics, that becomes new evidence for reconsidering a graph in
a later milestone.

## 6. Reuse of A002 control contracts

A006 deliberately reuses:

- `ActivationBudget`
- `ActivationState`
- `WorkingSetEntry`
- `WorkingSet`
- `RetrievalState`

A006 does not replace these contracts.

For the no-graph A006 profile:

- every emitted `ActivationState.hop == 0`;
- `ActivationBudget.max_relation_hops == 0`;
- `ActivationBudget.max_expansions == 0`;
- `ActivationBudget.max_model_input_tokens == 0` because A006 does not yet
  assemble model context;
- `max_working_set_items <= max_memory_nodes` is required by the A006
  selector profile.

Later milestones may use nonzero relation hops, expansions, or model-input
token budgets without changing the basic A006 selection result.

## 7. Input record: SelectiveRetrievalEvidence

A006 introduces an immutable wrapper around one A005 retrieval result.

Conceptually:

```python
SelectiveRetrievalEvidence(
    source_cue_id: str,
    result: VectorMemoryResult,
)
```

Requirements:

- `source_cue_id` is nonblank;
- one A006 selection request cannot contain duplicate `source_cue_id` values;
- each wrapped `VectorMemoryResult.query_id` must be unique;
- one source cue contributes at most one support to a given memory;
- duplicate memory IDs inside one malformed retrieval result fail closed;
- all retrieval results in one selection request must use the same embedding
  model name, model digest, and embedding profile.

A006 treats `source_cue_id` as provenance for activation.

## 8. Candidate consistency boundary

The same `memory_id` may appear in multiple retrieval results.

When that happens, immutable memory metadata visible in `VectorMemoryHit`
must agree across all occurrences:

- memory kind;
- proposition confidence;
- evidence IDs;
- entity IDs;
- context tags;
- source tags.

If the same memory ID carries conflicting immutable metadata across inputs,
A006 fails closed.

It does not guess which version is correct.

## 9. Similarity contribution

For each hit, A006 derives a nonnegative retrieval contribution:

```text
contribution = max(0.0, similarity)
```

This intentionally ignores negative cosine similarity as activation support.

A contribution:

- is not a probability;
- is not proposition confidence;
- is not evidence confidence;
- does not change the underlying memory record;
- exists only to prioritize active state.

A005 similarity remains separately inspectable in support evidence.

## 10. Multi-query bounded-union activation

For a memory with positive contributions
`c1, c2, ..., cn`, A006 computes:

```text
activation = 1 - product(1 - ci)
```

where each `ci` is already clamped to `[0,1]`.

Properties:

- activation stays in `[0,1]`;
- one support with similarity 0.8 yields activation 0.8;
- two independent 0.8 supports yield activation 0.96;
- more independent positive cues can raise priority;
- duplicate cue IDs cannot artificially inflate activation;
- activation remains a ranking/control signal only.

The formula is called **bounded-union activation**. In implementation terms,
`product(1 - ci)` means multiplying one `(1 - ci)` factor for every distinct
positive source-cue contribution.

It must not be described as a calibrated probability.

## 11. Activation support record

A006 adds a frozen audit record conceptually equivalent to:

```python
MemoryActivationSupport(
    memory_id: str,
    source_cue_ids: tuple[str, ...],
    similarities: tuple[float, ...],
    support_count: int,
    max_similarity: float,
    activation: float,
    memory_kind: MemoryKind,
    proposition_confidence: float,
    evidence_ids: tuple[str, ...],
)
```

Canonicalization rules:

- support entries are ordered by source cue ID;
- source cue IDs are unique;
- `similarities` align positionally with source cue IDs;
- `support_count == len(source_cue_ids)`;
- support_count counts only positive contributions;
- activation and max similarity are finite in `[0,1]`;
- proposition confidence is copied unchanged.

This record makes the reason for selection auditable without parsing a free-form
working-set reason string.

## 12. Candidate ranking

Positive-activation candidates are ranked deterministically by:

1. activation descending;
2. max similarity descending;
3. support count descending;
4. memory ID ascending.

The explicit order prevents platform-dependent tie behavior.

Proposition confidence is **not** a ranking key in A006 v0.1.

This is deliberate: the experiment tests selective activation, not truth
ranking.

## 13. Two strict budgets

A006 applies two separate strict budgets.

### 13.1 Active-memory budget

`ActivationBudget.max_memory_nodes` limits how many ranked positive-activation
memory candidates are retained as `ActivationState` values.

Candidates beyond this boundary are dropped from active memory.

### 13.2 Working-set budget

`ActivationBudget.max_working_set_items` limits how many retained activation
states become `WorkingSetEntry(kind=MEMORY)`.

The working-set budget may be smaller than the active-memory budget.

A006 never exceeds either budget to preserve ties.

Instead, it reports whether a tied activation/ranking group was cut at a
boundary.

## 14. Boundary-tie evidence

A006 records two booleans:

- `memory_budget_boundary_tie`
- `working_set_boundary_tie`

A boundary tie is true when the last retained candidate and the first dropped
candidate are equal on all ranking keys except final `memory_id` tie-break.

The selector still chooses deterministically by memory ID.

The flag exists because deterministic truncation can hide ambiguity even when
the implementation is correct.

A006 qualification must include a case where a tie is deliberately cut.

## 15. Working-set entries

Each selected memory becomes:

```python
WorkingSetEntry(
    ref_id=memory_id,
    kind=WorkingSetKind.MEMORY,
    activation=<bounded-union activation>,
    reason=<stable A006 reason code>,
)
```

A006 reason strings are stable machine-oriented codes rather than prose.

Initial reason codes:

- `single_cue_support`
- `multi_cue_convergence`

Detailed support provenance remains in `MemoryActivationSupport`.

## 16. Retrieval-state mapping

A006 maps structural selection state into the existing A002
`RetrievalState` conservatively:

- no positive candidate selected -> `INSUFFICIENT_EVIDENCE`;
- one or more candidates selected and no positive candidate was dropped by
  either A006 budget -> `RECALLED`;
- one or more candidates selected and at least one positive candidate was
  dropped by a budget -> `PARTIAL_RECALL`.

These labels describe **selection completeness relative to A006 input
evidence**, not factual truth.

A006 does not emit:

- `CONFLICTING_RECALL` because it has no contradiction detector;
- `KNOWN_BUT_NOT_RECALLED` because Familiarity is not an A006 input;
- identity or truth conclusions.

## 17. Selection result

A006 produces an immutable result conceptually equivalent to:

```python
SelectiveWorkingSetResult(
    working_set: WorkingSet,
    activation_states: tuple[ActivationState, ...],
    supports: tuple[MemoryActivationSupport, ...],
    input_result_count: int,
    input_hit_count: int,
    unique_candidate_count: int,
    positive_candidate_count: int,
    activated_candidate_count: int,
    selected_count: int,
    dropped_by_memory_budget_count: int,
    dropped_by_working_set_budget_count: int,
    memory_budget_boundary_tie: bool,
    working_set_boundary_tie: bool,
    embedding_model_name: str,
    embedding_model_digest: str | None,
    embedding_profile: str,
)
```

Count invariants are explicit and tested.

The `supports` tuple contains every positive candidate before either budget,
in deterministic candidate-ranking order. `activation_states` contains the
post-`max_memory_nodes` prefix, and `working_set.entries` contains the final
post-`max_working_set_items` prefix. This makes dropped evidence auditable.

The result contains no generated answer.

## 18. Selector interface

Proposed package:

```text
src/flywire_asca/selective_activation/
    __init__.py
    models.py
    selector.py
    baselines.py
    benchmark.py
```

Primary interface:

```python
select_working_set(
    evidence: Iterable[SelectiveRetrievalEvidence],
    *,
    budget: ActivationBudget,
) -> SelectiveWorkingSetResult
```

The iterable is materialized exactly once.

Selection is side-effect free.

## 19. Baseline modes

A006 compares three deterministic modes.

### SELECTIVE_CONVERGENCE

The proposed A006 algorithm:

- merge by memory ID;
- bounded-union activation;
- apply max-memory and working-set budgets.

### SINGLE_BEST

Control that ranks each memory only by its maximum single-query similarity.

It does not receive a multi-query convergence boost.

This baseline tests whether convergence itself improves selection.

### EXHAUSTIVE

Retains every positive unique candidate as active/working-set state using a
budget expanded exactly to fit all positive candidates.

This baseline is a logical active-state control.

It does not imply hardware compute measurement.

## 20. Important compute/efficiency boundary

A006 can demonstrate a smaller **active state**.

It cannot yet claim lower end-to-end retrieval compute because the A005 exact
vector index still scores all metadata-eligible vectors.

Therefore A006 records separately:

- A005 vectors scored upstream;
- A006 input hits;
- unique A006 candidates;
- positive candidates;
- activated candidates;
- final working-set items.

A reduction from unique candidates to selected working-set entries is called
**active-state reduction**, not compute reduction.

Any FLOP, power, energy, or hardware-efficiency claim remains out of scope.

## 21. Portable benchmark design

Portable qualification uses synthetic `VectorMemoryResult` values and does
not require Ollama.

The fixture covers at least:

1. single-query relevant memory;
2. multi-query convergence where a moderately similar memory supported by two
   cues beats a higher one-off distractor;
3. convergence parity where one support only behaves like SINGLE_BEST;
4. strict `max_memory_nodes` truncation;
5. strict `max_working_set_items` truncation;
6. memory-budget boundary tie;
7. working-set boundary tie;
8. same-name ambiguity preservation;
9. proposition-confidence independence;
10. no-positive-support / insufficient evidence;
11. conflicting immutable metadata for one memory ID fails closed;
12. duplicate source cue/query IDs fail closed;
13. embedding model/profile mismatch fails closed;
14. deterministic repeated output;
15. at least 256 synthetic distractor candidates.

## 22. Benchmark correctness labels

Each benchmark case declares one of:

- required selected memory IDs;
- allowed selected memory IDs for ambiguity cases;
- expected no-selection;
- expected validation failure.

Metrics include:

- required-memory coverage;
- selected-set precision on declared fixtures;
- convergence recovery count;
- convergence regression count;
- exhaustive coverage;
- active-memory coverage;
- working-set coverage;
- input hit count;
- unique candidate count;
- positive candidate count;
- activated candidate count;
- selected count;
- memory-budget drops;
- working-set-budget drops;
- boundary-tie count;
- active-state reduction ratio.

Raw counts remain primary.

## 23. Portable qualification gates

A006 portable qualification requires on the controlled fixture:

- required-memory coverage = 1.0;
- convergence regression count = 0;
- declared convergence recovery case succeeds;
- ambiguity-preservation failures = 0;
- confidence-separation failures = 0;
- budget violations = 0;
- count invariant failures = 0;
- deterministic output across repeated runs;
- no hidden graph traversal;
- no generative model dependency.

A006 does not require that every benchmark use fewer active items than
EXHAUSTIVE. Cases where all evidence fits in budget are valid.

## 24. Physical qualification

Physical A006 qualification composes the already-qualified A005 components:

```text
qwen3-embedding:0.6b
        |
        v
A005 exact vector-memory index
        |
        +--> query/cue A -> VectorMemoryResult
        +--> query/cue B -> VectorMemoryResult
        +--> query/cue C -> VectorMemoryResult
                         |
                         v
                A006 selector
                         |
                         v
                 bounded WorkingSet
```

The physical A006 profile is frozen before the final physical fixture:

- A005 query `top_k = 12` for each cue;
- A005 `minimum_similarity = 0.5037018224299838`;
- A006 `max_memory_nodes = 8`;
- A006 `max_working_set_items = 4`;
- A006 `max_relation_hops = 0`;
- A006 `max_expansions = 0`;
- A006 `max_model_input_tokens = 0`.

The physical model remains:

- `qwen3-embedding:0.6b`
- full digest:
  `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`
- expected dimension: 1024

A006 does not recalibrate the A005 retrieval threshold and does not tune the
A006 physical budget after final-fixture results are observed.

## 25. Physical fixture goals

The physical fixture includes at least:

1. English multi-query convergence;
2. Thai multi-query convergence;
3. Thai/English cross-lingual convergence;
4. same-name ambiguity under a working-set budget;
5. a strict budget-truncation case; exact boundary-tie behavior is qualified
   portably, while physical retained/dropped activation values are reported
   descriptively;
6. a no-hit/insufficient-evidence case;
7. a case where SINGLE_BEST misses a required memory but
   SELECTIVE_CONVERGENCE retains it;
8. an exhaustive comparison for every case.

The fixture uses fixed memory/query text declared before final qualification.

It is not tuned after observing final-case outcomes.

## 26. Physical metrics

Record at least:

- A005 vectors scored upstream;
- retrieval hits per cue;
- unique A006 candidates;
- positive candidates;
- active-memory candidates;
- final working-set size;
- required-memory coverage;
- SINGLE_BEST coverage;
- EXHAUSTIVE coverage;
- convergence recovery count;
- convergence regression count;
- boundary-tie events;
- active-state reduction ratio;
- embedding request/input counts;
- embedding timing/token metadata available from A005;
- deterministic repeated selector result.

These are experiment-specific software/system measurements.

## 27. Expected research interpretation

A006 supports the selective-activation hypothesis if:

- required-memory coverage remains high;
- working-set size is materially smaller than exhaustive active state on
  declared distractor-heavy cases;
- convergence recovers relevant evidence that SINGLE_BEST misses;
- ambiguity/tie truncation is visible rather than silently hidden;
- selection remains deterministic under fixed inputs/budgets.

A negative result is valid.

If convergence repeatedly hurts coverage or budget truncation loses necessary
evidence, A006 records that result rather than adjusting the fixture until it
passes.

## 28. No Qwen3.5:4b generation in A006

A006 does not send the working set to the A004 generative model.

This keeps two questions separate:

1. Can A006 select a compact useful active state?
2. Can a model reason well from that state?

Question 2 belongs to a later integration milestone.

No answer-quality claim is made from A006 alone.

## 29. Error handling

A006 fails closed on:

- malformed input evidence;
- duplicate source cue IDs;
- duplicate retrieval query IDs;
- duplicate memory ID inside one malformed result;
- inconsistent same-memory metadata;
- embedding model/digest/profile mismatch;
- non-finite similarity;
- invalid A006 budget profile;
- impossible count invariants.

A006 does not silently discard malformed inputs and continue.

## 30. Determinism

Given identical retrieval evidence and budget, A006 output must be byte/logical
equivalent at the contract level:

- same support ordering;
- same activation values within deterministic floating-point computation;
- same candidate ranking;
- same budget truncation;
- same WorkingSet order;
- same boundary-tie flags;
- same counts.

No random tie-break is used.

## 31. ActivationBudget policy for A006 v0.1

A006 validates:

```text
max_memory_nodes > 0
max_working_set_items > 0
max_working_set_items <= max_memory_nodes
max_relation_hops == 0
max_expansions == 0
max_model_input_tokens == 0
```

This is an A006 selector profile restriction, not a global change to the A002
`ActivationBudget` contract.

## 32. A006 completion evidence

A006 can close only when:

- task/roadmap state is activated and recoverable;
- portable selector/contracts are fully tested;
- convergence, budgets, ties, ambiguity, and confidence separation are covered;
- portable benchmark passes declared gates;
- physical A005+A006 composition is qualified with the pinned embedding model
  and A005 threshold;
- SELECTIVE_CONVERGENCE, SINGLE_BEST, and EXHAUSTIVE are compared;
- active-state reduction is reported without compute overclaim;
- A003, A004, and A005 qualification gates remain intact;
- FlyWireLLM remains paused/untouched;
- exact branch CI passes;
- whole-branch review addresses Critical/Important findings;
- final main CI passes;
- main is clean and synchronized 0/0.

## 33. Non-goals

A006 does not:

- build or traverse a typed graph;
- modify A005 embedding/retrieval semantics;
- recalibrate the A005 physical threshold;
- detect contradictions;
- emit `CONFLICTING_RECALL`;
- use familiarity as a prerequisite;
- use proposition confidence to boost activation;
- infer identity;
- build model prompts;
- enforce model token budgets;
- call Qwen3.5:4b generation;
- implement surprise/uncertainty expansion;
- implement procedural memory;
- claim end-to-end compute or energy savings.

## 34. Next milestone boundary

If A006 qualifies, the next planned milestone remains:

`A007 — Surprise, Uncertainty & Expansion`

A007 may use A006 evidence such as:

- insufficient evidence;
- partial recall caused by budgets;
- boundary ties;
- selected-state uncertainty.

A007, not A006, decides when to expand/retry retrieval or reasoning scope.

## 35. Success definition

A006 succeeds when FlyWireASCA can take multiple A005 retrieval results,
combine repeated memory support into a deterministic bounded activation signal,
construct a smaller auditable working set under strict budgets, preserve
ambiguity and confidence boundaries, and demonstrate on controlled portable and
physical fixtures whether multi-query convergence improves selection relative
to a single-best baseline without requiring graph traversal or generative-model
judgment.
