# PRE-A011 — Architecture & Process Consistency Stabilization Design

Date: 2026-10-10
Repository: `funggier/FlyWireASCA`
Gate: PRE-A011 — Architecture & Process Consistency Stabilization
Research milestone status: A011 remains PLANNED
A011 GitHub issue at design time: not created
PRE-A011 GitHub issue at design time: not created
Design status: APPROVED IN CHAT; WRITTEN SPEC PENDING USER REVIEW

## 1. Purpose

PRE-A011 is a maintenance and qualification-readiness gate between the completed
A010 research milestone and the planned A011 ASCA v0.x Qualification.

Its purpose is to make the repository's architecture description, task
lifecycle, qualification topology, CI contract, and evidence terminology
internally consistent before A011 evaluates the architecture as a whole.

PRE-A011 does **not** attempt to improve the A010 research result and does not
change any cognitive mechanism. It is successful when A011 can begin from a
repository whose current architecture, historical outcomes, portable gates,
physical gates, and lifecycle state are explicit, machine-checkable where
practical, and free of known contradictory process state.

## 2. Authoritative starting point

At design time, live state is authoritative and was observed as:

- branch: `main`;
- HEAD: `899c81d3567a58fb7ebcdac7480f4656c915db2e`;
- upstream: `origin/main`;
- ahead/behind: `0/0`;
- worktree: clean;
- full portable test suite: `531 passed`;
- architecture contract audit: PASS;
- repository qualification: PASS;
- A003 portable qualification: PASS;
- A008 portable qualification: PASS;
- A009 portable qualification: PASS with historical outcome `SUPPORTED`;
- A010 portable qualification: PASS with historical outcome
  `NOT_SUPPORTED`;
- GitHub Issues #1 through #10: closed as `completed`;
- A011: PLANNED with no GitHub issue.

Fresh local physical probes at design time also confirmed:

- A004 `qwen3.5:4b` physical baseline: qualified;
- A005 `qwen3-embedding:0.6b` physical vector-memory qualification: valid;
- A006 physical outcome: `NOT_SUPPORTED`;
- A007 physical outcome: `SUPPORTED`;
- A009 physical integration: valid with portable outcome `SUPPORTED`;
- A010 physical comparison: valid with portable outcome `NOT_SUPPORTED`.

These observations are baseline evidence only. PRE-A011 must rerun the required
gates after its changes.

## 3. Why this gate is needed

A001-A010 were developed incrementally and are individually evidence-rich, but
the repository now contains several cross-milestone consistency debts that
would make an architecture-wide A011 qualification harder to interpret.

The audit identified five blocking process/architecture-documentation issues and
two non-blocking code-organization debts.

### 3.1 Historical initial architecture design is easy to misread as current

`docs/superpowers/specs/2026-10-08-asca-architecture-design.md` still says
`DRAFT FOR USER REVIEW` and contains the pre-A004-insertion roadmap where the
then-planned A004-A010 milestones have different meanings from the actual
A004-A011 roadmap.

The repository does contain the correct migration record at:

`docs/development/roadmap-migrations/A004-qwen-insertion.md`

but the current architecture is not summarized in one canonical pre-A011
snapshot.

### 3.2 Historical milestone tests depend on mutable live-state documents

Completed milestone test files, especially A008/A009/A010 ledgers, read
`CURRENT.md` and/or `ROADMAP.md`. This makes old milestone tests fail when a
new milestone legitimately becomes current.

A010 closure exposed the failure mode directly: a documentation state update
made a stale live-state assertion fail even though A010 cognitive behavior and
qualification evidence had not changed.

Historical evidence tests should be immutable with respect to later task
activation. Current-state tests should be centralized.

### 3.3 Repository qualification does not check enough lifecycle coherence

The current repository qualifier checks core files, the FlyWireLLM boundary,
and machine-local paths. It does not validate task/roadmap consistency.

Consequently A009 is `DONE` while still containing the stale evidence sentence:

> final evidence commit exact-main CI and Issue #9 closure remain pending.

That is contradictory lifecycle prose which should have been caught before
A010 started.

