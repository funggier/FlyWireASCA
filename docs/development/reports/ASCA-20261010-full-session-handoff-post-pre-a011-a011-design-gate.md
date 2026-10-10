# FlyWireASCA Full Session Handoff — Post-PRE-A011 / A011 Design Gate

Date: 2026-10-10
Repository: `funggier/FlyWireASCA`
Local repository: `T:\Space\Projects\ProjectsAI\FlyWireASCA`

## 1. Read this first

This handoff is the authoritative narrative/resume document for the transition
from the completed PRE-A011 stabilization gate into the planned A011 system
qualification milestone.

**Do not resume PRE-A011 implementation. It is closed.**

**Do not create or activate A011 yet.**

At the time this handoff is written:

- A001-A010 are DONE;
- PRE-A011 is DONE and GitHub Issue #11 is CLOSED / COMPLETED;
- A011 — ASCA v0.x Qualification is PLANNED;
- no A011 GitHub issue exists;
- the A011 conversational design has been developed through four sections;
- the final written A011 spec has **not** been written yet;
- the A011 implementation plan has **not** been written yet;
- no A011 source implementation has started.

The immediate next action in a new session is to resume at the **A011 design
approval gate**, not at implementation.

The final A011 design section was presented to the user, but the conversation
moved to this handoff request before an explicit final approval of the complete
four-part design was given. Do not silently convert the handoff request into
design approval.

## 2. Why FlyWireASCA exists

FlyWireASCA started from a practical research question:

> Can useful AI cognition be organized so that only the relevant memories,
> associations, procedures, and reasoning paths become active for a task,
> instead of assuming that every problem should be solved by uniform dense
> computation alone?

The project name is:

**Associative Selective Cognition Architecture — ASCA**

The name describes the direction of the architecture, but the project was never
intended to force every experiment to prove that “selective” is always better.

That distinction became increasingly important as the milestones progressed.

The project has deliberately separated:

- architecture from marketing claims;
- engineering qualification from research-hypothesis support;
- deterministic software evidence from hardware-performance claims;
- retrieval evidence from identity/truth claims;
- procedural correctness from autonomous real-world action;
- local model/embedding physical evidence from portable CI.

This discipline is now one of the most important properties of the project.

## 3. The story so far

The architecture was built incrementally rather than as one large opaque
system.

### A001 — Repository & Research Foundation

Established the repository, research process, evidence discipline, CI, task
workflow, and explicit independence from FlyWireLLM.

Result: DONE.

### A002 — ASCA Architecture Contract

Defined the typed contracts and boundaries needed so later components could
exchange explicit evidence instead of hidden mutable state.

Result: DONE.

### A003 — Familiarity System

Added cheap deterministic familiarity evidence.

Important boundary:

Familiarity is not truth, identity, semantic equivalence, or proof that two
entities are the same.

Result: DONE.

### A004 — Local Model Adapter & Qwen3.5:4B Baseline

Added the local generative model boundary using Ollama and a pinned Qwen model.

Pinned terminal model:

`qwen3.5:4b`

Pinned digest:

`2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd`

Result: DONE.

### A005 — Semantic Vector Memory Retrieval

Added semantic embedding/retrieval using a pinned local embedding model.

Pinned embedding model:

`qwen3-embedding:0.6b`

Pinned digest:

`ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`

Embedding dimension:

`1024`

Frozen similarity threshold:

`0.5037018224299838`

Result: DONE.

### A006 — Working Set / Selective Activation

Tested bounded selective working-set construction and the convergence hypothesis.

Engineering qualification succeeded.

Research result:

**A006: `NOT_SUPPORTED`**

This was important. The physical fixture did not justify promoting the tested
convergence policy as generally superior to SINGLE_BEST.

The correct response was to keep the negative result, not retune the fixture.

### A007 — Surprise, Uncertainty & Expansion

Added bounded structural signal-driven expansion.

Research result:

**A007: `SUPPORTED`**

Frozen physical fixture fingerprint:

`59f95ef115534fe24e59570cb281c0564ab75aadf364f4c26feba0d4078213c9`

