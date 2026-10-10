# PRE-A011 Architecture & Process Consistency Stabilization Report

Date: 2026-10-10
Repository: `funggier/FlyWireASCA`
Gate: PRE-A011 — Architecture & Process Consistency Stabilization
GitHub Issue: #11
State at this report: ACTIVE / pre-review

## 1. PRE-A011 closure candidate

PRE-A011 closure candidate is qualification-ready for whole-change review.

This is a maintenance result, not a new A-numbered research outcome. A011 remains
PLANNED and unactivated.

Activation base:

`c8211fff43523b80c66fcfecff9088970d6c9981`

Exact activation-base CI:

`38020908291` — success

Qualified behavior SHA before report-only closure metadata:

`1c1f79a2213e248a0e1ea383943eee7281f1231a`

The qualified behavior SHA is intentionally distinguished from later
documentation/review/closure metadata commits.

## 2. Problems repaired

PRE-A011 repaired the cross-milestone consistency debt found before A011:

1. published a canonical implemented-architecture snapshot;
2. published one qualification matrix for portable versus local physical gates;
3. marked the 2026-10-08 initial architecture design as historical without
   rewriting its original roadmap body;
4. centralized mutable CURRENT/ROADMAP test ownership in
   `tests/test_task_ledger.py`;
5. removed mutable CURRENT/ROADMAP dependencies from historical A004-A010 ledger
   tests;
6. hardened repository qualification for lifecycle consistency, DONE-task
   hygiene, PRE-* maintenance gates, and local Markdown links;
7. hardened architecture audit with an explicit package dependency contract and
   cross-package cycle detection;
8. linked CI directly to the qualification matrix without changing portable
   command topology;
9. repaired stale A009 closure prose;
10. repaired A010 physical-evidence Markdown table formatting;
11. deduplicated private Ollama JSON shape validators while preserving
    model/embedding protocol exception domains.

## 3. Canonical architecture and process artifacts

Created:

- `docs/architecture/ASCA-PRE-A011-SNAPSHOT.md`
- `docs/development/QUALIFICATION-MATRIX.md`

Updated task workflow terminology distinguishes:

- Activation base
- Qualified behavior SHA
- Reviewed behavior SHA
- Integration SHA
- Repository closure state
- Closure metadata commit

Repository closure no longer requires a Markdown file to contain the SHA of the
commit containing that same Markdown file.

## 4. Mutable lifecycle ownership

Historical milestone tests A004-A010 no longer read `CURRENT.md` or
`ROADMAP.md`.

Mutable lifecycle state now has one canonical test owner:

`tests/test_task_ledger.py`

During PRE-A011:

- CURRENT = PRE-A011 / ACTIVE / Issue #11;
- PRE-A011 has its own maintenance task document;
- PRE-A011 is not added to the A-numbered research ROADMAP;
- A001-A010 remain DONE;
- A011 remains PLANNED.

A011 GitHub issue: not created.

## 5. Repository lifecycle qualification

`scripts/qualify_repository.py` now rejects:

- duplicate A-numbered ROADMAP task IDs;
- non-monotonic A-numbered ROADMAP ordering;
- invalid lifecycle status vocabulary;
- A-numbered CURRENT/ROADMAP status mismatch;
- PRE-* CURRENT without a matching maintenance task;
- guessed numeric issue numbers on PLANNED current tasks;
- ACTIVE task files without a numeric GitHub issue;
- DONE tasks with unchecked acceptance criteria;
- task filename/heading identity mismatch;
- broken repository-relative Markdown links;
- existing machine-local source paths and FlyWireLLM boundary violations.

Live result:

`repository_qualification=PASS`

## 6. Package architecture contract

The architecture audit now enforces the explicit pre-A011 direct package
dependency graph and rejects both undeclared reverse dependencies and
cross-package cycles.

Live result:

`architecture_contract_audit=PASS`

The current graph remains acyclic.

## 7. Bounded source cleanup classification

The only source files changed from the activation base are:

- `src/flywire_asca/contracts/validation.py`
- `src/flywire_asca/model/ollama.py`
- `src/flywire_asca/embedding/ollama.py`

The change is classified as **behavior-preserving**.

### Shared JSON shape validation

Five duplicated private validators were moved to the shared contract validation
module with caller-selected exception types:

- mapping;
- list;
- nonblank string;
- optional string;
- optional nonnegative integer.

The model adapter binds them to `ModelProtocolError`.

The embedding adapter binds them to `EmbeddingProtocolError`.

Focused characterization after the refactor:

`44 passed`

This covers shared helper semantics, model/embedding protocol errors, model
contracts, and embedding contracts.

