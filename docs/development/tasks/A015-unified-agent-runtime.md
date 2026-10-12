# A015 — End-to-End Unified Agent Runtime

Status: ACTIVE
GitHub Issue: #19
Execution method: Native
Branch: research/a015-unified-agent-runtime
Activation base: 4ca246df6976c7aa21ad07826017f167f0ee27da
Approved on: 2026-10-12 (Asia/Bangkok)

## Goal

Approach 3: create project_asca.agent_runtime as a new top-level Stage A
lifecycle receiving ordinary English/Thai text and reaching a verified internal
terminal result without caller routing/procedure/policy/gold controls.

## Scope

Stage A pure/in-memory interpretation, acquisition, context, strategy, execution,
observation, independent completion and bounded recovery. Future Stage B/C
capability/authorization/effect seams only; no real external effects or learned
procedure persistence. A009 is not the new orchestration center.

## Acceptance Criteria

- Approved design/plan and Native execution gates observed.
- Freeze 64 bilingual requests (32 pairs), public data/private oracle,
  prompts/schemas/profile and context-fit certificate before semantic tuning.
- Shared mechanical execution/verifier with direct one-shot pinned qwen3.5:4b.
- Portable control tests and source-bound three-repetition physical comparison:
  192 results/variant, 384 total; retain negative/mixed/incomplete evidence.
- Preserve A001-A014 history, A011 67-path guard, v0.1.0 and FlyWireLLM boundary.
- Exact feature/main CI, whole-branch independent review and authorized
  integration before DONE/Issue closure.

## Evidence

Design: docs/superpowers/specs/2026-10-12-a015-unified-agent-runtime-design.md
Approved design commit: cccbf0fc47ca301bef8a6b7ac25398c2e1eb4447
Plan: docs/superpowers/plans/2026-10-12-a015-unified-agent-runtime.md
Approved plan commit: 4ca246df6976c7aa21ad07826017f167f0ee27da
Isolated baseline: 1162 passed in 105.32s; repository qualification/audit PASS.
Exact activation-base CI: 38178491835 SUCCESS.
A011 profile: add06f285bf6decc7d492b987d3769dc64db4cb3d0177c8c6586d50ee5f6d46d
Protected blobs: 8df49f05fe54de43667ab2f8ef5de2caae9376ffedf2cb8f8d26f0e4abcca6b6
Release tag object: 0d2b2ebd0882d2b5e950b56e227cb4a0c5de898e
Release baseline: fd8d298c38625b2bcfc2073fa3c8f951415a9bb2
Ollama 0.32.15; generation/embedding digests match approved spec.

## Current Action

Task 1 activation: lifecycle tests observed RED (3 missing-A015 failures,
16 passed), then coherent ACTIVE metadata written. Final verification pending.
No new runtime source or frozen workload has been created.

## Next Action

Finish Task 1 GREEN/commit, then Task 2 foundations and Task 3 preflight;
Task 4 freeze precedes interpreter/ranking/controller implementation.

## Recovery and Resume

Private execution ledger:
.superpowers/sdd/2026-10-12-a015-unified-agent-runtime/progress.md
Read actual Git commits, per-task brief/BASE/logs and live Issue/runtime before
resuming. Task complete requires tests and ledger evidence, not a prose flag.
Do not reset/clean/rebase/force-push. Do not modify A011-protected source or
v0.1.0 tag/assets. FlyWireLLM is outside this work.
No release/version promotion, Stage B/C or another milestone auto-activation.

## Execution Rulings

- Use the existing ignored .superpowers/worktrees path through native LConnect
  rather than altering shared main for an ignore entry. Cost if wrong: relocate
  the linked worktree.
- Bundled execution-helper files and writing-good-tests.md were unavailable via
  skills.read. Use a Windows-native Python bookkeeping port retaining briefs,
  BASE, logs and test-gated completion; follow the loaded TDD principles.
  Cost if wrong: repair bookkeeping without changing product behavior.
- Existing setuptools/pytest environment needs no Poetry installation.
  Cost if wrong: install only a verified missing development dependency.
