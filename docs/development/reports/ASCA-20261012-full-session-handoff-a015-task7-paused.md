# Full session handoff - A015 Task 7 checkpoint, user-requested pause

Recorded: 2026-10-12, Asia/Bangkok.
Execution is PAUSED at the user's request; A015 remains ACTIVE and is not DONE.
Latest user instruction: find a suitable stopping point and rest for a while.
Resume only after the user asks to continue. Task 8 has not been started.

## Start here on resume

Read this handoff and the required older handoffs, then verify live Git, GitHub
and runtime. Current facts take precedence over old status prose; investigate
contradictions before acting. Read the approved spec/plan and the current
Task 8 brief before implementing. Do not replay completed Tasks 1-7.

Repository: funggier/ProjectASCA (renamed from FlyWireASCA).
Primary checkout: T:\Space\Projects\ProjectsAI\ProjectASCA
Active worktree: T:\Space\Projects\ProjectsAI\ProjectASCA\.superpowers\worktrees\a015-unified-agent-runtime
Branch: research/a015-unified-agent-runtime
Latest implementation commit: 5f527628602309592bb0c8538e6cfc2b18549cac
GitHub upstream readback matches that SHA.
Main: 4ca246df6976c7aa21ad07826017f167f0ee27da
Task 7 exact CI: 38212420311 SUCCESS
CI URL: https://github.com/funggier/ProjectASCA/actions/runs/38212420311
A015 Issue #19 remains open: https://github.com/funggier/ProjectASCA/issues/19
Local tree was clean after Task 7 commit/push, before this documentation checkpoint.
This handoff and the skill draft are recorded in a separate documentation commit.

## Authority and approvals already completed

Approach 3 was selected by the user: a new top-level unified runtime, not a
wrapper around A009 and no rewrite of frozen A009/A011 history.
Conversational design, written specification, implementation plan and Native
execution selection were approved before activation.
Spec: docs/superpowers/specs/2026-10-12-a015-unified-agent-runtime-design.md
Spec commit: cccbf0fc47ca301bef8a6b7ac25398c2e1eb4447
Spec SHA256: ee4ab10cc4827381b494560704692c88de27822586e607ed20416cfbdfdffe91
Plan: docs/superpowers/plans/2026-10-12-a015-unified-agent-runtime.md
Plan approval/main commit: 4ca246df6976c7aa21ad07826017f167f0ee27da
The documents' earlier inactive/review checkpoints are historical; live issue,
current task ledger and activation commit establish current ACTIVE state.
Final integration choice has not been approved. Do not merge into main,
close Issue #19, promote a release or mark A015 DONE at this checkpoint.

## Completed implementation tasks

| Task | Commit | Evidence |
|---|---|---|
| 1 activation/lifecycle ledger | 82994994195720c99e25dc5676690ca4346448bb | full1163 |
| 2 contracts/global control | 3097b2e5bf8e0ad26740f1e61940d9aac6afa1d5 | full1211 |
| 3 broker, transport, token certificate | adf470ec4d59ad6c5f277170e1a5dc410edf239a | focused29/full1240 |
| 4 G2 bilingual workload freeze | 7fc3c0ea901bfe49f9e788065bfc7de3626c0984 | focused12/full1252 |
| 5 trusted goals/semantics | 006ab4353ba1b7fec186fcef390dd9eebf15cbc3 | focused29/full1281 |
| 6 bounded acquisition/context adapters | 4549ee96c5067a22ee85347243f2bb83506d0360 | focused29/full1294 |
| 7 strategy validation/A008 execution | 5f527628602309592bb0c8538e6cfc2b18549cac | focused35/full1312 in107.05s |

Task 7 adds resolver/composer, charged closed-schema validation, unchanged A008
CHUNKED execution through a neutral injected ExecutionPort, fresh attempts
from the same initial state, blocked-versus-executed counters, and observations
checked against the actual ordered capability steps.
A successful validation permits one execution for that exact plan, goal and
context. A second attempt needs another validation; the test helper was fixed
to follow this contract. Goal/context substitution and registered-but-wrong
action observations are rejected.
Duplicate canonical legacy CALL paths are rejected before dispatch because
A008 paths omit CALL-site IDs. If future support is needed, instance-qualify
the adapter compilation; do not edit frozen A008 source.
Both architecture audits passed. A011 preservation and frozen inputs passed.
No primary workload model inference or physical comparison has been run.

## Preserved research and frozen authority

A001-A014 status and historical conclusions remain unchanged. A014 is closed.
A010 does not establish automatic retrieval/computation savings.
A014 frozen workload: Hybrid32/32, Model-only32/32, model calls9 versus32,
with no false/missed activations in that workload. This is not an A015 result.