### Explicit no-refactor decisions

- shared HTTP transport: not refactored. Model and embedding transport layers
  retain distinct protocol/timeout/unavailable exception domains; a forced
  abstraction would add more complexity than the duplication removed.
- benchmark modules: not split. File size alone does not provide a sufficiently
  strong cohesion boundary before A011.
- retrieval scheduling: not changed. The A010 repeated-retrieval weakness is a
  future research hypothesis, not maintenance cleanup.

No selector, retrieval ranking, expansion policy, procedure behavior, A009
controller policy, A010 classifier, frozen fixture, threshold, model identity,
or research outcome was changed.

## 8. Final portable verification before review

Fresh complete portable gate:

- full pytest: **552 passed**
- `architecture_contract_audit=PASS`
- `repository_qualification=PASS`
- A003 familiarity qualification: PASS
- A008 procedural-memory qualification: PASS
- A009 portable qualification: PASS
- A010 portable qualification: PASS
- `git diff --check`: PASS

Frozen portable identity:

- A009 scope: `deterministic_integrated_cognitive_loop_a009`
- A009 fixture version: `a009-deterministic-v1`
- A009 fingerprint:
  `2f92b5092de346f62879ac2cbb9f96d6de5d6f919e12d0693345c8228b01ab2a`
- A009 outcome: `SUPPORTED`
- A010 scope: `deterministic_dense_nonselective_baseline_a010`
- A010 fixture version: `a010-deterministic-v1`
- A010 fingerprint:
  `69d20542cd1e7e5c25a0fb61b9060f622379206b519da3cec7624e00bb6e5d4c`
- A010 outcome: `NOT_SUPPORTED`

## 9. Final local physical verification before review

All required local physical commands completed with exit code 0.

- A004 physical qualification: GREEN
  - model: `qwen3.5:4b`
  - digest:
    `2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd`
  - qualification: true
- A005 physical qualification: GREEN
  - model: `qwen3-embedding:0.6b`
  - digest:
    `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`
  - dimension: 1024
  - threshold: `0.5037018224299838`
  - graph decision: `VECTOR_SUFFICIENT`
- A006 physical qualification: GREEN
  - A006: `NOT_SUPPORTED`
- A007 physical qualification: GREEN
  - A007: `SUPPORTED`
- A009 physical qualification: GREEN
  - physical integration valid: true
  - portable outcome: `SUPPORTED`
  - embedding/model identities exactly match the pinned values above
- A010 physical qualification: GREEN
  - physical integration valid: true
  - portable outcome: `NOT_SUPPORTED`
  - embedding identity exactly matches the pinned value above

Physical timing observations are descriptive secondary evidence only and are not
used to create a PRE-A011 performance claim.

## 10. Historical outcome preservation

PRE-A011 preserves exactly:

- A006: `NOT_SUPPORTED`
- A007: `SUPPORTED`
- A008: `SUPPORTED`
- A009: `SUPPORTED`
- A010: `NOT_SUPPORTED`

Engineering/process hardening does not reinterpret any research outcome.

## 11. FlyWireLLM and A011 boundaries

FlyWireLLM remains untouched.

PRE-A011 does not import, train, restart, or modify FlyWireLLM.

A011 remains PLANNED and its exact GitHub issue title search returned no issue.

PRE-A011 Issue #11 remains open until reviewed behavior is integrated to main
and exact main CI is GREEN.

## 12. Claims boundary

PRE-A011 establishes process/engineering properties only:

- lifecycle state is structurally checked;
- repository-relative documentation links are checked;
- package dependency direction/cycle freedom is machine checked;
- portable/physical qualification topology is explicit;
- bounded validator deduplication preserved observed adapter behavior;
- historical outcomes and pinned identities remain unchanged.

PRE-A011 does not establish lower FLOPs, energy, power, memory bandwidth,
general latency, superiority over dense LLMs, biological equivalence, AGI, or
consciousness.

## 13. Closure-candidate local gate

After adding this report and its task-ledger regression tests, the local
closure-candidate gate completed with **556 passed**, while architecture and
repository audits remained PASS.

This does not redefine the qualified behavior SHA: the additional changes are
documentation/test metadata around the already-qualified behavior.

## 14. Remaining gates

Before PRE-A011 may close:

- whole-change review must complete;
- every Critical/Important review finding must be resolved;
- exact post-review feature-branch CI must be GREEN;
- reviewed behavior must integrate to main without history rewriting;
- exact main CI must be GREEN;
- Issue #11 must close as completed;
- CURRENT must return to A011 / PLANNED / no issue;
- final closure metadata CI must be GREEN;
- main must be clean and synchronized.