# A009 — Integrated Cognitive Loop Qualification Report

Date: 2026-10-10
Milestone: A009 — Integrated Cognitive Loop
GitHub Issue: #9
Branch: `research/a009-integrated-cognitive-loop`
Initial qualified branch SHA: `eecca7d842753fd2b39e8c565c704fb2e6303896`
Initial exact branch CI run: `37992245085` - success
Reviewed behavior SHA: `4796d28e9285dc395240010987126a45c4e5ed5d`
Exact post-review branch CI run: `37999918527` - success
Primary A009 hypothesis outcome: `SUPPORTED`

## Executive result

A009 qualifies a bounded integrated control loop that composes:

- A003 exact familiarity evidence;
- A005 exact vector-memory retrieval;
- A006 `SINGLE_BEST` working-set selection;
- A007 `SIGNAL_DRIVEN` initial structural expansion;
- A008 `CHUNKED` procedure execution;
- A009-level procedure-outcome mismatch recovery;
- optional A004 `qwen3.5:4b` terminal-only diagnostic fallback.

The primary deterministic result is `SUPPORTED`.

The frozen fixture demonstrates two genuine procedure-mismatch recoveries over
the `NO_PROCEDURE_RECOVERY` control, zero regressions, equal final success
coverage to `ALWAYS_MAX_SCOPE` on declared recoverable cases, fewer total
scope evaluations than `ALWAYS_MAX_SCOPE`, bounded replay, deterministic
logical replay, and zero model-control leakage failures.

This is a control/mechanism qualification. It is not evidence of lower FLOPs,
lower energy, lower token usage, general latency superiority, human-like
cognition, or safe replay of real-world side effects.

## Approved architecture

Primary policy:

`MISMATCH_DRIVEN_RECOVERY`

Controls:

- `NO_PROCEDURE_RECOVERY`;
- `ALWAYS_MAX_SCOPE`.

Primary selector:

`SINGLE_BEST`

Primary procedure mode:

`CHUNKED`

A009 recovery cause:

`PROCEDURE_OUTCOME_MISMATCH`

The A007 structural trigger enum remains unchanged. Procedure mismatch is owned
by A009 rather than being retrofitted into A007.

Every A009 replay is a fresh A008 execution with:

- a new deterministic execution ID;
- a fresh simulator instance;
- the same immutable pre-execution world snapshot;
- the same explicit root procedure;
- the next declared retrieval scope only.

A008 still performs zero automatic retry internally.

## Frozen portable fixture

Qualification scope:

`deterministic_integrated_cognitive_loop_a009`

Fixture version:

`a009-deterministic-v1`

Frozen SHA-256 fingerprint:

`2f92b5092de346f62879ac2cbb9f96d6de5d6f919e12d0693345c8228b01ab2a`

Frozen case IDs:

1. `easy-familiar-success`
2. `unfamiliar-semantic-success`
3. `structural-expansion-success`
4. `procedure-recovery-round-one`
5. `procedure-recovery-round-two`
6. `persistent-procedure-mismatch`
7. `max-scope-mismatch`
8. `same-name-ambiguity-preserved`
9. `model-terminal-fallback`
10. `invalid-contract`

Policies executed for every valid case:

- `NO_PROCEDURE_RECOVERY`;
- `MISMATCH_DRIVEN_RECOVERY`;
- `ALWAYS_MAX_SCOPE`.

The invalid-contract case is required to fail closed before uncontrolled
execution.

## Portable raw metrics

Fresh exact-branch qualification at
`eecca7d842753fd2b39e8c565c704fb2e6303896` produced:

| Metric | Value |
| --- | ---: |
| case_count | 10 |
| valid_case_count | 9 |
| invalid_case_count | 1 |
| recoverable_case_count | 2 |
| genuine_recovery_count | 2 |
| regression_count | 0 |
| primary_recoverable_success_count | 2 |
| always_recoverable_success_count | 2 |
| primary_total_scope_evaluations | 19 |
| always_total_scope_evaluations | 27 |
| primary_success_count | 6 |
| always_success_count | 6 |
| primary_final_state_correct_count | 6 |
| primary_same_name_ambiguity_failure_count | 0 |
| CHUNKED/FLAT diagnostic case count | 6 |
| CHUNKED/FLAT equivalence count | 6 |
| max_procedure_attempt_count | 3 |
| max_scope_index | 2 |
| duplicate_execution_id_failure_count | 0 |
| model_fallback_call_count | 1 |
| model_control_leakage_failure_count | 0 |
| deterministic_repeat_match | true |