### 3.4 Architecture dependency direction is good but not enforced

The current source dependency graph is acyclic and has a sensible direction:

```text
contracts
  |
  +--> model
  +--> embedding --> vector_memory --> selective_activation
  |                                      |
  +--> familiarity                       v
  +--> procedural_memory           uncertainty_expansion
                  \                    /
                   \                  /
                    +--> integrated_loop
                              |
                              v
                     baseline_comparison
```

The exact graph has no cross-package cycle at design time, but the architecture
audit does not currently prevent a future lower-level package from importing a
higher-level package.

A011 should start with this layering explicitly frozen as a qualification input.

### 3.5 Qualification topology is correct but distributed

CI intentionally runs portable gates only. A004-A007 physical qualifiers depend
on local Ollama and therefore must remain local-only. A009/A010 each have both a
portable gate and a separate local physical gate.

This behavior is correct, but it is represented indirectly across workflow YAML,
individual CLI scripts, milestone tests, and reports. There is no single
qualification matrix explaining:

- which gate is portable;
- which gate is physical;
- which gates belong in CI;
- which local model/digest is required;
- which historical research outcome must be preserved;
- whether a negative research outcome is a valid successful qualification.

A011 should not have to reconstruct this topology ad hoc.

### 3.6 Evidence terminology can create self-referential closure loops

The repository sometimes uses terms such as "final-main evidence SHA" and
"closure SHA" without clearly distinguishing behavior qualification from later
documentation-only closure commits.

A commit cannot record its own SHA in its content. Requiring every closure
metadata commit to name itself would create an infinite sequence of new commits.

The process therefore needs explicit evidence roles rather than an implicit
"latest commit is the qualified behavior" assumption.

### 3.7 Non-blocking organization debt

Two code-organization observations are real but are not PRE-A011 blockers:

- benchmark modules are large, including A009/A010 benchmark files;
- model and embedding Ollama adapters contain structurally similar JSON/HTTP
  transport and validation helpers.

PRE-A011 must not refactor these solely for aesthetics. They are deferred unless
a concrete correctness defect appears.

## 4. Selected approach

Three stabilization approaches were considered.

### Approach A — Documentation-only cleanup

Repair stale prose and add an architecture summary.

Advantages:

- smallest diff;
- low regression risk.

Rejected because it would not address the root causes of stale task assertions,
weak lifecycle qualification, or unenforced package layering.

### Approach B — Full pre-A011 refactor

Refactor large benchmark modules, unify Ollama transports, optimize A009/A010
retrieval, and reorganize task/qualification infrastructure.

Rejected because it mixes process stabilization with cognitive/runtime changes
and would invalidate the clean interpretation of A001-A010 evidence immediately
before A011.

### Approach C — Process hardening with cognitive source freeze

Selected.

PRE-A011 will:

1. create a canonical current architecture snapshot;
2. preserve the historical initial design while clearly marking its relationship
   to the migrated roadmap;
3. centralize mutable current-task/roadmap assertions;
4. strengthen repository lifecycle qualification;
5. enforce the current acyclic package dependency direction;
6. create a canonical qualification matrix;
7. clarify evidence roles to eliminate self-referential closure expectations;
8. repair known stale documentation;
9. rerun portable and physical evidence gates;
10. prove that cognitive source code did not change.

## 5. Hard no-behavior-change boundary

PRE-A011 must not modify files under:

`src/flywire_asca/`

This includes:

- contracts;
- model adapter behavior;
- embedding adapter behavior;
- familiarity;
- vector memory;
- selective activation;
- uncertainty expansion;
- procedural memory;
- integrated cognitive loop;
- A010 baseline comparison behavior.

The final review must verify that:

```text
git diff <activation-base>..HEAD -- src/flywire_asca
```

is empty.

If PRE-A011 discovers a cognitive/runtime defect that truly requires source
changes, that defect is recorded separately and PRE-A011 does not silently
absorb the behavior change.

## 6. Historical research outcomes are immutable inputs

PRE-A011 preserves exactly:

- A006: `NOT_SUPPORTED`;
- A007: `SUPPORTED`;
- A008: `SUPPORTED`;
- A009: `SUPPORTED`;
- A010: `NOT_SUPPORTED`.

