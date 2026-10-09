# A006 — Working Set / Selective Activation

Status: DONE
GitHub Issue: #6
Branch: research/a006-working-set

## Goal

Take one or more A005 `VectorMemoryResult` values, aggregate repeated memory
support into a deterministic bounded activation signal, and build a smaller
auditable working set under strict budgets.

## Scope

Delivered:

- immutable A006 evidence/support/result contracts;
- SELECTIVE_CONVERGENCE bounded-union activation;
- strict active-memory and working-set budgets;
- explicit boundary-tie evidence;
- SINGLE_BEST and EXHAUSTIVE controls;
- portable benchmark and engineering qualifier;
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
- Exact qualification/review/integration: DONE as branch closure candidate;
  final main CI/synchronization remain external integration gates.

## Physical Frozen Profile

- A005 model: `qwen3-embedding:0.6b`
- digest: `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`
- dimension: 1024
- A005 `minimum_similarity = 0.5037018224299838`
- A005 `top_k = 12`
- A006 `max_memory_nodes = 8`
- A006 `max_working_set_items = 4`
- relation hops / expansions / model-input tokens = 0

A006 did not recalibrate the A005 threshold or tune these budgets after the
final physical outcome.

## Acceptance Criteria

- [x] A006 records validate provenance/support/count invariants.
- [x] Bounded-union activation is deterministic and bounded.
- [x] Similarity/activation remain separate from proposition confidence.
- [x] Strict memory and working-set budgets never expand for ties.
- [x] Boundary ties are reported.
- [x] Same-name ambiguity is not converted into identity.
- [x] SINGLE_BEST and EXHAUSTIVE use the same evidence validation.
- [x] Portable qualification passes declared engineering gates.
- [x] Physical experiment emits one frozen-rule outcome.
- [x] Physical outcome is `NOT_SUPPORTED`, recorded without fixture tuning.
- [x] Active-state reduction is not described as compute/FLOP/energy reduction.
- [x] A003/A004/A005 qualification boundaries remain intact.
- [x] FlyWireLLM remains paused and untouched.
- [x] Exact branch CI passes; final main CI remains an integration gate.
- [x] Final main clean/sync 0/0 remains an integration gate before Issue #6 closure.

## Evidence

Approved spec:

`docs/superpowers/specs/2026-10-09-a006-working-set-design.md`

Approved implementation plan:

`docs/superpowers/plans/2026-10-09-a006-working-set.md`

Branch candidate:

`224864cc9d70228d4feb80a9fcbc07f2776808d3`

Exact branch CI:

`37927165972` — success

Fresh branch tests:

- pytest: 238 passed
- architecture audit: PASS
- repository qualifier: PASS
- A003 familiarity qualification: PASS
- diff check: PASS

Portable benchmark:

- required-memory coverage: 1.0
- SINGLE_BEST coverage: 0.9230769230769231
- convergence recovery: 1
- convergence regression: 0
- boundary ties: 2
- aggregate active-state reduction: `0.942652329749104`
- deterministic repeat: PASS

Physical qualification on behavior commit
`43afe2dfb2f6a1365c1be3fc5333c55901d52f21`:

- experiment validity: PASS
- final hypothesis outcome: `NOT_SUPPORTED`
- fixture: `a006-physical-v1`
- fingerprint:
  `e51fea2e58186e94d7affc964509e96d96fc656759677d7dcc073e5b36b91035`
- required-memory coverage: 1.0
- convergence recovery count: 0
- convergence regression count: 0
- ambiguity failures: 0
- no-selection failures: 0
- strict budget observations: 1
- positive candidates: 34
- selected working-set items: 22
- aggregate active-state reduction:
  `0.35294117647058826`
- deterministic repeat: PASS
- embedding requests: 21
- embedding inputs: 52
- prompt tokens: 943
- total duration: 4,527,985,600 ns across 21 responses
- load duration: 1,570,494,900 ns across 13 reported responses

The physical result is valid negative research evidence: convergence changed
some ordering but did not recover a required memory that SINGLE_BEST omitted
under the frozen working-set budget.

Detailed evidence:

`docs/development/reports/ASCA-20261009-A006-working-set-selective-activation.md`

## Current Action

The qualified implementation has been fast-forward merged into `main`; merged
implementation CI run `37932246076` passed at
`90ee1709bfd6a827246f5c6292e73f264bf07c2c`. Verify the final
documentation-only closure commit on exact `main`, then close Issue #6.

## Next Action

After final closure-evidence `main` CI and synchronization are GREEN, remove
the clean A006 worktree/local branch. A007 — Surprise, Uncertainty & Expansion
remains PLANNED for a separate design/task.
