# A011 — ASCA v0.x Qualification

Status: ACTIVE
GitHub Issue: #12
Branch: qualification/a011-asca-v0x
Activation base: e8f75a862e0cb0d28b7e4efe25a77fa088ad646f

## Goal

Qualify the declared ASCA v0.x engineering architecture through a qualification
pack, fresh system replay, and frozen evidence audit. Preserve separate
milestone research outcomes, including negative evidence.

This is a system qualification/certification layer. It is not an optimization
milestone, a new research benchmark, or an automatic release gate.

## Scope

- typed engineering/gate/evidence records and deterministic classification;
- independently frozen profile and strict identity/evidence validation;
- fresh portable replay, remaining Ollama-free;
- fresh local physical replay with pinned models;
- traceable machine-readable pack and human report;
- whole-change review, exact branch/main CI, and evidence-driven closure.

## Non-scope

No A003-A010 cognitive semantics change. No A009/A010 retrieval optimization.
No fixture/cue/threshold/outcome/sentinel retuning. No automatic model pull or
replacement. No real cognitive OS/API/tool action execution.
No FlyWireLLM changes. Keep package version `0.1.0.dev0`.
No tag, release, stable promotion, or automatic `0.1.0` promotion.
Do not reopen PRE-A011 or invent A012.

## Design and planning authority

Written spec:
[2026-10-10-a011-asca-v0x-qualification-design.md](../../superpowers/specs/2026-10-10-a011-asca-v0x-qualification-design.md)

The user explicitly approved proceeding with the conversational design by
saying “อนุมัติให้ทำไปเลยครับ” in this session.

Written-spec approval was received with “โอเคครับ ทำต่อได้เลย” on
2026-10-10 at 16:11:41 +07:00, after the published written spec was presented.
This unlocks writing-plans; it does not approve the future implementation plan.

Implementation plan:
[2026-10-10-a011-asca-v0x-qualification.md](../../superpowers/plans/2026-10-10-a011-asca-v0x-qualification.md)

The writing-plans skill has been invoked. The plan defines concrete files,
interfaces, named RED/GREEN tests, commands, commit boundaries, physical
evidence, review, integration, and closure in 11 execution Tasks. This file
remains the canonical Q01-Q11 inventory; the written plan refines dependency
order by implementing artifact publication before the runners that consume it.
The plan is written, author self-reviewed, committed/pushed, and exact-CI GREEN.
User approved the plan and Native execution with “ทำ Native ได้เลยครับ ถ้าจำเป็นก็ Subagent-driven ได้” on 2026-10-10 16:52:26 +07:00.

## Approval gates

| Gate | Deliverable / permission unlocked | Current state |
| --- | --- | --- |
| G00 | Read handoff and verify live Git/GitHub/runtime baseline | PASS at `c1498e8e30a23fb67965239d13f0531d5326079e` |
| G01 | Explicit approval of complete conversational design; permits written spec | PASS — user approval in this session |
| G02 | Written spec, inline self-review, commit/push, exact spec-commit CI | PASS — spec published at `6eb5fb1399bc21a05599b92d9aa8b312df70c9e1`; exact CI `38039670308` success |
| G03 | User explicitly reviews/approves the written spec | PASS — user “โอเคครับ ทำต่อได้เลย”, 2026-10-10 16:11:41 +07:00 |
| G04 | Invoke writing-plans, create/self-review/publish implementation plan, exact CI | PASS — plan published at `9d17350a6e4f4305b797e7d2766bb619416a510b`; exact CI `38042470411` success |
| G05 | User reviews/approves plan and selects execution method | PASS — explicit user approval 2026-10-10 16:52:26 +07:00; Native |
| G06 | Create A011 issue, isolated worktree, and coherent ACTIVE task/ledger | PASS — Issue #12; isolated qualification/a011-asca-v0x; ACTIVE ledger |

A reply approves the stage actually presented. G01 does not approve a
previously nonexistent written spec or plan. Do not collapse G03 and G05.
G06 is complete. Execution status is recorded below; historical approval and publication observations remain preserved.

## Advance work-item inventory

These are local identifiers inside A011, not separate A-numbered milestones
or GitHub issues.

