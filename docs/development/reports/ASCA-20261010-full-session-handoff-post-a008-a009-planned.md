# FlyWireASCA Full Session Handoff — Post-A008 / A009 Planned

Date: 2026-10-10
Repository: `funggier/FlyWireASCA`
Local repository: `T:\Space\Projects\ProjectsAI\FlyWireASCA`

## 1. Read this first

This handoff supersedes the partial conversational context that ended while A008
Task 4 appeared to be WIP.

**Do not resume from A008 Task 4.**

Git/GitHub/live CI are authoritative. A008 has already been fully qualified,
reviewed, integrated into `main`, and closed GREEN.

The next architectural milestone is:

`A009 — Integrated Cognitive Loop`

A009 is currently **PLANNED** with **no GitHub issue**.

Do not create an A009 issue until the A009 conversational design and written
spec/plan gates are approved.

## 2. Authoritative live FlyWireASCA state before this handoff commit

Main repository:

- branch: `main`
- HEAD: `f1833113c9739e4ecc1b700899b22bda9766ee12`
- origin/main: same SHA
- ahead/behind: `0/0`
- worktree: clean

Final A008 main commit:

`f1833113c9739e4ecc1b700899b22bda9766ee12`

Commit message:

`Close A008 integration ledger`

Exact final-main CI:

- run: `37962342825`
- head SHA: `f1833113c9739e4ecc1b700899b22bda9766ee12`
- conclusion: **success**

GitHub Issue #8:

- title: `A008 — Procedural Memory / Skill Chunking`
- state: **CLOSED**
- state reason: **completed**

A008 local worktree was removed and the local A008 feature branch was deleted
non-force during closure. The remote history is intentionally preserved:

`origin/research/a008-procedural-memory`

Remote branch head:

`0142973814fb67dd28a54fa454f25fa88f7dfcd9`

## 3. Roadmap state

Current roadmap:

- A001 — DONE
- A002 — DONE
- A003 — DONE
- A004 — DONE
- A005 — DONE
- A006 — DONE
- A007 — DONE
- A008 — DONE
- A009 — PLANNED
- A010 — PLANNED
- A011 — PLANNED

No A009 GitHub issue exists.

## 4. A008 final result

A008 task:

`docs/development/tasks/A008-procedural-memory-skill-chunking.md`

A008 qualification report:

`docs/development/reports/ASCA-20261009-A008-procedural-memory-skill-chunking.md`

Approved design:

`docs/superpowers/specs/2026-10-09-a008-procedural-memory-design.md`

Approved implementation plan:

`docs/superpowers/plans/2026-10-09-a008-procedural-memory.md`

Primary A008 hypothesis outcome:

`SUPPORTED`

Primary architecture qualified by A008:

**Hierarchical Procedure + explicit step-level checkpoints (CHUNKED)**

This is the previously discussed “architecture option 1”.

Controls:

- `FLAT`
- `CHUNKED`
- `BLIND_CHUNKED`

CHUNKED is the recommended representation to carry into A009.

BLIND_CHUNKED remains a negative control, not the recommended runtime policy.

## 5. A008 frozen deterministic qualification

Qualification scope:

`deterministic_procedural_memory_a008`

Fixture version:

`a008-deterministic-v1`

Fixture fingerprint:

`f52fbd4ab018386ff3cbfb62a68cc44a4b40e54ec4fd9a3b2e885dd2c5663fc6`

Maximum procedure call depth:

`8`

Recursion:

forbidden

Matcher:

exact observation kind + exact payload reference

Automatic retry/recovery:

none

Final frozen case families:

- `tea-success`
- `coffee-success`
- `document-backup-success`
- `package-preparation-success`
- `heat-water-failure`
- `direct-recursion-invalid`
- `indirect-recursion-invalid`
- `missing-callee-invalid`
- `depth-nine-invalid`

## 6. Key A008 evidence

Failure-free success cases:

- FLAT: 4/4
- CHUNKED: 4/4
- BLIND_CHUNKED: 4/4
- FLAT final-state correctness: 4/4
- CHUNKED final-state correctness: 4/4
- BLIND final-state correctness: 4/4
- FLAT ↔ CHUNKED primitive-sequence equivalence: 4/4

Root-visible dispatches across the four success cases:

- FLAT: 13
- CHUNKED: 8
- absolute reduction: 5
- relative reduction on this frozen fixture: `5 / 13 = 0.38461538461538464`
- maximum deliberative compression ratio: `2.0`

These are software/control-state measurements only.

Do not convert them into claims about:

- FLOPs
- energy
- power
- token use
- wall-clock speed
- production runtime efficiency

Shared chunk reuse:

- procedure ID: `heat-water`
- reused by parent `tea`
- reused by parent `coffee`
- distinct parent use count: 2

Injected checked failure:

`tea/heat-water::heat`

Localization:

- FLAT: exact primitive localization 1/1
- CHUNKED: exact primitive localization 1/1
- BLIND_CHUNKED: nearest CALL-boundary localization 1/1
- explanation provenance: 3/3
- post-interruption execution failures: 0

This is why CHUNKED should be preferred over BLIND_CHUNKED for A009 when
precise internal failure localization matters.

## 7. A008 branch qualification history

Task 1:

`6720fea` — Add A008 procedure library contracts and task activation

Task 2:

`f8f6373` — Add A008 exact verifier and deterministic simulator

Task 3:

`38d8aa5` — Add A008 hierarchical procedural runner

Task 4:

`0bfee1d` — Add A008 deterministic procedural qualification

Initial closure candidate:

`655336a` — Qualify A008 procedural memory skill chunking

Review hardening:

`b0ad2f1abed08683ea8218861c97f3c2d47384d3`

Post-review evidence:

`0142973814fb67dd28a54fa454f25fa88f7dfcd9`

Main integration evidence:

`1972c98b1b7d1346bd4b66458ac92b4ef00e11cd`

Final integration ledger:

`f1833113c9739e4ecc1b700899b22bda9766ee12`

## 8. A008 exact CI evidence

Initial exact branch qualification candidate:

- SHA: `0bfee1dfc424934ed783150f6c4d86140c6502d2`
- CI: `37956221852`
- result: success
- local suite: 370 passed

Whole-branch review hardened candidate:

- SHA: `b0ad2f1abed08683ea8218861c97f3c2d47384d3`
- CI: `37959983484`
- result: success
- post-review local full suite: 381 passed

First merged-main behavior/evidence:

- SHA: `0142973814fb67dd28a54fa454f25fa88f7dfcd9`
- CI: `37961029994`
- result: success
- merged-main local suite: 383 passed

Main integration evidence commit:

- SHA: `1972c98b1b7d1346bd4b66458ac92b4ef00e11cd`
- CI: `37961779986`
- result: success

Final integration ledger:

- SHA: `f1833113c9739e4ecc1b700899b22bda9766ee12`
- CI: `37962342825`
- result: success

## 9. Whole-branch review findings already resolved

The A008 whole-branch author self-review found three Important issues.

All were fixed under RED -> GREEN tests before final integration:

1. `ProcedureLibrary.max_call_depth` allowed values above the architecture cap
   even though A008 fixes the maximum at 8.
2. Invalid-library fixtures could contaminate chunk-reuse accounting even though
   invalid cases must not enter success/final-state/root-visible-dispatch
   denominators.
3. Qualification validation allowed impossible count/reuse relationships even
   though individual counters were nonnegative.

After the fixes:

- deterministic qualification reran;
- frozen fingerprint remained unchanged;
- outcome remained `SUPPORTED`;
- FLAT / CHUNKED root-visible dispatches remained 13 / 8;
- maximum compression remained 2.0;
- failure localization remained FLAT/CHUNKED/BLIND = 1/1, 1/1, 1/1;
- exact post-review branch CI passed.

Do not re-open these findings unless new evidence demonstrates a regression.

## 10. Important A008 semantics to preserve into A009

### Reused A002 contracts

A008 reuses:

- `ProcedureRef`
- `Observation`

Do not create duplicate procedure or observation identity types in A009.

### Procedure architecture

A008 procedures are immutable and hierarchical.

Step kinds:

- `ACTION`
- `CALL_PROCEDURE`

Outcome matcher:

- `EXACT`

A CALL completion contract compares:

- observation kind
- expected payload ref
- matcher

The parent CALL expectation ID may differ from the child completion outcome ID.

### CHUNKED behavior

CHUNKED:

- preserves hierarchy;
- root CALL is one root-visible dispatch;
- checks primitive ACTION outcomes internally;
- checks CALL completion boundaries;
- interrupts immediately on checked mismatch;
- performs zero automatic retry;
- does not synthesize a parent CALL result after an interrupted child;
- executes no later primitive after checked interruption.

### BLIND_CHUNKED behavior

BLIND_CHUNKED:

- suppresses checked primitive outcomes below root;
- still checks CALL completion boundaries;
- can therefore localize corrupted child state only at a coarser CALL boundary.

This is intentional negative-control behavior.

### Explanation-memory IDs

Explanation-memory IDs are provenance references.

A008 does not infer causal truth from them.

## 11. Boundaries that remain in force

A008 itself does not:

- execute real OS/API/LConnect/BConnect actions;
- use Qwen3.5:4b;
- use Ollama;
- use embeddings;
- traverse an ASCA semantic graph;
- automatically invoke A007;
- automatically retry/recover;
- select procedures from natural language;
- claim hardware/runtime efficiency.

Do not silently erase these boundaries when designing A009.

A009 may deliberately integrate additional qualified subsystems, but each
integration should be explicit in its approved design.

## 12. Previous milestone results that A009 must preserve

A003 Familiarity:

- exact cheap familiarity lookup;
- deterministic;
- not truth/identity/semantic equivalence.

A004 Model Adapter:

- local generative baseline based on `qwen3.5:4b`;
- keep model semantics separate from memory/control evidence.

A005 Vector Memory Retrieval:

- physical result: `VECTOR_SUFFICIENT` for retrieval scope;
- model: `qwen3-embedding:0.6b`;
- pinned digest:
  `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`;
- embedding dimension: 1024;
- frozen physical threshold:
  `0.5037018224299838`.

A006 Working Set / Selective Activation:

- deterministic bounded working-set mechanism qualified;
- frozen physical convergence-benefit outcome:
  `NOT_SUPPORTED`;
- this negative result remains valid and must not be rewritten by later tasks;
- `SINGLE_BEST` remained the stronger physical selector under the A006 frozen
  fixture.

A007 Surprise, Uncertainty & Expansion:

- final structural-expansion result: `SUPPORTED`;
- primary physical selector: `SINGLE_BEST`;
- SIGNAL_DRIVEN recovery: 3;
- regression: 0;
- required-memory coverage SIGNAL_DRIVEN: 1.0;
- ALWAYS_EXPAND coverage: 1.0;
- rounds NO/SIGNAL/ALWAYS: 8 / 15 / 24;
- A007 structural triggers are not yet qualified as true prediction surprise.

A008 Procedural Memory / Skill Chunking:

- final result: `SUPPORTED`;
- CHUNKED is the recommended procedural representation for A009.

## 13. Recommended A009 design direction

A009 is architectural and must use the full design/spec/plan gate.

Recommended starting question:

> Can the already-qualified A003/A005/A006/A007/A008 mechanisms and A004 model
> adapter be composed into one deterministic, inspectable cognitive control
> loop without collapsing the boundaries between retrieval evidence,
> working-set state, expansion decisions, procedural expectations, and model
> generation?

A009 should consider an integrated flow broadly like:

```text
Input / Goal
   |
   v
A003 Familiarity
   |
   v
A005 Retrieval
   |
   v
A006 Working Set
   |
   +---- sufficient ----------------------+
   |                                      |
   +---- structural trigger --> A007 -----+
                                          |
                                          v
                                 Procedure Selection
                                          |
                                          v
                                A008 CHUNKED Runner
                                          |
                       +------------------+------------------+
                       |                                     |
                    success                              mismatch
                       |                                     |
                       v                                     v
                 continue/answer                  interruption evidence
                                                         |
                                                         v
                                               higher-level control
                                                         |
                                  +----------------------+----------------+
                                  |                                       |
                           bounded expansion                       A004 reasoning
                                  |                                       |
                                  +----------------------+----------------+
                                                         |
                                                         v
                                                   next decision
```

This is only a starting architectural sketch.

Do not implement it before A009 design is explicitly approved.

## 14. Key A009 design questions

The next session should resolve these before implementation:

1. What is the exact state object for one integrated cognitive-loop turn?
2. Which subsystem owns termination?
3. Which events may invoke A007 expansion?
4. How does A008 execution mismatch become higher-level uncertainty evidence?
5. When may A004 Qwen reasoning be called?
6. Is procedure selection explicit/deterministic first, or is natural-language
   selection part of A009?
7. What is the bounded maximum number of control iterations?
8. How are retries represented so A008's zero-auto-retry guarantee is not
   silently bypassed?
9. Which evidence is preserved in the final trace?
10. What control baselines should A009 compare?
11. What exact research hypothesis determines SUPPORTED/MIXED/NOT_SUPPORTED?
12. Which parts remain portable/deterministic CI and which, if any, require
    local physical model qualification?

Recommended conservative approach:

- start A009 with an explicit root procedure ID / deterministic routing fixture;
- integrate A007 expansion only through typed control events;
- keep A004 generation optional and separately measurable;
- preserve a full execution trace;
- bound all loops/retries/expansions;
- avoid real OS/API tools until the integrated control semantics are qualified.

## 15. Current documentation caveat

Before this handoff was written, `docs/development/tasks/CURRENT.md` correctly
identified A009 as PLANNED, but some prose still said A008 final integration
"remains the finishing gate."

That wording is stale.

Authoritative reality:

- A008 final integration is GREEN;
- final main CI `37962342825` succeeded;
- Issue #8 is closed;
- main is clean/synchronized 0/0.

This handoff and live Git/GitHub state supersede that stale prose.

## 16. FlyWireLLM isolation state

Separate repository:

`T:\Space\Projects\ProjectsAI\FlyWireLLM`

Live state checked during handoff:

- branch: `research/l004-base50m-pretraining`
- HEAD:
  `9aa8acba1ecdefcdce4678b2914fc2d2dcaacc14`
- upstream: same
- ahead/behind: 0/0
- worktree: clean
- no matching training/pretraining runner observed

FlyWireLLM remains paused/untouched.

Do not restart or mutate it as part of A009 unless explicitly authorized by the
user and the A009 design requires it.

## 17. Session-new startup procedure

In a new session:

1. Read this handoff first.
2. Read `docs/development/tasks/CURRENT.md`.
3. Read `docs/development/tasks/ROADMAP.md`.
4. Read the A008 report/spec/plan listed above.
5. Verify live:
   - `git status`
   - `git rev-parse HEAD`
   - `git rev-list --left-right --count origin/main...HEAD`
   - latest exact main CI
   - Issue #8 CLOSED
   - no A009 issue exists
6. Treat Git/GitHub/runtime as authoritative over stale text.
7. Do not recreate A008 worktree or resume A008 Task 4.
8. Start A009 through the architectural brainstorming/design gate.
9. Do not create Issue #9 until A009 implementation/task activation stage
   defined by its approved plan.
10. Keep FlyWireLLM paused/untouched.

## 18. Suggested new-session prompt

Use:

```text
@use-local-workspace
ทำ funggier/FlyWireASCA ต่อจาก Full Handoff ล่าสุด โดยอ่าน
docs/development/reports/ASCA-20261010-full-session-handoff-post-a008-a009-planned.md
ก่อน ยึด Git/GitHub/runtime สดเป็น authoritative source ห้าม reset/clean
worktree และอย่าย้อนกลับไปทำ A008 Task 4 เพราะ A008 ปิด GREEN และ integrated
แล้ว ให้ตรวจ main/CI/Issue #8 ก่อน จากนั้นเริ่ม A009 — Integrated Cognitive
Loop ผ่าน architectural design/spec/plan gates โดยคงผล A006 NOT_SUPPORTED,
A007 SUPPORTED, A008 SUPPORTED และใช้ CHUNKED (architecture option 1) เป็น
procedural representation หลัก ห้ามสร้าง A009 issue ก่อนถึง task activation
ตาม plan และห้ามแตะ FlyWireLLM
```

## 19. Immediate next action

The immediate next work is **not code**.

Start A009 architectural design.

The first design section should define the integrated cognitive-loop state
machine and ownership boundaries between:

- Familiarity
- retrieval
- working-set selection
- bounded expansion
- procedural execution
- model reasoning
- termination/recovery

Do not implement A009 until its conversational design, written spec, and
implementation plan are approved.