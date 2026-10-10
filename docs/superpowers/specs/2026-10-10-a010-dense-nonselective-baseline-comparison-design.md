# A010 — Dense / Non-selective Baseline Comparison Design

Date: 2026-10-10
Repository: `funggier/FlyWireASCA`
Milestone: A010 — Dense/Non-selective Baseline Comparison
Status at design time: PLANNED
GitHub issue at design time: not created

## 1. Purpose

A010 tests the first system-level comparison promised by the FlyWireASCA
architecture: compare the qualified integrated ASCA control path against a
deliberately non-selective baseline on frozen controlled workloads.

The primary research question is:

> Can the A009 selective cognitive loop preserve the deterministic task-success
> and final-state coverage of a fair dense/non-selective baseline while using
> less logical retrieval and active-memory state on the same frozen cases?

A010 is an evidence task. It may end as `SUPPORTED`, `MIXED`, or
`NOT_SUPPORTED`. A negative result is valid and must not be tuned away.

A010 does not alter the historical outcomes:

- A006 selective-convergence hypothesis: `NOT_SUPPORTED`;
- A007 structural-expansion hypothesis: `SUPPORTED`;
- A008 procedural-memory hypothesis: `SUPPORTED`;
- A009 integrated-loop hypothesis: `SUPPORTED`.

FlyWireLLM remains separate and untouched.

## 2. Authoritative starting point

At design time the live repository state is:

- branch: `main`;
- HEAD: `ae0347e46741e9a01cd446db03a91dc6643929b0`;
- upstream: `origin/main`;
- ahead/behind: `0/0`;
- worktree: clean;
- exact final A009 CI: `38000755347`, conclusion `success`;
- A009 GitHub Issue #9: closed with reason `completed`;
- A010: PLANNED with no GitHub issue.

A010 must re-check live Git/GitHub/CI state before activation.

The repository README contains one stale A009 sentence saying Issue #9 remains
open. That sentence is documentation drift only. A010 activation may repair it,
but the stale prose is not evidence that A009 is unfinished.

## 3. Why A009 ALWAYS_MAX_SCOPE is not the A010 dense baseline

A009 already contains an `ALWAYS_MAX_SCOPE` control, but it remains selective:

- it evaluates all A007 scopes;
- it still uses A006 `SINGLE_BEST`;
- it still obeys bounded working-set budgets.

Therefore it is a useful wide-selective control, but it is not a
dense/non-selective baseline.

A010 must distinguish:

1. widening the selective retrieval scope; from
2. removing selective activation and retaining all eligible retrieval evidence.

The existing A006 `select_exhaustive()` implementation is the canonical
non-selective activation primitive for A010. A010 must reuse it rather than
invent a weaker baseline.

## 4. Considered approaches

### Approach A — Max-scope SINGLE_BEST only

Compare A009 `MISMATCH_DRIVEN_RECOVERY` against A009
`ALWAYS_MAX_SCOPE`.

Advantages:

- almost no new control code;
- already qualified by A009;
- directly measures progressive scope evaluation.

Rejected as the primary A010 comparison because `ALWAYS_MAX_SCOPE` is still
selective and bounded by `SINGLE_BEST`. It does not satisfy the architecture
requirement for a deliberately non-selective baseline.

It remains a secondary decomposition control.

### Approach B — Full-memory bypass

Bypass A005/A006 and place every stored memory directly into one giant working
set.

Advantages:

- maximally non-selective;
- simple to explain.

Rejected as the primary baseline because it changes too many mechanisms at
once. It would bypass the same retrieval threshold, retrieval evidence,
identity handling, and A006 evidence preparation that ASCA uses. A win against
such a baseline would be hard to interpret.

It may be considered in a later milestone if a true full-memory-processing
baseline becomes necessary.

### Approach C — Shared A005 evidence + exhaustive A006 activation

Recommended and selected.

The dense baseline:

- uses the same A005 index;
- uses the same memory corpus;
- uses the same cue tiers;
- uses the same similarity threshold;
- evaluates every declared cue tier immediately;
- sets retrieval `top_k` high enough to return every above-threshold document
  available from that index;
- merges that evidence with the already-qualified A006
  `select_exhaustive()`;
- executes the same explicit A008 root procedure in `CHUNKED` mode;
- uses the same immutable pre-execution world snapshot;
- performs no scope recovery because all declared retrieval scope is already
  available.

