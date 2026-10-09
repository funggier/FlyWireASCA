# FlyWireASCA A005 Semantic Vector Memory Retrieval Qualification

Date: 2026-10-09
Task: A005 — Semantic Vector Memory Retrieval
GitHub Issue: #5
Branch: research/a005-vector-memory

## Decision

A005 implementation candidate is GREEN on exact branch commit:

`78099fe3e36e8e1292085425f1553a05b95a820e`

The candidate passed portable repository qualification, local physical
embedding calibration, and the declared six-case physical vector-memory
qualification using a threshold frozen before the final physical fixture ran.

This report records the initial controlled-fixture decision. The whole-branch
review is still required before final integration and may invalidate or narrow
this decision if it finds a methodological or implementation gap.

Final graph decision: `VECTOR_SUFFICIENT`

This decision is scoped to the declared A005 controlled evidence. It means the
current experiments do not justify adding a typed graph yet. It does **not**
claim that explicit relation/path semantics are universally unnecessary.

## Delivered subsystem

A005 adds:

- backend-neutral embedding contracts and `EmbeddingAdapter` protocol;
- finite/nonzero/dimension-safe normalized embedding vectors;
- local Ollama `/api/embed` adapter;
- immutable Vector + Metadata retrieval records;
- deterministic exact-cosine in-memory retrieval;
- metadata pre-filtering before vector scoring;
- explicit similarity/proposition-confidence separation;
- portable threshold calibration and qualification fixtures;
- physical development calibration separate from physical qualification;
- three-way graph-decision evaluator.

A005 does not construct or traverse `AssociationEdge`, call Qwen3.5:4b for
memory selection, use an ANN/vector database, or infer identity/truth from
similarity.

## Exact portable branch qualification

Candidate SHA:

`78099fe3e36e8e1292085425f1553a05b95a820e`

Fresh local evidence on the exact candidate:

- `python -m pytest -q`: **151 passed**
- `python scripts/audit_architecture_contract.py`:
  **architecture_contract_audit=PASS**
- `python scripts/qualify_repository.py`:
  **repository_qualification=PASS**
- `python scripts/run_familiarity_benchmark_a003.py --qualify`: PASS
- `git diff --check HEAD^ HEAD`: PASS
- branch worktree: clean
- A004 model-layer files changed by A005: none

Exact portable branch CI:

- workflow: CI
- run id: `37906978728`
- head SHA: `78099fe3e36e8e1292085425f1553a05b95a820e`
- event: push
- conclusion: **success**

GitHub Actions remains portable and does not pull/run the physical embedding
model or call local Ollama embedding endpoints.

## Portable benchmark evidence

The deterministic fake-vector layer verifies the algorithm independently from
physical Qwen embedding behavior.

Portable development calibration:

- threshold: `0.5`
- origin: `portable_fake_geometry_only`

That value is algorithm-test evidence only and was **not** reused as the
physical Qwen threshold.

Portable qualification:

- 12 declared cases;
- 256 distractor documents;
- English semantic paraphrase;
- Thai semantic paraphrase;
- Thai-to-English and English-to-Thai retrieval;
- exact wording;
- same-name ambiguity;
- entity/context metadata filtering;
- proposition-confidence independence;
- threshold no-hit;
- deterministic score tie ordering;
- Recall@1: 1.0;
- Recall@K: 1.0;
- MRR: 1.0;
- no-hit correctness: 1.0;
- metadata-filter correctness: 1.0;
- false retrieval count: 0;
- ambiguity failure count: 0.

## Physical embedding identity

The local model was absent before A005 and was installed only after the
portable qualification tooling was committed.

Observed runtime/model identity:

- backend: `ollama`
- Ollama version: `0.32.15`
- model: `qwen3-embedding:0.6b`
- full digest:
  `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`
- format: GGUF
- architecture/family: `qwen3`
- exact parameter count: `595,776,512`
- reported parameter size: `595.78M`
- quantization: `Q8_0`
- context length: `32768`
- embedding dimension: `1024`
- Ollama-reported capabilities: embedding, thinking, tools

A005 uses only the embedding capability. Thinking/tools are not invoked by the
A005 retrieval path.

## Physical vector-health evidence

The physical qualification performs repeated English and Thai embedding
probes.

