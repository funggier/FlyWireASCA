# FlyWireASCA A008 Procedural Memory / Skill Chunking Qualification

Date: 2026-10-09
Task: A008 — Procedural Memory / Skill Chunking
Primary architecture: CHUNKED hierarchical procedures with explicit step-level checkpoints

## Qualification summary

A008 qualified the deterministic procedural-memory mechanism on the frozen
standard-library-only fixture.

Final A008 hypothesis outcome: `SUPPORTED`

This is a mechanism result for the declared deterministic fixture. It does not
claim real-world tool robustness, lower hardware cost, or general superiority
over flat execution.

## Exact branch candidate

- branch: `research/a008-procedural-memory`
- candidate SHA: `0bfee1dfc424934ed783150f6c4d86140c6502d2`
- exact branch CI: `37956221852` — success
- local full suite: `370 passed`
- architecture contract audit: PASS
- repository qualification: PASS
- A003 familiarity qualification: PASS
- `git diff --check`: PASS
- branch worktree: clean

GitHub CI also executed:

`python scripts/qualify_procedural_memory_a008.py`

on the exact candidate SHA.

## Frozen deterministic fixture

- qualification scope: `deterministic_procedural_memory_a008`
- fixture version: `a008-deterministic-v1`
- fixture fingerprint:
  `f52fbd4ab018386ff3cbfb62a68cc44a4b40e54ec4fd9a3b2e885dd2c5663fc6`
- maximum call depth: 8
- recursion: forbidden
- matcher: exact kind/payload matching
- automatic retry: none

Frozen case IDs:

- `tea-success`
- `coffee-success`
- `document-backup-success`
- `package-preparation-success`
- `heat-water-failure`
- `direct-recursion-invalid`
- `indirect-recursion-invalid`
- `missing-callee-invalid`
- `depth-nine-invalid`

The fixture was fingerprinted before the final qualification result was used as
closure evidence.

## Comparative modes

### FLAT

CALL_PROCEDURE hierarchy is expanded to primitive ACTION steps before execution.
Every primitive outcome is checked.

### CHUNKED

Hierarchy is preserved. Root CALL_PROCEDURE is one root-visible dispatch while
internal primitive outcomes and CALL completion boundaries remain checked.

This is the recommended/primary A008 architecture.

### BLIND_CHUNKED

Hierarchy is preserved but primitive checks below the root are suppressed.
CALL completion boundaries remain checked. This is a negative control rather
than the recommended runtime policy.

## Success correctness

Declared failure-free success cases: 4.

Results:

- FLAT success count: 4/4
- CHUNKED success count: 4/4
- BLIND_CHUNKED success count: 4/4
- FLAT final-state correctness: 4/4
- CHUNKED final-state correctness: 4/4
- BLIND_CHUNKED final-state correctness: 4/4
- FLAT ↔ CHUNKED ordered primitive-sequence equivalence: 4/4
- deterministic logical replay: PASS

Therefore CHUNKED changed the control representation without changing the
primitive action sequence or final deterministic world state in the declared
success cases.

## Root-visible dispatch / chunking result

Across the four declared success cases:

- FLAT root-visible dispatches: 13
- CHUNKED root-visible dispatches: 8
- absolute reduction: 5 dispatches
- relative reduction on this fixture: `5 / 13 = 0.38461538461538464`
- maximum deliberative compression ratio: 2.0

These are control-state / root-controller-visible dispatch measurements.

They do not establish lower FLOPs, energy use, token count, wall-clock latency,
or real-world execution cost.

## Chunk reuse

The same `heat-water` procedure ID is referenced by two distinct parent
procedures:

- `tea`
- `coffee`

Qualified reuse evidence:

- reused procedure: `heat-water`
- distinct parent uses: 2
- declared chunk reuse count: 2

The child definition is reused rather than copied into each parent.

## Expected-outcome / failure localization

Injected checked failure:

`tea/heat-water::heat`

### FLAT

- state: INTERRUPTED
- failing procedure: `heat-water`
- failing step: `heat`
- call path: `tea / heat-water`
- exact primitive localization: PASS

### CHUNKED

- state: INTERRUPTED
- failing procedure: `heat-water`
- failing step: `heat`
- call path: `tea / heat-water`
- exact primitive localization: PASS
- unfinished parent CALL completion was not synthesized
- no automatic retry occurred

### BLIND_CHUNKED negative control

- internal primitive checks were suppressed
- the corrupted child state propagated to the nearest CALL completion probe
- interruption was localized at parent CALL step `tea::heat-call`
- chunk-boundary localization: PASS
- localization was intentionally coarser than CHUNKED

Aggregate failure evidence:

- checked failure cases: 1
- FLAT exact primitive localization: 1/1
- CHUNKED exact primitive localization: 1/1
- BLIND_CHUNKED declared CALL-boundary localization: 1/1
- explanation-provenance checks: 3/3
- post-interruption execution failures: 0

