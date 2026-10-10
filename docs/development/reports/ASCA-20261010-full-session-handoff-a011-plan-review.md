# FlyWireASCA Full Session Handoff — A011 Plan Review Gate

Date: 2026-10-10
Repository: `funggier/FlyWireASCA`
Local repository: `T:\Space\Projects\ProjectsAI\FlyWireASCA`
Resume stage: **implementation-plan review/approval + execution-method selection**
A011: **PLANNED / not activated / no GitHub Issue**

## 1. Read this first and follow live authority

This supersedes the written-spec-review handoff as the current resume document:

- previous: [ASCA-20261010-full-session-handoff-a011-written-spec-review.md](ASCA-20261010-full-session-handoff-a011-written-spec-review.md);
- original architectural-design resume: [ASCA-20261010-full-session-handoff-post-pre-a011-a011-design-gate.md](ASCA-20261010-full-session-handoff-post-pre-a011-a011-design-gate.md).

The written spec is now user-approved and the detailed implementation plan is
written, self-reviewed, committed, pushed, and exact-CI GREEN. The user has
**not yet reviewed this newly written plan or selected an execution method**.
Do not infer those decisions from approval given before the plan existed.

ยังห้ามเริ่ม implementation: ให้อ่านแผนและหยุดที่ G05 เพื่อให้ผู้ใช้ review/approve
implementation plan และเลือก Native หรือ Subagent-driven ก่อน จึงเริ่ม Task 1 ได้

Read with:

1. [CURRENT](../tasks/CURRENT.md)
2. [A011 planned Task](../tasks/A011-asca-v0x-qualification.md)
3. [ROADMAP](../tasks/ROADMAP.md)
4. [Approved written spec](../../superpowers/specs/2026-10-10-a011-asca-v0x-qualification-design.md)
5. [Implementation plan](../../superpowers/plans/2026-10-10-a011-asca-v0x-qualification.md)
6. [Architecture snapshot](../../architecture/ASCA-PRE-A011-SNAPSHOT.md)
7. [Qualification matrix](../QUALIFICATION-MATRIX.md)
8. [PRE-A011 final report](ASCA-20261010-PRE-A011-architecture-process-stabilization.md)

Git/GitHub/runtime are authoritative. Inspect current Git/remote/exact CI and
issues rather than assuming a historical SHA is still HEAD.
The approved spec's AWAITING USER REVIEW label and previous handoff's WAITING
gate record their publication-time states. This current approval ledger
supersedes those stage labels; the approved spec blob was deliberately preserved.

## 2. Approval ledger and actual authorization

| Gate | Evidence/state |
| --- | --- |
| G00 | Original handoff + live source check PASS at c149...; fresh planning checks PASS at 0ca... and published plan9d... |
| G01 | User “อนุมัติให้ทำไปเลยครับ” approved full conversational design and writing spec |
| G02 | Written spec self-review/publication/exact CI PASS at 6eb... / run38039670308 |
| G03 | User “โอเคครับ ทำต่อได้เลย”, 2026-10-10 16:11:41 +07:00, after written spec was presented: PASS |
| G04 | writing-plans invoked; plan author self-review/publication/exact CI PASS at 9d... / run38042470411 |
| G05 | **WAITING: user plan review/approval + execution method** |
| G06 | NOT STARTED: requires G05; no issue/worktree/ACTIVE/implementation |

User's original staged gates remain controlling. G03 is not G05.
Approval and method selection may be given in one reply, but must be explicit.
No final conversational-design gate needs to be repeated: it was completed.

## 3. Exact publication and CI evidence