This isolates the main variable of interest: selective progressive activation
versus dense/exhaustive activation over the same retrieval system.

## 5. Primary compared systems

A010 defines two primary systems.

### 5.1 ASCA_PRIMARY

The selective system is the already-qualified A009 primary path:

- A003 exact familiarity evidence;
- A005 exact vector retrieval;
- A006 `SINGLE_BEST`;
- A007 `SIGNAL_DRIVEN` initial expansion;
- A008 `CHUNKED`;
- A009 `MISMATCH_DRIVEN_RECOVERY`;
- explicit deterministic root procedure;
- recovery advances exactly one frozen scope at a time;
- maximum three procedure attempts;
- fresh execution ID and fresh deterministic simulator for each replay;
- no model-controlled retrieval, replay, verification, or primary outcome.

A010 must call the real A009 controller for this primary variant. It must not
copy the A009 controller into a benchmark fork.

### 5.2 DENSE_EXHAUSTIVE

The non-selective system uses:

- the same A005 `ExactVectorMemoryIndex`;
- all declared A010 cue tiers immediately;
- the same minimum similarity threshold as ASCA;
- query `top_k = max(1, index.document_count)`, so A005 does not truncate
  above-threshold evidence merely because of a selective top-k budget;
- A006 `select_exhaustive()`, retaining every positive candidate returned by
  the shared A005 evidence;
- the same explicit root procedure;
- A008 `CHUNKED`;
- the same immutable initial world state;
- one procedure attempt;
- no retrieval expansion and no replay.

The dense runner must fail closed on malformed evidence and must preserve
memory IDs exactly, including same-display-name cases.

## 6. Secondary controls and ablations

A010 also records controls required by the top-level architecture, but they do
not replace the primary ASCA-versus-dense comparison.

### 6.1 ASCA_ALWAYS_MAX_SCOPE

Reuse the A009 `ALWAYS_MAX_SCOPE` control.

Purpose:

- separate savings caused by progressive scope evaluation from savings caused
  by bounded working-set selection.

This remains a selective control, not the dense baseline.

### 6.2 ASCA_NO_STRUCTURAL_EXPANSION

A benchmark-only ablation begins at A007 scope 0 with A007
`NO_EXPANSION` semantics instead of `SIGNAL_DRIVEN`.

A009-level procedure-mismatch recovery may remain enabled. This isolates the
effect of A007 structural expansion from A009 mismatch recovery.

The ablation must be implemented through existing A007/A009 public primitives.
It must not change A007 trigger enums or mutate A009 primary behavior.

### 6.3 ASCA_FAMILIARITY_DISABLED

A benchmark-only diagnostic omits A003 familiarity evidence from the comparison
trace while preserving the same retrieval/procedure inputs.

Because A009 intentionally treats familiarity as evidence rather than a
retrieval veto or truth signal, the expected deterministic control result is
semantic equivalence with ASCA_PRIMARY for cases where familiarity is not
otherwise consumed.

Any control-result difference is a qualification failure, not a new A003
feature.

## 7. Comparison architecture

Proposed A010 package:

```text
src/flywire_asca/baseline_comparison/
    __init__.py
    models.py
    dense.py
    ablations.py
    benchmark.py
```

Responsibilities:

- `models.py`
  - immutable variant names;
  - normalized per-run evidence;
  - comparison case/result/report contracts.

- `dense.py`
  - evaluate all declared cue tiers;
  - create A005 queries using full index top-k;
  - aggregate through A006 `select_exhaustive()`;
  - execute the A008 CHUNKED root procedure once;
  - retain raw retrieval and procedure evidence.

- `ablations.py`
  - benchmark-only structural-expansion and familiarity diagnostics;
  - no mutation of A007/A009 production semantics.

- `benchmark.py`
  - frozen deterministic A010 fixture;
  - run ASCA_PRIMARY, DENSE_EXHAUSTIVE, and secondary controls;
  - derive raw logical-work metrics;
  - classify the primary A010 research outcome;
  - validate impossible relationships and fixture identity.

Qualification scripts:

```text
scripts/
    qualify_baseline_comparison_a010.py
    qualify_baseline_comparison_a010_physical.py
```

The portable deterministic script belongs in CI. The physical script remains
local-only.

## 8. Shared-input fairness contract

Every primary pair must share exactly:

- case ID;
- goal text;
- root procedure ID;
- memory corpus and memory IDs;
- retrieval text;
- cue-tier query texts;
- A005 embedding vectors or physical embedding model;
- A005 minimum similarity threshold;
- explicit procedure definition;
- action-memory requirements;
- A008 expected outcomes;
- immutable initial simulated world state;
- deterministic action definitions;
- success and final-state criteria.

The primary variants may differ only where the design explicitly intends:

- progressive versus immediate all-tier retrieval;
- selective bounded activation versus exhaustive activation;
- mismatch-driven widening/replay versus no widening after dense retrieval.

The benchmark validator rejects hidden per-policy fixture changes.

## 9. A010 deterministic fixture

A010 creates a new frozen fixture rather than modifying the frozen A009 fixture.

The fixture should contain controlled families that expose both correctness and
active-state behavior. At minimum:

1. `easy-local-many-distractors`
   - target available in the narrowest tier;
   - many above-threshold distractors exist;
   - ASCA should succeed at narrow scope;
   - dense should succeed with a much larger active set.

2. `unfamiliar-semantic-many-distractors`
   - A003 is unfamiliar;
   - semantic retrieval remains sufficient;
   - verifies familiarity is not a veto.

3. `structural-expansion-required`
   - A007 structural trigger is required before success;
   - dense has the target from its immediate all-tier retrieval.

4. `procedure-recovery-one-scope`
   - A007 initially stops before the procedure-required memory;
   - ASCA recovers after one mismatch-driven wider scope;
   - dense succeeds on its one procedure attempt.

5. `procedure-recovery-two-scopes`
   - ASCA requires both allowed recovery steps;
   - dense starts with all declared retrieval evidence.

6. `persistent-missing-memory`
   - required memory is absent from the corpus or all eligible evidence;
   - both systems fail deterministically;
   - ASCA remains bounded.

7. `selective-routing-miss-sentinel`
   - deliberately creates a case where a relevant memory can be present in
     dense evidence but threatened by selective ranking/budget;
   - exists to detect an honest dense-only success rather than designing only
     ASCA-friendly cases.

8. `same-name-identity`
   - distinct memories share display text;
   - both variants must preserve identities.

9. `tie-heavy-distractors`
   - exercises deterministic ranking/tie boundaries without identity collapse.

10. `structural-expansion-ablation`
    - primary succeeds because of A007 structural expansion;
    - no-structural-expansion diagnostic demonstrates the intended difference.

11. `familiarity-disabled-equivalence`
    - ASCA_PRIMARY and familiarity-disabled control must have identical
      deterministic control outcome.

12. `invalid-contract`
    - malformed input/evidence fails closed before uncontrolled execution.

The final ordered case-ID set is frozen before accepting the first final A010
outcome.

## 10. Fixture scaling

A010 should include deterministic distractor populations large enough to make
selection differences observable without becoming a hardware benchmark.

Recommended fixed corpus-size classes:

- small: 16 memories;
- medium: 64 memories;
- large: 256 memories.

Not every case needs every size. The final fixture should keep runtime
reasonable in portable CI.

Distractor generation must be deterministic and canonical. Relevant targets
must not be moved or retuned after seeing the final classification.

## 11. Portable embedding boundary

Portable A010 uses the real A005 `ExactVectorMemoryIndex` with a deterministic
qualification-only embedding adapter, as A009 did.

The adapter:

- has a fixed descriptor;
- returns frozen predeclared vectors;
- performs no network call;
- exposes deterministic query/document vectors;
- is not evidence about a physical embedding model.

A010 does not fabricate final working sets. Both primary variants must pass
through the real A005 result contracts.

## 12. Primary logical-work metrics

A010 records integer counts first and derives ratios only from validated counts.

Per variant and aggregate, record at minimum:

### Correctness

- valid case count;
- procedure-success count;
- final-state-correct count;
- dense-only success count;
- ASCA-only success count;
- shared-success count;
- same-name identity failure count;
- deterministic repeat mismatch count.

### Retrieval work

- A005 query count;
- A005 cumulative `stored_count`;
- A005 cumulative `metadata_eligible_count`;
- A005 cumulative `scored_vector_count`;
- A005 cumulative `above_threshold_count`;
- A005 cumulative `returned_count`;
- distinct retrieval scope count.

`scored_vector_count` is a software logical count produced by the exact A005
index. It is not a FLOP count.

