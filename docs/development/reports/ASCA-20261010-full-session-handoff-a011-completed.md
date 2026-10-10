# Full Session Handoff — A011 completed

Closure date: 2026-10-10 (Asia/Bangkok). User requested a detailed task plan and a reusable new-session handoff; the approved11-task plan has been executed.

## Read this first / correct resume point

**A011 engineering milestone is DONE / ENGINEERING_QUALIFIED. Issue12 is CLOSED / COMPLETED, verified through a separate live fetch after the update. PRE-A011 Issue11 remains CLOSED / COMPLETED. No next milestone, release or version promotion is authorized.**

Current main publication before this handoff: `4053cb42bb50a683965d83bee20cbffb25668f02`; exact push/main CI [38059824196](https://github.com/funggier/FlyWireASCA/actions/runs/38059824196) completed/success; clean/exact origin/main0/0. This is closure metadata, distinct from the physically qualified integration below.

This handoff's containing commit is a later documentation-only SHA. Resolve it with Git log for this path and require its own latest exact CI; do not replace the physically qualified SHA with the metadata SHA or start a self-SHA update loop. Final session completion is claimed only after that exact CI/clean synchronization is verified.

First read this handoff, then `docs/development/tasks/CURRENT.md`, `docs/development/tasks/ROADMAP.md`, `docs/development/tasks/A011-asca-v0x-qualification.md`, [final evidence report](ASCA-20261010-A011-v0x-qualification.md) and `docs/development/QUALIFICATION-MATRIX.md`. Read the approved spec/plan if changing qualification. Historical PRE/design/plan handoffs are historical stage snapshots; their PLANNED/no-issue language is not current authority.

Verify live Git/GitHub/runtime before any new work. Do not redo PRE-A011, approval gates, or completed execution Tasks1-11. With no new scoped user request, stop after read-only state verification; no automatic A012 issue/worktree, implementation, tag or release.

## Workspace and live issues

- Main: `T:\Space\Projects\ProjectsAI\FlyWireASCA`.
- Preserved feature worktree: `T:\Space\Projects\ProjectsAI\FlyWireASCA-worktrees\a011-asca-v0x-qualification`.
- Preserved branch: `qualification/a011-asca-v0x` at `e96d71b033212668bc3ce98873903618c9c44bcf`. No cleanup/deletion performed.
- Plan-owned persistent execution/review/brief/BASE/raw-test/audit ledger: `T:\Space\Projects\ProjectsAI\FlyWireASCA-worktrees\a011-asca-v0x-qualification\.superpowers\sdd\2026-10-10-a011-asca-v0x-qualification`. First line identifies the approved plan; complete task rows are authoritative together with Git.
- [A011 Issue12](https://github.com/funggier/FlyWireASCA/issues/12): CLOSED/COMPLETED, closedUTC `2026-10-10T14:33:14Z`, Bangkok `2026-10-10T21:33:14+07:00`.
- [PRE-A011 Issue11](https://github.com/funggier/FlyWireASCA/issues/11): CLOSED/COMPLETED; never reopened.
- [PR13](https://github.com/funggier/FlyWireASCA/pull/13): merged normally, preserving all10 feature commits. No squash/rebase/force.

## Approval record and binding documents

| Gate | Actual approval/evidence |
| --- | --- |
| G01 conversational design | User: อนุมัติให้ทำไปเลยครับ; not inferred from the original handoff instruction |
| G02 spec publication | 6eb5fb1399bc21a05599b92d9aa8b312df70c9e1 / [38039670308](https://github.com/funggier/FlyWireASCA/actions/runs/38039670308) success |
| G03 written spec approval | User: โอเคครับ ทำต่อได้เลย; 2026-10-10 16:11:41 +07:00 |
| G04 implementation plan | writing-plans invoked;9d17350a6e4f4305b797e7d2766bb619416a510b / [38042470411](https://github.com/funggier/FlyWireASCA/actions/runs/38042470411) success |
| G05 plan/method approval | User: ทำ Native ได้เลยครับ ถ้าจำเป็นก็ Subagent-driven ได้; 2026-10-10 16:52:26 +07:00 |
| G06 activation | Issue12 + isolated worktree + ACTIVE ledger created only after G05; activation base`e8f75a862e0cb0d28b7e4efe25a77fa088ad646f` / [38042756382](https://github.com/funggier/FlyWireASCA/actions/runs/38042756382) success |

- Approved spec: `docs/superpowers/specs/2026-10-10-a011-asca-v0x-qualification-design.md`; unchanged Git blob `c14b921f3f6b83166f2bb6e554f226636fc7ed29`.
- Approved plan: `docs/superpowers/plans/2026-10-10-a011-asca-v0x-qualification.md`; unchanged Git blob `758e91ba2e55dc09aa65b99229bace8b3fe365fc`.

Native implementation applied executing-plans/TDD task-by-task. Necessary fresh whole-change review subagent was explicitly authorized. Approved Task10 authorized normal evidence-driven PR integration; approved Task11 authorized exact-CI metadata publication and live issue completion. No repeated permission request was required.

## Preserved architecture and detailed scope

1. Engineering qualification uses strict immutable records, exact v1 manifests, mandatory coverage and causal evidence. Final states are ENGINEERING_QUALIFIED, ENGINEERING_NOT_QUALIFIED, QUALIFICATION_BLOCKED; verified hard failure dominates an external blocker. Portable-only has is_final=false and engineering_verdict=null.
2. Qualification Pack + Fresh System Replay + Frozen Evidence Audit binds one clean exact source/profile before/after execution. Fresh portable P00-P09 precedes sequential local physical H00-H07 in the same new external pack. Typed raw/normalized acceptance, indexed hashes and atomic publication must agree; existing directories/unsafe links/publication failures fail closed.
3. Frozen expectations are independent of fresh observations: model identities/dimension/threshold, fixtures/fingerprints, full portable semantics, five research outcomes, A010 counts/sentinel and policies cannot bless drift. A006/A007 physical evidence is primary; A008 portable is primary; A009/A010 portable is primary with physical secondary. Historical references are never claimed fresh.
4. Qualification owns infrastructure only. Cognitive modules never depend on qualification; script-owned legacy validators perform no inference at import. Existing CLI settings/adapter limits/acceptance are retained, no stricter physical process deadline, hidden retries, model pull/substitution/restart or calibration. Suspected cognitive defects stop qualification and require a separate explicitly approved repair task.

Qualification modules: records/manifest/classifier/profile/provenance/process/evidence/artifacts/portable/physical under src/flywire_asca/qualification. Entry points: scripts/qualify_asca_v0x_a011.py and scripts/qualify_asca_v0x_a011_physical.py; pure bridge scripts/_a011_legacy_evidence.py. Profile: docs/development/qualification/a011-v0x-profile-v1.json. Tests: tests/qualification; CI retains every previous standalone portable gate and uploads the indexed nonfinal A011 pack with if:always.

## Execution Tasks and verification

| Execution Task | Final result / local evidence |
| --- | --- |
| 1 Activation | DONE; lifecycle RED2/GREEN; baseline/full563 |
| 2 Records/schema/classifier | DONE; full607 |
| 3 Frozen profile/provenance | DONE; profile-leaf/type/unknown mutation and shallow/CRLF coverage; full826 |
| 4 Process/evidence adapters | DONE; raw JSON/exit/validator agreement; full862 |
| 5 Artifacts/publication | DONE; nonoverwrite/links/atomic failure coverage; full884 |
| 6 Portable pack | DONE; fresh/repeat/source/finality coverage; full902 |
| 7 Physical pack | DONE; pinned metadata/blocker/failure coverage; full926 |
| 8 Portable CI | DONE; old/new gate topology; full929; exactCI38048466684 artifact audited |
| 9 Fresh candidate | DONE; f360801 full18 gates/94 checks/86 artifacts, retained historical pack |
| 10 Review/repairs/integration | DONE; independent review2 Important, one TDD repair pass; full952; fresh repaired feature and main packs; exact branch/PR/main CI |
| 11 Report/lifecycle/closure/handoff | DONE; lifecycle RED2/GREEN16; repository/ledger37; full95279.42s; closure metadata exactCI38059824196 success; live Issue12 completed; this handoff receives its own exact CI before final session claim |

Per-task observed RED/GREEN, task briefs, BASEs, final logs and exact completion ranges are in progress.md/task-*-final.log. Native task-driver-main.py preserves the original worktree ledger while recording actual main Git identities for operational Tasks10-11. No completed Task was restarted on resume.

Commits after activation base (full history retained):

| Exact commit | Subject |
| --- | --- |
| `c96d3d0318ccb6e23b00b8998a319905fc965efd` | docs(a011): activate approved system qualification |
| `143a0f4b3c8628e06b89aead4d9930a4fb7bee2c` | feat(a011): define strict qualification records and verdicts |
| `254c6fe6ca766c2b6c4321d749230854bba93828` | feat(a011): freeze profile and verify candidate provenance |
| `c74636a8588dd82349a3b85a73cac584f0dc85f4` | feat(a011): normalize existing qualifier evidence |
| `c8f3d9f16de4c3e15e72f654b327e4a84cee3157` | feat(a011): publish validated qualification artifacts |
| `f62cf4924d7942b768c8ae0d1813f94b4ea9c62b` | feat(a011): replay portable system qualification |
| `2ee26f98b0df8e63d49b1f2d301f7ce285a9b9b6` | feat(a011): qualify pinned local physical system |
| `f36080155957e30a0a9ab6be2270a67330a151e0` | ci(a011): retain portable system qualification evidence |
| `ba7b150cba8f4738415745678db5977f898dcde1` | docs(a011): record fresh candidate qualification evidence |
| `e96d71b033212668bc3ce98873903618c9c44bcf` | fix(qualification): validate physical details and partial runtime loss |
| `f83bf1febbb6ac0bdcba3d8bf05dc8d437edc5ac` | Merge A011 ASCA v0.x system qualification (#13) |
| `4053cb42bb50a683965d83bee20cbffb25668f02` | docs(a011): record qualified integration and terminal lifecycle |

## Qualified, reviewed, integration and metadata identities

| Role | Exact SHA | Exact CI / applicability |
| --- | --- | --- |
| Historical qualified candidate | `f36080155957e30a0a9ab6be2270a67330a151e0` | [38048466684](https://github.com/funggier/FlyWireASCA/actions/runs/38048466684) success; prior physical pack only |
| Independent reviewed range head | `ba7b150cba8f4738415745678db5977f898dcde1` | [38048998834](https://github.com/funggier/FlyWireASCA/actions/runs/38048998834) success; reviewed from activation base |
| TDD-repaired qualified feature | `e96d71b033212668bc3ce98873903618c9c44bcf` | [38058426606](https://github.com/funggier/FlyWireASCA/actions/runs/38058426606) success; new real full pack |
| PR trigger head | `e96d71b033212668bc3ce98873903618c9c44bcf` | [38058683663](https://github.com/funggier/FlyWireASCA/actions/runs/38058683663) success; CI binds actual PR checkout HEAD |
| Physically qualified integration/main | `f83bf1febbb6ac0bdcba3d8bf05dc8d437edc5ac` | [38058896880](https://github.com/funggier/FlyWireASCA/actions/runs/38058896880) success; separate new real full pack |
| Closure docs/lifecycle metadata | `4053cb42bb50a683965d83bee20cbffb25668f02` | [38059824196](https://github.com/funggier/FlyWireASCA/actions/runs/38059824196) success; not relabelled physical evidence |
| This handoff metadata | Resolve containing commit using Git | Require latest exact push/main CI after publication; no self-SHA loop |

Feature/integration source trees matched `a97c287539f7d44e765bb534017cb1f834e3d1e6`. Closure changes are documentation and mutable lifecycle tests only. The physically qualified integration is `f83bf1febbb6ac0bdcba3d8bf05dc8d437edc5ac`; later metadata has its own exact CI. A future behavior/profile/qualifier change requires applicable new qualification and cannot reuse these historical pack identities.

## Fresh real physical packs

Repaired feature: `T:\Space\Projects\ProjectsAI\FlyWireASCA-qualification-evidence\a011-e96d71b-reviewed-1791641331086`.

Integration/main: `T:\Space\Projects\ProjectsAI\FlyWireASCA-qualification-evidence\a011-f83bf1f-main-1791641770439`.

Each was invoked as the real full CLI outside pytest, exit0, FULL_SYSTEM/is_final=true/ENGINEERING_QUALIFIED,18 gates/94 frozen checks PASS,86 indexed artifacts independently decoded/hash/raw/source/identity/role audited; errors/blockers empty. Test-only injected packs are not physical evidence.

| Gate | Integration status |
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

| Pack | File | SHA256 |
| --- | --- | --- |
| Repaired feature | artifact-index.json | `daffd0300237d5e07ccb26eeb9b386fde2eb0cf697bbd199d702ef465ffca14c` |
| Repaired feature | qualification.json | `4c831003728604e9efca81ad0d7d5d2e74eec2b4bd7b52e6f5af9ed5c3cf155d` |
| Repaired feature | qualification.md | `76d675ddb7819052db2ffe2f3649cab55349fb1f585c8f4cea42c98a641ece98` |
| Integration/main | artifact-index.json | `0685306d087395c679c165369b0547c4ca610068e54b2972633555c9904509fa` |
| Integration/main | qualification.json | `73491f44d1feb0d1d19b4adb4a20ed5d8684e4cc651d771e11c70afed4a8d6cc` |
| Integration/main | qualification.md | `304e20b8c2f364891d2c47f7470f5ead69378e37ff9ed7e1c04166f9c2f2f908` |

| Pack | Before UTC | After UTC |
| --- | --- | --- |
| Repaired feature | 2026-10-10T14:08:53.988647+00:00 | 2026-10-10T14:10:51.174476+00:00 |
| Integration/main | 2026-10-10T14:16:13.086883+00:00 | 2026-10-10T14:18:11.331635+00:00 |

Raw evidence is under each root: profile.json, source snapshots, runtime/preflight.json, runtime/completion.json and raw/<gate>/ stdout/stderr/process/output/validation records, including independent repeat observations. Manifest/report/index are publication metadata and the raw/profile/source/runtime artifacts are indexed. Existing packs remain preserved; never overwrite them.

Historical f360801 pack: `T:\Space\Projects\ProjectsAI\FlyWireASCA-qualification-evidence\a011-f360801-candidate-61cbe52ea47d4665ab72eaa67739df0b`; manifestSHA256`5b62d61c64bd5168601abcb9d49b0aee7fc21b2d1b9549fbbe5625601f4625d2`. Actual detail was valid; the review gaps did not establish a failed historical replay. It was not reused for repaired/main qualification.

## Exact portable CI evidence

| Exact run | Artifact | Archive SHA256 | Manifest SHA256 |
| --- | --- | --- | --- |
| [38058426606](https://github.com/funggier/FlyWireASCA/actions/runs/38058426606) | 11671998484 | `45323e9e602241e3ad590105b77397ddc878945f3b7206f463927f4a5e252225` | `e75853c42ef73691e7001f6dd227def768ce4241ffe400b8367783fc12601d3a` |
| [38058896880](https://github.com/funggier/FlyWireASCA/actions/runs/38058896880) | 11671649254 | `da3bc5bca90c8e554adc8e258efabbfb1e3cb8e2f7e4d81e706bec955dd76817` | `79d4e348d511ce12ee28b845a90d2d04557fd235b9ec813b882fdc9a214517de` |

Downloaded directories and audits remain under `T:\Space\Projects\ProjectsAI\FlyWireASCA-worktrees\a011-asca-v0x-qualification\.superpowers\sdd\2026-10-10-a011-asca-v0x-qualification\ci`. Both packs: PORTABLE_ONLY/is_final=false/verdict=null,10 gates/34 checks PASS,52 indexed artifacts. Strict raw/hash/coverage/source/finality checks passed. CI is Ollama-free and does not substitute for local physical evidence. Earlier CI38048466684/artifact11667799249 is retained separately in the ledger.

## Live runtime and frozen identities

Read-only runtime verification before handoff: `2026-10-10T14:35:58.934658+00:00`; host `CDQ-P`, `Windows-10-10.0.19045-SP0`, Python `3.14.6`, Ollama `0.32.15`, `http://127.0.0.1:11434`. Issues empty; package `0.1.0.dev0`.

| Identity | Frozen/preserved value |
| --- | --- |
| Terminal tag | `qwen3.5:4b` |
| Terminal digest | `2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd` |
| Embedding tag | `qwen3-embedding:0.6b` |
| Embedding digest | `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d` |
| Embedding / A005 observed dimension | 1024 |
| A005 threshold | `0.5037018224299838` |
| Profile7481-byte SHA256 | `add06f285bf6decc7d492b987d3769dc64db4cb3d0177c8c6586d50ee5f6d46d` |
| Protected67 mode/path/blob SHA256 | `8df49f05fe54de43667ab2f8ef5de2caae9376ffedf2cb8f8d26f0e4abcca6b6` |

| Milestone | Frozen outcome | Fresh evidence role | Fixture fingerprint |
| --- | --- | --- | --- |
| A006 | NOT_SUPPORTED | PHYSICAL_PRIMARY | `e51fea2e58186e94d7affc964509e96d96fc656759677d7dcc073e5b36b91035` |
| A007 | SUPPORTED | PHYSICAL_PRIMARY | `59f95ef115534fe24e59570cb281c0564ab75aadf364f4c26feba0d4078213c9` |
| A008 | SUPPORTED | PORTABLE_PRIMARY | `f52fbd4ab018386ff3cbfb62a68cc44a4b40e54ec4fd9a3b2e885dd2c5663fc6` |
| A009 | SUPPORTED | PORTABLE_PRIMARY + PHYSICAL_SECONDARY | `2f92b5092de346f62879ac2cbb9f96d6de5d6f919e12d0693345c8228b01ab2a` |
| A010 | NOT_SUPPORTED | PORTABLE_PRIMARY + PHYSICAL_SECONDARY | `69d20542cd1e7e5c25a0fb61b9060f622379206b519da3cec7624e00bb6e5d4c` |

| Portable replay | Frozen full semantic SHA256 |
| --- | --- |
| A008 | `4883b4eba174a2edc8c753297e02903c940f0b0fc38a71f80d5b76541b49e7c3` |
| A009 | `5fb0c8b803b0c15888907ca388aa8f705d904351a9f23da43cdf7a285c9052b7` |
| A010 | `8e57b744e96294565551061728ff90b4ddba43b66051237124378f981db185d5` |

A010 retains12 total/9 primary cases; primary counts:

| Count | Frozen value |
| --- | --- |
| asca_cumulative_selected_count | 66 |
| asca_only_success_count | 0 |
| asca_peak_selected_count | 12 |
| asca_procedure_attempt_count | 14 |
| asca_query_count | 28 |
| asca_scored_vector_count | 1984 |
| asca_success_count | 7 |
| dense_cumulative_selected_count | 480 |
| dense_only_success_count | 1 |
| dense_peak_selected_count | 256 |
| dense_procedure_attempt_count | 9 |
| dense_query_count | 27 |
| dense_scored_vector_count | 1440 |
| dense_success_count | 8 |
| primary_case_count | 9 |
| shared_success_count | 7 |

Dense-only sentinel `selective-routing-miss-sentinel`: ASCA_PRIMARY=false / DENSE_EXHAUSTIVE=true. All original ablations are retained. Policies: EVIDENCE_ONLY, SINGLE_BEST, SIGNAL_DRIVEN, CHUNKED, MISMATCH_DRIVEN_RECOVERY; max_procedure_attempts3; hidden_automatic_retry0. Optional top-level note is the only excluded portable semantic key.

## Independent whole-change review and repair

Completed reviewer `/root/a011_whole_change_review_resumed` (gpt-6-astra/high), fresh context, exact `e8f75a862e0cb0d28b7e4efe25a77fa088ad646f..ba7b150cba8f4738415745678db5977f898dcde1`. First review attempt hit usage limit without a result; resumed reviewer completed the single independent review. Critical0 / Important2 / Minor0. Declined to judge: none.

- I1 missing/contradictory A005 benchmark or A009/A010 physical detail could publish18-PASS qualified with injected matching output. Fixed by required actual detail, strict acceptance primitives, unchanged legacy acceptance and metadata/detail consistency; synthetic factories now reflect original physical fixture/CLI shape.
- I2 tags/version succeeded then both /show requests lost transport, inventing null-dimension drift. Fixed by distinguishing unobserved transport-loss measurement from a wrong dimension/malformed reachable response; observed bad digest still dominates absence.

Root retained both Important grades. ONE author TDD pass: RED21 failed/2 passed13.12s -> focused78 passed43.71s -> full952 passed77.72s; architecture/repository/whitespace PASS. Independent focused398 passed66.41s. No second independent review claimed. Fresh repaired-feature and integration physical packs followed the fixes. No cognitive defect/out-of-scope repair was established.

Review artifacts: independent-review.md, review-package.json, review-focus.md, independent-review-reproduce.py, independent-review-reproductions.json, independent-review-full-reproduction.json, independent-review-tests.log and review-regressions-red/green/full logs under the preserved plan workspace. Injected diagnostic packs/reproducers are explicitly test-only and make no model calls.

## Rulings I made — exhaustive and ordered

1. Ruling: The advertised sdd-workspace helper and writing-good-tests reference could not be read; use an equivalent local Python task driver for ignored workspace/briefs/BASE/test logs/completion ledger — preserves the supplied main skill workflow without a new dependency — cost if wrong: weaker bookkeeping, mitigated by exact Git and raw test logs.
2. Ruling: Preserve this plan's ignored execution workspace and worktree through closure instead of deleting evidence automatically — user requires WIP/history/evidence preservation and approved plan forbids automatic cleanup — cost if wrong: local disk use.
3. Task 1: Ruling: full suite exposed two PRE-A011 historical tests still owning mutable CURRENT/ROADMAP, a file omitted from plan Task1 — move their live-state ownership to canonical test_task_ledger while preserving all PRE closure assertions/documents/Issue#11 — cost if wrong: historical resume assertion weakened; mitigated by keeping the exact checked historical resume line and current-state canonical coverage.
4. Task 6: Ruling: child Python commands explicitly use -X utf8 so Windows stdout/file JSON have the required UTF-8 bytes — no workload, model, threshold, acceptance, or adapter timeout changes — cost if wrong: different text encoding behavior; mitigated by existing CLI/payload and fresh real replay verification.
5. Task 6: Ruling: --repo-root must resolve to the checkout executing the CLI — prevents orchestrator code from one candidate qualifying a different checkout — cost if wrong: cross-checkout invocation refused; run the script located in the intended checkout instead.
6. Task 6: Ruling: artifact checker gains a private schema callback, a Task5 file omitted from Task6 file list — fixed P09/H07 prefix validation reuses the same link/hash checks without a synthetic validator gate — cost if wrong: extra private coupling; default publication still enforces complete strict manifest.
7. Task 6: Ruling: accepted partial repeat observations can belong to executed FAIL P08 — preserves valid A008/A009 replays completed before a later repeat fails; never fabricates unexecuted evidence — cost if wrong: consumer may infer complete audit from observation alone; mitigated by explicit P08 FAIL, final FAIL, and independent raw semantic checks.
8. Task 7: Ruling: consume the actual flattened A006/A007 CLI evidence and pass that payload to existing pure validators; repair evidence.py, bridge, and test factories omitted from Task7 file list — live CLI is authoritative, cognitive scripts/fixtures/outcomes untouched — cost if wrong: adapter acceptance mismatch; mitigated by real-CLI-shape RED/GREEN and later fresh physical replay.
9. Task 7: Ruling: factor the fresh portable builder and parameterize final source artifact path in portable.py — one newly executed pack/store can extend through physical replay without importing a prior pack or overwriting source/after.json — cost if wrong: private orchestration coupling; public run_portable contract and fresh full-flow tests retained.
10. Task 7: Ruling: A004 adapter verifies existing six-case/all-pass baseline and original profile name instead of trusting qualified=true plus positive case_count — existing source acceptance is authoritative, no baseline workload or criterion changed — cost if wrong: stricter evidence-shape compatibility; mitigated by original legacy fixtures and fresh physical replay.
11. Task 8: Ruling: tests/qualification becomes an explicit pytest package via __init__.py — full suite exposed an existing root test_ci_contract.py basename collision under prepend import mode; retain both required test files and all assertions — cost if wrong: test import namespace changes; mitigated by focused/full suite on Windows and exact Linux CI.
12. Task 10: Ruling: advertised review-package helper and code-reviewer.md template cannot be read through the skill provider — prepare an exact base/head Git diff review package and supply the available skill requirements, full spec/plan, verbatim Review Focus, evidence and rulings to one fresh most-capable reviewer — cost if wrong: template-specific review checks omitted; mitigated by explicit complete scope/severity/readiness/declined-to-judge requirements and actual source/evidence.
13. Task 11: Ruling: approved Step3 writes terminal DONE before its metadata CI and Step4 live issue completion, while the existing repository gate forbids unchecked engineering acceptance under DONE — preserve the unchanged final report/issue/main closure requirement as an explicit separate publication gate, still unchecked until live completion; mark only verified engineering/boundary acceptance complete and retain explicit OPEN/pending prose — cost if wrong: intermediate DONE may be mistaken for externally closed; mitigated by CURRENT/task/report publication-gate warnings and verified closure before final handoff.

## Deferred minors

None. Declined-to-judge behaviors: none.

## Scope boundaries and operational limitations

- Keep0.1.0.dev0. No automatic0.1.0, tag/release, A012 or FlyWireLLM work.
- No reset/clean/rebase/force-push or WIP/history destruction. Preserve feature branch/worktree, ignored ledger and all real/injected diagnostic evidence.
- No A003-A010 cognitive change, A009/A010 retrieval optimization or fixture/cue/threshold/model/outcome/sentinel retuning inside A011. A real cognitive defect requires a separate explicit repair task.
- Qualification is project-internal for one declared profile/source/runtime observation, not external certification or aggregate intelligence/performance evidence. Local durations are descriptive, not FLOPs/energy/power/general latency claims.
- Frozen-source identity covers67 reviewed original paths; profile anchoring is literal and shallow-safe. Artifact hashes establish recorded integrity; no externally signed attestation or ongoing runtime guarantee is claimed.
- Later runtime/model drift fails closed on requalification. An unobserved dimension after independently confirmed transport loss is BLOCKED; wrong observed identity/malformed evidence FAILS and dominates blockers.

## Next-session checklist / authorized next action

1. Read this file first and the linked final report, CURRENT/ROADMAP/task/matrix; preserve already completed stages.
2. Verify main/worktree cleanliness and exact remote refs without destructive commands. Resolve the handoff-containing SHA with Git log, then check latest exact push/main CI for the actual current HEAD.
3. Fetch Issue11/12 and PR13 live. Expected: both issues CLOSED/COMPLETED, PR merged, A001-A011 DONE; no next milestone is invented.
4. Inspect the pinned runtime read-only if needed; use retained raw packs/audits for qualification assertions. Any source/runtime mismatch is explained before further work.
5. Wait for a new explicit scoped user objective. New creative scope follows conversational design -> approved written spec -> approved plan/method -> issue/worktree/activation -> TDD/evidence/review. No automatic release or optimization follows A011 completion.

Safe read-only Git examples (run in main):

    git status --porcelain=v1 --untracked-files=all
    git rev-parse HEAD
    git ls-remote origin refs/heads/main
    git log -1 --format=%H -- docs/development/reports/ASCA-20261010-full-session-handoff-a011-completed.md

Detailed qualification source/evidence: [final A011 report](ASCA-20261010-A011-v0x-qualification.md). Every future replay uses the script located in the intended checkout, its exact clean HEAD and a new outside-checkout output directory. No prior pack import/reuse can claim fresh full qualification.
