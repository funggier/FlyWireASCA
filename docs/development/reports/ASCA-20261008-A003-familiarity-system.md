# FlyWireASCA A003 Familiarity System Qualification

Date: 2026-10-08
Task: A003 — Familiarity System
GitHub Issue: #3
Branch: research/a003-familiarity-system

## Decision

The initial A003 implementation candidate was GREEN on exact commit
`6c9534cb743123c60184e9e00244f836c3e901e1` and branch CI run
`37803237340`.

Whole-branch review then found one Important qualification gap. The reviewed
implementation after the RED→GREEN fix is exact commit
`3a70afa07475d86ea523d0dfe1433c2006bb683f`, which passed branch CI run
`37804356820`.

This report and task transition form the documentation closure layer. The
closure documentation commit itself must also pass exact branch CI before
fast-forward integration to `main`.

## Delivered subsystem

A003 adds the first model-independent familiarity subsystem:

- immutable `FamiliarityTrace`, `FamiliarityCost`, and
  `FamiliarityResult`;
- conservative Unicode surface normalization using NFKC, Unicode whitespace
  collapse, and `casefold()`;
- typed familiarity keys preserving `CueKind`;
- `ExactFamiliarityIndex`;
- `ExhaustiveFamiliarityBaseline`;
- deterministic controlled benchmark and qualification CLI;
- explicit GitHub Actions benchmark qualification gate.

A003 deliberately does not implement semantic/associative recall, identity
resolution, graph traversal, learned familiarity, embeddings, working-set
routing, surprise-driven expansion, or FlyWireLLM integration.

## Exact candidate qualification

Candidate SHA:

`6c9534cb743123c60184e9e00244f836c3e901e1`

Fresh local evidence on that exact commit:

- `python -m pytest -q`: **66 passed**
- `python scripts/audit_architecture_contract.py`:
  **architecture_contract_audit=PASS**
- `python scripts/qualify_repository.py`:
  **repository_qualification=PASS**
- `python scripts/run_familiarity_benchmark_a003.py --qualify`: PASS
- `git diff --check HEAD^ HEAD`: PASS
- worktree: clean

Exact branch CI:

- workflow: CI
- run id: `37803237340`
- head SHA: `6c9534cb743123c60184e9e00244f836c3e901e1`
- event: push
- conclusion: **success**

## Controlled benchmark qualification

Scope: `controlled_fixture_only`

The controlled fixture contains 263 familiarity traces including 256 synthetic
distractor traces/regions and 9 declared test cases.

Qualified summary:

- classification_accuracy: 1.0
- correct_classification_count: 9 / 9
- false_familiarity_count: 0
- false_unfamiliar_count: 0
- ambiguity_failure_count: 0
- semantic_mismatch_count: 0
- exact_logical_probes: 9
- exhaustive_logical_probes: 2367
- total_trace_count: 263

The exact and exhaustive implementations returned semantically identical state,
score, candidate-region IDs, matched-trace IDs, matched counts, and total trace
counts for every controlled case. They differed only in the intended logical
probe accounting.

Logical probe counts are software-work counters for this controlled
experiment. They are not FLOP, power, energy, or hardware-compute-reduction
measurements.

## Same-name ambiguity evidence

The fixture contains two ENTITY traces with normalized surface `A`:

- `person-a-primary`
- `person-a-neighbor`

The same-name ambiguity lookup returned both regions in deterministic order:

`("person-a-neighbor", "person-a-primary")`

No identity winner, `same_person` conclusion, or resolved entity ID is exposed
by `FamiliarityResult`. Familiarity therefore remains a candidate-narrowing
signal rather than identity inference.

## Normalization and type-boundary evidence

Qualification tests cover:

- ASCII case/outer whitespace normalization;
- NFKC compatibility characters such as full-width Latin text;
- Thai text with non-breaking/multiple whitespace;
- cue-kind separation, so ENTITY and TEXT surfaces do not collide;
- deterministic output ordering;
- duplicate trace-ID rejection;
- multiple traces to one region, where regions deduplicate but matching trace
  IDs remain visible.

## FlyWireLLM isolation evidence

FlyWireLLM remained a separate live training workload throughout A003.

At A003 candidate publication:

- repository: `T:\Space\Projects\ProjectsAI\FlyWireLLM`
- HEAD: `fc949583a7ecbbf3e717021efc9a3183295cb9e5`
- branch: `research/l004-base50m-pretraining`
- upstream: `origin/research/l004-base50m-pretraining`
- ahead/behind: 0/0
- worktree: clean
- training parent PID: 16328
- training child PID: 3868
- command:
  `scripts\run_pretraining_post_warmup_sustained_l004.py --external-root T:\Space\Projects\ProjectsAI\FlyWireLLM-data`
- child working set observed around 2.09 GB

A003 did not stop, restart, signal, import, invoke, or inspect checkpoints from
the FlyWireLLM training workload.

## Whole-branch review and fix pass

Native execution used an author self-review because no separate subagent
reviewer tool/template was available in the installed skill bundle.

The review found one Important issue: `qualify_a003_report` could accept a
non-ambiguity benchmark case where exact and exhaustive engines agreed with
each other but both returned the wrong candidate region. The controlled
fixture happened to be correct, but the qualifier itself did not enforce that
all `regions_correct` flags were true.

Regression test
`test_qualifier_rejects_wrong_candidate_regions_even_when_engines_agree`
was observed RED before the fix. The qualifier now rejects any such case with
`region mismatch cases must be 0`.

Post-review fix evidence:

- fix commit: `3a70afa07475d86ea523d0dfe1433c2006bb683f`
- focused regression: 2 passed
- full suite: 68 passed
- benchmark qualification: PASS
- architecture audit: PASS
- repository qualifier: PASS
- diff check: PASS
- exact fix branch CI run: `37804356820`
- CI conclusion: success

Two minor review notes are deferred because they do not affect the qualified
controlled path: the internal exact-index bucket annotation is broader than
necessary, and hand-crafted external benchmark reports are only partially
cross-validated beyond the CLI-generated report path.

## Deferred research

The following remain intentionally deferred:

- fuzzy lexical familiarity;
- embeddings/vector similarity;
- learned/neural familiarity estimation;
- recency/usage-strength learning;
- cross-modal familiarity;
- semantic/associative recollection;
- graph spreading activation;
- working-set routing;
- surprise-driven compute expansion;
- FlyWireLLM model adapter experiments.

## Next milestone

A004 — Associative Memory & Recall.

A004 remains **PLANNED**. Closing A003 does not activate A004 automatically.