It also preserves all frozen fixtures, fingerprints, thresholds, model tags,
model digests, case IDs, selectors, expansion policies, procedure modes, and
primary classifiers established by A003-A010.

No benchmark case may be changed to make A010 more favorable to ASCA.

## 7. Canonical pre-A011 architecture snapshot

Create:

`docs/architecture/ASCA-PRE-A011-SNAPSHOT.md`

This becomes the architecture-wide qualification input that A011 should read
before creating its own design.

The snapshot records:

### 7.1 Current implemented components

- A002 versioned contracts;
- A003 exact familiarity index;
- A004 generic model adapter and pinned local Qwen baseline;
- A005 semantic vector + metadata retrieval;
- A006 bounded working-set selection with `SINGLE_BEST` as the retained
  primary selector;
- A007 signal-driven structural expansion;
- A008 hierarchical CHUNKED procedural memory with deterministic simulation;
- A009 bounded integrated cognitive loop with mismatch-driven outer recovery;
- A010 dense/non-selective comparison harness.

### 7.2 Current dependency direction

The snapshot documents the allowed cross-package dependency graph and states
that it is acyclic.

### 7.3 Implemented versus deferred initial-design concepts

The snapshot explicitly records that the initial architecture design was a
research direction, not a promise that every subsystem would be implemented in
the first cycle.

It must distinguish:

Implemented:

- typed contracts;
- exact familiarity;
- semantic vector retrieval;
- bounded selective activation;
- structural uncertainty/expansion;
- reusable procedural chunks;
- integrated recovery loop;
- model adapter boundary;
- controlled dense baseline comparison.

Not implemented or intentionally deferred:

- typed associative graph traversal;
- persistent graph database;
- learned/neural familiarity;
- automatic memory consolidation;
- autonomous learning/self-modification;
- real OS/API/LConnect/BConnect action execution;
- external knowledge/tool retrieval in the cognitive loop;
- robotics/perception stack;
- hardware selective neural compute;
- general FLOP/energy superiority claims.

### 7.4 Research outcome summary

The snapshot records the exact A006-A010 outcomes and the distinction between:

- engineering qualification success; and
- research hypothesis support.

In particular, A010 is an engineering-successful milestone whose primary
research hypothesis is `NOT_SUPPORTED`.

### 7.5 Known evidence-driven architectural implications

The snapshot may state only implications justified by frozen evidence:

- familiarity remains evidence-only, not truth/routing authority;
- A006 selective convergence is not promoted;
- A007 structural expansion remains useful on its frozen workload;
- A008 CHUNKED procedure representation remains the primary qualified mode;
- A009 mismatch-driven recovery remains bounded and supported on its fixture;
- A010 shows substantially smaller selected working-state counts for ASCA but
  does not support the declared system-level retrieval-work hypothesis because
  ASCA does not beat dense on all required dimensions and has a dense-only
  success.

It must not turn these controlled-fixture results into general claims.

## 8. Preserve the original architecture design as historical evidence

Do not rewrite or renumber the body of:

`docs/superpowers/specs/2026-10-08-asca-architecture-design.md`

Instead add a small archival notice near the top stating:

- this file is the original initial design artifact;
- its original milestone numbering predates the A004 model-adapter insertion;
- current milestone numbering is defined by
  `docs/development/roadmap-migrations/A004-qwen-insertion.md`;
- current implemented architecture is summarized by
  `docs/architecture/ASCA-PRE-A011-SNAPSHOT.md`;
- the historical body is retained for provenance.

The notice must not silently rewrite the original design's meaning.

## 9. Task-ledger test ownership

Mutable repository state must have one test owner.

### 9.1 Historical milestone tests

Files such as:

- `test_a004_task_ledger.py`;
- `test_a005_task_ledger.py`;
- ...
- `test_a010_task_ledger.py`

should validate only evidence that belongs to the historical milestone itself,
such as:

- task status recorded in that task file;
- issue identity/closure when historical;
- frozen outcome;
- exact historical evidence SHA/CI where recorded;
- migration artifact specific to that milestone;
- milestone-specific report content.