The result supports the frozen structural-expansion hypothesis only. It does not
establish calibrated scalar uncertainty, true prediction surprise, lower FLOPs,
or universal speed improvement.

### A008 — Procedural Memory / Skill Chunking

Added deterministic hierarchical procedural memory with explicit checkpoints.

Primary representation carried forward:

`CHUNKED`

Research result:

**A008: `SUPPORTED`**

A008 deliberately performs zero hidden automatic retry.

### A009 — Integrated Cognitive Loop

Composed the already-qualified components into one bounded and inspectable
control loop.

Important properties:

- A003 familiarity is evidence-only;
- A005 performs vector retrieval;
- A006 primary selector remains SINGLE_BEST;
- A007 primary expansion policy remains SIGNAL_DRIVEN;
- A008 primary procedure mode remains CHUNKED;
- mismatch recovery occurs at the outer A009 control level;
- each recovery attempt receives fresh execution state;
- maximum procedure attempts remain bounded at 3;
- A004 terminal generation is optional/terminal and non-controlling;
- no real OS/API/LConnect/BConnect actions are executed.

Research result:

**A009: `SUPPORTED`**

Frozen deterministic fixture:

`a009-deterministic-v1`

Frozen fingerprint:

`2f92b5092de346f62879ac2cbb9f96d6de5d6f919e12d0693345c8228b01ab2a`

### A010 — Dense/Non-selective Baseline Comparison

A010 compared the real A009 path against a deliberately dense/exhaustive
baseline under a frozen controlled workload.

This milestone is one of the most important reasons A011 must be designed
carefully.

Frozen primary result:

**A010: `NOT_SUPPORTED`**

Frozen fixture:

`a010-deterministic-v1`

Frozen fingerprint:

`69d20542cd1e7e5c25a0fb61b9060f622379206b519da3cec7624e00bb6e5d4c`

Primary portable comparison:

- primary cases: 9
- ASCA procedure successes: 7
- Dense procedure successes: 8
- shared successes: 7
- dense-only successes: 1
- ASCA-only successes: 0
- ASCA query count: 28
- Dense query count: 27
- ASCA scored-vector count: 1984
- Dense scored-vector count: 1440
- ASCA cumulative selected count: 66
- Dense cumulative selected count: 480
- ASCA peak selected count: 12
- Dense peak selected count: 256
- ASCA procedure attempts: 14
- Dense procedure attempts: 9

Interpretation:

ASCA maintained a much smaller active selected state on the frozen fixture, but
the progressive/recovery path re-scored wider scopes often enough that it did
not support the declared system-level retrieval-work hypothesis. The frozen
routing-miss sentinel also produced one dense-only success.

The correct scientific conclusion is therefore `NOT_SUPPORTED`.

Do not optimize A009/A010 inside A011 merely to change this result.

## 4. Why the negative results are important

A006 and A010 are not project failures.

They are evidence that the project is using falsifiable hypotheses rather than
engineering toward a predetermined narrative.

This matters because ASCA would lose scientific value if later milestones
silently:

- retuned thresholds;
- rewrote fixtures;
- changed cue text after seeing the result;
- changed routing to remove a dense-only case;
- changed the hypothesis definition;
- reclassified `NOT_SUPPORTED` as a technical failure;
- created a new benchmark whose purpose was only to obtain a positive result.

A011 therefore must preserve the distinction:

**engineering qualification can be GREEN while some research hypotheses remain
NOT_SUPPORTED.**

This is the central philosophical and technical reason for the current A011
design.

## 5. Why PRE-A011 was necessary

Before A011, the repository was audited as a whole.

The audit found that the cognitive architecture itself was coherent, but the
repository/process layer had accumulated enough cross-milestone debt that a
system qualification could produce misleading evidence if performed
immediately.

PRE-A011 was created as:

**Architecture & Process Consistency Stabilization**

It was deliberately not assigned an A-numbered research milestone.

PRE-A011 repaired:

- stale lifecycle prose;
- mutable CURRENT/ROADMAP assertions inside historical milestone tests;
- evidence-role terminology;
- repository lifecycle qualification;
- package dependency direction/cycle auditing;
- portable/physical qualification topology;
- Markdown relative-link qualification;
- duplicated private Ollama JSON shape validation;
- staged whitespace verification;
- malformed roadmap fail-closed behavior;
- active issue-number coherence;
- relative-import dependency-audit bypass.