The primary policy evaluated 19 scopes across the frozen valid fixture versus
27 for `ALWAYS_MAX_SCOPE`, while preserving the same six successful cases.

This scope-count difference is retrieval/control evidence only. It is not a
claim about FLOPs, energy, tokens, latency, or hardware efficiency.

## Genuine recovery evidence

### Round-one recovery

`procedure-recovery-round-one`:

- `NO_PROCEDURE_RECOVERY`: procedure does not complete at scope 0;
- `MISMATCH_DRIVEN_RECOVERY`: scope sequence `0 -> 1`;
- procedure attempt sequence: `0 -> 1`;
- attempt 0 interrupts on checked expected-vs-observed mismatch;
- attempt 1 uses a new execution ID and fresh simulator snapshot;
- attempt 1 completes;
- `ALWAYS_MAX_SCOPE`: completes using scopes `0 -> 1 -> 2` before one attempt.

### Round-two recovery

`procedure-recovery-round-two`:

- `NO_PROCEDURE_RECOVERY`: procedure does not complete at scope 0;
- `MISMATCH_DRIVEN_RECOVERY`: scope sequence `0 -> 1 -> 2`;
- attempts `0 -> 1 -> 2`;
- the first recovery scope remains insufficient;
- the second and final recovery scope supplies the required memory;
- attempt 2 completes with a fresh execution ID.

No scope 3 and no fourth attempt are permitted or observed.

## Bounded failure evidence

`persistent-procedure-mismatch`:

- mismatch remains unrecoverable across all declared scopes;
- primary policy executes exactly three attempts;
- final scope index is 2;
- terminal reason is `PROCEDURE_MISMATCH_EXHAUSTED`;
- no fourth attempt occurs.

`max-scope-mismatch`:

- the initial A007 path already reaches scope 2;
- procedure mismatch occurs at the maximum scope;
- A009 performs zero replay because no wider scope exists.

## Familiarity boundary

`unfamiliar-semantic-success` proves that A003 `UNFAMILIAR` does not veto
semantic retrieval.

A003 familiarity remains exact cheap evidence, not a truth judgment and not a
semantic-equivalence oracle.

## Same-name identity boundary

`same-name-ambiguity-preserved` retains distinct IDs:

- `mem-alex-a`;
- `mem-alex-b`.

Both remain distinct through A005 retrieval, A006 working-set construction, A009
trace evidence, and final working-set evidence.

Primary same-name ambiguity failure count is 0.

## Procedure representation diagnostic

Declared successful integrated cases were replayed under A008 `FLAT` as a
secondary diagnostic using the same final working set.

Result:

- diagnostic cases: 6;
- CHUNKED/FLAT equivalence: 6/6.

The diagnostic compares:

- ordered primitive action references;
- deterministic final world state;
- success/failure classification.

`CHUNKED` remains the primary A009 procedure representation.

## Model-control isolation

A004 generation is terminal-only.

The model is not allowed to choose:

- retrieval scope;
- cue generation;
- procedure identity;
- expected outcomes;
- expected-vs-observed match results;
- replay eligibility;
- deterministic termination;
- primary A009 hypothesis outcome.

The deterministic benchmark reruns the terminal-fallback case using different
model response content while holding deterministic evidence fixed.

Result:

`model_control_leakage_failure_count = 0`

Changing generated diagnostic text did not change the deterministic control
projection.

## Portable engineering gates

Fresh exact candidate gate at
`eecca7d842753fd2b39e8c565c704fb2e6303896`:

- targeted A009 benchmark/qualification/physical-contract/CI tests: 35 passed;
- full pytest suite: 455 passed;
- architecture contract audit: PASS;
- repository qualification: PASS;
- A003 familiarity qualification: PASS;
- A008 procedural-memory qualification: PASS;
- A009 portable qualification: PASS;
- A009 primary outcome: `SUPPORTED`;
- `git diff --check`: PASS;
- branch worktree: clean.

Exact GitHub branch CI:

- run: `37992245085`;
- head SHA: `eecca7d842753fd2b39e8c565c704fb2e6303896`;
- conclusion: success;
- CI contains deterministic A009 qualification;
- CI does not run physical Ollama qualification.

