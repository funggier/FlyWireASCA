# A003 Familiarity System Design Specification

Date: 2026-10-08
Status: DESIGN FOR USER REVIEW
Task: A003 — Familiarity System
GitHub Issue: #3
Branch: research/a003-familiarity-system
Base contract: ASCA Contract v0.1

## 1. Purpose

A003 builds the first model-independent familiarity subsystem for FlyWireASCA.

Its purpose is deliberately narrow:

> Given a typed cue, determine cheaply whether the system has encountered the
> same normalized cue before and identify the opaque memory regions that may be
> relevant, without retrieving full memories and without inferring identity,
> truth, causality, or semantic equivalence.

A003 is not the recall system. Associative recollection begins in A004.

The first implementation is a transparent deterministic baseline so later
learned, fuzzy, embedding-based, or neural familiarity mechanisms have a clean
control to beat.

## 2. Design classification

A003 is an architectural subsystem because later ASCA tasks will depend on its
public behavior. Its first implementation remains intentionally small.

The subsystem must preserve these ASCA invariants:

- familiarity is not truth;
- familiarity is not identity;
- familiarity is cheaper/narrower than full recollection;
- candidate regions are hints, not resolved memories;
- cost is measured explicitly;
- behavior is deterministic for the same trace set and cue;
- no external model, cloud service, database, or FlyWireLLM runtime is required.

## 3. Approaches considered

### 3.1 Recommended — exact typed familiarity index

Index traces by:

`(CueKind, normalized_surface_value)`

A lookup performs one typed-key probe and returns all matching trace/region
references.

Advantages:

- transparent and deterministic;
- makes false-positive behavior easy to audit;
- cheap enough to establish the intended selectivity contract;
- preserves ambiguity naturally when one surface form maps to multiple regions;
- does not conflate A003 with A004 semantic/associative recall;
- provides a stable baseline for later learned estimators.

Limitations:

- does not recognize paraphrases, spelling variants beyond normalization,
  semantic similarity, or approximate matches;
- familiarity strength is binary in v0.1;
- not intended as the final familiarity mechanism.

### 3.2 Deferred — fuzzy lexical familiarity

Could add edit distance, token overlap, phonetic similarity, or hand-written
rules.

This may improve coverage but introduces tuning choices and false familiarity
before the exact baseline is measured. It is therefore deferred.

### 3.3 Deferred — embedding/neural familiarity

Could use a learned encoder, embedding index, or dedicated neural familiarity
head.

This is closer to the long-term research direction but would confound the first
experiment with model quality, embedding choice, training data, thresholds,
and hardware cost. It is therefore deferred until the exact baseline exists.

## 4. Public data model

A003 adds a small familiarity namespace that consumes A002 `Cue` and
`CueKind` contracts.

### 4.1 FamiliarityTrace

A trace records that a typed surface cue has been encountered and associates
that encounter with an opaque candidate region.

Proposed fields:

- `trace_id: str`
- `cue_kind: CueKind`
- `surface_value: str`
- `region_id: str`
- `evidence_ids: tuple[str, ...] = ()`

The trace does not contain or duplicate full memory content.

The same normalized cue may have multiple traces and multiple candidate
regions. This is required for ambiguous same-name cases.

### 4.2 FamiliarityResult

A lookup returns:

- `cue_id: str`
- `retrieval_state: RetrievalState`
  - exact match -> `FAMILIAR`
  - no exact match -> `UNFAMILIAR`
- `familiarity_score: float`
  - v0.1 exact baseline uses exactly `1.0` or `0.0`
- `candidate_region_ids: tuple[str, ...]`
- `matched_trace_ids: tuple[str, ...]`
- `cost: FamiliarityCost`

The result must not expose a resolved person/entity identity.

### 4.3 FamiliarityCost

Logical cost instrumentation, not a hardware FLOP claim:

- `index_probes: int`
- `matched_trace_count: int`
- `total_trace_count: int`

For one exact lookup, `index_probes == 1`.

The exhaustive control scans `total_trace_count` traces so benchmark results
can compare logical work without pretending that Python object counts equal
CPU/GPU FLOPs.

## 5. Normalization contract

A003 normalization is intentionally conservative.

For a cue surface string:

1. Unicode normalize with NFKC;
2. strip leading/trailing whitespace;
3. collapse internal whitespace runs to one ASCII space;
4. apply Unicode `casefold()`.

The cue type remains part of the key. Therefore identical text under different
`CueKind` values is not automatically familiar across types.

Examples:

- `"  Alice  "` and `"alice"` under `CueKind.ENTITY` -> same key;
- the same surface under `CueKind.TEXT` vs `CueKind.ENTITY` -> different keys;
- Thai text remains supported through Unicode normalization without
  English-only tokenization.

Normalization does not perform stemming, transliteration, typo correction,
translation, semantic similarity, or entity resolution.

Empty-after-normalization values are invalid.

## 6. ExactFamiliarityIndex behavior

The first engine is `ExactFamiliarityIndex`.

Construction:

- accepts a finite sequence of `FamiliarityTrace`;
- rejects duplicate `trace_id` values;
- builds an in-memory mapping from typed normalized key to trace bucket;
- preserves the original trace records;
- has no online mutation API in A003 v0.1.

Lookup:

