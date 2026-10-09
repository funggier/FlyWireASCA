# FlyWireASCA A006 Working Set / Selective Activation Qualification

Date: 2026-10-09
Task: A006 — Working Set / Selective Activation
GitHub Issue: #6
Branch: research/a006-working-set

## Decision

A006 engineering qualification is GREEN on exact branch candidate:

`224864cc9d70228d4feb80a9fcbc07f2776808d3`

Exact branch CI run:

`37927165972` — success

The A006 mechanism is implemented and qualified as a deterministic bounded
working-set selector. The physical research hypothesis is intentionally
reported separately from engineering correctness.

**Final A006 hypothesis outcome: `NOT_SUPPORTED`**

Under the frozen real-Qwen embedding fixture, bounded-union multi-query
convergence preserved every declared required memory and caused zero
convergence regressions, but it recovered zero required memories that the
SINGLE_BEST control missed. The implementation is therefore valid while the
specific physical convergence-benefit hypothesis is not supported by this
fixture.

No threshold, query text, model, top_k, or A006 budget was tuned after the
final physical result.

## Delivered architecture

A006 adds a no-graph active-state layer over A005 retrieval:

```text
A005 VectorMemoryResult(s)
        |
        v
validate provenance / immutable metadata
        |
        v
merge supports by memory_id
        |
        v
bounded-union activation
        |
        v
max_memory_nodes
        |
        v
max_working_set_items
        |
        v
A002 WorkingSet
```

The selector:

- does not re-embed or re-search memory;
- does not build or traverse `AssociationEdge`;
- does not infer identity, truth, causality, or temporal relations;
- does not call `qwen3.5:4b` generation;
- does not use proposition confidence as an activation/ranking boost.

## Activation rule

For each positive A005 similarity contribution:

```text
ci = max(0, similarity)
activation = 1 - product(1 - ci)
```

Only distinct positive source-cue supports contribute.

Activation is a bounded control/ranking signal, not a calibrated probability,
truth score, or proposition confidence.

SELECTIVE_CONVERGENCE ranking is:

1. activation descending;
2. maximum similarity descending;
3. positive support count descending;
4. memory ID ascending.

SINGLE_BEST ranks by maximum positive similarity descending and then memory ID.
EXHAUSTIVE retains every positive unique candidate.

## Strict budget semantics

A006 uses the existing A002 `ActivationBudget`.

For the A006 profile:

- `max_relation_hops = 0`;
- `max_expansions = 0`;
- `max_model_input_tokens = 0`;
- every emitted `ActivationState.hop = 0`;
- working-set budget cannot exceed active-memory budget;
- neither budget expands to preserve tied candidates;
- memory and working-set boundary ties are reported explicitly.

A smaller working set is described only as **active-state reduction**. It is not
evidence of lower retrieval FLOPs, power use, energy use, or end-to-end compute
because the A005 exact vector index still scores every metadata-eligible
vector.

## Portable engineering qualification

The synthetic portable fixture contains 14 cases and at least 256 distractor
candidates in the distractor-heavy case.

Fresh portable metrics on the candidate branch:

- case count: 14
- required-memory coverage: 1.0
- active-memory required coverage: 1.0
- SINGLE_BEST required-memory coverage: 0.9230769230769231
- EXHAUSTIVE required-memory coverage: 1.0
- selected-set precision: 0.8125
- convergence recovery count: 1
- convergence regression count: 0
- ambiguity failure count: 0
- confidence-separation failure count: 0
- budget violation count: 0
- count-invariant failure count: 0
- validation failure count: 0
- total input hits: 282
- total unique candidates: 281
- total positive candidates: 279
- total activated candidates: 28
- total selected working-set items: 16
- memory-budget drops: 251
- working-set-budget drops: 12
- boundary-tie count: 2
- aggregate active-state reduction ratio: 0.942652329749104
- deterministic repeat: PASS

The portable fixture therefore demonstrates that the algorithm can produce a
controlled convergence recovery and very large active-state reduction under
synthetic geometry. It does not establish that real embeddings will create the
same ranking advantage.

## Frozen physical profile

Physical qualification used:

- Ollama runtime: `0.32.15`
- embedding model: `qwen3-embedding:0.6b`
- full digest:
  `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`