| Publication | Exact SHA | Exact CI |
| --- | --- | --- |
| PRE-A011/design-gate baseline | `c1498e8e30a23fb67965239d13f0531d5326079e` | [38038307095](https://github.com/funggier/FlyWireASCA/actions/runs/38038307095), success |
| Spec + advance Task | `6eb5fb1399bc21a05599b92d9aa8b312df70c9e1` | [38039670308](https://github.com/funggier/FlyWireASCA/actions/runs/38039670308), success |
| Written-spec handoff metadata | `0ca486b136da127ce69543f8c5c9258b6663ece6` | [38039978481](https://github.com/funggier/FlyWireASCA/actions/runs/38039978481), success |
| Implementation plan + Task/CURRENT | `9d17350a6e4f4305b797e7d2766bb619416a510b` | [38042470411](https://github.com/funggier/FlyWireASCA/actions/runs/38042470411), completed/success, push/main |

Approved spec Git blob: `c14b921f3f6b83166f2bb6e554f226636fc7ed29`.
Published plan Git blob: `758e91ba2e55dc09aa65b99229bace8b3fe365fc`.

At the plan-publication verification, main was clean, cached origin/main matched,
git ls-remote origin refs/heads/main matched exact9d..., ahead/behind0/0.

This handoff and ledger publication evidence are a subsequent documentation-only
commit. Discover its exact containing SHA from live Git, and query exact CI for
the live HEAD; do not assume 9d... remains HEAD or embed a self-referential SHA.
The publishing session verifies that final metadata commit's CI before returning.

## 4. What this session changed

Created the detailed implementation plan with:

- 11 ordered execution Tasks mapped to Q01-Q11;
- exact file responsibility map and typed immutable v1 schema;
- shared APIs/signatures and existing qualifier output contracts;
- named RED/GREEN tests and command/commit boundaries;
- five realistic Review Focus failure modes mapped to owning tests;
- canonical future profile preview and literal independent hash anchor;
- shallow-clone/Windows-CRLF-safe Git protected-source fingerprint;
- portable + physical orchestration, safe artifacts, exact CI;
- fresh full qualification, whole-change review, reviewed integration and closure;
- execution-method choice and correct resume instructions.

Updated A011 Task and CURRENT for G03 PASS/G04 PASS/G05 WAITING.
Advance inventory dependencies were refined: Q07 artifact publication precedes
Q04/Q06 runners, matching the concrete plan. No new milestone was invented.
Created this full session handoff.

Only documentation changed in this planning session. No production profile,
qualification package, new script, source/test/workflow/version change, issue,
worktree, tag, release, or A011 activation was created.

## 5. Live task/issue state and historical stabilization

A001-A010 are DONE. A011 remains PLANNED.
PRE-A011 is DONE; GitHub Issue #11 is CLOSED / COMPLETED.
All-state paginated issue inspection found #1-#11 closed/completed and no A011
issue. Recheck on resume; never create a duplicate or guess the new issue number.

Do not reopen PRE-A011. Its report's early ACTIVE/pre-review narrative is
historical; later closure evidence and live Issue #11 establish completion.
No cognitive repair, optimization, retuning or release belongs to A011.

## 6. Four-part approved design

### Part 1 — Results

Engineering states:
ENGINEERING_QUALIFIED / ENGINEERING_NOT_QUALIFIED / QUALIFICATION_BLOCKED.

Internal gates: PASS / FAIL / BLOCKED / NOT_RUN.
Any verified hard failure dominates simultaneous external blockers.
Blockers require independently confirmed unavailable runtime/model prerequisites.
Unknown/inconsistent/missing evidence fails closed.

Portable-only: PORTABLE_ONLY, is_final=false, engineering_verdict=null.
Full-system: FULL_SYSTEM, is_final=true, one final state, every required gate once.
Portable PASS never claims full qualification.

Research remains separate and milestone-specific:

| Milestone | Outcome | Role |
| --- | --- | --- |
| A006 | NOT_SUPPORTED | frozen physical primary |
| A007 | SUPPORTED | frozen physical primary |
| A008 | SUPPORTED | portable primary |
| A009 | SUPPORTED | portable primary; physical secondary |
| A010 | NOT_SUPPORTED | portable primary; physical secondary |

No aggregate ASCA intelligence score. Valid negative research evidence can PASS
engineering qualification.

### Part 2 — Pack, replay and audit

Qualification Pack + Fresh System Replay + Frozen Evidence Audit:
repository/architecture integrity, frozen identities, fresh portable replay,
fresh physical replay, validated final manifest/report.

Portable gates: P00_PROFILE_SOURCE, P01_TESTS, P02_ARCHITECTURE,
P03_REPOSITORY, P04_A003, P05_A008, P06_A009, P07_A010,
P08_FROZEN_AUDIT, P09_PACK_VALIDATION.

Physical gates: H00_PREREQUISITES, H01_A004, H02_A005, H03_A006,
H04_A007, H05_A009, H06_A010, H07_FULL_VALIDATION.

Full physical run first performs fresh portable locally on the same candidate/
profile. Existing standalone CI gates remain, and later implementation adds
A011 portable. CI stays Ollama-free; no physical gates in GitHub Actions.

P08 repeats existing A008/A009/A010 deterministic workloads. Only optional
top-level note is excluded from semantic digest. Case order, execution IDs,
counts, policies and outcomes remain included; unknown fields fail.
Physical byte equality/timing determinism is not required.

### Part 3 — Source and artifact boundaries

Future package `src/flywire_asca/qualification/` imports only stdlib/contracts.
Scripts orchestrate unchanged qualifier CLIs and inject their existing validators.
Cognitive packages never import qualification. Add dependency-audit vocabulary
and mutable lifecycle tests only during approved implementation.

Future entry points:
`scripts/qualify_asca_v0x_a011.py`,
`scripts/qualify_asca_v0x_a011_physical.py`.

Future profile:
`docs/development/qualification/a011-v0x-profile-v1.json`.

Manifest v1 exact top keys:
schema_version, profile, source, scope, is_final, portable_status,
engineering_verdict, gates, frozen_checks, research_evidence, replay_identity,
physical_environment, errors, blockers, artifact_index, claims_boundary.

Artifacts: qualification.json, derived qualification.md, raw gate logs/JSON,
frozen profile copy and artifact-index.json. Relative refs/hash lengths/bytes
must agree. Index excludes itself/manifest/report, preventing circular hashing.
New outside-checkout directory, atomic final publication, no overwrite/links/
path escape. Write failure cannot return success.

### Part 4 — Execution and failure flow

Precheck clean exact source/profile; run portable; inspect local prerequisites;
run sequential physical qualifiers; inspect identities/source again; validate
all gates/artifacts; classify and publish.

PROFILE_DRIFT / IDENTITY_DRIFT / REPLAY_DRIFT / EVIDENCE_INVALID /
SOURCE_MISMATCH / QUALIFIER_FAILED are hard failures.
PREREQUISITE_UNAVAILABLE / MODEL_MISSING are blockers only with proof.
ARTIFACT_WRITE_FAILED is hard infrastructure failure.
Do not infer blockers from free-text error keywords.

Stop on real/suspected cognitive defect and separate an explicit repair task.
No A003-A010 semantic change or A009/A010 retrieval optimization inside A011.
No hidden retry, auto-pull, calibration, model substitution or runtime restart.

## 7. Task-by-task implementation resume map

| Task | Deliverable | Inventory |
| --- | --- | --- |
| 1 | Gate-authorized actual issue/worktree/ACTIVE ledger | G06 |
| 2 | Immutable records, strict manifest, classifier, dependency edge | Q01 |
| 3 | Frozen profile/literal anchor, clean/source fingerprint | Q02/Q03 |
| 4 | Explicit process runner/existing-evidence adapters | Q03 |
| 5 | Safe indexed artifacts/atomic publication | Q07 |
| 6 | Portable nonfinal pack/frozen repeat audit | Q04 |
| 7 | Physical preflight/full-system pack/blocker taxonomy | Q06 |
| 8 | Portable CI step/artifact retention, exact branch run | Q05 |
| 9 | Fresh full candidate qualification/raw frozen audit | Q08 |
| 10 | Whole-change review/RED-GREEN repairs/reviewed integration | Q09/Q10 |
| 11 | Final report/issue/ledger closure/full handoff | Q11 |

Recommended method: **Native**, one implementer across shared record/evidence/
artifact/runner interfaces, then one fresh whole-change reviewer.
Alternative: **Subagent-driven**, fresh implementer/reviewer per Task2-8 and final
whole-change review. The user has not selected either method.
No workers were dispatched during plan writing; plan self-review was by author.

After G05, use required execution skill for chosen method and using-git-worktrees.
Suggested feature branch qualification/a011-asca-v0x and worktree
T:\Space\Projects\ProjectsAI\FlyWireASCA-worktrees\a011-asca-v0x-qualification.
Check actual destinations/WIP first. Activation base is live reviewed publication
HEAD, not a historic planning SHA. Record returned issue number, never assumed12.

## 8. Frozen identities to preserve

| Identity | Exact value |
| --- | --- |
| Package | 0.1.0.dev0 |
| Terminal tag | qwen3.5:4b |
| Terminal digest | 2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd |
| Embedding tag | qwen3-embedding:0.6b |
| Embedding digest | ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d |
| Embedding dimension | 1024 |
| A005 threshold | 0.5037018224299838 |
| A006 physical fingerprint | e51fea2e58186e94d7affc964509e96d96fc656759677d7dcc073e5b36b91035 |
| A007 physical fingerprint | 59f95ef115534fe24e59570cb281c0564ab75aadf364f4c26feba0d4078213c9 |
| A008 portable fingerprint | f52fbd4ab018386ff3cbfb62a68cc44a4b40e54ec4fd9a3b2e885dd2c5663fc6 |
| A009 deterministic fingerprint | 2f92b5092de346f62879ac2cbb9f96d6de5d6f919e12d0693345c8228b01ab2a |
| A010 deterministic fingerprint | 69d20542cd1e7e5c25a0fb61b9060f622379206b519da3cec7624e00bb6e5d4c |

Policies: familiarity EVIDENCE_ONLY; selector SINGLE_BEST; expansion SIGNAL_DRIVEN;
procedure CHUNKED; recovery MISMATCH_DRIVEN_RECOVERY; max procedure attempts3;
hidden automatic retry0; terminal model is non-controlling.

A010 total fixture case_count=12; primary comparison case_count=9.
Frozen comparison ASCA/dense:
success7/8; queries28/27; scored vectors1984/1440;
cumulative selected66/480; peak selected12/256; procedure attempts14/9.
Shared success7, dense-only1, ASCA-only0.
Sentinel selective-routing-miss-sentinel must remain dense-only.

## 9. Planning trust-anchor refinements

Future profile canonical bytes: UTF-8, json.dumps ensure_ascii=False,
sort_keys=True, separators=(",",":"), no newline/BOM.
Length7481; SHA256:
`add06f285bf6decc7d492b987d3769dc64db4cb3d0177c8c6586d50ee5f6d46d`.

Profile JSON preview and all67 protected paths are in plan Appendix A.
No production profile was created. Its independently reviewed expected hash
becomes a literal in future profile.py after G06.

Protected source SHA256:
`8df49f05fe54de43667ab2f8ef5de2caae9376ffedf2cb8f8d26f0e4abcca6b6`.

Coverage:57 pre-existing src Python paths plus10 existing qualifier scripts.
Sorted records with path/mode/Git-blob SHA, same compact sorted JSON hashing.
Use HEAD committed identity, not CRLF worktree bytes; no historical baseline
object/fetch dependency. Detect additional cognitive paths as well as modified/
missing existing protected paths. Candidate SHA binds new qualification files.

Semantic payload digests (optional top-level note only omitted):
- A008: `4883b4eba174a2edc8c753297e02903c940f0b0fc38a71f80d5b76541b49e7c3`
- A009: `5fb0c8b803b0c15888907ca388aa8f705d904351a9f23da43cdf7a285c9052b7`
- A010: `8e57b744e96294565551061728ff90b4ddba43b66051237124378f981db185d5`

These were observed from unchanged existing portable workloads. They are added
qualification identity checks, not new benchmark/hypothesis/retuning.

## 10. Existing interface findings the next implementer needs

- A003 prints JSON and exit status under --qualify; no --output or PASS marker.
- A008/A009/A010 aggregate key is aggregate_metrics; their run_qualification()
  returns payload dict and validate_qualification_payload() returns errors.
- A004 succeeds with qualified true plus errors empty/exit0.
- A005 must be mode qualification and retrieval_qualified true, threshold exact,
  threshold_origin physical_frozen_threshold_v1; vector_health.dimension is the
  actual observed vector dimension, distinct from metadata.
- A006/A007 pure validate_physical_experiment accepts experiment member.
- A009/A010 physical require BOTH physical_prerequisites_valid and
  physical_integration_valid plus exit0; portable_primary_outcome is secondary
  metadata and cannot change primary evidence.
- Physical A004-A007 use120s adapter defaults; A009/A010 keep their own defaults.
  A011 adds no stricter process deadline.
- A009/A010 physical CLI has no base-url option; plan uses fixed existing
  http://127.0.0.1:11434 with no endpoint override/legacy source changes.
- Failed physical CLIs often use free-text errors: independently confirm absence;
  never turn every exit1 into BLOCKED.
- Current CI uses Python3.11/fetch-depth2; local Python3.14.6.
- Runner tests must use injected fake processes; real full pytest runs only
  outside pytest. Real portable CLI replay requires a clean committed candidate.

## 11. Runtime metadata and verification limits

Local host CDQ-P; Windows10 10.0.19045; Intel Core Ultra5 245K; approximately32GB RAM.
Python3.14.6: C:\DATAstore\Python\Python3-14-3\python.exe.
Ollama0.32.15 at http://127.0.0.1:11434.
LConnect process16892 was observed in the prior environment check.

Runtime metadata at 2026-10-10T09:15:16.837Z matched pinned digests and embedding
dimension1024. This is preflight metadata, not new physical inference evidence.
No A004/A005/A006/A007/A009/A010 physical replay occurred in this plan session.

Planning verification:
- existing full suite:563 passed in4.79s;
- architecture_contract_audit=PASS, exit0;
- repository_qualification=PASS, exit0;
- cached whitespace PASS;
- source protected67-path fingerprint unchanged;
- preview7481 bytes/add06... exact;
- no incomplete markers/broken plan links;
- approved spec blob unchanged;
- new product paths absent; version0.1.0.dev0 unchanged;
- exact plan CI38042470411 completed/success with all existing gates;
- author self-review scope/type/coverage/Review Focus PASS, unresolved
  Critical/Important plan findings0.

These are planning/baseline checks, not an implemented A011 qualified system.

## 12. Closure discipline for later execution

Retain exact branch/qualified behavior/whole-review/integration/metadata SHAs.
Fresh physical evidence must bind same candidate/profile. Plan requires a fresh
full pack on integration/main before claiming that exact integration SHA qualified.
Docs-only changes record qualified behavior separately.

Require full ENGINEERING_QUALIFIED, frozen data unchanged, whole-change review,
Critical/Important infrastructure fixes with RED/GREEN, exact reviewed branch CI,
exact integration/main CI, clean sync, coherent task/issue state.
A correctly classified FAILED/BLOCKED pack does not close A011 GREEN.
No version promotion, tag/release, A012 or FlyWireLLM change.

## 13. Next-session procedure

1. Read this file first, then CURRENT/Task/ROADMAP/spec/plan/snapshot/matrix.
2. Use use-local-workspace and required relevant superpowers skills.
3. Read live main/status/origin exact40hex/latest exact CI.
4. Verify Issue #11 closed/completed; A011 PLANNED; no A011 issue.
5. Preserve approval ledger: written spec approved, implementation plan awaiting
   review/method; do not repeat completed design/spec work.
6. Present plan review with Native recommendation and Subagent-driven alternative.
7. If G05 not explicitly complete, stop there; no code/issue/worktree/ACTIVE.
8. After G05, begin plan Task1 with live recheck, actual issue, isolated worktree,
   ledger TDD/ACTIVE, then Tasks2-11 under chosen execution skill.
9. Preserve full task/evidence/physical/exactCI/review discipline.

Copy-ready prompt:

```text
@use-local-workspace
ทำ funggier/FlyWireASCA ต่อ โดยอ่าน
docs/development/reports/ASCA-20261010-full-session-handoff-a011-plan-review.md
ใน repo ก่อนเป็นอันดับแรก แล้วตรวจ live Git/GitHub/runtime, CURRENT, A011 Task,
ROADMAP, approved spec, implementation plan, snapshot และ qualification matrix

Written spec ผ่าน approval แล้ว แผนถูก publish พร้อม exact CI
Resume ที่ G05: ขอ user review/approve implementation plan และเลือก Native หรือ
Subagent-driven ก่อน ห้ามถือ approval เก่าของ written spec เป็น approval แผน

A011 ยัง PLANNED ไม่มี Issue/worktree/implementation; PRE-A011 #11 ต้อง
CLOSED/COMPLETED ห้าม reset/clean/rebase/force-push ห้ามแตะ FlyWireLLM
คง version0.1.0.dev0 ไม่สร้าง tag/release/0.1.0 หรือ A012
รักษา A006 NOT_SUPPORTED, A007/A008/A009 SUPPORTED, A010 NOT_SUPPORTED
ไม่ retune frozen models/digests/threshold/fingerprints/counts/cues/sentinel
A011 เป็น qualification layer ไม่ใช่ optimization/benchmark ใหม่
```