1. validate/normalize the incoming `Cue`;
2. perform one typed-key probe;
3. if no bucket exists, return `UNFAMILIAR`, score 0.0, and no regions;
4. if a bucket exists, return `FAMILIAR`, score 1.0;
5. return deduplicated candidate region IDs in deterministic sorted order;
6. return matching trace IDs in deterministic sorted order;
7. report logical cost.

A003 must not choose one region when multiple regions match.

## 7. Exhaustive control

A003 also defines an `ExhaustiveFamiliarityBaseline` with the same observable
matching semantics but scans every trace.

Purpose:

- correctness oracle for the exact index;
- explicit non-selective cost control;
- benchmark comparison for candidate narrowing.

The exact index and exhaustive baseline must return the same familiarity state,
score, candidate regions, and matched trace IDs for every benchmark cue.

They may differ only in cost instrumentation and measured runtime.

## 8. Ambiguity and identity safety

The key safety case is same-name ambiguity.

Fixture example:

- trace 1: ENTITY `"A"` -> region `person-a-primary`
- trace 2: ENTITY `"A"` -> region `person-a-neighbor`

Lookup of ENTITY `"A"` must return:

- FAMILIAR;
- both candidate regions;
- both matched traces;
- no `same_person` conclusion;
- no selected winner.

Identity resolution belongs to later typed associative evidence/recollection,
not familiarity.

This is a required acceptance test.

## 9. Benchmark fixture design

A003 controlled benchmark cases cover at least:

1. known unique cue;
2. completely unknown cue;
3. normalization-equivalent cue;
4. same surface under a different `CueKind`;
5. same-name ambiguity mapping to multiple regions;
6. duplicate traces pointing to the same region;
7. Unicode/Thai cue normalization;
8. empty/invalid input rejection;
9. larger synthetic trace set for logical-cost comparison.

No external dataset is required for A003 qualification.

## 10. Metrics

A003 records at minimum:

- familiar/unfamiliar correctness;
- false familiarity count/rate;
- false unfamiliar count/rate;
- ambiguity preservation correctness;
- candidate region count;
- candidate region fraction when a universe size is known;
- exact-index logical probes;
- exhaustive traces scanned;
- matched trace count;
- optional wall-clock latency, reported as descriptive evidence only.

A003 must not claim hardware compute reduction from logical probe counts alone.

## 11. Benchmark acceptance

For the deterministic qualification fixture:

- exact index and exhaustive baseline outputs are semantically identical;
- familiar/unfamiliar classification is 100% correct for declared fixtures;
- false familiarity count is 0;
- false unfamiliar count is 0;
- all declared ambiguous same-name candidates are preserved;
- no identity winner is produced;
- typed cue-kind separation is preserved;
- normalization cases behave exactly as documented;
- exact lookup reports one index probe;
- exhaustive baseline reports scanning the full trace set;
- full repository tests and architecture audit remain GREEN.

These acceptance values describe the controlled A003 fixture only, not a
general real-world accuracy claim.

## 12. Package boundaries

Proposed files:

```text
src/flywire_asca/familiarity/
    __init__.py
    models.py
    normalization.py
    exact.py
    benchmark.py

tests/
    test_familiarity_models.py
    test_familiarity_normalization.py
    test_familiarity_exact.py
    test_familiarity_benchmark.py

docs/development/tasks/
    A003-familiarity-system.md

docs/development/reports/
    ASCA-20261008-A003-familiarity-system.md
```

The A002 contracts package remains unchanged except for additive imports only if
strictly necessary. A003 should consume the existing contract rather than
rewrite it.

## 13. Error handling

Fail closed on malformed records:

- blank IDs;
- blank region IDs;
- empty normalized surface values;
- duplicate trace IDs;
- invalid probability/state fields if any are added later.

Unknown valid cues are not errors; they return `UNFAMILIAR`.

Ambiguous matches are not errors; they return all candidate regions.

## 14. Determinism

Given the same trace set and cue:

- normalization output is stable;
- result ordering is stable;
- result state/score is stable;
- benchmark summaries are stable except explicitly separated wall-clock fields.

No random seed is required for the exact baseline.

## 15. FlyWireLLM boundary

A003 does not import, call, stop, restart, inspect checkpoints from, or train
FlyWireLLM.

FlyWireLLM remains a separate live training workload. When training is complete
and independently qualified, a later model-adapter experiment may use it to
test ASCA behavior. That future integration must compare against deterministic
A003 behavior rather than replace the baseline.

## 16. Deferred research

A003 v0.1 explicitly defers:

- fuzzy lexical matching;
- embedding similarity;
- learned familiarity scores;
- recency/usage-strength learning;
- confidence calibration from experience;
- cross-modal familiarity;
- semantic recollection;
- graph spreading activation;
- dynamic working-set routing;
- surprise-driven budget expansion.

These belong to later experiments after the exact baseline is qualified.

## 17. Completion evidence

A003 is not DONE until:

- implementation follows TDD;
- focused tests pass;
- full regression passes;
- architecture audit passes;
- repository qualifier passes;
- benchmark qualification passes;
- `git diff --check` passes;
- exact branch CI passes;
- closure commit CI passes;
- main is fast-forward integrated and synchronized 0/0;
- FlyWireLLM isolation is verified;
- GitHub Issue #3 records final exact evidence.

A004 remains PLANNED when A003 closes.
