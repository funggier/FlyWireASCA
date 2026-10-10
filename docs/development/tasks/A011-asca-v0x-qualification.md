# A011 — ASCA v0.x Qualification

Status: PLANNED
GitHub Issue: not created
Branch: not created
Activation base: not assigned

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

This file is an **advance task inventory**. Work items below describe scope,
dependencies, deliverables, and evidence. They are not a reviewed implementation
plan and do not authorize execution. No writing-plans invocation or
implementation plan exists yet. Concrete file edits, RED/GREEN commands,
commits, and execution scheduling are decided only after written-spec approval.

## Approval gates

| Gate | Deliverable / permission unlocked | Current state |
| --- | --- | --- |
| G00 | Read handoff and verify live Git/GitHub/runtime baseline | PASS at `c1498e8e30a23fb67965239d13f0531d5326079e` |
| G01 | Explicit approval of complete conversational design; permits written spec | PASS — user approval in this session |
| G02 | Written spec, inline self-review, commit/push, exact spec-commit CI | Publication verification pending |
| G03 | User explicitly reviews/approves the written spec | WAITING USER REVIEW |
| G04 | Invoke writing-plans, create/self-review/publish implementation plan, exact CI | NOT STARTED — requires G03 |
| G05 | User reviews/approves plan and selects execution method | NOT STARTED — requires G04 |
| G06 | Create A011 issue, isolated worktree, and coherent ACTIVE task/ledger | NOT STARTED — requires G05 |

A reply approves the stage actually presented. G01 does not approve a
previously nonexistent written spec or plan. Do not collapse G03 and G05.
All future implementation work items remain PLANNED until G06.

## Advance work-item inventory

These are local identifiers inside A011, not separate A-numbered milestones
or GitHub issues.

| ID | Responsibility | Depends on | Required delivery/evidence |
| --- | --- | --- | --- |
| Q01 | Qualification records and final classifier | G06 | Strict scope/finality/gate contracts; precedence and incomplete-evidence RED -> GREEN tests |
| Q02 | Frozen qualification profile and independent anchor | Q01 | Reviewed immutable identity profile; every expected-value mutation rejected |
| Q03 | Existing qualifier evidence adapters and provenance | Q01, Q02 | Reuse existing CLI outputs/validators; command/exit/raw hashes/source context coherent |
| Q04 | Portable orchestrator and deterministic replay audit | Q03 | All mandatory portable gates covered; repeat checks; no Ollama calls or recursive pytest |
| Q05 | Portable CI integration | Q04 | Existing CI topology preserved; A011 portable pack tested on exact branch commit |
| Q06 | Physical preflight and full-system orchestrator | Q03, Q04 | Missing runtime/model distinguished from wrong identity; fresh local portable plus sequential physical replay |
| Q07 | Pack/report publication and artifact validation | Q01, Q03, Q04, Q06 | Atomic JSON/Markdown/raw-index output; hashes, roles, scopes, and finality agree |
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

- [ ] Written spec explicitly approved.
- [ ] Implementation plan reviewed/approved and execution method selected.
- [ ] A011 issue/worktree/activation follow G06.
- [ ] Portable pack passes from a clean checkout without Ollama.
- [ ] Fresh local physical qualification reproduces pinned identities.
- [ ] Frozen fingerprints, threshold, A010 counts/sentinel, and outcomes preserved.
- [ ] Mutation/malformed/incomplete/provenance tests fail closed.
- [ ] Complete full-system pack yields ENGINEERING_QUALIFIED.
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

These are baseline/planning observations, not A011 implementation or fresh
A011 full-system qualification evidence. No new physical qualifier replay is
claimed in this documentation session.

## Current Action

A011 remains PLANNED. Prepare and publish written spec, advance Task, and
next-session handoff after author self-review and exact CI.

## Next Action

Stop for explicit user review/approval of the published written spec.
Only then invoke writing-plans. Stop again for plan review and execution-method
selection before creating an issue, worktree, ACTIVE state, or implementation.