Observed:

- repeated requests: 8
- vectors checked: 16
- dimension: 1024
- zero/near-zero vectors accepted: 0
- non-finite vectors accepted: 0
- normalized norm minimum: 1.0
- normalized norm maximum: 1.0

A successful HTTP status alone is never accepted as sufficient vector-health
evidence.

## Physical threshold calibration

The physical threshold was calibrated from a development-only fixture before
the final physical qualification fixture.

Physical calibration case IDs:

- `physical-cal-bike`
- `physical-cal-cat`

Frozen threshold:

`0.5037018224299838`

Threshold origin:

`physical_development_fixture_v1`

The final qualification case IDs/content are disjoint from these calibration
cases. The threshold was not tuned after the qualification fixture was scored.

## Physical final qualification

Implementation/pin commit used for physical qualification:

`7dfd4b0f477128007eae4c14c7e8948d610c18f3`

Only documentation changed between that implementation commit and the exact
branch candidate.

Physical final result:

- experiment validity: PASS
- retrieval qualification: PASS
- cases: **6/6**
- Recall@1: 1.0 on cases declaring one best result
- Recall@K: 1.0
- mean reciprocal rank: 1.0
- metadata-filter correctness: 1.0
- false retrieval count: 0
- ambiguity failure count: 0
- relation-semantic failure count: 0 on this declared fixture
- scalability warning count: 0 on this six-document fixture
- embedding requests: 7
- embedding inputs: 12
- stored documents: 6
- vectors scored across queries: 31

Physical qualification cases:

1. English paraphrase -> red-scooter memory — PASS
2. Thai paraphrase -> green-parrot memory — PASS
3. Thai query -> English backup-drive memory — PASS
4. English query -> Thai meeting-room memory — PASS
5. same-name Somchai ambiguity -> both candidate memories preserved — PASS
6. explicit entity filter -> only `person-b` memory eligible/scored — PASS

The physical fixture does not contain a no-hit case. The benchmark report
currently emits its neutral aggregate default for unexercised no-hit metrics;
this report therefore does **not** present physical no-hit correctness as
measured evidence. Portable qualification does exercise no-hit behavior.

## Similarity and confidence boundary

Vector similarity is used only for retrieval ranking/thresholding.

A memory's `proposition_confidence` is preserved independently and is never
increased or replaced by vector similarity. Same-name vector similarity also
does not create `SAME_PERSON` identity.

## Selectivity / compute boundary

The A005 index is exact brute-force cosine search after metadata filtering.

The physical six-case fixture scored 31 vectors in total. This count is
software-work evidence, not a FLOP, power, energy, or generalized compute
reduction claim. Top-K output alone is not treated as proof of selective
compute savings.

## A004 and FlyWireLLM isolation

A005 did not change A004 model-layer implementation files.

FlyWireLLM was inspected read-only before A005 branch publication:

- HEAD: `9aa8acba1ecdefcdce4678b2914fc2d2dcaacc14`
- branch: `research/l004-base50m-pretraining`
- upstream: `origin/research/l004-base50m-pretraining`
- ahead/behind: 0/0
- worktree: clean
- no FlyWireLLM training runner observed in the Python process list

FlyWireLLM remains paused and was not started, stopped, or mutated by A005.

## Initial graph decision rationale

The declared A005 controlled evidence shows:

- strong same-language semantic retrieval;
- Thai/English cross-lingual retrieval;
- same-name ambiguity preservation;
- explicit metadata disambiguation;
- no false retrievals in the declared portable/physical positive fixtures;
- no current controlled case proving a need for typed relation traversal.

Therefore the initial controlled-fixture result remains `VECTOR_SUFFICIENT`.

This means continue without automatically creating a graph milestone. A later
experiment may still justify a graph if reproducible multi-memory,
causal/temporal/ownership/path failures appear.

## Deferred scope

A005 deliberately defers:

- typed graph construction/traversal;
- multi-hop relation reasoning;
- ANN/vector database acceleration;
- vector persistence;
- reranking;
- Qwen3.5:4b context integration;
- embedding training/fine-tuning;
- A003 Familiarity gating of vector search.

## Next milestone

A006 — Working Set / Selective Activation.

A006 remains **PLANNED**. A005 closure does not activate it automatically.