It also published:

`docs/architecture/ASCA-PRE-A011-SNAPSHOT.md`

and:

`docs/development/QUALIFICATION-MATRIX.md`

PRE-A011 did **not** change A003-A010 cognitive semantics.

## 6. PRE-A011 final closure state

PRE-A011 GitHub Issue:

`#11 — PRE-A011 — Architecture & Process Consistency Stabilization`

State:

**CLOSED / COMPLETED**

Reviewed/integration SHA:

`de7b9ab7227afc6e914ca0435b780d30b41eeea3`

Exact reviewed-main CI:

`38023542634` — success

Final closure metadata commit:

`7ca59177f650dce80f58f5db2ba8cd1953e6a20b`

Exact final closure CI:

`38025501003` — success

Final local closure suite:

**563 passed**

Final audits:

- `architecture_contract_audit=PASS`
- `repository_qualification=PASS`

Review method:

author self-review because no independent reviewer/subagent mechanism was
available in the harness.

Review findings:

- Critical: 0
- Important: 3 — fixed
- Minor: 1 — fixed

The isolated PRE-A011 worktree was removed cleanly.

The local PRE-A011 branch was deleted non-force.

Remote maintenance history remains preserved:

`origin/maintenance/pre-a011-architecture-process-stabilization`

## 7. Authoritative live repository state before this handoff commit

Before this handoff document itself is committed:

- branch: `main`
- HEAD: `7ca59177f650dce80f58f5db2ba8cd1953e6a20b`
- origin/main: same
- ahead/behind: `0/0`
- worktree: clean
- latest exact main CI: `38025501003` — success

Package version:

`0.1.0.dev0`

No release tag has been created by A011.

## 8. Current roadmap state

- A001 — DONE
- A002 — DONE
- A003 — DONE
- A004 — DONE
- A005 — DONE
- A006 — DONE
- A007 — DONE
- A008 — DONE
- A009 — DONE
- A010 — DONE
- A011 — PLANNED

Current pointer:

`A011 / PLANNED / GitHub Issue: not created`

No A011 GitHub issue exists.

Do not invent an A012 milestone during A011 closure unless the user explicitly
chooses the next roadmap direction later.

## 9. The purpose of A011

A011 is not intended to prove that ASCA is universally superior.

A011 is intended to answer a different question:

> Is the currently implemented ASCA v0.x architecture profile internally
> coherent, reproducible, identity-stable, deterministic where declared,
> physically reproducible where required, and supported by traceable evidence
> sufficient to call the engineering architecture qualified?

A011 should therefore be a **system qualification/certification layer** over the
already-built milestones.

It should not become a hidden optimization milestone.

## 10. A011 design path chosen so far

Three high-level approaches were considered.

### Approach A — Meta qualification only

Aggregate existing reports and declare pass/fail.

Rejected as the primary direction because it risks becoming “qualified because
the documents exist” without enough fresh system replay.

### Approach B — Qualification pack + fresh system replay + frozen evidence audit

**Recommended direction.**

A011 should:

- reuse frozen evidence;
- verify pinned identities;
- run fresh portable replay;
- run fresh physical replay;
- verify deterministic/fingerprint/outcome stability;
- aggregate results into one qualification manifest;
- make engineering qualification separate from research outcomes.

This provides meaningful system qualification without inventing a new research
hypothesis.

### Approach C — New comprehensive benchmark

Potentially useful research, but rejected for A011 because a new workload would
mix qualification of existing work with a new experiment.

If desired later, this belongs in a later research milestone rather than being
hidden inside A011.

## 11. A011 Design Section 1 — Qualification result semantics

The proposed A011 result is split into two dimensions.

### 11.1 Engineering qualification

Allowed final states:

- `ENGINEERING_QUALIFIED`
- `ENGINEERING_NOT_QUALIFIED`
- `QUALIFICATION_BLOCKED`

Meaning:

#### ENGINEERING_QUALIFIED

All mandatory repository, architecture, frozen identity, portable replay, and
physical qualification gates passed.

#### ENGINEERING_NOT_QUALIFIED

A real system/evidence failure occurred, such as:

- contract violation;
- repository lifecycle inconsistency;
- frozen fingerprint drift;
- deterministic replay mismatch;
- wrong model identity;
- wrong embedding identity;
- threshold drift;
- invalid fixture;
- required qualifier failure;
- research outcome unexpectedly changing from its frozen result.

#### QUALIFICATION_BLOCKED

Qualification cannot complete because an external/local prerequisite is
unavailable, for example:

- Ollama unavailable;
- pinned model absent;
- pinned embedding model absent;
- local runtime prerequisite unavailable.

A blocked environment must not be misreported as a system defect.

### 11.2 Research evidence summary

A011 should not create one aggregate “ASCA research score.”

Instead it preserves:

- A006: `NOT_SUPPORTED`
- A007: `SUPPORTED`
- A008: `SUPPORTED`
- A009: `SUPPORTED`
- A010: `NOT_SUPPORTED`

A011 can therefore be `ENGINEERING_QUALIFIED` while preserving negative
scientific results.

## 12. A011 Design Section 2 — Qualification pack

The proposed A011 qualification pack has five layers.

### Layer 1 — Repository / Architecture Integrity

Run:

- `python -m pytest -q`
- `python scripts/audit_architecture_contract.py`
- `python scripts/qualify_repository.py`

Verify:

- package dependency direction;
- no dependency cycles;
- lifecycle coherence;
- current architecture contract;
- FlyWireLLM independence boundary;
- documentation link validity;
- task/roadmap consistency.

### Layer 2 — Frozen Evidence Identity

Pin and verify at minimum:

- A005 similarity threshold;
- A004 terminal model tag/digest;
- A005 embedding model tag/digest/dimension;
- A006 frozen outcome;
- A007 frozen outcome and physical fixture fingerprint;
- A008 frozen outcome;
- A009 frozen fixture fingerprint and outcome;
- A010 frozen fixture fingerprint, outcome, and primary comparison counts.

If frozen identity changes unexpectedly:

**hard fail — ENGINEERING_NOT_QUALIFIED**

Do not silently accept a rewritten manifest.

### Layer 3 — Fresh Portable Replay

Run:

- full pytest;
- A003 familiarity qualification;
- A008 procedural qualification;
- A009 portable integrated-loop qualification;
- A010 portable baseline-comparison qualification;
- A011 portable orchestrator/manifest validation.

Portable replay must not require Ollama.

### Layer 4 — Fresh Local Physical Replay

Run:

- A004 Qwen physical qualifier;
- A005 vector-memory physical qualifier;
- A006 selective-activation physical qualifier;
- A007 uncertainty/expansion physical qualifier;
- A009 integrated physical qualifier;
- A010 physical comparison qualifier;
- A011 physical orchestration.

Physical timing observations remain descriptive unless an existing qualifier
already defines a timing rule.

### Layer 5 — Final Qualification Manifest / Classifier

Produce a machine-readable qualification result plus a human report.

The manifest should record:

- engineering verdict;
- blocker/error list;
- individual gate results;
- frozen identity checks;
- research evidence summary;
- physical identity;
- portable replay identity;
- claims boundary.

## 13. A011 Design Section 3 — Proposed artifacts and source boundaries

Proposed new qualification-only package:

`src/flywire_asca/qualification/`

Its job is qualification schema/classification, not cognition.

Proposed orchestrators:

`scripts/qualify_asca_v0x_a011.py`

and:

`scripts/qualify_asca_v0x_a011_physical.py`

Proposed frozen profile/manifest artifact:

a canonical A011 v0.x qualification profile under
`docs/development/qualification/` or an equivalent approved path.

Proposed final report:

`docs/development/reports/ASCA-20261010-A011-v0x-qualification.md`

A011 should reuse existing qualifier logic where possible.

It should not copy/reimplement cognitive algorithms merely to aggregate their
results.

If existing qualifiers need better machine-readable APIs, only backward-
compatible infrastructure exposure should be added unless a real defect is
found.