- architecture: `qwen3`
- parameter count: 595,776,512
- reported parameter size: `595.78M`
- quantization: `Q8_0`
- embedding dimension: 1024
- A005 frozen minimum similarity: `0.5037018224299838`
- A005 top_k: 12
- A006 max memory nodes: 8
- A006 max working-set items: 4
- relation hops: 0
- expansions: 0
- model-input tokens: 0
- selector profile: `a006-selective-convergence-v1`
- embedding profile: `qwen3-embedding-0.6b-vector-memory-v1`

No A005 threshold recalibration occurred.

## Frozen physical fixture

Fixture version:

`a006-physical-v1`

Final fixture fingerprint:

`e51fea2e58186e94d7affc964509e96d96fc656759677d7dcc073e5b36b91035`

Case IDs:

- `physical-en-convergence`
- `physical-th-convergence`
- `physical-cross-lingual-convergence`
- `physical-same-name-ambiguity`
- `physical-budget-truncation`
- `physical-no-hit`
- `physical-convergence-recovery-challenge`

## Physical result

Final live run was structurally valid and exited 0.

Metrics:

- experiment validity: PASS
- required-memory coverage: 1.0
- convergence recovery count: 0
- convergence regression count: 0
- ambiguity failure count: 0
- no-selection failure count: 0
- strict budget observation count: 1
- total positive candidates: 34
- total selected working-set items: 22
- aggregate active-state reduction ratio: 0.35294117647058826
- deterministic repeated selector output: PASS
- embedding request count: 21
- embedding input count: 52
- prompt tokens total: 943 across 21 responses
- total duration: 4,527,985,600 ns across 21 responses
- load duration: 1,570,494,900 ns across 13 responses where the backend reported it

These token/timing values are backend evidence for this local physical run only;
they are not FLOP, power, energy, or general performance claims.

The real fixture therefore showed a 35.29% reduction from positive unique
candidates to selected working-set items while preserving all declared required
memories. However, it did not show a selection-success advantage over
SINGLE_BEST.

In the declared convergence-recovery challenge, SELECTIVE_CONVERGENCE ranked
`challenge-shared` first while SINGLE_BEST ranked it fourth, but the frozen
working-set budget was four items. Both modes therefore retained the required
memory, so this is reprioritization rather than a recovery.

This distinction is why the predeclared physical rule yields
`NOT_SUPPORTED`, not `SUPPORTED`.

## Physical per-case observations

### English convergence

SELECTIVE_CONVERGENCE ranked `en-shared-launch` first and retained it.
SINGLE_BEST also retained it within the four-item working set.

Active-state reduction: 0.2.

### Thai convergence

Both SELECTIVE_CONVERGENCE and SINGLE_BEST retained `th-shared-trip`.

Active-state reduction: 0.0.

### Cross-lingual convergence

Both modes retained `cross-shared`.

Active-state reduction: 0.0.

### Same-name ambiguity

Both `somchai-a` and `somchai-b` remained selected. No vector-convergence
identity collapse occurred.

Active-state reduction: 0.0.

### Strict budget truncation

Twelve near-equivalent status-note memories passed the A005 threshold.
SELECTIVE_CONVERGENCE retained eight active memories and four working-set
entries.

Active-state reduction: 0.6666666666666666.

No individual status-note ID is treated as semantically required in this case.

### No hit

No memory passed the frozen threshold. A006 returned an empty working set with
`INSUFFICIENT_EVIDENCE`.

### Convergence-recovery challenge

SELECTIVE_CONVERGENCE ranked `challenge-shared` first.
SINGLE_BEST ranked it fourth.
Both retained it under the four-item working-set budget.

Active-state reduction: 0.42857142857142855.

This case demonstrates ordering impact but not a successful recovery under the
frozen budget.

## Fixture-validity correction

The first physical run exposed a fixture-label defect rather than a selector
defect.

The strict budget case contains 12 deliberately near-identical status notes.
The initial fixture arbitrarily declared `budget-00` as required, although
the case was intended only to measure strict truncation and no semantic basis
made that ID preferable to the other equivalent notes.

Regression:

`test_budget_truncation_case_does_not_label_an_arbitrary_equal_status_note_as_required`

was observed RED before the correction.

Only the expected required-memory label was changed from `budget-00` to an
empty required set. The following remained unchanged:

- all document text;
- all query text;
- embedding model/digest;
- A005 threshold;
- A005 top_k;
- A006 budgets;
- selector/baseline logic.

Fixture-validity fix commit:

`43afe2dfb2f6a1365c1be3fc5333c55901d52f21`

