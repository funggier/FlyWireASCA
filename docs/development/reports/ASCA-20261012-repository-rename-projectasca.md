# ProjectASCA Repository Rename

Date: 2026-10-12 (Asia/Bangkok)
Scope: repository identity and workspace maintenance; no A015 activation

## Current identity

- GitHub repository: `funggier/ProjectASCA`
- Stable GitHub repository ID: `1410092474`
- Previous repository name: `funggier/FlyWireASCA`
- Primary checkout: `T:\Space\Projects\ProjectsAI\ProjectASCA`
- Previous checkout: `T:\Space\Projects\ProjectsAI\FlyWireASCA`
- Origin: `https://github.com/funggier/ProjectASCA.git`
- Visibility remains public.
- Default branch remains main.

The user explicitly requested this rename during the A015 conversational
architecture design. Repository rename and maintenance are authorized separately
from the A015 architectural design/spec/plan gates.

## Preserved baseline

Before maintenance documentation, local/main and GitHub/main were exactly:

`fd8d298c38625b2bcfc2073fa3c8f951415a9bb2`

The preserved annotated tag `v0.1.0` remains unchanged:

- tag object: `0d2b2ebd0882d2b5e950b56e227cb4a0c5de898e`
- peeled commit: `fd8d298c38625b2bcfc2073fa3c8f951415a9bb2`

Existing release asset names, archive bytes, checksums and historical reports are
retained. Historical occurrences of FlyWireASCA describe the identity at the time
of those experiments; they must not be globally replaced.

## Local workspace repair

An initial folder rename was blocked by directory handles held by the existing
Ollama app, its server and its cmd launcher. Inspection identified the exact
processes and their creation times. The launcher ran only the Ollama app with
`--hide --fast-startup`; Ollama reported no loaded models before maintenance.

The identified idle processes were stopped, the folder was renamed, and Ollama
was restarted with the same app flags from its own installation directory.
The backend returned HTTP 200 afterward and retained:

- Ollama `0.32.15`
- `qwen3.5:4b` digest
  `2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd`
- `qwen3-embedding:0.6b` digest
  `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`

`git worktree repair` updated the three historical linked-worktree .git pointers
to the relocated common repository. Historical worktree/evidence directories
remain at their recorded paths; no worktree content or branch history was reset.

## Frozen identity and architecture boundaries

The existing Python namespace remains `flywire_asca`. Distribution metadata
remains `FlyWireASCA` / `0.1.0.dev0`; the existing repository contract and frozen
source identity remain valid. The user-facing project and repository are now
ProjectASCA.

A new public namespace for A015 is a conversational design proposal, not an
implemented package. No source scaffold, design specification, implementation
plan or A015 task/Issue is created by this maintenance change.

Preserve all A001-A014 historical conclusions and the A011 anchors:

- frozen profile SHA256:
  `add06f285bf6decc7d492b987d3769dc64db4cb3d0177c8c6586d50ee5f6d46d`
- protected paths: 67
- protected mode/path/blob SHA256:
  `8df49f05fe54de43667ab2f8ef5de2caae9376ffedf2cb8f8d26f0e4abcca6b6`

FlyWireLLM remains outside this work.

## Session continuation

Read the A015 direction handoff at:

`docs/development/reports/ASCA-20261011-full-session-handoff-post-a014-a015-unified-agent-runtime-direction.md`

Its old project name/path and pre-release SHA are historical context. Current
Git/GitHub/runtime evidence and this rename record resolve that difference.

A014 remains DONE / Issue #18 completed. A015 remains unactivated and is at the
conversational detailed-design review gate. The approved direction remains
Approach 3, long-term Stage C, first qualification Stage A without external
application/tool side effects.

## Maintenance verification

Fresh local checks after relocation and documentation updates:

- repository/frozen-preservation/documentation tests: 14 passed
- architecture contract audit: PASS
- A011 frozen profile and all 67 protected blobs: PASS
- A014 committed physical evidence verifier: experiment_valid=true
- historical linked-worktree HEADs unchanged and worktrees clean
- v0.1.0 local tag object and peeled commit unchanged
- git diff whitespace check: PASS

These are maintenance checks, not a new A015 implementation qualification.
Exact maintenance commit and its CI are available through the current Git/GitHub
history. Historical baseline/main and tag CI are retained separately.
