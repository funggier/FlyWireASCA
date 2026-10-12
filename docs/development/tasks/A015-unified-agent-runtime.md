# A015 â€” End-to-End Unified Agent Runtime

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

Task 1 complete: commit 82994994195720c99e25dc5676690ca4346448bb.
Focused lifecycle GREEN 19; full suite GREEN 1163 in 102.93s.
Task 2 complete: 3097b2e5bf8e0ad26740f1e61940d9aac6afa1d5.
Full suite 1211 passed; exact feature CI 38201594388 SUCCESS.
Task 3 complete: adf470ec4d59ad6c5f277170e1a5dc410edf239a.
Focused 29 passed; full suite 1240 passed in 105.37s; both audits/guard PASS.
Metadata-only certificate:
f68470eb8b0c5bf9e3ee4d4b40b5bdeb06cc614ba151eec71c4eb84fe7ee2bdf.
Actual GGUF: 256-byte alphabet complete; all 247587 merge products exist;
11935649 metadata bytes independently hashed. Bound is rendered UTF-8 bytes
plus two, not reported token usage.
Task 4 G2 freeze is this commit; its exact SHA is recorded at the next
checkpoint. Canonical aggregate:
774bc3352242bee5cb588f499f6597a264c67f612feb518828058dc4c1efa882.
64 requests /32 EN-TH pairs; private oracle and all public records, schemas,
assembled role templates, A014 router fingerprint, profile and certificate
locked. Full direct prompts all fit: maximum upper bound 7145 plus output
allowance 1024 =8169 <=8192. No workload generation or performance tuning.

Setup correction retained: one generic non-workload token was generated while
testing a mistaken render-only API flag; setup invocation 1, prompt tokens 23,
output tokens 1. Excluded from primary benchmark denominators. Correct flag
_debug_render_only subsequently verified without generation.

## Next Action

Read the G2 commit/readback, then Task 5 trusted semantics and interpretation.
Frozen inputs/templates must remain unchanged; changed inputs require a new
disclosed workload version.

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

- Add values.py and control.py to keep immutable DTOs separate from mutable
  ledger/lifecycle control and prevent import cycles. Public request/result API
  unchanged; cost if wrong: internal import adaptation.

- Before G2, compact shared typed serialization: optional entity display names,
  state defaults by entity kind, entity-bound procedure step IDs and concise
  capability/schema descriptions. Full information remains visible to both
  variants. Context-fit checks were metadata-only; no benchmark tuning.
