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
- qualified evidence references when available

`CURRENT.md` is the canonical resume pointer for the **current task state**.
The current task may be PLANNED, ACTIVE, or BLOCKED. A PRE-* maintenance gate
may be current without becoming an A-numbered research-roadmap row when its own
maintenance task document exists and records the same state.

A task is not DONE merely because code exists.

When documentation disagrees with live state, **Git/GitHub/runtime** is the
authoritative source and stale prose must be corrected rather than trusted.

## Evidence roles

### Activation base

The clean main commit from which a task's implementation branch/worktree starts.

### Qualified behavior SHA

The commit whose implementation behavior, frozen evidence, tests, and required
qualifiers have passed the relevant qualification gate.

A later behavior-preserving documentation commit does not automatically replace
the qualified behavior SHA.

### Reviewed behavior SHA

The qualified behavior commit after Critical/Important review findings affecting
behavior or evidence validity are resolved.

### Integration SHA

The main commit containing the reviewed behavior. Under fast-forward
integration it may be identical to the reviewed behavior SHA.

### Repository closure state

The live Git/GitHub/task state showing that required evidence is integrated,
required exact CI is GREEN, issue state is closed/completed where applicable,
CURRENT/ROADMAP are coherent, and main is clean/synchronized.

Repository closure state does not require a Markdown file to contain the SHA of
the commit that contains that same Markdown file.

### Closure metadata commit

A documentation/test-only commit that records closure facts after behavior
qualification. It may receive exact CI, but it does not automatically become a
new qualified behavior SHA when behavior is unchanged.

This terminology avoids self-referential evidence loops.

## Local commit hygiene

Before committing a task boundary:

1. run the focused/full tests required by that task;
2. stage only the intended files;
3. run `git diff --cached --check` so newly added files are included in the
   whitespace gate;
4. inspect staged file names before committing.

A pre-staging `git diff --check` is still useful while editing, but it does not
cover untracked files. Exact CI remains the final committed-diff check.

## Handoffs

Long or interrupted sessions should add a handoff under
`docs/development/reports/` recording branch, HEAD, worktree status,
synchronization, running processes, evidence, unresolved failures, current
action, next action, and do-not-do constraints.