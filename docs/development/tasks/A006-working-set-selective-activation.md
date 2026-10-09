# A006 — Working Set / Selective Activation

Status: ACTIVE
GitHub Issue: #6
Branch: research/a006-working-set

## Goal

Take one or more A005 `VectorMemoryResult` values, aggregate repeated memory
support into a deterministic bounded activation signal, and build a smaller
auditable working set under strict budgets.

## Scope

In scope:

- immutable A006 evidence/support/result contracts;
- multi-query bounded-union activation;
- strict active-memory and working-set budgets;
- boundary-tie evidence;
- SINGLE_BEST and EXHAUSTIVE controls;
- portable benchmark;
- physical A005+A006 composition with local `qwen3-embedding:0.6b`.

Normative boundary: A006 does not build or traverse a typed graph.

A006 does not call `qwen3.5:4b` generation and does not use proposition
confidence as an activation boost.

## Phases

- A006 contracts and task activation: DONE.
- SELECTIVE_CONVERGENCE selector: DONE.
- SINGLE_BEST / EXHAUSTIVE baselines: DONE.
- Portable benchmark/qualification: DONE.
- Physical A005+A006 qualification: DONE.
- Exact qualification/review/integration: ACTIVE.

## Physical Frozen Profile

- A005 model: `qwen3-embedding:0.6b`
- digest: `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`
- dimension: 1024
- A005 `minimum_similarity = 0.5037018224299838`
- A005 `top_k = 12`
- A006 `max_memory_nodes = 8`
- A006 `max_working_set_items = 4`
- relation hops / expansions / model-input tokens = 0

A006 does not recalibrate the A005 threshold or tune these budgets after final
physical fixture outcomes are observed.

## Acceptance Criteria

- [ ] A006 records validate provenance/support/count invariants.
- [ ] Bounded-union activation is deterministic and bounded.
- [ ] Similarity/activation remain separate from proposition confidence.
- [ ] Strict memory and working-set budgets never expand for ties.
- [ ] Boundary ties are reported.
- [ ] Same-name ambiguity is not converted into identity.
- [ ] SINGLE_BEST and EXHAUSTIVE use the same evidence validation.
- [ ] Portable qualification passes declared engineering gates.
- [ ] Physical experiment emits SUPPORTED, MIXED, or NOT_SUPPORTED.
- [ ] Active-state reduction is not described as compute/FLOP/energy reduction.
- [ ] A003/A004/A005 qualification boundaries remain intact.
- [ ] FlyWireLLM remains paused and untouched.
- [ ] Exact branch and final-main CI pass.
- [ ] Main is clean and synchronized 0/0.

## Evidence

Approved spec:

`docs/superpowers/specs/2026-10-09-a006-working-set-design.md`

Approved implementation plan:

`docs/superpowers/plans/2026-10-09-a006-working-set.md`

Activation baseline:

- base main: `6147b9a6f6bc8c27b66735812e54c0050f13df36`;
- branch: `research/a006-working-set`;
- GitHub Issue: #6;
- A005 verdict: `VECTOR_SUFFICIENT` for retrieval scope;
- A005 frozen threshold: `0.5037018224299838`.

Physical qualification on implementation commit `43afe2dfb2f6a1365c1be3fc5333c55901d52f21`:

- experiment validity: PASS;
- hypothesis outcome: `NOT_SUPPORTED`;
- Ollama runtime: `0.32.15`;
- embedding model: `qwen3-embedding:0.6b`;
- full digest: `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`;
- embedding dimension: 1024;
- fixture version: `a006-physical-v1`;
- fixture fingerprint: `e51fea2e58186e94d7affc964509e96d96fc656759677d7dcc073e5b36b91035`;
- required-memory coverage: 1.0;
- convergence recovery count: 0;
- convergence regression count: 0;
- ambiguity failure count: 0;
- no-selection failure count: 0;
- strict budget observation count: 1;
- positive candidates total: 34;
- selected working-set items total: 22;
- aggregate active-state reduction ratio: `0.35294117647058826`;
- deterministic repeated selector result: PASS;
- result interpretation: bounded-union convergence preserved all declared required memories and caused no regression, but did not recover any required memory that SINGLE_BEST missed under the frozen physical fixture, so the predeclared rule yields `NOT_SUPPORTED` rather than tuning the fixture.

The first live attempt exposed one fixture-label bug in the strict budget case: 12 near-identical status notes had arbitrarily labeled `budget-00` as required. Regression `test_budget_truncation_case_does_not_label_an_arbitrary_equal_status_note_as_required` was observed RED, then the label alone was removed while texts, threshold, top_k, budgets, and selector behavior remained frozen. Raw physical JSON remains scratch-only.

## Current Action

Run Task 6 exact branch qualification on the physically qualified A006 candidate,
then publish the branch for exact portable CI.

## Next Action

After exact branch CI is GREEN, write the A006 closure report with the valid
`NOT_SUPPORTED` physical research outcome, transition A007 to PLANNED, review
the whole branch, and fast-forward `main`.

The next milestone after qualified A006 remains A007 — Surprise, Uncertainty &
Expansion.