G2 aggregate: 774bc3352242bee5cb588f499f6597a264c67f612feb518828058dc4c1efa882
G2 GitHub lock blob: 3b20d3c77a6ca63e144f88337eadf8585db5ae97
Frozen folder: fixtures/a015/stage-a-v1/
Exactly32 EN/TH pairs,64 requests,8 families,48 solvable and16 controls.
Three repetitions per variant are required later:192 results/variant,384 total.
Requests/public/oracle/prompts/schemas/profile/certificate/lock are frozen.
Any changed frozen input requires a disclosed new version and retained old evidence.
Largest complete direct prompt upper bound7145 + output1024 =8169 <=8192.
The byte-based certificate is a conservative bound, not actual token usage.

Setup generation correction remains part of history: a mistaken debug_render_only
flag caused one generic non-workload token generation, prompt23/output1.
It is excluded from primary benchmark denominators. Correct _debug_render_only
was subsequently verified without generation. Never claim zero setup calls.

## Live runtime checked at pause

Machine: CDQ-P; Native Windows workspace through LConnect.
Ollama: 0.32.15
Generation: qwen3.5:4b
Digest: 2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd
Embedding: qwen3-embedding:0.6b
Digest: ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d
These tags/digests were reread at pause; no model inference was dispatched.
The Task 7 full-suite managed process exited0 and all streams closed.

## Hard boundaries

Stage A PURE/IN_MEMORY only; configured inference is infrastructure.
Preserve flywire_asca, distribution FlyWireASCA and version0.1.0.dev0.
Do not access or modify FlyWireLLM.
No reset, clean, rebase, force-push, tag movement or release replacement.
v0.1.0 tag object: 0d2b2ebd0882d2b5e950b56e227cb4a0c5de898e
Peeled baseline: fd8d298c38625b2bcfc2073fa3c8f951415a9bb2
A011 profile: add06f285bf6decc7d492b987d3769dc64db4cb3d0177c8c6586d50ee5f6d46d
Protected67-path hash: 8df49f05fe54de43667ab2f8ef5de2caae9376ffedf2cb8f8d26f0e4abcca6b6
Fresh preservation check passed; its claim is historical preservation, not
qualification of the current HEAD as A011/v0.x.

## Next work after user resumes

1. Verify branch/HEAD/upstream/CI/runtime and preserved baselines.
2. Read private progress.md and generate/read Task 8 brief with its new BASE.
3. Task 8: independent non-vacuous completion verifier and rendering.
4. Task 9: FSM, composition factory, public runtime and bounded recovery.
5. Task 10: private oracle, direct one-shot baseline and portable evaluation.
6. Task 11: source-bound physical comparison/offline verifier/additive CI.
7. Task 12: report, whole-branch independent review and concrete integration gate.
Do not infer SUCCEEDED from model claims, A008 completion markers or a plan alone.
Keep false success, bounded failures, evidence/identity/budget failures and
unknown usage visible. Retain negative/MIXED/INCOMPLETE research outcomes.
Continue normal authorized tasks without asking whether to continue at each
ordinary checkpoint, once the user explicitly resumes this paused session.

Private Native execution workspace:
.superpowers/sdd/2026-10-12-a015-unified-agent-runtime/
progress.md, flow.py, task briefs/BASE and task-N-final.log survive on the user's
machine but are Git-ignored. flow.py is the previously documented Native
bookkeeping port because the bundled helper resources were unavailable.
Task 7 done gate recorded the commit range and focused35 pass.
Leave the workspace in place at this pause.

## Separate ChatGPT workflow skill draft

The user requested a reusable thinking/planning/execution style across tasks,
then explicitly requested appropriate subagents. Native remains the main A015
execution method; delegation may support independent work and fresh review.
Draft name: working-from-goals-to-completion
Display name: คิด วางแผน และทำงานจนจบ
Durable draft folder: docs/development/skill-drafts/working-from-goals-to-completion/
Contains SKILL.md, agents/openai.yaml and domain/delegation references.
The draft is separate documentation and does not alter runtime/frozen evidence.

Creator/writing-skills were read. init_skill.py was run and quick_validate.py
passed in the ChatGPT skills workspace. Five fresh no-guidance controls were
manually read: all passed core calculation/authority/gate behavior; no discipline
failure was observed. Repeated evidence/status presentation motivated a positive
integrated-deliverable recipe. Do not invent a failing discipline baseline or
claim a measured improvement from these controls.
One fresh guided repetition completed and was read: core controls passed,
including distinguishing calculation from live-system verification.
Remaining: four guided repetitions, cross-domain/delegation forward test,
review gaps and final validation/deployment.
The user pause supersedes continuing these tests now.
No push to the ChatGPT Skills master branch has occurred; this is a DRAFT,
not a completed or installed skill. The original untracked draft also remains
at /root/.codex/skills/remote-skills/working-from-goals-to-completion in this
ChatGPT execution environment; the GitHub-backed copy is the durable source.
Resume by reading the draft, then complete tests and follow skill-creator's
Work Mode Persistence: stage only that skill, commit and push the current
remote-skills branch. Do not stop at a ZIP or claim installation before push.

Supplementary testing-skills-with-subagents.md was unavailable via skills.read;
the complete loaded writing-skills instructions guided fresh-context raw-artifact
controls and manual inspection. No skill-specific executable scripts are needed.