They must not assert which task is currently active/planned at repository HEAD.

They also should not assert the current ROADMAP status of unrelated future
milestones.

### 9.2 Current-state tests

`tests/test_task_ledger.py` becomes the canonical owner of mutable task
lifecycle state.

It should validate:

- the current pointer exists;
- current task ID exists exactly once in ROADMAP;
- current status matches ROADMAP;
- A001-A010 are DONE;
- A011 is PLANNED before activation;
- A011 has no GitHub issue recorded before activation;
- no duplicate task IDs exist;
- roadmap ordering is monotonic and unique;
- historical task files do not need edits merely because CURRENT advances.

This separation makes milestone completion evidence stable.

## 10. Stronger repository lifecycle qualification

Extend `scripts/qualify_repository.py` without adding runtime dependencies.

The qualifier should parse the repository's own text files and fail closed on
structural lifecycle errors.

Required checks:

### 10.1 ROADMAP structure

- task IDs are unique;
- task IDs are ordered monotonically;
- statuses are in `PLANNED / ACTIVE / BLOCKED / DONE`;
- every A001-A010 task row has a corresponding task document;
- A011 may be PLANNED without a task document until activation if that is the
  documented workflow.

### 10.2 CURRENT/ROADMAP coherence

- CURRENT task ID exists in ROADMAP;
- CURRENT status equals ROADMAP status;
- before A011 activation, CURRENT may legitimately point at A011/PLANNED;
- a PLANNED current task must not record a guessed numeric GitHub issue;
- an ACTIVE research task must have a numeric GitHub issue in its task file once
  activated under the project workflow.

### 10.3 Completed task hygiene

For every task document whose top-level status is DONE:

- no unchecked acceptance checkbox remains;
- required task sections remain present;
- task filename ID matches document heading ID;
- contradictory current-lifecycle markers known to mean unfinished work are
  rejected in the final-current-action area.

The qualifier should avoid naive global rejection of the word "pending" inside
historical explanations. It should validate the task's structured final state,
not ban ordinary English.

### 10.4 Local Markdown references

Relative Markdown links within repository documentation must resolve when they
point to repository files.

External URLs are not fetched by this qualifier.

### 10.5 Whitespace

Repository-controlled current docs/scripts/tests touched by PRE-A011 must pass
`git diff --check`. Existing CI continues to enforce commit-level whitespace.

## 11. Architecture dependency audit

Extend `scripts/audit_architecture_contract.py` to validate current package
layering.

Allowed direct package dependencies at PRE-A011 are:

```text
contracts              -> {}
model                  -> {contracts}
embedding              -> {contracts}
familiarity            -> {contracts}
procedural_memory      -> {contracts}
vector_memory          -> {contracts, embedding}
selective_activation   -> {contracts, vector_memory}
uncertainty_expansion  -> {contracts, selective_activation}
integrated_loop        -> {
    contracts,
    embedding,
    familiarity,
    model,
    procedural_memory,
    selective_activation,
    uncertainty_expansion,
    vector_memory,
}
baseline_comparison    -> {
    contracts,
    embedding,
    familiarity,
    integrated_loop,
    model,
    procedural_memory,
    selective_activation,
    uncertainty_expansion,
    vector_memory,
}
```

The audit must:

- parse imports using Python AST;
- reject an undeclared cross-package dependency;
- reject a cross-package cycle;
- continue rejecting FlyWireLLM imports;
- remain independent of optional third-party packages;
- ignore intra-package imports.

The allowed graph is an explicit pre-A011 architecture contract. A future
milestone may change it deliberately with design evidence; accidental drift
must fail CI.

## 12. Qualification matrix

Create:

`docs/development/QUALIFICATION-MATRIX.md`

The matrix is the single human-readable map from milestone to qualification
type.

It must record at minimum:

| Milestone | Portable CI gate | Local physical gate | Frozen outcome role |
| --- | --- | --- | --- |
| A003 | familiarity qualifier | none required | engineering benchmark |
| A004 | unit/fake transport coverage | Qwen model qualifier | physical baseline |
| A005 | unit/portable vector tests | vector-memory qualifier | physical retrieval |
| A006 | unit/portable selector tests | selective-activation qualifier | `NOT_SUPPORTED` |
| A007 | unit/portable expansion tests | expansion qualifier | `SUPPORTED` |
| A008 | procedural qualifier | none required | `SUPPORTED` |
| A009 | integrated-loop qualifier | integrated physical qualifier | `SUPPORTED` |
| A010 | baseline-comparison qualifier | A010 physical qualifier | `NOT_SUPPORTED` |

The matrix also records pinned local model identities and claims boundaries.

It must clearly state that:

- physical qualifiers are local-only and intentionally absent from GitHub CI;
- a valid `NOT_SUPPORTED` outcome can still be a passing qualification;
- physical evidence is secondary when the milestone defines a portable primary
  outcome.

## 13. Portable CI contract

PRE-A011 does not add Ollama to GitHub Actions.

The CI workflow must remain network/model independent after package install.

The portable CI gate should make the intended coverage explicit:

- full pytest;
- architecture audit;
- repository lifecycle qualification;
- A003 familiarity qualification;
- A008 procedural-memory qualification;
- A009 integrated-loop qualification;
- A010 baseline-comparison qualification;
- whitespace check.

A004-A007 physical scripts remain absent from CI by design.

The CI contract tests must cross-check the qualification matrix so the reason
for each omission is explicit rather than accidental.

A separate portable-orchestrator script is optional. PRE-A011 should add one
only if it materially simplifies the contract without duplicating qualifier
logic. The default design is to keep existing individual portable commands and
make the matrix/tests authoritative, avoiding unnecessary orchestration code.

## 14. Evidence role terminology

Update the task workflow documentation to define these terms.

### 14.1 Activation base

The clean main commit from which a task's implementation branch/worktree starts.

### 14.2 Qualified behavior SHA

The commit whose implementation behavior, frozen evidence, tests, and required
qualifiers have passed the relevant gate.

For behavior-preserving documentation commits after that point, this SHA does
not move merely because HEAD moves.

### 14.3 Reviewed behavior SHA

The behavior SHA after Critical/Important review findings affecting behavior or
evidence validity are resolved.

If review changes only prose with no qualification semantics, the behavior SHA
need not be redefined.

### 14.4 Integration SHA

The main commit containing the reviewed behavior. Under fast-forward
integration, it may equal the reviewed behavior SHA.

### 14.5 Repository closure state

The live Git/GitHub/task state indicating that:

- required evidence is integrated;
- required exact CI gates are green;
- issue state is closed/completed where applicable;
- CURRENT/ROADMAP are coherent;
- main is clean and synchronized.

A repository closure state does **not** require a Markdown file to contain the
SHA of the commit that contains that same Markdown file.

### 14.6 Closure metadata commit

A docs/test-only commit that records closure facts after behavior
qualification.

It may receive exact CI, but it does not automatically become a new
"qualified behavior SHA" when behavior is unchanged.

This terminology removes the self-referential evidence loop.

## 15. Known stale documentation repairs

PRE-A011 must repair at least:

### A009 task ledger

Remove or reframe the stale line saying final evidence CI and Issue #9 closure
remain pending.

Preserve the historical intermediate integration evidence, but make the final
DONE state unambiguous.

### A010 physical evidence Markdown formatting

Repair the previously deferred formatting-only issue where bullet rows appear
inside the physical-evidence table.

No values or research conclusions may change.

### Task workflow README

Update `docs/development/tasks/README.md` so `CURRENT.md` is described as
the canonical resume pointer for the current task state, which may be PLANNED,
ACTIVE, or BLOCKED, rather than only "the active task."

## 16. PRE-A011 task lifecycle

PRE-A011 is a maintenance gate, not a new A-numbered research milestone.

After the written spec and implementation plan are approved:

- create a GitHub issue titled
  `PRE-A011 — Architecture & Process Consistency Stabilization`;
- create
  `docs/development/tasks/PRE-A011-architecture-process-stabilization.md`;