| ID | Responsibility | Depends on | Required delivery/evidence |
| --- | --- | --- | --- |
| Q01 | Qualification records and final classifier | G06 | Strict scope/finality/gate contracts; precedence and incomplete-evidence RED -> GREEN tests |
| Q02 | Frozen qualification profile and independent anchor | Q01 | Reviewed immutable identity profile; every expected-value mutation rejected |
| Q03 | Existing qualifier evidence adapters and provenance | Q01, Q02 | Reuse existing CLI outputs/validators; command/exit/raw hashes/source context coherent |
| Q04 | Portable orchestrator and deterministic replay audit | Q03, Q07 | All mandatory portable gates covered; repeat checks; no Ollama calls or recursive pytest |
| Q05 | Portable CI integration | Q04 | Existing CI topology preserved; A011 portable pack tested on exact branch commit |
| Q06 | Physical preflight and full-system orchestrator | Q03, Q04, Q07 | Missing runtime/model distinguished from wrong identity; fresh local portable plus sequential physical replay |
| Q07 | Pack/report publication and artifact validation | Q01, Q02, Q03 | Atomic JSON/Markdown/raw-index output; hashes, roles, scopes, and finality agree |
| Q08 | Fresh system qualification and frozen evidence audit | Q05, Q06, Q07 | Complete portable/physical evidence on exact candidate; frozen identities/counts/outcomes unchanged |
| Q09 | Whole-change review and applicable repairs | Q08 | Recorded review method; Critical/Important findings resolved with RED -> GREEN evidence |
| Q10 | Reviewed main integration and exact CI | Q09 | Exact reviewed branch CI; non-destructive integration; exact main CI; clean/sync main |
| Q11 | Final report and repository closure | Q10 | Engineering verdict and separate research table; issue/ledger coherence; evidence roles; explicit claims boundaries |

### Q01 — Records and classification

Define immutable normalized records for profile/source identity, gate evidence,
frozen checks, research evidence, replay identity, physical environment, and
final manifest.

Final engineering states are exactly ENGINEERING_QUALIFIED,
ENGINEERING_NOT_QUALIFIED, QUALIFICATION_BLOCKED. Internal gate states are
PASS/FAIL/BLOCKED/NOT_RUN. Portable-only packs are nonfinal and have no final
engineering verdict.

Evidence must prove:
- a hard failure takes precedence over a simultaneous external blocker;
- all mandatory gates are required for a full qualified verdict;
- missing, duplicate, malformed, or contradictory evidence fails closed;
- valid A006/A010 NOT_SUPPORTED evidence remains acceptable.

### Q02 — Frozen profile and trust

Create `docs/development/qualification/a011-v0x-profile-v1.json` only after
implementation is authorized. Freeze it from approved evidence and verify its
bytes against an independently reviewed anchor.

Include all identities and A010 counts in the spec. Preserve policy identities
and primary/secondary evidence roles. Reject runtime drift instead of copying
observed values into expected values.

Evidence must prove changed profile bytes, tags/digests, threshold/dimension,
fingerprints, outcomes, and A010 counts cannot bless themselves.

### Q03 — Evidence adapters and source identity

Invoke real existing qualifier CLIs using explicit argument arrays. Preserve
existing validators, output fields, acceptance rules, and nonzero failures.
Do not copy cognitive algorithms into qualification.

Capture exact source commit/profile, process context, exit codes, raw output
hashes, and normalized verdicts. Unknown/unparseable output is a failure.
Any genuinely needed API exposure must be infrastructure-only,
backward-compatible, reviewed, and characterized.

### Q04 — Portable qualification

Cover full pytest, architecture audit, repository qualification, A003, A008,
A009, A010, and A011 frozen/pack validation.

Reuse the frozen A008/A009/A010 workloads for deterministic repeats. Declare
only nonsemantic metadata exclusions. Preserve case IDs/order, fingerprints,
logical counts, and outcomes. Do not invent another benchmark.

The portable runner and its tests must run without Ollama. Runner tests use
fake process providers; a pytest test must not recursively invoke real pytest.

### Q05 — CI

Keep existing standalone portable gates. Add A011 portable qualification and
check its nonfinal pack. Physical/model gates remain absent from GitHub CI.

Exact SHA/run evidence is required. A previous green run on another commit
cannot qualify this change. Negative research outcomes do not fail CI.

### Q06 — Physical qualification

Preflight runtime/model availability separately from installed identity.
Use qwen3.5:4b and qwen3-embedding:0.6b only at their frozen digests/dimension.

Run fresh local portable qualification and then A004, A005, A006, A007, A009
physical, A010 physical. Preserve existing timeout/settings/acceptance rules.
Validate observed descriptors and the A005 observed embedding dimension.
Inspect identities again at completion.

No hidden automatic retry, recalibration, runtime restart, or model replacement.
A confirmed external absence is BLOCKED; identity drift or invalid evidence
is FAIL. Timing remains descriptive within existing contracts.