This supports using CHUNKED rather than BLIND_CHUNKED when precise internal
failure localization is required.

## Invalid-library qualification

Four invalid libraries were required to fail before execution:

- direct recursion
- indirect recursion
- missing callee
- static call depth 9 while max depth is 8

Expected invalid cases: 4.
Unexpected validation behavior: 0.

Invalid-library cases were excluded from success/final-state/root-visible
dispatch denominators.

## Determinism

Identical library, initial state, simulator definitions, failure map, execution
ID, and mode produced identical logical execution evidence.

The qualification contains no timing metric and no randomness.

Deterministic repeat: PASS.

## Isolation / dependency boundary

A008 uses a deterministic simulator only.

There is:

- no real tool, OS command, API, LConnect, or BConnect action execution;
- no Ollama dependency;
- no Qwen3.5:4b inference;
- no embedding dependency;
- no semantic graph traversal;
- no automatic retry or automatic recovery;
- no automatic A007 invocation.

A002 `ProcedureRef` and `Observation` contracts were reused and not modified.
A004 model paths were not modified.
A007 closure evidence remains unchanged with its historical `SUPPORTED`
outcome.

FlyWireLLM remained paused and untouched, with its repository clean and
synchronized and no training runner observed during A008 exact qualification.

## Interpretation

The frozen deterministic evidence supports architecture option 1:

**Hierarchical Procedure + explicit step-level checkpoints (CHUNKED).**

Within the declared fixture, it achieved all of the following simultaneously:

- exact primitive/final-state equivalence to FLAT on success cases;
- actual reuse of a shared procedure chunk;
- fewer root-controller-visible dispatches;
- exact primitive failure localization equal to FLAT;
- preserved explanation-memory provenance;
- deterministic bounded execution with no retry;
- clearer failure localization than BLIND_CHUNKED.

Therefore CHUNKED is the appropriate procedural representation to carry into
A009 Integrated Cognitive Loop.

The evidence is deliberately narrow: it demonstrates control-state compression
and procedural semantics, not a hardware/runtime efficiency improvement.

## Claims boundary

A008 may claim deterministic procedure reuse, exact expected-outcome checks,
failure localization, and root-visible dispatch reduction on this fixture.

A008 does not claim:

- human-like or biological procedural memory;
- lower FLOPs, energy, or power;
- fewer model tokens;
- faster real-world tools;
- production OS/API robustness;
- natural-language procedure selection.

## Next milestone

A009 — Integrated Cognitive Loop remains PLANNED with no GitHub issue.

A009 is the appropriate milestone to combine qualified A003/A005/A006/A007/A008
mechanisms and the A004 model adapter, including use of real procedural
mismatch evidence as an input to higher-level control decisions.

## Whole-branch review and post-review qualification

The required final whole-branch review was performed as a separate author
self-review because no fresh reviewer/subagent tool was available in this
harness.

Three findings were graded **Important**:

1. `ProcedureLibrary.max_call_depth` accepted values above the A008 architectural
   cap even though the approved spec fixes the maximum at 8;
2. invalid-library fixture definitions could contaminate chunk-reuse accounting,
   even though those cases are explicitly excluded from success/final-state/
   root-visible-dispatch denominators;
3. the qualification payload validator enforced nonnegative counters but did
   not reject impossible count/reuse relationships, allowing structurally
   inconsistent evidence to survive validation.

All three findings were fixed under RED -> GREEN tests.

Post-review behavior candidate:

`b0ad2f1abed08683ea8218861c97f3c2d47384d3`

Exact post-review branch CI:

`37959983484` — success

Post-review deterministic qualification was rerun because benchmark/validation
semantics changed.

Post-review deterministic qualification:

- experiment validity: PASS;
- Post-review A008 hypothesis outcome: `SUPPORTED`;
- fixture fingerprint unchanged:
  `f52fbd4ab018386ff3cbfb62a68cc44a4b40e54ec4fd9a3b2e885dd2c5663fc6`;
- FLAT / CHUNKED root-visible dispatches: 13 / 8;
- maximum deliberative compression ratio: 2.0;
- shared `heat-water` reuse count: 2;
- FLAT exact failure localization: 1/1;
- CHUNKED exact failure localization: 1/1;
- BLIND_CHUNKED boundary localization: 1/1;
- invalid-library validation failures: 0;
- post-interruption execution failures: 0;
- deterministic logical replay: PASS.

Fresh post-review local gates:

- targeted library/benchmark/qualification tests: 28 passed;
- full suite: 381 passed;
- architecture contract audit: PASS;
- repository qualification: PASS;
- A003 familiarity qualification: PASS;
- `git diff --check`: PASS.

These review fixes do not change the A008 mechanism conclusion or claims
boundary. They strengthen enforcement of the already-approved architecture and
qualification evidence contract.