# FlyWireASCA Full Session Handoff — A011 Written-Spec Review

Date: 2026-10-10
Repository: `funggier/FlyWireASCA`
Local repository: `T:\Space\Projects\ProjectsAI\FlyWireASCA`
Resume gate: **A011 written-spec review / explicit user approval**
Milestone: A011 / PLANNED / GitHub Issue not created

## 1. Read first and resume correctly

This handoff supersedes the earlier design-approval resume pointer:
[post-PRE-A011 handoff](ASCA-20261010-full-session-handoff-post-pre-a011-a011-design-gate.md).

The earlier four-part conversational design has now received explicit user
approval. A detailed written spec and advance Task were written, self-reviewed,
committed, pushed, and exact-commit CI qualified.

**The written spec has not been approved by the user yet.**
No implementation plan exists. No writing-plans invocation, A011 GitHub issue,
isolated A011 worktree, activation, or implementation has occurred.

Do not restart the conversational design from scratch. Do not treat approval
of that design as approval of the newly written spec or a future plan.
The next action is to present/review the published written spec.

Do not resume PRE-A011: it is DONE, Issue #11 CLOSED / COMPLETED.

## 2. User request and approval chronology

The user requested:

1. read the prior handoff first;
2. verify live main/CI/Issue #11/CURRENT/ROADMAP/runtime;
3. preserve all frozen identities/outcomes and architectural gates;
4. prepare advance Task work and a full next-session handoff;
5. add detailed design.

Then the user explicitly said:

> อนุมัติให้ทำไปเลยครับ

The assistant acknowledged that approval as approval of the complete
conversational A011 design, summarized its four parts, and stated that the
next deliverable would be the written spec plus advance Task/handoff.

That approval permits this written-spec preparation. It does not collapse
the remaining written-spec and implementation-plan approvals.

## 3. Authoritative live baseline verified before writing

Initial main/local/exact remote SHA:

`c1498e8e30a23fb67965239d13f0531d5326079e`

Exact initial main CI:

[38038307095](https://github.com/funggier/FlyWireASCA/actions/runs/38038307095) —
completed/success, push/main, exact initial SHA.

Initial checks:

| Check | Result |
| --- | --- |
| main checkout | PASS |
| clean worktree, including untracked entries | PASS |
| exact remote main/local/cached origin match | PASS |
| exact ahead/behind | 0/0 |
| latest exact HEAD CI | PASS |
| PRE-A011 Issue #11 | CLOSED / COMPLETED |
| A011 CURRENT/ROADMAP | PLANNED |
| A011 GitHub issue | absent |
| GitHub issue completeness check | paginated all-state enumeration: Issues #1-#11, all closed/completed; none is A011 |
| package version | 0.1.0.dev0 |
| isolated worktrees | main only |
| local tags | none at baseline |

No repository/ancestor AGENTS.md was found in the checked instruction paths.
No FlyWireLLM folder, file, training process, or runtime was inspected or modified.

## 4. Historical prose versus live state

The PRE-A011 report begins with `ACTIVE / pre-review` and retains its earlier
552/556/561/562-test checkpoints. Its later sections record reviewed integration,
Issue #11 closure, and the final 563-test closure-metadata gate.

Those are historical stages, not evidence that PRE-A011 is still active.
Live Issue #11, CURRENT/ROADMAP, and main determine the present state.

Likewise the previous handoff records `7ca59177...` as main **before that
handoff commit**. The live startup HEAD was `c1498e8e...`, whose exact CI title
was “Add A011 design gate full handoff”. Do not use the earlier pre-handoff SHA
as current main.

The old reports were preserved; no historical outcome was rewritten.

## 5. Published written spec and Task

Written spec:

[2026-10-10-a011-asca-v0x-qualification-design.md](../../superpowers/specs/2026-10-10-a011-asca-v0x-qualification-design.md)

Advance Task:

[A011-asca-v0x-qualification.md](../tasks/A011-asca-v0x-qualification.md)

Canonical current pointer:

[CURRENT.md](../tasks/CURRENT.md)

Other required architecture references:

- [ROADMAP.md](../tasks/ROADMAP.md)
- [ASCA-PRE-A011-SNAPSHOT.md](../../architecture/ASCA-PRE-A011-SNAPSHOT.md)
- [QUALIFICATION-MATRIX.md](../QUALIFICATION-MATRIX.md)
- [PRE-A011 report](ASCA-20261010-PRE-A011-architecture-process-stabilization.md)

Exact written-spec/Task publication commit:

`6eb5fb1399bc21a05599b92d9aa8b312df70c9e1`

Exact spec-commit CI:

[38039670308](https://github.com/funggier/FlyWireASCA/actions/runs/38039670308) —
completed/success, push/main, head SHA exactly the spec publication commit.

The spec was also read back from GitHub at that exact SHA; its contents matched
the authored/reviewed document. Blob SHA:

`c14b921f3f6b83166f2bb6e554f226636fc7ed29`

After that push, main was clean and exactly synced to origin/main at
`6eb5fb1399bc21a05599b92d9aa8b312df70c9e1`, ahead/behind 0/0.

This handoff and its task/CURRENT publication bookkeeping are a later
documentation-only commit. Resolve the containing commit and latest exact CI
from live Git/GitHub. This file intentionally does not require its own future
commit SHA or CI run ID inside itself. The spec publication SHA above remains
the exact written-spec review target.

## 6. Detailed design summary — four parts

### Part 1 — Result semantics

Final engineering states:

- ENGINEERING_QUALIFIED;
- ENGINEERING_NOT_QUALIFIED;
- QUALIFICATION_BLOCKED.

Research evidence remains a five-row milestone summary, never an intelligence
score. A006/A010 NOT_SUPPORTED is expected, valid evidence.

Internal gates use PASS/FAIL/BLOCKED/NOT_RUN. Portable-only packs have
PORTABLE_ONLY scope, is_final=false, and engineering_verdict=null.
A portable PASS cannot certify the full system.

Any verified hard failure dominates a simultaneous blocker. Unexplained missing
or contradictory evidence is a hard failure. A blocker requires an identified,
verified external/local prerequisite.

### Part 2 — Qualification pack and replay

Use Qualification Pack + Fresh System Replay + Frozen Evidence Audit.

Five layers:

1. repository/architecture integrity;
2. frozen identity/profile audit;
3. fresh portable replay;
4. fresh local physical replay;
5. validated final manifest and derived human report.

Portable required gates: P00-P09 — profile/source precheck, full tests,
architecture audit, repository qualification, A003, A008, A009, A010, frozen
audit, and pack validation.

Physical required gates: H00-H07 — runtime preflight, A004/A005/A006/A007,
A009 physical, A010 physical, and full-system consistency/classification.

The full physical path first reruns portable locally on the same exact candidate
and profile, then runs physical qualifiers sequentially. Existing standalone
portable CI gates remain, with the A011 portable gate added later.

### Part 3 — Source and evidence boundaries

Future qualification package:

`src/flywire_asca/qualification/`

Future orchestrators:

- `scripts/qualify_asca_v0x_a011.py`
- `scripts/qualify_asca_v0x_a011_physical.py`

Future frozen profile:

`docs/development/qualification/a011-v0x-profile-v1.json`

Future final milestone report:

`docs/development/reports/ASCA-20261010-A011-v0x-qualification.md`

These are design targets; no such production source/profile/report was created.

Qualification package dependencies are qualification -> contracts, plus standard
library. Cognitive packages must not depend on qualification.
Reuse real existing qualifier CLIs and validators; do not duplicate cognition.

Freeze profile bytes against an independently reviewed expected hash.
Do not regenerate expected values from the current runtime.
Bind fresh evidence to exact source commit/profile and protected cognitive content.
Do not mix artifacts from different candidates or treat historical reports as
fresh A011 replay.

### Part 4 — Failure flow, verification, and claims

Wrong installed identity, threshold/fingerprint/outcome/count drift, malformed
evidence, untrusted profile, or source mismatch -> ENGINEERING_NOT_QUALIFIED.

Confirmed unavailable runtime or absent required model -> QUALIFICATION_BLOCKED
unless a hard failure already exists.

Unknown errors or unexplained timeouts are not automatically external blockers.
No hidden retry, recalibration, runtime restart, model replacement, or automatic
model pull occurs.

A real/suspected cognitive defect stops qualification and requires a separate
explicit repair task. A011 cannot optimize A009/A010 or repair cognition to make
itself GREEN.

Keep 0.1.0.dev0. No tag/release/stable promotion.
Certification is internal qualification of the declared profile, not certification
by an external standards body or an intelligence/performance claim.

## 7. Important spec review points

The written spec explicitly resolves these risks:

1. portable success being mistaken for complete engineering certification;
2. a runtime-derived profile silently accepting its own drift;
3. external blockers masking an already observed system failure;
4. duplicate/missing gates or malformed raw evidence appearing as PASS;
5. mixing portable and physical artifacts from different source/profile identities;
6. treating entire physical artifact byte equality as determinism;
7. circular hashes where a manifest would have to hash itself;
8. unexecuted physical evidence appearing as a fresh observation;
9. a new wrapper deadline silently becoming a performance target;
10. implementation/release gates being skipped by conversational approval.

For existing A008/A009/A010 portable payloads, the only excluded payload field
from a stable digest is the optional top-level `note`. Execution IDs and semantic
counts remain included. A011 envelope runtime metadata is separate; raw hashes
still record actual artifacts.

The author self-review checked incomplete markers, contradictions, ambiguity,
and scope. No placeholder markers remain in the spec. Clarifications were made
inline before publication. Unresolved Critical/Important spec findings: 0.
This is author self-review, not independent peer review.

The user still needs to review the published written spec as a whole.

## 8. Advance Tasks prepared for later planning

The planned Task contains Q01-Q11 with dependencies, responsibility, required
outputs, failure rules, and evidence expectations.

| Work item | Responsibility |
| --- | --- |
| Q01 | Typed qualification records and classifier |
| Q02 | Frozen profile and independent trust anchor |
| Q03 | Existing qualifier adapters and source provenance |
| Q04 | Portable orchestration and deterministic replay audit |
| Q05 | Portable CI integration |
| Q06 | Physical preflight and full-system orchestration |
| Q07 | Atomic pack/report publication and artifact validation |
| Q08 | Fresh system qualification and frozen evidence audit |
| Q09 | Whole-change review and applicable explicit repairs |
| Q10 | Reviewed main integration and exact CI |
| Q11 | Final report, issue/ledger coherence, closure |

These are **advance work items**, not a detailed implementation plan.
No concrete implementation edits, new tests, issue creation, or execution method
were authorized by their publication. All Q items remain PLANNED.

Do not execute from this inventory. After written-spec approval,
invoke writing-plans to turn it into an actual reviewed implementation plan.

## 9. Gate state at handoff

| Gate | State |
| --- | --- |
| G00 — read handoff/live-state verification | PASS |
| G01 — complete conversational design approval | PASS |
| G02 — written spec/self-review/publication/exact CI | PASS at 6eb5fb1399bc21a05599b92d9aa8b312df70c9e1 / run 38039670308 |
| G03 — user written-spec review/approval | WAITING |
| G04 — writing-plans and published exact-CI implementation plan | NOT STARTED |
| G05 — user plan review/approval and execution method | NOT STARTED |
| G06 — issue/worktree/ACTIVE activation | NOT STARTED |

A011 status remains PLANNED. GitHub Issue remains not created.
No activation base, feature branch, or worktree has been assigned.
CURRENT now points to written-spec review rather than conversational design approval.

## 10. Verification performed in this session

Local documentation/spec publication gate:

- full pytest: **563 passed in 4.83s**, exit 0;
- architecture contract audit: PASS, exit 0;
- repository qualification: PASS, exit 0;
- `git diff --cached --check`: PASS;
- staged publication paths: only written spec, planned Task, CURRENT;
- spec incomplete-marker scan: PASS;
- spec staged whitespace/readback: PASS;
- exact spec-commit CI: success;
- remote spec exact-content readback: PASS;
- main clean/exact synced after spec publication: PASS.

The subsequent handoff publication commit changes documentation only.
Its relative links, lifecycle state, staged whitespace, exact diff scope, and
exact CI must also be verified before this session is declared complete.
The final assistant response records the containing documentation commit and run.
A next session must re-read live status rather than assuming an old SHA is latest.

No product source, existing tests, CI workflow, fixture, threshold, or package
version was changed during this session. No new A011 test was added.
The existing full suite therefore remains 563 tests.

## 11. Runtime observations and physical-evidence limits

Target machine verified through LConnect:

- hostname: CDQ-P;
- Windows 10, 10.0.19045;
- Intel Core Ultra 5 245K;
- local Python: 3.14.6;
- Ollama HTTP version: 0.32.15.

Read-only Ollama `/api/version` and `/api/tags` succeeded.
Observed tags/digests matched both pinned models; embedding tag metadata reported
embedding_length=1024.

This is runtime identity/preflight evidence only.
No A004/A005/A006/A007/A009/A010 physical qualifier replay was executed in this
documentation session. The observed metadata dimension is not presented as a
fresh measured embedding-vector replay. No inference, model pull, training,
runtime restart, or background test process was started.

Historical PRE-A011 physical evidence is in its report. Future A011 full-system
qualification still requires fresh physical replay after implementation approval.

## 12. Frozen identities and outcomes

| Identity | Frozen value |
| --- | --- |
| Terminal model | `qwen3.5:4b` |
| Terminal digest | `2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd` |
| Embedding model | `qwen3-embedding:0.6b` |
| Embedding digest | `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d` |
| Dimension | 1024 |
| A005 threshold | `0.5037018224299838` |
| A006 physical fingerprint | `e51fea2e58186e94d7affc964509e96d96fc656759677d7dcc073e5b36b91035` |
| A007 physical fingerprint | `59f95ef115534fe24e59570cb281c0564ab75aadf364f4c26feba0d4078213c9` |
| A008 portable fingerprint | `f52fbd4ab018386ff3cbfb62a68cc44a4b40e54ec4fd9a3b2e885dd2c5663fc6` |
| A009 deterministic fingerprint | `2f92b5092de346f62879ac2cbb9f96d6de5d6f919e12d0693345c8228b01ab2a` |
| A010 deterministic fingerprint | `69d20542cd1e7e5c25a0fb61b9060f622379206b519da3cec7624e00bb6e5d4c` |

Research outcomes:

- A006: NOT_SUPPORTED;
- A007: SUPPORTED;
- A008: SUPPORTED;
- A009: SUPPORTED;
- A010: NOT_SUPPORTED.

A010 frozen portable primary counts:

- cases: 9;
- ASCA/dense successes: 7/8;
- shared/dense-only/ASCA-only successes: 7/1/0;
- queries: 28/27;
- scored vectors: 1984/1440;
- cumulative selected: 66/480;
- peak selected: 12/256;
- procedure attempts: 14/9;
- `selective-routing-miss-sentinel` remains dense-only.

Do not retune any of these to improve the narrative.

## 13. Next-session startup and continuation

1. Read this handoff first.
2. Read CURRENT, ROADMAP, planned A011 Task, and the written spec.
3. Read the architecture snapshot and qualification matrix.
4. Verify live main/local/exact remote, clean state, latest exact HEAD CI,
   Issue #11 CLOSED/COMPLETED, A011 PLANNED/no issue, and runtime identities.
5. Confirm the written spec still corresponds to its review target and identify
   any later changes explicitly.
6. Present the spec for user review. Make requested spec changes, self-review
   them, commit/push, and require exact CI for the changed spec commit.
7. Only after explicit written-spec approval, invoke writing-plans.
8. Write/self-review/commit/push the implementation plan and require exact CI.
9. Stop for user plan review/approval and execution-method selection.
10. Only then create the A011 issue, isolated worktree, ACTIVE state, and TDD work.
11. Preserve task/evidence roles, exact CI, physical applicability, and review
    evidence through integration/closure.

No reset, clean, rebase, force-push, WIP/history destruction, PRE-A011 rework,
FlyWireLLM operation, model substitution, retuning, or automatic release.

## 14. Suggested next-session prompt

```text
@use-local-workspace

ทำ funggier/FlyWireASCA ต่อ โดยอ่านไฟล์นี้ใน repo ก่อน:
docs/development/reports/ASCA-20261010-full-session-handoff-a011-written-spec-review.md

จากนั้นอ่าน CURRENT.md, ROADMAP.md,
docs/development/tasks/A011-asca-v0x-qualification.md,
docs/superpowers/specs/2026-10-10-a011-asca-v0x-qualification-design.md,
ASCA-PRE-A011-SNAPSHOT.md และ QUALIFICATION-MATRIX.md

ยึด Git/GitHub/runtime สดเป็น authoritative source ตรวจ main clean/sync,
latest exact CI, Issue #11 CLOSED/COMPLETED, A011 PLANNED และไม่มี A011 issue
ห้าม reset/clean/rebase/force-push และห้ามแตะ FlyWireLLM

Conversational design อนุมัติแล้ว และ written spec ถูกเผยแพร่ที่
6eb5fb1399bc21a05599b92d9aa8b312df70c9e1
exact CI 38039670308 success
แต่ written spec ยังไม่ผ่าน user review/approval และยังไม่มี implementation plan

Resume ที่ written-spec review gate ให้ผม review spec ก่อน
ห้าม invoke writing-plans จนกว่าผมจะ approve written spec
หลัง plan ถูก review/approve และเลือก execution method แล้วเท่านั้น
จึงสร้าง issue/worktree เปลี่ยน ACTIVE และทำ implementation ด้วย TDD

Q01-Q11 เป็น Task ล่วงหน้า ไม่ใช่ implementation plan ที่อนุมัติแล้ว
คง 0.1.0.dev0; ห้ามสร้าง tag/release อัตโนมัติ
คง A006 NOT_SUPPORTED, A007 SUPPORTED, A008 SUPPORTED,
A009 SUPPORTED, A010 NOT_SUPPORTED และ frozen identities ทั้งหมด
A011 เป็น qualification layer ไม่ใช่ optimization/benchmark ใหม่
```

## 15. Immediate next action

**Explicit user review/approval of the published written spec.**

Then writing-plans; then a separate plan review/execution selection gate;
then issue/worktree/activation/TDD. Preserve that order.