- set `CURRENT.md` to PRE-A011 / ACTIVE while work is in progress;
- keep ROADMAP research milestones unchanged:
  - A001-A010 DONE;
  - A011 PLANNED;
- do not create the A011 GitHub issue;
- create branch
  `maintenance/pre-a011-architecture-process-stabilization`;
- use an isolated worktree;
- record activation base and exact activation-base CI.

On closure:

- PRE-A011 task becomes DONE;
- PRE-A011 GitHub issue closes as completed;
- CURRENT returns to A011 / PLANNED / no issue;
- ROADMAP remains A001-A010 DONE and A011 PLANNED.

## 17. TDD requirements

All behavior of repository/audit/test infrastructure must follow RED -> GREEN.

Examples:

- write a repository-qualifier test that fails on CURRENT/ROADMAP mismatch
  before implementing the check;
- write an architecture-audit test that fails on a forbidden reverse import
  before adding dependency validation;
- first demonstrate that historical milestone tests fail when CURRENT advances
  under the old coupling, then remove that coupling and centralize the current
  assertion;
- write qualification-matrix/CI contract tests before changing workflow prose or
  enforcement.

Documentation-only corrections do not require synthetic failing unit tests, but
they must be covered by the repository lifecycle qualifier where appropriate.

## 18. Baseline and final verification

### 18.1 Portable baseline

Before implementation:

- full pytest;
- architecture audit;
- repository qualifier;
- A003 qualifier;
- A008 qualifier;
- A009 qualifier;
- A010 qualifier.

### 18.2 Physical baseline/final local gate

When the pinned local runtimes are available:

- A004 Qwen qualifier;
- A005 vector-memory qualifier;
- A006 selective-activation qualifier;
- A007 uncertainty-expansion qualifier;
- A009 integrated-loop physical qualifier with portable outcome
  `SUPPORTED`;
- A010 physical qualifier with portable outcome `NOT_SUPPORTED`.

A physical gate failure caused by unavailable/mismatched local runtime is
reported honestly and does not get disguised as a portable result.

### 18.3 Final source-freeze proof

Final review must show no diff under `src/flywire_asca/` from the activation
base.

### 18.4 Final repository gate

Require:

- full pytest PASS;
- architecture audit PASS;
- repository qualifier PASS;
- portable milestone qualifiers PASS;
- physical local qualification PASS when prerequisites remain available;
- `git diff --check` PASS;
- exact feature-branch CI PASS;
- whole-change review with all Critical/Important findings resolved;
- integration to main without history rewriting;
- exact main CI PASS;
- clean/synchronized main;
- PRE-A011 issue closed completed;
- A011 still PLANNED with no issue.

## 19. Review requirements

PRE-A011 requires a whole-change review before main integration.

Review severity:

- Critical: data/history corruption, changed research outcome, cognitive source
  change, broken qualification validity;
- Important: lifecycle/audit hole that can allow contradictory state, missing
  CI coverage, false claims, evidence-role ambiguity;
- Minor: formatting or naming improvements with no validity effect.

If no independent reviewer/subagent is available, record that the review is an
author self-review and do not describe it as independent peer review.

## 20. Claims boundary

PRE-A011 may claim only process/engineering properties demonstrated by its
checks, such as:

- package dependency graph is acyclic under the declared contract;
- task lifecycle files are structurally coherent;
- portable qualification topology is explicit;
- local physical qualifiers passed on the observed runtime;
- historical research outcomes were preserved;
- cognitive source code was not changed.

PRE-A011 must not claim:

- that ASCA is now more efficient because process infrastructure improved;
- that A010 changed from `NOT_SUPPORTED`;
- lower FLOPs/energy/power;
- general latency superiority;
- general superiority to dense LLMs;
- biological fidelity;
- AGI, consciousness, or production safety.

## 21. Deferred code-organization debt

The following are explicitly deferred beyond PRE-A011 unless a correctness bug
requires them:

- shared Ollama transport abstraction between model and embedding packages;
- decomposition of large benchmark modules;
- generic benchmark framework unification;
- retrieval caching/incremental-scope optimization;
- real Action/Tool Adapter;
- associative graph database/traversal;
- learned familiarity;
- memory consolidation.