### Cognitive behavior freeze

A011 should not change:

- A003 familiarity semantics;
- A005 retrieval/ranking/filtering semantics;
- A006 selector semantics;
- A007 expansion semantics;
- A008 procedure semantics;
- A009 controller/recovery policy;
- A010 comparison/classification semantics;
- frozen thresholds;
- frozen fixtures;
- frozen fingerprints;
- model identities;
- historical outcomes.

If A011 discovers a real cognitive defect, qualification should stop and the
defect should be treated as an explicit repair task rather than hidden inside
qualification.

## 14. Version and release semantics

Current package version:

`0.1.0.dev0`

Recommended A011 rule:

**keep `0.1.0.dev0` unchanged throughout A011.**

A011 qualifies the architecture profile.

A011 does not automatically promote:

- package version;
- Git tag;
- GitHub Release;
- “stable” status.

If A011 becomes `ENGINEERING_QUALIFIED`, a later explicit release-readiness
gate can decide whether to publish `0.1.0` or another release version.

This avoids making release promotion a hidden requirement for scientific
qualification.

## 15. A011 Design Section 4 — Execution and failure flow

Portable path:

1. full tests;
2. architecture audit;
3. repository qualifier;
4. A003 portable;
5. A008 portable;
6. A009 portable;
7. A010 portable;
8. A011 portable orchestrator;
9. manifest consistency;
10. deterministic/frozen identity checks.

This path belongs in GitHub CI and must remain Ollama-free.

Physical path:

1. A004 physical;
2. A005 physical;
3. A006 physical;
4. A007 physical;
5. A009 physical;
6. A010 physical;
7. A011 physical orchestration;
8. pinned identity validation.

A final `ENGINEERING_QUALIFIED` verdict requires both the portable evidence and
the required physical evidence.

## 16. A011 hard-fail and blocked rules

### Hard fail / ENGINEERING_NOT_QUALIFIED

Use when:

- architecture contract fails;
- repository qualification fails;
- deterministic replay changes;
- frozen fingerprint changes;
- threshold changes;
- pinned model/digest/dimension changes;
- fixture becomes invalid;
- required qualifier fails;
- previously frozen research outcome changes unexpectedly;
- manifest is malformed or inconsistent;
- required evidence cannot be parsed reliably.

### QUALIFICATION_BLOCKED

Use when:

- Ollama runtime is unavailable;
- required pinned local model is missing;
- required pinned embedding model is missing;
- another explicitly external/local prerequisite is unavailable.

Do not use `QUALIFICATION_BLOCKED` to hide a real system failure.

### Existing NOT_SUPPORTED milestones

A006/A010 `NOT_SUPPORTED` remain valid qualified scientific evidence and are
not engineering hard failures.

## 17. A011 canonical manifest rule

Recommended important rule:

The A011 qualification profile/manifest becomes the canonical list of expected
frozen identities for A011 orchestration.

Tests must prove fail-closed behavior by deliberately mutating expected values
in test fixtures and confirming qualification fails.

Examples:

- fake A009 fingerprint -> fail;
- fake A010 fingerprint -> fail;
- fake A005 threshold -> fail;
- fake terminal digest -> fail;
- fake embedding digest/dimension -> fail;
- fake A006/A010 outcome -> fail.

The production manifest itself must not be silently regenerated from current
runtime values during qualification, otherwise drift could bless itself.

## 18. A011 explicit non-goals

A011 must not:

- retune thresholds;
- retune fixtures;
- change cue text to improve an outcome;
- optimize A009/A010 retrieval;
- remove the dense-only sentinel;
- create a new benchmark to obtain a positive narrative;
- change model tags/digests silently;
- aggregate milestones into an “ASCA intelligence score”;
- claim FLOPs savings;
- claim electrical power/energy savings;
- claim universal latency superiority;
- claim AGI/consciousness/biological equivalence;
- add real OS/API/LConnect/BConnect action execution;
- add persistent graph DB;
- add learned familiarity;
- add memory consolidation;
- touch FlyWireLLM;
- promote package version/tag/release automatically.