The final live run was executed on that committed behavior.

## Exact branch qualification

Candidate SHA:

`224864cc9d70228d4feb80a9fcbc07f2776808d3`

Fresh local gates:

- `python -m pytest -q`: **238 passed**
- `python scripts/audit_architecture_contract.py`:
  **architecture_contract_audit=PASS**
- `python scripts/qualify_repository.py`:
  **repository_qualification=PASS**
- `python scripts/run_familiarity_benchmark_a003.py --qualify`: PASS
- `git diff --check HEAD^ HEAD`: PASS
- A006 worktree: clean

Exact branch CI:

- workflow: CI
- run: `37927165972`
- head SHA: `224864cc9d70228d4feb80a9fcbc07f2776808d3`
- conclusion: **success**

GitHub CI remains portable and does not run local A004/A005/A006 physical
qualification.

## Whole-branch review findings

A separate reviewer/subagent facility was not available in the current harness,
so the final review was performed as a dedicated whole-branch author review
against the approved spec and plan rather than being conflated with
implementation.

That review found two Important issues before merge:

1. the physical CLI previously rejected nondeterminism but could still emit
   `experiment_valid=true` when frozen fixture identity, ambiguity preservation,
   no-hit behavior, or strict-budget evidence drifted;
2. A006 physical evidence did not retain the embedding request/input and
   token/timing metadata exposed by A005's `EmbeddingResponse`.

Both were fixed in:

`224864cc9d70228d4feb80a9fcbc07f2776808d3`

The fix adds fail-closed physical engineering validation while keeping
`SUPPORTED` / `MIXED` / `NOT_SUPPORTED` as research outcomes. A structurally
valid `NOT_SUPPORTED` experiment therefore still exits 0.

It also wraps the existing A005 embedding adapter only for evidence collection;
A005 adapter/index implementation remains unchanged.

Focused review regressions passed 10/10 and the fresh full suite passed
238/238 before the physical rerun.

One Minor note remains deferred: internal `_CandidateMetadata.memory_kind` is
annotated as `object`; runtime type safety is still enforced by
`VectorMemoryHit` and `MemoryActivationSupport`, so this does not affect A006
qualification.

## Isolation evidence

A006 branch diff from base
`6147b9a6f6bc8c27b66735812e54c0050f13df36`
contains no changes under the qualified A004 model-adapter paths or A005
embedding/vector-memory implementation paths.

The A005 physical constants remain:

- digest:
  `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`
- threshold: `0.5037018224299838`
- embedding dimension: 1024

FlyWireLLM was checked read-only before branch publication:

- HEAD: `9aa8acba1ecdefcdce4678b2914fc2d2dcaacc14`
- branch: `research/l004-base50m-pretraining`
- ahead/behind: 0/0
- worktree: clean
- no FlyWireLLM training runner was observed in the Python process list

FlyWireLLM remains paused and untouched by A006.

## Interpretation

A006 produces two different conclusions, both important:

1. **Engineering conclusion — qualified.** The selector is deterministic,
   bounded, auditable, preserves ambiguity/confidence boundaries, obeys strict
   budgets, and composes successfully with the real A005 embedding/retrieval
   system.
2. **Research conclusion — physical convergence benefit not supported.** The
   synthetic benchmark proves bounded-union convergence can create a recovery
   under constructed score geometry, but the frozen real-Qwen fixture produced
   zero recoveries over SINGLE_BEST.

A006 should therefore not promote bounded-union convergence to a universally
superior selector. Future integrated experiments should retain SINGLE_BEST as a
serious control and treat convergence as an optional policy whose benefit must
be demonstrated in the target workload.

This result does not justify creating a typed graph automatically.

## Deferred questions

A006 intentionally does not answer:

- whether a smaller working-set budget would expose a physical convergence
  recovery;
- whether different task distributions make convergence useful;
- whether learned weighting should replace bounded-union;
- whether A003 Familiarity should gate retrieval;
- whether graph paths are needed;
- whether selected working sets improve Qwen3.5:4b answer quality;
- whether active-state reduction produces hardware compute or energy savings.

Those require future experiments and must not be inferred from A006.

## Next milestone

A007 — Surprise, Uncertainty & Expansion remains **PLANNED**.

A007 should consume A006 structural signals such as insufficient evidence,
partial recall, boundary truncation, or other declared uncertainty evidence.
It must not assume bounded-union convergence is superior merely because A006
implemented it.