### Active state

- cumulative unique candidates observed;
- cumulative activated candidates;
- cumulative selected working-set items;
- peak selected working-set size;
- final selected working-set size.

These are state-item counts, not bytes of RAM or hardware memory traffic.

### Procedural control

- procedure attempt count;
- successful first-attempt count;
- mismatch count;
- forced recovery-scope count;
- maximum observed attempt count;
- duplicate execution-ID failure count;
- post-completion extra-attempt count.

A010 must not hide the fact that selective recovery can trade fewer retrieval
queries/active items for additional procedure attempts.

## 13. No synthetic scalar efficiency score

A010 must not combine retrieval, active-state, and procedure counts into one
weighted "efficiency score".

There is no justified conversion rate between:

- one vector score;
- one active memory;
- one procedure attempt;
- one model token;
- one nanosecond.

Report the dimensions separately.

This prevents arbitrary weights from manufacturing a preferred outcome.

## 14. Primary A010 hypothesis

A010 tests:

> On the frozen controlled workload, ASCA_PRIMARY preserves the deterministic
> procedure-success/final-state coverage of DENSE_EXHAUSTIVE while reducing
> logical retrieval work and active-memory state.

The primary outcome is exactly one of:

- `SUPPORTED`;
- `MIXED`;
- `NOT_SUPPORTED`.

### 14.1 SUPPORTED

Require all:

- no dense-only procedure success on valid primary comparison cases;
- ASCA and dense procedure-success counts are equal;
- final-state correctness passes for every shared success;
- same-name identity failures = 0 for both variants;
- ASCA aggregate A005 query count is strictly lower than dense;
- ASCA aggregate A005 `scored_vector_count` is strictly lower than dense;
- ASCA aggregate cumulative selected working-set items are strictly lower than
  dense;
- at least one designated case shows success parity with strictly smaller ASCA
  selected working set;
- A009 boundedness remains intact: no more than 3 procedure attempts and no
  scope above the declared maximum;
- duplicate execution-ID failures = 0;
- post-completion extra-attempt failures = 0;
- ASCA_PRIMARY repeat run is logically identical;
- DENSE_EXHAUSTIVE repeat run is logically identical;
- no hidden fixture or threshold drift is detected.

Procedure attempts are reported but are not required to be lower for ASCA,
because mismatch-driven recovery can intentionally exchange additional
procedure attempts for narrower earlier retrieval.

### 14.2 MIXED

Use when there is real selective benefit but the full SUPPORTED contract does
not hold, for example:

- ASCA reduces retrieval/active-state counts but dense succeeds on one or more
  cases that ASCA misses;
- correctness is equal but only one of the declared logical-work dimensions is
  reduced;
- aggregate savings exist but a required deterministic diagnostic fails while
  evidence remains otherwise valid.

### 14.3 NOT_SUPPORTED

Use when valid frozen evidence shows no useful support for the primary
hypothesis, including either:

- ASCA provides no strict reduction in the declared retrieval/active-state
  dimensions; or
- no declared case demonstrates correctness parity with a selective-state
  reduction; or
- valid results otherwise show that the selective objective is not supported
  on this frozen workload.

A valid `MIXED` or `NOT_SUPPORTED` experiment exits with success status.
Invalid evidence exits nonzero.

## 15. Dense-only success is first-class evidence

The benchmark must include and report `dense_only_success_count`.

A dense-only success:

- is never silently discarded;
- cannot be reclassified as a fixture error merely because ASCA loses;
- prevents `SUPPORTED`;
- contributes directly to `MIXED` or `NOT_SUPPORTED` classification.

The sentinel routing-miss case exists specifically to prevent a benchmark that
contains only easy ASCA wins.

## 16. A007 and A003 ablation requirements

### Structural expansion ablation

The no-structural-expansion control must prove that its only intended
difference is the A007 initial policy.

It must not:

- change the A005 threshold;
- change cue texts;
- increase A006 budgets;
- change A008 expectations;
- alter procedure requirements.

### Familiarity-disabled diagnostic

The familiarity-disabled control is expected to preserve deterministic
retrieval/procedure behavior because A009 familiarity is evidence-only.

A control-result difference indicates an architecture leak and invalidates the
diagnostic.

A010 does not reinterpret A003 familiarity as semantic truth or routing
authority.

## 17. Physical qualification