## 19. Proposed A011 acceptance criteria

A011 should only reach DONE when:

1. written spec and implementation plan were explicitly approved;
2. A011 issue/task activation followed the approved gate;
3. portable qualification can run from a clean checkout without Ollama;
4. physical qualification reproduces required pinned identities locally;
5. frozen fingerprints/outcomes remain exact;
6. A006/A010 negative results remain unchanged;
7. manifest mutation tests fail closed;
8. unexpected incomplete/malformed evidence fails closed;
9. portable + physical results produce one coherent engineering verdict;
10. whole-change review completes;
11. Critical/Important findings are fixed under RED -> GREEN evidence;
12. exact branch CI is GREEN;
13. reviewed behavior integrates to main;
14. exact main CI is GREEN;
15. final report states claims boundaries explicitly;
16. FlyWireLLM remains untouched;
17. no version/tag/release promotion occurs unless separately approved.

## 20. Current design approval state — very important

The A011 conversational design has been presented in four sections.

User responses so far:

- after Section 1, the user explicitly said to follow the recommended direction;
- Sections 2 and 3 were allowed to continue;
- Section 4 was presented with a request for approval of the complete design;
- before giving an explicit final design approval, the user requested this full
  handoff.

Therefore:

**Do not assume the complete A011 design is finally approved yet.**

The safe next-session gate is:

1. read this handoff;
2. verify live state;
3. summarize the four-part A011 design briefly;
4. ask for/receive explicit approval of the complete design;
5. only then write the A011 written spec.

The handoff request itself is not permission to skip the final design-approval
gate.

## 21. Required architecture workflow for A011

A011 is architectural work.

Follow the full gate:

1. read-only live-state verification;
2. conversational design approval;
3. write written spec;
4. self-review spec for incomplete markers, contradictions, ambiguity, and scope;
5. commit/push spec and require exact CI;
6. user explicitly reviews/approves written spec;
7. invoke writing-plans;
8. write detailed implementation plan;
9. commit/push plan and require exact CI;
10. user explicitly reviews/approves plan and selects execution method;
11. only then create A011 GitHub issue;
12. create isolated A011 worktree;
13. activate CURRENT/ROADMAP/task state;
14. implement under TDD;
15. full portable/physical qualification;
16. review;
17. integrate/close.

Do not collapse these approvals into one.

## 22. Suggested written-spec direction after design approval

Suggested spec filename:

`docs/superpowers/specs/2026-10-10-a011-asca-v0x-qualification-design.md`

Suggested title:

**A011 — ASCA v0.x System Qualification Design**

The spec should preserve all decisions in Sections 9-19 of this handoff.

It should explicitly state that A011 is a qualification milestone, not an
optimization/research-retuning milestone.

## 23. Likely implementation-plan decomposition after spec approval

A future implementation plan will probably need tasks similar to:

1. activate A011 only after plan approval;
2. define typed A011 qualification result/schema;
3. freeze canonical qualification profile/manifest;
4. implement manifest validation and mutation/fail-closed tests;
5. implement portable A011 orchestrator;
6. integrate portable A011 gate with CI;
7. implement local physical A011 orchestrator;
8. verify pinned local identities;
9. produce machine-readable final qualification artifact;
10. run full portable qualification;
11. run full physical qualification;
12. whole-change review;
13. exact branch CI;
14. main integration/exact main CI;
15. final A011 report/closure.

This is a planning hint only.

Do not implement from this list before written spec + plan approval.

## 24. A011 qualification evidence that must remain pinned

At minimum preserve:

### Terminal model

- model: `qwen3.5:4b`
- digest:
  `2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd`

### Embedding model

- model: `qwen3-embedding:0.6b`
- digest:
  `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`
- dimension: `1024`

### A005 threshold

`0.5037018224299838`

### A007 physical fixture

`59f95ef115534fe24e59570cb281c0564ab75aadf364f4c26feba0d4078213c9`

### A009 deterministic fixture

`2f92b5092de346f62879ac2cbb9f96d6de5d6f919e12d0693345c8228b01ab2a`

Outcome:

`SUPPORTED`

### A010 deterministic fixture