The retrieval caching/incremental-scope item is especially important: A010
showed a real retrieval-work weakness. Optimizing it now would be a new research
hypothesis after observing A010 and therefore must not be hidden inside process
cleanup.

## 22. Files expected to change

Expected documentation changes include:

- new
  `docs/architecture/ASCA-PRE-A011-SNAPSHOT.md`;
- new
  `docs/development/QUALIFICATION-MATRIX.md`;
- new PRE-A011 task/report after activation;
- small archival notice in the original architecture design;
- task workflow README;
- A009 stale lifecycle sentence;
- A010 formatting-only repair;
- CURRENT during activation and closure.

Expected process/test changes include:

- `scripts/qualify_repository.py`;
- `scripts/audit_architecture_contract.py`;
- `tests/test_repository_qualification.py`;
- `tests/test_architecture_audit.py`;
- `tests/test_task_ledger.py`;
- completed milestone task-ledger tests that currently own mutable CURRENT or
  ROADMAP assertions;
- `tests/test_ci_contract.py`;
- CI workflow only if needed to align wording/coverage with the explicit matrix.

Not expected to change:

- any file under `src/flywire_asca/`;
- frozen research benchmark fixtures/classifiers;
- A011 research implementation, because A011 has not started.

## 23. Migration safety

PRE-A011 must not reset, clean, rebase, or force-push the repository.

It must preserve:

- existing tags/releases;
- historical issues;
- historical evidence SHAs;
- remote A009/A010 research branches already intentionally retained;
- roadmap migration history;
- FlyWireLLM state.

No completed milestone is renumbered.

## 24. Acceptance criteria

PRE-A011 is complete only when all are true:

- [ ] Written current architecture snapshot exists and matches live A001-A010
  implementation/outcomes.
- [ ] Historical initial design is clearly marked as historical without
  rewriting its original roadmap body.
- [ ] Mutable CURRENT/ROADMAP assertions have one canonical test owner.
- [ ] Historical milestone tests no longer require edits when CURRENT advances.
- [ ] Repository qualifier rejects CURRENT/ROADMAP mismatch.
- [ ] Repository qualifier rejects duplicate/malformed task lifecycle state.
- [ ] DONE-task acceptance hygiene is validated.
- [ ] A009 stale pending closure sentence is repaired.
- [ ] A010 deferred Markdown formatting issue is repaired without changing
  evidence.
- [ ] Architecture audit rejects forbidden package dependency drift.
- [ ] Architecture audit rejects cross-package cycles.
- [ ] Qualification matrix documents portable/physical topology and frozen
  outcomes.
- [ ] CI remains Ollama-free and portable-only.
- [ ] Evidence role terminology eliminates the self-referential closure
  requirement.
- [ ] Full portable regression/qualification gates pass.
- [ ] Local physical A004/A005/A006/A007/A009/A010 gates pass when pinned
  prerequisites are available.
- [ ] No file under `src/flywire_asca/` changes from activation base.
- [ ] Historical outcomes remain A006 `NOT_SUPPORTED`, A007 `SUPPORTED`,
  A008 `SUPPORTED`, A009 `SUPPORTED`, A010 `NOT_SUPPORTED`.
- [ ] FlyWireLLM remains untouched.
- [ ] Exact branch CI passes.
- [ ] Whole-change Critical/Important review findings are resolved.
- [ ] Main integration and exact main CI pass.
- [ ] Main is clean and synchronized.
- [ ] PRE-A011 issue is closed completed.
- [ ] CURRENT returns to A011 / PLANNED / no GitHub issue.
- [ ] No A011 GitHub issue is created by PRE-A011.

## 25. Success definition

PRE-A011 succeeds when FlyWireASCA reaches a qualification-ready state in which
A011 can answer architecture-wide research questions without first repairing
task-history coupling, stale architecture numbering, ambiguous evidence roles,
or hidden package-layer drift.

The gate is intentionally conservative: it improves the reliability of the
research process while preserving the exact cognitive implementation and
historical experimental outcomes produced by A001-A010.