A010 includes a local physical integration layer after the deterministic fixture
is frozen.

Physical retrieval may use the already-qualified A005 embedding identity:

- model: `qwen3-embedding:0.6b`;
- digest:
  `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`;
- embedding dimension: 1024;
- minimum similarity threshold:
  `0.5037018224299838`.

The physical comparison must use the same documents and query texts for both
variants.

The physical result is secondary evidence. It may record:

- procedure success/failure;
- query count;
- returned/selected memory counts;
- observed wall-clock duration around the comparison runner;
- backend identity and version when available.

Observed timing is descriptive only unless a later task adds a statistically
defined timing protocol.

## 18. Model boundary

A010 does not add model calls to successful cases merely to manufacture a
model-token comparison.

A004 `qwen3.5:4b` may remain available only where an already-declared terminal
fallback diagnostic requires it.

If a physical model call occurs, record:

- exact model tag;
- exact digest;
- prompt tokens when reported;
- generated tokens when reported;
- backend timing when reported;
- request count;
- nonempty-content status.

These observations do not control A010 procedure success or the primary
classification.

A010 therefore does not claim general model-token savings unless the actual
frozen workloads exercise comparable model calls on both variants.

## 19. CI boundary

GitHub CI may run:

- full unit tests;
- portable A010 deterministic benchmark;
- portable A010 qualification CLI;
- existing architecture/repository/A003/A008/A009 portable gates.

GitHub CI must not:

- require Ollama;
- download Qwen models;
- run physical Qwen embedding/model qualification;
- infer hardware performance from portable logical counts.

## 20. Experiment validity

Portable qualification exits nonzero for invalid evidence, including:

- fixture fingerprint drift;
- ordered case-ID drift;
- hidden per-variant corpus or query drift;
- different minimum similarity threshold between primary variants;
- dense `top_k` below index document count;
- dense runner not using `select_exhaustive()`;
- ASCA primary runner not using the actual A009 primary path;
- A008 mode other than `CHUNKED` in primary comparison;
- duplicate procedure execution IDs;
- procedure attempt after completion;
- ASCA scope above declared maximum;
- malformed A005 counts;
- impossible aggregate/raw count relationships;
- identity collapse;
- nondeterministic repeated logical result;
- ablation changing fields outside its declared axis;
- model output changing deterministic procedure-success classification.

## 21. Determinism

Portable A010 contains no timing requirement and no randomness.

Given identical:

- case fixture;
- deterministic embedding vectors;
- A005 corpus and threshold;
- cue tiers;
- A007 profile;
- A006 selector/exhaustive policy;
- A008 procedure library;
- action-memory requirements;
- world snapshot;

the logical normalized result for every variant must be identical.

The benchmark should run each primary variant at least twice and compare the
normalized logical evidence exactly.

## 22. Trace and normalized evidence

A010 should not compare raw implementation objects field-by-field when the
systems intentionally use different control paths.

Each variant instead produces an immutable normalized result containing:

- variant;
- case ID;
- success flag;
- final-state-correct flag;
- final world-state reference;
- evaluated scope indices;
- query/result count summaries;
- final working-set memory IDs;
- cumulative/peak working-set counts;
- procedure execution IDs;
- procedure states;
- mismatch/recovery counts;
- identity-preservation flag;
- stable logical trace signature.

Raw A005/A008/A009 evidence remains attached or referenceable for validation.

## 23. Same-name identity boundary

A010 continues the project rule that display text is not identity.

Dense activation must not collapse memories because:

- names match;
- retrieval text matches partially;
- content text is equal.

Identity is the stable memory ID.

Any same-name collapse invalidates qualification.

## 24. Error handling

A010 fails closed on:

- blank case/variant/procedure IDs;
- unknown root procedure;
- empty primary fixture;
- duplicate case IDs;
- duplicate memory IDs;
- malformed cue tiers;
- mismatched primary inputs;
- impossible dense top-k;
- invalid A005 result counts;
- unsupported A008 primary mode;
- missing immutable world snapshot;
- invalid procedure requirement;
- duplicate execution IDs;
- inconsistent normalized/raw evidence;
- invalid research classification inputs.

Malformed cases are not skipped silently.

## 25. Claims boundary

If A010 is `SUPPORTED`, it may claim only what is directly measured, such as:

- equal deterministic procedure-success coverage to the declared dense baseline
  on the frozen controlled workload;
