# A012 — Relational Reasoning / Structure Decision Gate Implementation Plan

Date: 2026-10-10
Method: Native TDD, evidence-driven
Approved by user in-session with authorization to create and continue.

## Goal

Implement the approved A012 decision experiment without changing A005-A010
frozen cognitive behavior or the A011 frozen v0.x protected source set.

## Task 1 — Activate the milestone coherently

Files:
- `docs/development/tasks/A012-relational-reasoning-structure-decision.md`
- `docs/development/tasks/CURRENT.md`
- `docs/development/tasks/ROADMAP.md`
- `README.md`
- `tests/test_a012_task_ledger.py`
- `tests/test_task_ledger.py`

Steps:
1. Publish design and this plan.
2. Run task-ledger/repository qualification while A012 is PLANNED.
3. Create GitHub Issue A012 only after the planned documents are coherent.
4. Change task/CURRENT/ROADMAP to ACTIVE and record the real issue number.
5. Record activation base `23b96f4502b81cddb9563b55c26fdd0adc731265`.

Acceptance:
- no guessed issue number;
- repository qualifier passes in both PLANNED and ACTIVE lifecycle states;
- A011 stays DONE and Issue #12 stays closed.

## Task 2 — Define strict A012 records

Create:
- `src/flywire_asca/relational_reasoning/models.py`
- `src/flywire_asca/relational_reasoning/__init__.py`
- `tests/test_relational_reasoning_models.py`

Records/enums:
- comparison variant;
- traversal termination reason;
- traversal request/result/path evidence;
- benchmark case/result/report;
- architecture decision.

RED tests first:
- invalid budgets rejected;
- duplicate IDs rejected;
- unknown targets rejected;
- non-finite weights are already rejected by Contract v0.1 edges;
- report aggregate/count invariants fail closed.

## Task 3 — Implement bounded explicit relation traversal

Create:
- `src/flywire_asca/relational_reasoning/index.py`
- `tests/test_relational_reasoning_index.py`

TDD behaviors:
- directed outgoing edges only;
- relation allowlist;
- confidence threshold;
- deterministic frontier ordering;
- maximum hops/nodes/scanned edges;
- cycle suppression;
- exact path edge/evidence provenance;
- no SAME_NAME -> SAME_PERSON inference;
- explicit termination reason.

No third-party graph library.

## Task 4 — Build the frozen deterministic comparison

Create:
- `src/flywire_asca/relational_reasoning/benchmark.py`
- `tests/test_relational_reasoning_benchmark.py`

Use real A005 `ExactVectorMemoryIndex`, `VectorMemoryDocument`, and
`VectorMemoryQuery`.

Fixture cases:
- WORKS_AT;
- CAUSED_BY;
- OCCURRED_BEFORE;
- PART_OF two-hop;
- USED_FOR;
- same-name disambiguation;
- vector-direct control;
- cycle control;
- low-confidence control;
- relation-allowlist control;
- missing-target control;
- invalid-contract control.

Freeze:
- ordered case IDs;
- fixture fingerprint;
- shared-input fingerprints;
- variant membership.

Classifier:
- `EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED`
- `VECTOR_METADATA_REMAINS_SUFFICIENT`
- `MIXED`

The classifier must derive its result from measured case outcomes.

## Task 5 — Portable qualifier and CI

Create:
- `scripts/qualify_relational_reasoning_a012.py`
- `tests/test_relational_reasoning_qualification_cli.py`

Update:
- `.github/workflows/ci.yml`
- `tests/test_ci_contract.py`
- `docs/development/QUALIFICATION-MATRIX.md`

Requirements:
- deterministic JSON output;
- nonzero exit only for invalid experiment/qualification errors, not because a
  valid research result is MIXED or VECTOR_METADATA_REMAINS_SUFFICIENT;
- A012 portable CI remains Ollama-free;
- existing A003/A008/A009/A010 gates remain present;
- do not rerun A011 against the post-A011 HEAD. Preserve the unchanged frozen
  A011 profile/67 protected blobs with a dedicated preservation check instead.

## Task 6 — Local physical secondary replay

Create:
- `scripts/qualify_relational_reasoning_a012_physical.py`
- `tests/test_relational_reasoning_physical.py`

Use pinned:
- `qwen3-embedding:0.6b`
- digest `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`
- dimension 1024
- A005 threshold `0.5037018224299838`

The physical runner preserves the portable fixture semantics and only swaps the
embedding evidence source. It is local-only and secondary.

## Task 7 — Architecture audit and A011 boundary

Update:
- `scripts/audit_architecture_contract.py`
- `tests/test_architecture_audit.py`
- documentation as needed

Add `relational_reasoning` to the dependency audit with allowed dependencies
`contracts`, `embedding`, and `vector_memory`.

Explicitly verify the A011 frozen profile bytes and all listed protected blobs
remain unchanged. A012 must not edit any path listed by
`docs/development/qualification/a011-v0x-profile-v1.json::protected_source.paths`.
The original A011 qualifier remains strict and historical; do not weaken its
complete-source-universe check merely to admit the new A012 package.

## Task 8 — Evidence, review, and repair

Run:
- focused A012 tests;
- full `pytest -q`;
- architecture audit;
- repository qualifier;
- A012 portable qualifier;
- A011 frozen-profile/blob preservation check on the exact candidate;
- local A012 physical qualifier;
- `git diff --check`.

Perform a whole-change review. Any Critical/Important finding receives one
evidence-driven repair pass with RED -> GREEN tests before integration.

## Task 9 — Integration and closure

Requirements:
- exact feature-branch CI GREEN;
- non-destructive integration to main;
- exact main CI GREEN;
- final A012 evidence report;
- task/ROADMAP/CURRENT lifecycle moved to DONE only after evidence;
- GitHub issue closed as completed only after exact-main evidence;
- final full-session handoff records exact SHAs/runs/runtime and next authorized
  action.

No tag, release, version promotion, FlyWireLLM change, A005-A010 retuning, or
persistent graph database is authorized by this plan.
