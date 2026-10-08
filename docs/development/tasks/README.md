# Development Task Workflow

FlyWireASCA uses task-driven and evidence-driven development.

Allowed task states are:

`PLANNED / ACTIVE / BLOCKED / DONE`

Each substantial task records:

- Goal
- Scope and non-scope
- phases or implementation checkpoints
- Acceptance Criteria
- Evidence
- Current Action
- Next Action
- qualified commit SHA when available

`CURRENT.md` is the canonical resume pointer for the active task. A task is
not DONE merely because code exists.

When documentation disagrees with live state, **Git/GitHub/runtime** is the
authoritative source and stale prose must be corrected rather than trusted.

Long or interrupted sessions should add a handoff under
`docs/development/reports/` recording branch, HEAD, worktree status,
synchronization, running processes, evidence, unresolved failures, current
action, next action, and do-not-do constraints.