### Q07 — Pack and report

Produce validated `qualification.json`, derived `qualification.md`,
per-gate raw logs/JSON, frozen profile copy, and an artifact hash index.

Distinguish frozen expectations, historical references, fresh portable
observations, and fresh physical observations. Portable-only evidence cannot
claim physical replay. Full-system evidence must refer to one candidate/profile.
Atomic output and non-overwrite behavior must be verified.

### Q08 — Fresh final qualification

Run all mandatory paths on the exact candidate and retain actual output/exit
evidence. Validate model/embedding identities, A005 threshold, A006-A010
outcomes, fingerprints, and A010 counts/sentinel.

Stop on a real/suspected cognitive defect and separate it into an explicit
repair task. Never repair cognition or optimize A009/A010 inside A011 to turn
qualification GREEN.

A correctly classified blocked/failed pack is retained, but does not close the
milestone as engineering-qualified. Record the blocker/failure and resume point.

### Q09 — Review

Record whether review is independent or author self-review; do not relabel
self-review as peer review. Preserve whole-change findings and applicability
of physical evidence.

Fix Critical/Important infrastructure findings with appropriate RED -> GREEN
evidence. Any cognitive defect requires separately approved repair scope.
Behavior/evidence changes invalidate affected earlier qualification and require
a fresh run.

### Q10 — Integration

Require GREEN CI for the exact reviewed branch commit. Integrate reviewed
behavior without reset/clean/rebase/force-push or WIP destruction. Then require
exact integration/main CI, clean main, exact origin/main synchronization, and
applicable physical evidence.

Keep qualified behavior SHA, reviewed behavior SHA, integration SHA, and later
documentation/closure metadata SHA distinct.

### Q11 — Closure

Publish the final report only from validated evidence. State one engineering
verdict and the five individual research outcomes. Record blocker/error lists,
profile/source identities, gate coverage, physical/portable roles, exact CI,
review findings, and claims boundaries.

Close the issue and update task/ledger only after integration/exact-main gates.
Do not create an A012 or release as part of closure.

## Acceptance Criteria

- [x] Written spec explicitly approved.
- [x] Implementation plan reviewed/approved and execution method selected.
- [x] A011 issue/worktree/activation follow G06.
- [x] Portable pack passes from a clean checkout without Ollama.
- [x] Fresh local physical qualification reproduces pinned identities.
- [x] Frozen fingerprints, threshold, A010 counts/sentinel, and outcomes preserved.
- [x] Mutation/malformed/incomplete/provenance tests fail closed.
- [x] Complete full-system pack yields ENGINEERING_QUALIFIED.
- [ ] Whole-change review completed and Critical/Important findings resolved.
- [ ] Exact reviewed branch CI and exact integration/main CI GREEN.
- [ ] Final report/issue/task/CURRENT/ROADMAP coherent; final main clean/synced.
- [ ] FlyWireLLM untouched; package remains 0.1.0.dev0; no tag/release promotion.

## Preserved evidence

| Milestone | Outcome |
| --- | --- |
| A006 | NOT_SUPPORTED |
| A007 | SUPPORTED |
| A008 | SUPPORTED |
| A009 | SUPPORTED |
| A010 | NOT_SUPPORTED |

Terminal:
`qwen3.5:4b` /
`2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd`.

Embedding:
`qwen3-embedding:0.6b` /
`ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`;
dimension 1024; A005 threshold `0.5037018224299838`.

The written spec records the exact A006/A007/A008/A009/A010 fingerprints and
A010 portable primary comparison counts.

## Evidence