`69d20542cd1e7e5c25a0fb61b9060f622379206b519da3cec7624e00bb6e5d4c`

Outcome:

`NOT_SUPPORTED`

### Historical research outcomes

- A006: `NOT_SUPPORTED`
- A007: `SUPPORTED`
- A008: `SUPPORTED`
- A009: `SUPPORTED`
- A010: `NOT_SUPPORTED`

## 25. Important claims boundary

Even if A011 becomes `ENGINEERING_QUALIFIED`, that must not be rewritten as:

- “ASCA is more intelligent than dense models”;
- “ASCA uses fewer FLOPs in general”;
- “ASCA is always faster”;
- “ASCA consumes less energy”;
- “ASCA is brain-like”;
- “ASCA proves consciousness”;
- “ASCA is AGI.”

The defensible A011 claim is narrower:

> The declared FlyWireASCA v0.x engineering architecture profile is internally
> coherent and reproducible under its pinned portable and physical qualification
> contracts, while preserving the recorded positive and negative research
> outcomes of its component milestones.

That is a meaningful result by itself.

## 26. FlyWireLLM boundary

FlyWireLLM is a separate project.

A011 does not need to train, restart, modify, or qualify FlyWireLLM.

Do not use FlyWireLLM merely because it exists in the wider workspace.

The ASCA architecture should remain independently qualifiable.

## 27. Startup procedure for the next session

In a new session:

1. read this handoff first;
2. read `docs/development/tasks/CURRENT.md`;
3. read `docs/development/tasks/ROADMAP.md`;
4. read `docs/architecture/ASCA-PRE-A011-SNAPSHOT.md`;
5. read `docs/development/QUALIFICATION-MATRIX.md`;
6. verify:
   - main HEAD;
   - origin/main;
   - ahead/behind;
   - clean worktree;
   - latest exact main CI;
   - Issue #11 CLOSED / COMPLETED;
   - no A011 issue exists;
7. treat live Git/GitHub/runtime as authoritative;
8. do not reopen PRE-A011;
9. do not implement A011 yet;
10. obtain explicit approval of the complete four-part A011 conversational
    design;
11. after approval, write the A011 design spec;
12. keep `0.1.0.dev0` unchanged;
13. keep FlyWireLLM untouched.

## 28. Suggested next-session prompt

Use:

```text
@use-local-workspace
ทำ funggier/FlyWireASCA ต่อจาก Full Handoff ล่าสุด โดยอ่าน
docs/development/reports/ASCA-20261010-full-session-handoff-post-pre-a011-a011-design-gate.md
ก่อน ยึด Git/GitHub/runtime สดเป็น authoritative source ห้าม reset/clean/rebase/
force-push และห้ามย้อนกลับไปทำ PRE-A011 เพราะ PRE-A011 ปิด GREEN แล้ว

ให้ตรวจ main/CI/Issue #11/CURRENT/ROADMAP ก่อน และยืนยันว่า A011 ยัง PLANNED
ไม่มี GitHub issue จากนั้น resume ที่ A011 architectural design approval gate
ก่อน: สรุป design 4 ส่วนจาก handoff และขอ explicit final design approval
ห้ามเขียน spec จนกว่าจะได้รับ approval นั้น

A011 ต้องเป็น ASCA v0.x system qualification/certification layer ไม่ใช่
optimization milestone ต้องคง A006 NOT_SUPPORTED, A007 SUPPORTED, A008
SUPPORTED, A009 SUPPORTED, A010 NOT_SUPPORTED; ห้าม retune fixtures/thresholds
หรือ optimize A009/A010 เพื่อเปลี่ยนผล ห้ามสร้าง A011 issue ก่อน written spec
และ implementation plan ผ่าน approval gates และห้ามแตะ FlyWireLLM
```

## 29. Immediate next action

The immediate next action is **not code** and **not GitHub issue activation**.

Resume the A011 architectural workflow at:

**explicit approval of the complete four-part conversational design**

Then:

- write the A011 written spec;
- self-review it;
- commit/push it;
- require exact CI;
- ask the user to review the written spec.

Only after written-spec approval may the implementation plan be written.