- lower A005 query count on that workload;
- lower exact-index logical vector-scoring count on that workload;
- lower cumulative/peak selected-memory counts on that workload;
- bounded recovery and deterministic replay;
- preserved identity and final-state correctness.

It must not convert those results into unsupported claims of:

- lower FLOPs;
- lower energy or power;
- lower hardware memory bandwidth;
- lower RAM usage in bytes;
- lower general latency;
- lower general model-token use;
- superiority to dense LLM architectures;
- superiority on open-domain reasoning;
- biological efficiency;
- AGI or consciousness.

"Fewer logical vector scores" is not "fewer FLOPs" unless separately measured.

## 26. No historical outcome rewriting

A010 must not reinterpret earlier results.

In particular:

- A006 remains `NOT_SUPPORTED` for its frozen convergence-benefit hypothesis,
  even if A010 selective system-level behavior is favorable;
- A007 remains `SUPPORTED`;
- A008 remains `SUPPORTED`;
- A009 remains `SUPPORTED`.

A010 answers a different system-level question.

## 27. No A009 mutation as a shortcut

A010 may import and call A009 public APIs.

It must not change A009 primary semantics merely to simplify the comparison.

If A010 requires benchmark-only ablations, keep them in the A010 comparison
package and prove that the A010 ASCA_PRIMARY path delegates to the real A009
controller.

The frozen A009 fixture/fingerprint remain unchanged.

## 28. FlyWireLLM boundary

A010 does not:

- read or modify FlyWireLLM checkpoints;
- restart FlyWireLLM training;
- import FlyWireLLM source;
- use FlyWireLLM as the embedding or generative model;
- change FlyWireLLM repository state.

## 29. Task activation gate

A010 remains PLANNED while this design and its implementation plan are under
review.

No A010 GitHub issue may be created before the approved implementation plan
reaches its explicit activation task.

At activation:

- re-check main/origin synchronization and CI;
- create the actual A010 GitHub issue and capture its returned number;
- create the A010 task ledger;
- mark A010 ACTIVE;
- create an isolated feature branch/worktree;
- repair the stale README A009 issue sentence;
- keep A011 PLANNED with no issue.

Do not pre-write a guessed issue number into repository documents.

## 30. Qualification and closure gates

A010 may close only when:

- deterministic fixture identity is frozen;
- primary ASCA path demonstrably delegates to A009;
- dense path demonstrably uses A005 + A006 `select_exhaustive()`;
- shared-input fairness checks pass;
- portable deterministic qualification is valid;
- the primary outcome is recorded exactly as
  `SUPPORTED`, `MIXED`, or `NOT_SUPPORTED`;
- physical qualification is recorded when runtime prerequisites are available;
- historical A006/A007/A008/A009 outcomes remain unchanged;
- FlyWireLLM remains untouched;
- exact feature-branch CI passes;
- whole-branch Critical/Important findings are resolved;
- reviewed behavior is integrated to main;
- exact final-main CI passes;
- final main is clean and synchronized 0/0;
- A010 issue closes only after final-main evidence is GREEN.

## 31. Non-goals

A010 v0.1 does not:

- change A003 familiarity semantics;
- retune the A005 physical threshold;
- promote A006 `SELECTIVE_CONVERGENCE`;
- modify A007 trigger enums;
- change A008 CHUNKED semantics;
- change A009 primary policy;
- execute real OS/API/LConnect/BConnect actions;
- benchmark real-world tool side effects;
- train or fine-tune a model;
- add artificial model calls for token accounting;
- collapse logical counts into a synthetic efficiency score;
- claim hardware/energy/FLOP superiority;
- touch FlyWireLLM;
- perform A011 final ASCA v0.x qualification.

## 32. Success definition

A010 succeeds as an engineering milestone when it produces a fair, frozen,
reproducible comparison between the real A009 selective path and a deliberately
non-selective A005+A006 exhaustive path, with explicit correctness, retrieval,
active-state, and procedural evidence.

The research hypothesis is `SUPPORTED` only if ASCA matches the dense
baseline's deterministic success/final-state coverage on the frozen primary
cases while strictly reducing the declared aggregate logical retrieval and
selected-memory state counts.

If the evidence is mixed or negative, A010 still succeeds as a research task by
recording `MIXED` or `NOT_SUPPORTED` without retuning the fixture.