## Local physical qualification

The local physical qualifier was run from the exact branch candidate without
pulling, replacing, or retuning models.

Physical fixture version:

`a009-physical-v1`

A005 embedding identity:

- tag: `qwen3-embedding:0.6b`;
- digest:
  `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`;
- embedding dimension: 1024;
- frozen minimum similarity: `0.5037018224299838`.

A004 terminal model identity:

- tag: `qwen3.5:4b`;
- digest:
  `2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd`.

Physical success case:

- real embedding adapter used;
- A005 real vector index used;
- A006 `SINGLE_BEST` used;
- A007 initial path used;
- A008 `CHUNKED` used;
- successful procedure attempt count: 1;
- successful scope count: 1;
- final working set contains `mem-physical`.

Physical terminal-fallback case:

- deterministic procedure requirement deliberately remains unsatisfied;
- primary attempts: 3;
- evaluated scopes: 3;
- deterministic result: `PROCEDURE_MISMATCH_EXHAUSTED`;
- terminal model invoked: true;
- terminal model request count: 1;
- model response nonempty: true;
- prompt tokens reported: 151;
- generated tokens reported: 256;
- total model duration reported: 21,030,954,900 ns.

Physical integration validity:

`true`

Physical evidence is secondary and does not rewrite the portable primary
`SUPPORTED` outcome.

## Historical milestone preservation

A009 preserves:

- A006 final hypothesis outcome: `NOT_SUPPORTED`;
- A007 final hypothesis outcome: `SUPPORTED`;
- A008 final hypothesis outcome: `SUPPORTED`.

A009 does not promote A006 `SELECTIVE_CONVERGENCE` to primary.

A009 does not add procedure mismatch to A007 structural triggers.

A009 does not add automatic retry to A008.

## Isolation

A009 adds no real OS/API/LConnect/BConnect procedure execution path.

The A009 procedure fixture remains a deterministic simulator.

FlyWireLLM is a separate repository and remained untouched by A009 work.

No FlyWireLLM training runner was started, modified, or resumed.

## Experiment validity and outcome

Experiment validity is separate from research outcome.

The frozen evidence is valid.

The primary A009 hypothesis outcome is:

`SUPPORTED`

The support basis is exactly:

- at least one genuine mismatch recovery: observed 2;
- regression count = 0;
- primary recoverable success = always-max recoverable success = 2;
- primary total scope evaluations 19 < always-max 27;
- unique execution IDs: no failures;
- maximum attempts <= 3: observed 3;
- maximum scope index <= 2: observed 2;
- final-state correctness: 6/6 primary successful cases;
- same-name ambiguity failures = 0;
- CHUNKED/FLAT declared equivalence = 6/6;
- model-control leakage failures = 0;
- deterministic logical replay = true.

## Claims boundary

Supported claims:

- deterministic A003/A005/A006/A007/A008 composition;
- bounded procedure-mismatch recovery;
- exact recovery/regression/scope/attempt counts on the frozen fixture;
- snapshot-safe simulated replay;
- deterministic trace/replay;
- final-state correctness on declared cases;
- same-name identity preservation;
- terminal model isolation;
- real local Qwen embedding/model integration metadata.

Unsupported claims:

- human-like cognition;
- biological surprise;
- calibrated probabilistic uncertainty;
- autonomous safe recovery of real external side effects;
- lower FLOPs;
- lower power or energy;
- lower token use;
- general speed or latency superiority;
- superiority over a dense/non-selective baseline.

The last system-level comparison remains A010.

## Whole-branch review

Review range:

`8d0721a77abaae5d0cc6d6c7c81d4795c5d355fa..4796d28e9285dc395240010987126a45c4e5ed5d`

Reviewed behavior SHA:

`4796d28e9285dc395240010987126a45c4e5ed5d`

Exact post-review branch CI:

`37999918527` - success

Post-review local gate:

- full pytest suite: 463 passed;
- A009 portable qualification: PASS;
- primary outcome: `SUPPORTED`;
- frozen fixture fingerprint unchanged:
  `2f92b5092de346f62879ac2cbb9f96d6de5d6f919e12d0693345c8228b01ab2a`;