Live baseline:
- SHA `c1498e8e30a23fb67965239d13f0531d5326079e`;
- exact main CI [38038307095](https://github.com/funggier/FlyWireASCA/actions/runs/38038307095): success;
- clean main, exact origin/main match, ahead/behind 0/0;
- Issue #11 closed/completed; no A011 issue;
- runtime metadata: Ollama 0.32.15; pinned models/digests/dimension match.

Written-spec publication:
- spec/advance Task commit: `6eb5fb1399bc21a05599b92d9aa8b312df70c9e1`;
- exact spec CI [38039670308](https://github.com/funggier/FlyWireASCA/actions/runs/38039670308): success;
- local full suite: 563 passed in 4.83s;
- architecture contract audit and repository qualification: PASS;
- staged whitespace: PASS;
- spec self-review: incomplete markers/contradictions/ambiguity/scope PASS;
- unresolved Critical/Important spec findings: 0;
- publication main clean/synced at the spec commit.

These are baseline/planning observations, not A011 implementation or fresh
A011 full-system qualification evidence. No new physical qualifier replay was
claimed at those historical publication stages.

Implementation-plan publication:
- plan commit: `9d17350a6e4f4305b797e7d2766bb619416a510b`;
- exact plan CI [38042470411](https://github.com/funggier/FlyWireASCA/actions/runs/38042470411): completed/success, push/main;
- plan Git blob: `758e91ba2e55dc09aa65b99229bace8b3fe365fc`;
- local existing full suite: 563 passed in 4.79s; architecture/repository audits PASS;
- author plan self-review and cached whitespace PASS; unresolved Critical/Important 0;
- protected 67-path source SHA256: `8df49f05fe54de43667ab2f8ef5de2caae9376ffedf2cb8f8d26f0e4abcca6b6`, unchanged;
- future profile preview: 7481 bytes / `add06f285bf6decc7d492b987d3769dc64db4cb3d0177c8c6586d50ee5f6d46d`; production profile not created;
- clean/sync main at publication; no issue/worktree/activation/implementation.

Latest full handoff:
[ASCA-20261010-full-session-handoff-a011-plan-review.md](../reports/ASCA-20261010-full-session-handoff-a011-plan-review.md)

## Execution progress

Method: Native. Necessary subagent use authorized; final independent review required.
Activation base: `e8f75a862e0cb0d28b7e4efe25a77fa088ad646f` / exact CI38042756382 success.
Issue #12 created open, isolated worktree created from exact base.
Baseline suite:563 passed in6.29s.
Task 1 RED: test_current_points_to_active_a011_with_actual_issue and
test_pre_a011_stays_completed_during_a011_lifecycle failed on ACTIVE assertion;
2 failed,14 passed. No historical closure assertions weakened.

| Execution Task | State |
| --- | --- |
| 1 Activation | DONE — mutable ledger RED/GREEN verified |
| 2 Records/schema/classifier | DONE |
| 3 Frozen profile/provenance | DONE |
| 4 Process/evidence adapters | DONE |
| 5 Artifacts/publication | DONE |
| 6 Portable pack | DONE |
| 7 Physical pack | DONE |
| 8 Portable CI | DONE |
| 9 Fresh qualification | DONE |
| 10 Review/integration | ACTIVE — independent review complete, repairs GREEN; new qualification/integration pending |
| 11 Closure/handoff | PLANNED |

Ruling: Skill helper/reference resources were not available via advertised
paths; an equivalent ignored local Python task driver retains briefs/BASE/
test logs/progress. Main skill requirements still apply. Cost if wrong:
bookkeeping gaps, checked against Git and raw logs.
Ruling: Preserve execution workspace/worktree through closure; no automatic
cleanup of evidence. Cost: local disk use.

Task 1: Ruling: full suite exposed two PRE-A011 historical tests still owning mutable CURRENT/ROADMAP, a file omitted from plan Task1 — move their live-state ownership to canonical test_task_ledger while preserving all PRE closure assertions/documents/Issue#11 — cost if wrong: historical resume assertion weakened; mitigated by keeping the exact checked historical resume line and current-state canonical coverage.

## Current Action

A011 ACTIVE. Tasks1-9 are GREEN. Task10 independent review found two Important
qualification infrastructure defects; both are repaired with observed
RED/GREEN and full suite952 PASS. Qualify the repaired feature SHA with fresh
evidence/exact CI, then integrate and qualify the exact main SHA.

## Next Action

Continue approved Tasks10-11 without repeating completed approval gates.
Preserve pinned research results/source and full physical/exact-CI evidence.

## Fresh candidate qualification — 2026-10-10

Qualified behavior SHA: `f36080155957e30a0a9ab6be2270a67330a151e0`.
Exact push/branch CI [38048466684](https://github.com/funggier/FlyWireASCA/actions/runs/38048466684): SUCCESS.
Portable CI artifact: `11667799249` / `a011-portable-38048466684-1`; downloaded and schema/index/raw hashes/source/finality audited.

Fresh full replay: `FULL_SYSTEM`, `is_final=true`, `ENGINEERING_QUALIFIED`, exit0.
Source before/after clean on the same SHA; 18 mandatory gates once/PASS,
94 frozen checks PASS, 86 indexed artifacts validated; errors/blockers empty.
Physical process ran 2026-10-10T11:31:44.850Z–11:33:45.680Z (duration descriptive).

Pack root:
`T:\Space\Projects\ProjectsAI\FlyWireASCA-qualification-evidence\a011-f360801-candidate-61cbe52ea47d4665ab72eaa67739df0b`

| File | SHA256 |
| --- | --- |
| artifact-index.json | `6222146925aca446ade4380fc996580e869d31c47b9e4c394b49125b545a39c2` |
| qualification.json | `5b62d61c64bd5168601abcb9d49b0aee7fc21b2d1b9549fbbe5625601f4625d2` |
| qualification.md | `c043734a1b68efa9af0e1ef49cdb30356fc4fe4be070b902e65d03939a89f06f` |

Profile SHA256: `add06f285bf6decc7d492b987d3769dc64db4cb3d0177c8c6586d50ee5f6d46d`.
Protected Git-tree SHA256: `8df49f05fe54de43667ab2f8ef5de2caae9376ffedf2cb8f8d26f0e4abcca6b6` (all 67 original paths unchanged).
Host `CDQ-P`, `Windows-10-10.0.19045-SP0`, Python `3.14.6`,
Ollama `0.32.15`, endpoint `http://127.0.0.1:11434`.
Pinned terminal/embedding digests match before/after; actual embedding/vector-health dimension1024;
A005 actual threshold `0.5037018224299838` / physical_frozen_threshold_v1.

| Gate | State |
| --- | --- |
| P00_PROFILE_SOURCE | PASS |
| P01_TESTS | PASS |
| P02_ARCHITECTURE | PASS |
| P03_REPOSITORY | PASS |
| P04_A003 | PASS |
| P05_A008 | PASS |
| P06_A009 | PASS |
| P07_A010 | PASS |
| P08_FROZEN_AUDIT | PASS |
| P09_PACK_VALIDATION | PASS |
| H00_PREREQUISITES | PASS |
| H01_A004 | PASS |
| H02_A005 | PASS |
| H03_A006 | PASS |
| H04_A007 | PASS |
| H05_A009 | PASS |
| H06_A010 | PASS |
| H07_FULL_VALIDATION | PASS |

| Research milestone | Frozen outcome | Fresh evidence role |
| --- | --- | --- |
| A006 | NOT_SUPPORTED | PHYSICAL_PRIMARY |
| A007 | SUPPORTED | PHYSICAL_PRIMARY |
| A008 | SUPPORTED | PORTABLE_PRIMARY |
| A009 | SUPPORTED | PORTABLE_PRIMARY + PHYSICAL_SECONDARY |
| A010 | NOT_SUPPORTED | PORTABLE_PRIMARY + PHYSICAL_SECONDARY |

A010: 12 total cases, 9 primary; ASCA/dense successes7/8, shared7, dense-only1,
ASCA-only0, queries28/27, scored vectors1984/1440, cumulative selections66/480,
peak selections12/256, procedure attempts14/9. Dense-only sentinel
`selective-routing-miss-sentinel`: ASCA_PRIMARY=false / DENSE_EXHAUSTIVE=true.
All original ablations/cases/repeat payloads retained and full frozen semantic digests match.

This is candidate evidence. Whole-change review and integration/main qualification remain required.
The commit containing this ledger is documentation metadata, distinct from qualified behavior SHA.

## Whole-change review and infrastructure repairs

Independent fresh reviewer: /root/a011_whole_change_review_resumed,
gpt-6-astra/high; exact range
e8f75a862e0cb0d28b7e4efe25a77fa088ad646f..ba7b150cba8f4738415745678db5977f898dcde1.
The first review attempt ended at usage limit without a review result.
Critical0 / Important2 / Minor0; declined to judge none.

- I1: require actual A005 benchmark and A009/A010 physical detail structures,
  strict acceptance primitives and summary/metadata agreement. Missing or
  contradictory detail now fails; unchanged legacy workloads/criteria retained.
- I2: confirmed partial /api/show transport loss leaves dimension unobserved;
  classify absence as BLOCKED while observed wrong digest or malformed reachable
  metadata still FAILS. No retries or inference added.

Root retained both Important grades and completed one TDD repair pass:
regression RED21 failed/2 passed; focused GREEN78 passed; full suite952 passed
in77.72s. Architecture/repository audits and whitespace PASS.
Independent focused review tests398 passed; protected67 paths/profile unchanged.
No second review was dispatched; repair verification is author TDD/full suite.
All review/reproducer/logs retained in this plan's ignored execution workspace.

The prior real f360801 pack has consistent actual details and remains historical
evidence for that SHA. It does not qualify these repairs or integration/main.
Fresh repaired-feature and exact integration qualification are required.