- genuine recoveries: 2;
- regressions: 0;
- primary / always-max scope evaluations: 19 / 27;
- maximum procedure attempts: 3;
- maximum scope index: 2;
- model-control leakage failures: 0;
- architecture contract audit: PASS;
- repository qualification: PASS;
- A003 qualification: PASS;
- A008 qualification: PASS;
- `git diff --check`: PASS.

Post-review physical qualification was rerun with exact identity validation and
remained GREEN:

- embedding tag/digest/dimension unchanged;
- terminal `qwen3.5:4b` tag and digest unchanged;
- success case: 1 attempt;
- fallback case: 3 attempts;
- terminal model requests: 1;
- physical integration valid: true;
- prompt/generated token metadata: 151 / 256;
- observed terminal model duration: 15,185,478,500 ns.

### Review method and limitation

The available environment did not provide an independent code-review subagent
or separate reviewer identity. The review was therefore an author self-review
of the entire A009 branch diff, with targeted static searches, subsystem-diff
checks, RED -> GREEN regression tests, full local qualification, exact branch
CI, and a repeated local physical qualification.

This limitation is recorded explicitly: there was no independent reviewer.
The evidence below should be interpreted as rigorous author self-review rather
than independent peer review.

Critical findings: 0

Important findings: 5

### Important finding 1 - completed primitive evidence

A context-bound action blocked by a missing memory requirement was being
included in `completed_primitive_step_paths` even though the delegate action
did not execute and no state write occurred.

Fix:

- move primitive-path recording until after the memory precondition passes;
- regression-test that the blocked failing step is absent from completed
  primitive evidence.

### Important finding 2 - fail-closed integrated result invariants

A manually constructed `CognitiveLoopResult` could previously represent
evidence the controller itself would never emit, including scope skipping,
snapshot drift, more than three attempts, and final-state reference drift.

Fix:

- require at most three attempts;
- require first attempt scope to equal the initial A007 final scope;
- require each replay scope to advance exactly one level;
- require all attempt `initial_world_state_ref` values to match;
- require one recovery scope evaluation per recovery attempt;
- require final working-set/evidence/world-state references to be internally
  consistent;
- reject attempts after a completed attempt.

### Important finding 3 - exact physical terminal-model identity

The physical A009 script pinned the A005 embedding identity exactly but
initially validated only the terminal model tag.

Fix:

- add `TERMINAL_MODEL_DIGEST`;
- require exact
  `qwen3.5:4b` digest
  `2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd`;
- pass the digest as `expected_digest` to the live A004 adapter;
- rerun physical qualification successfully.

### Important finding 4 - aggregate/result evidence drift

The portable payload validator originally recomputed the hypothesis outcome
from aggregate counters, but it did not independently derive those aggregate
counters from raw case records.

Fix:

- recompute aggregate recovery, regression, success, scope, boundedness,
  identity, final-state, diagnostic, and model-call metrics from case evidence;
- reject any aggregate value that does not match case evidence;
- retain valid `SUPPORTED`, `MIXED`, and `NOT_SUPPORTED` as research
  outcomes when the underlying case evidence is internally consistent.

### Important finding 5 - raw model-control isolation evidence

`model_control_leakage_failure_count` was computed by the benchmark but was
only visible as an aggregate counter.

Fix:

- expose `model_control_isolated` on the terminal-fallback case result;
- include it in the portable case payload;
- recompute `model_control_leakage_failure_count` from raw case evidence;
- reject payloads whose aggregate leakage metric disagrees with that evidence.

### Additional review checks

- A007 source under `src/flywire_asca/uncertainty_expansion` is unchanged from
  the activation base;
- A008 source under `src/flywire_asca/procedural_memory` is unchanged from the
  activation base;
- A009 core imports no LConnect/BConnect, subprocess, PowerShell, or direct
  network transport;
- A009 core contains no `SELECTIVE_CONVERGENCE` primary path;
- A009 core contains no `BLIND_CHUNKED` primary path;
- A009 does not import or mutate A007 `ExpansionTrigger`;
- claims remain explicitly bounded away from hardware/energy/token/general
  latency and real-world side-effect safety claims.

Whole-branch review: GREEN.

## Closure condition

This report qualifies the reviewed branch behavior. Whole-branch author
self-review and exact post-review branch CI are GREEN. A009 Issue #9 remains
open until reviewed behavior is integrated to main, exact final-main CI is
GREEN, final synchronization is 0/0 and clean, and final-main evidence is
recorded.
