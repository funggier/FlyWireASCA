# A005 Semantic Vector Memory Retrieval Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and qualify a safe multilingual Vector + Metadata memory retriever for FlyWireASCA, then use measured evidence to decide whether a typed graph is actually justified.

**Architecture:** A005 adds a backend-neutral embedding boundary plus a deterministic in-memory exact-cosine vector-memory index. Portable CI uses deterministic fake embeddings and frozen benchmark fixtures; real `qwen3-embedding:0.6b` is qualified locally through Ollama, with strict vector validation, fixed threshold/profile evidence, and no generative Qwen call in retrieval.

**Tech Stack:** Python >=3.11 standard library only, frozen dataclasses, `Protocol`, `urllib.request`, `math`, JSON, pytest, local Ollama embedding API, planned physical model `qwen3-embedding:0.6b`.

**Spec:** `docs/superpowers/specs/2026-10-09-a005-vector-memory-design.md`

## Global Constraints

- Repository: public `funggier/FlyWireASCA`.
- Work branch: `research/a005-vector-memory`.
- A005 title: **Semantic Vector Memory Retrieval**.
- A005 is **Vector + Metadata**, not Hybrid Vector + Graph.
- A002 `AssociationEdge` remains intact but is not built or traversed by A005.
- A003 Familiarity remains independent and is not a hard gate for A005 retrieval.
- A004 `qwen3.5:4b` generative model is not called by A005 retrieval.
- Planned local embedding model-under-test: `qwen3-embedding:0.6b`.
- Planned embedding dimension: full 1024 dimensions; no MRL truncation in A005.
- Query profile string is exactly:
  `Instruct: Retrieve stored memories that are semantically relevant to the query.\nQuery: <query text>`
- Generic embedding/vector-memory contracts must not depend on Ollama/Qwen.
- The physical adapter uses local Ollama `/api/embed` through the standard library; no new mandatory dependency is added.
- Vectors must be finite, dimensionally consistent, nonzero/near-zero rejected using raw L2 norm <= `1e-12`, and accepted vectors are client-normalized to unit L2 norm.
- Exact cosine search is the A005 correctness baseline; no ANN/vector database.
- Metadata filtering occurs before vector scoring.
- `allowed_memory_kinds` is membership filtering; required entity/context/source sets use all-required/contains semantics; filter fields combine with logical AND.
- Duplicate `memory_id` values fail closed.
- Query `top_k > 0`; `minimum_similarity` must be finite within [-1, 1].
- Similarity never changes `MemoryRecord.proposition_confidence`.
- Vector similarity never creates identity, truth, causal, temporal, or graph relations.
- Same-name ambiguity is preserved unless explicit metadata filters constrain it.
- Portable CI must not install/pull/run the physical embedding model.
- Development/calibration and final qualification fixtures are distinct at both portable-test and physical-model layers. Fake-vector calibration tests only the calibration algorithm; the threshold used for real Qwen embedding qualification is calibrated from a separate physical development fixture, frozen, recorded, and never tuned on the physical qualification fixture.
- Physical qualification may install/pull `qwen3-embedding:0.6b` after software gates are GREEN, then records the full local model digest.
- FlyWireLLM remains paused and untouched.
- A005 closure must record exactly one decision outcome: `VECTOR_SUFFICIENT`, `VECTOR_NEEDS_INDEX_OR_METADATA`, or `GRAPH_JUSTIFIED`.
- No graph milestone is created merely because it was previously considered.
- Exact branch CI, physical embedding qualification, final main CI, clean worktree, and main sync 0/0 are required before A005 closes.

## File Structure

- `src/flywire_asca/embedding/__init__.py`: public embedding exports.
- `src/flywire_asca/embedding/contracts.py`: generic immutable embedding records and vector validation/normalization.
- `src/flywire_asca/embedding/adapter.py`: backend-neutral `EmbeddingAdapter` protocol.
- `src/flywire_asca/embedding/errors.py`: embedding adapter exception hierarchy.
- `src/flywire_asca/embedding/ollama.py`: local Ollama descriptor/embed mapping through JSON transport.
- `src/flywire_asca/vector_memory/__init__.py`: public vector-memory exports.
- `src/flywire_asca/vector_memory/models.py`: retrieval document/query/hit/result contracts.
- `src/flywire_asca/vector_memory/index.py`: immutable exact-cosine in-memory index.
- `src/flywire_asca/vector_memory/benchmark.py`: deterministic portable calibration/qualification fixtures, raw metrics, and graph-decision evaluation.
- `scripts/qualify_vector_memory_a005.py`: local physical embedding/vector-memory qualification CLI.
- `tests/test_embedding_contracts.py`: embedding records/vector validation.
- `tests/test_ollama_embedding_adapter.py`: fake-transport adapter tests.
- `tests/test_vector_memory_index.py`: exact search, filters, ambiguity, cost, and confidence-separation tests.
- `tests/test_vector_memory_benchmark.py`: portable benchmark/calibration/decision-gate tests.
- `tests/test_vector_memory_qualification_cli.py`: local CLI tests with fake adapter.
- `tests/test_a005_task_ledger.py`: A005 activation/closure/decision evidence.
- `docs/development/tasks/A005-semantic-vector-memory-retrieval.md`: recoverable A005 task ledger.
- `docs/development/reports/ASCA-20261009-A005-vector-memory-retrieval.md`: final qualification/decision report.

## Review Focus

1. **Zero/near-zero and non-finite vectors:** HTTP/API success must never allow unusable vectors into storage/search; Task 1 contract tests and Task 2 adapter tests must pin raw-norm, NaN/Inf, and post-normalization checks.
2. **Batch-order/count/dimension drift:** embedding batches with missing, extra, reordered, or dimension-changing vectors must fail closed rather than silently align the wrong vector with the wrong memory; Task 2 tests pin response count and stable dimension.
3. **Metadata ambiguity:** same-name memories without identity metadata must both remain eligible; with an explicit entity filter, only matching metadata survives before vector scoring; Task 3 tests pin both paths.
4. **Similarity/confidence conflation:** highest semantic similarity must not overwrite or rank by proposition confidence unless a future algorithm explicitly chooses that; Task 3 tests pin the original confidence value independently from similarity.
5. **Threshold overfitting / graph verdict bias:** threshold calibration fixture and qualification fixture must be separate, and the graph decision must derive from declared raw metrics/failure categories rather than a hard-coded preferred outcome; Task 4 benchmark tests pin fixture separation and deterministic decision rules.

---

### Task 1: Add generic embedding contracts, activate A005, and rename the roadmap milestone

**Files:**
- Create: `src/flywire_asca/embedding/__init__.py`
- Create: `src/flywire_asca/embedding/contracts.py`
- Create: `src/flywire_asca/embedding/adapter.py`
- Create: `src/flywire_asca/embedding/errors.py`
- Create: `tests/test_embedding_contracts.py`
- Create: `tests/test_a005_task_ledger.py`
- Create: `docs/development/tasks/A005-semantic-vector-memory-retrieval.md`
- Modify: `docs/development/tasks/CURRENT.md`
- Modify: `docs/development/tasks/ROADMAP.md`
- Modify: `README.md`
- Modify: `tests/test_task_ledger.py`

**Interfaces:**
- Produces `EmbeddingInputKind(str, Enum)`:
  - `DOCUMENT="document"`
  - `QUERY="query"`
- Produces immutable `EmbeddingRequest(request_id: str, input_kind: EmbeddingInputKind, texts: tuple[str, ...])`.
- Produces immutable `EmbeddingDescriptor(backend_name: str, backend_version: str, model_name: str, model_digest: str | None, architecture: str | None, parameter_count: int | None, parameter_size: str | None, quantization: str | None, context_length: int | None, embedding_dimension: int, capabilities: tuple[str, ...])`.
- Produces immutable `EmbeddingVector(values: tuple[float, ...], dimension: int)`; public construction requires already normalized unit vectors.
- Produces internal/public helper `normalize_embedding_values(values: Iterable[float], *, expected_dimension: int | None = None) -> EmbeddingVector`.
- Produces immutable `EmbeddingResponse(request_id: str, model_name: str, model_digest: str | None, vectors: tuple[EmbeddingVector, ...], input_count: int, prompt_tokens: int | None, total_duration_ns: int | None, load_duration_ns: int | None)`.
- Produces `EmbeddingAdapter(Protocol)`:
  - `inspect(self) -> EmbeddingDescriptor`
  - `embed(self, request: EmbeddingRequest) -> EmbeddingResponse`
- Produces exceptions: `EmbeddingAdapterError`, `EmbeddingUnavailableError`, `EmbeddingModelNotFoundError`, `EmbeddingIdentityMismatchError`, `EmbeddingProtocolError`, `EmbeddingTimeoutError`.

- [ ] **Step 1: Write failing generic embedding contract tests**

Pin:
- all public records are frozen;
- runtime values, not only type hints, are validated;
- blank request/text/model/backend fields fail;
- request texts are nonempty strings;
- input kind must be `EmbeddingInputKind`;
- descriptor embedding dimension is positive;
- capabilities are canonical sorted/unique;
- optional integer metrics are nonnegative;
- generic files/names contain no Ollama/Qwen coupling.

- [ ] **Step 2: Write failing vector-normalization tests**

Pin:
- `normalize_embedding_values((3.0, 4.0))` returns approximately `(0.6, 0.8)`, dimension 2;
- accepted vector unit norm is within `1e-12` of 1.0;
- empty vector fails;
- raw L2 norm <= `1e-12` fails;
- NaN/Inf fail;
- `expected_dimension` mismatch fails;
- bool/non-numeric vector values fail;
- direct `EmbeddingVector` construction rejects non-unit vectors.

- [ ] **Step 3: Run contract tests and verify RED**

Run:
```powershell
python -m pytest -q tests/test_embedding_contracts.py
```

Expected: import/collection FAIL because `flywire_asca.embedding` does not exist.

- [ ] **Step 4: Implement contracts/protocol/errors only**

Use frozen/slotted dataclasses and standard-library math. Keep backend-specific parsing out of these files.

- [ ] **Step 5: Write failing A005 task/roadmap tests**

Pin:
- CURRENT points to A005 ACTIVE / Issue #5 / branch `research/a005-vector-memory`;
- ROADMAP A005 title is `Semantic Vector Memory Retrieval` and ACTIVE;
- A006-A011 remain unchanged/planned;
- README states A005 is Vector + Metadata and graph is deferred to an evidence gate;
- task file records the three decision outcomes and no graph implementation scope.

- [ ] **Step 6: Run ledger tests and verify RED**

Run:
```powershell
python -m pytest -q tests/test_a005_task_ledger.py tests/test_task_ledger.py
```

Expected: FAIL because A005 is still PLANNED under the old title.

- [ ] **Step 7: Create GitHub Issue #5 and activate A005**

Issue title:
`A005 — Semantic Vector Memory Retrieval`

Record Issue #5 in CURRENT/task doc. Do not open a graph task.

- [ ] **Step 8: Update roadmap/README/task docs**

A005 becomes ACTIVE with the approved Vector + Metadata boundary. Preserve A001-A004 historical reports.

- [ ] **Step 9: Run Task 1 gates**

Run:
```powershell
python -m pytest -q tests/test_embedding_contracts.py tests/test_a005_task_ledger.py tests/test_task_ledger.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
git diff --check
```

Expected: all PASS.

- [ ] **Step 10: Commit Task 1**

Commit:
```text
Add A005 embedding contracts and task activation
```

### Task 2: Implement local Ollama embedding adapter with strict vector validation

**Files:**
- Create: `src/flywire_asca/embedding/ollama.py`
- Create: `tests/test_ollama_embedding_adapter.py`
- Modify: `src/flywire_asca/embedding/__init__.py`
- Modify: `docs/development/tasks/A005-semantic-vector-memory-retrieval.md`

**Interfaces:**
- Consumes A004-style JSON transport semantics but does not depend on `ModelAdapter`.
- Produces internal `EmbeddingJsonTransport(Protocol)`:
  - `request_json(self, method: str, path: str, payload: dict[str, object] | None, timeout_seconds: float) -> dict[str, object]`.
- Produces `UrllibEmbeddingJsonTransport(base_url: str)`.
- Produces `OllamaEmbeddingAdapter(model_name: str, *, base_url: str = "http://127.0.0.1:11434", expected_digest: str | None = None, expected_dimension: int | None = None, timeout_seconds: float = 120.0, keep_alive: str = "5m", transport: EmbeddingJsonTransport | None = None)`.
- `inspect()` calls GET `/api/version`, GET `/api/tags`, POST `/api/show`.
- `embed()` calls POST `/api/embed` with `model`, `input`, and bounded keep-alive/options required by the qualified profile.
- Query request mapping prepends the fixed profile instruction to each query text; document requests send retrieval text without that query instruction.

- [ ] **Step 1: Write failing descriptor/identity tests with fake transport**

Pin:
- runtime version/tag/full digest parsing;
- architecture/family/parameter metadata/context/dimension parsing when provided by `/api/show`;
- exact tag matching;
- missing model -> `EmbeddingModelNotFoundError`;
- strict digest mismatch -> `EmbeddingIdentityMismatchError`;
- successful descriptor cached per adapter instance, failed inspection not cached.

- [ ] **Step 2: Write failing embed-request mapping tests**

Assert:
- document request preserves text order and content;
- query request transforms each input to exactly:
  `Instruct: Retrieve stored memories that are semantically relevant to the query.\nQuery: <text>`;
- no generative chat endpoint, tools, images, or Qwen3.5:4b call;
- batch input order is preserved;
- keep-alive and model tag are explicit.

- [ ] **Step 3: Write failing response/vector safety tests**

Pin:
- response vector count equals request text count;
- each vector is normalized client-side;
- raw zero/near-zero vector fails;
- NaN/Inf fails;
- inconsistent dimensions in one batch fail;
- dimension differing from strict `expected_dimension` fails;
- later request dimension drift against the cached qualified descriptor/observed dimension fails;
- malformed/non-object JSON and HTTP non-2xx fail as protocol errors;
- socket timeout -> `EmbeddingTimeoutError`;
- connection/URL failure -> `EmbeddingUnavailableError`;
- token/timing metadata maps only when valid nonnegative integers.

- [ ] **Step 4: Run focused tests and verify RED**

Run:
```powershell
python -m pytest -q tests/test_ollama_embedding_adapter.py
```

Expected: FAIL because the embedding adapter does not exist.

- [ ] **Step 5: Implement transport and adapter minimally**

Use standard-library HTTP/JSON. Treat a 200 response containing unusable vectors as failure. Do not retry or restart Ollama automatically.

- [ ] **Step 6: Run focused/full portable gates**

Run:
```powershell
python -m pytest -q tests/test_ollama_embedding_adapter.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
git diff --check
```

Expected: all PASS without requiring Ollama.

- [ ] **Step 7: Update resume pointer and commit Task 2**

Commit:
```text
Add local Ollama embedding adapter
```

### Task 3: Implement immutable Vector + Metadata exact-cosine index

**Files:**
- Create: `src/flywire_asca/vector_memory/__init__.py`
- Create: `src/flywire_asca/vector_memory/models.py`
- Create: `src/flywire_asca/vector_memory/index.py`
- Create: `tests/test_vector_memory_index.py`
- Modify: `docs/development/tasks/A005-semantic-vector-memory-retrieval.md`

**Interfaces:**
- Produces immutable `VectorMemoryDocument(memory: MemoryRecord, retrieval_text: str, entity_ids: tuple[str, ...] = (), context_tags: tuple[str, ...] = (), source_tags: tuple[str, ...] = ())`.
- Produces immutable `VectorMemoryQuery(query_id: str, query_text: str, top_k: int = 5, minimum_similarity: float = 0.0, allowed_memory_kinds: tuple[MemoryKind, ...] = (), required_entity_ids: tuple[str, ...] = (), required_context_tags: tuple[str, ...] = (), required_source_tags: tuple[str, ...] = ())`.
- Produces immutable `VectorMemoryHit(memory_id: str, similarity: float, memory_kind: MemoryKind, proposition_confidence: float, evidence_ids: tuple[str, ...], entity_ids: tuple[str, ...], context_tags: tuple[str, ...], source_tags: tuple[str, ...])`.
- Produces immutable `VectorMemoryResult(query_id: str, hits: tuple[VectorMemoryHit, ...], stored_count: int, metadata_eligible_count: int, scored_vector_count: int, above_threshold_count: int, returned_count: int, embedding_model_name: str, embedding_model_digest: str | None, embedding_profile: str)`.
- Produces `ExactVectorMemoryIndex(documents: Iterable[VectorMemoryDocument], adapter: EmbeddingAdapter, *, embedding_profile: str)`.
- `search(self, query: VectorMemoryQuery) -> VectorMemoryResult`.
- Index construction embeds all document retrieval texts once using `EmbeddingInputKind.DOCUMENT` and stores normalized vectors.
- Search embeds one query using `EmbeddingInputKind.QUERY`.

- [ ] **Step 1: Write failing model-validation tests**

Pin:
- retrieval text nonblank;
- metadata tuples canonical sorted/unique;
- query ID/text nonblank;
- `top_k > 0`;
- threshold finite in [-1, 1];
- allowed memory kinds canonical unique;
- required filters canonical sorted/unique;
- hit similarity finite in [-1, 1];
- proposition confidence preserved from underlying memory.

- [ ] **Step 2: Write failing deterministic cosine/index-construction tests**

Using a deterministic fake embedding adapter:
- duplicate `memory_id` fails;
- document embedding response count must equal document count;
- every stored vector has same dimension;
- generator input is materialized once;
- index keeps immutable document/vector tuples;
- exact cosine ranking descends by score then ties by `memory_id`.

- [ ] **Step 3: Write failing metadata-filter tests**

Pin exact AND/all-required semantics:
- allowed memory kind excludes nonmembers before scoring;
- required entity IDs must all be contained;
- required context tags must all be contained;
- required source tags must all be contained;
- fields combine with logical AND;
- `metadata_eligible_count` is the post-filter count;
- `scored_vector_count == metadata_eligible_count`.

- [ ] **Step 4: Write failing ambiguity/confidence/threshold/top-K tests**

Pin:
- same-name documents without entity filter can both be returned;
- explicit entity filter can restrict one identity without vector-inferred identity;
- similarity ordering does not mutate or replace proposition confidence;
- below-threshold hits are removed;
- `above_threshold_count` is before Top-K truncation;
- `returned_count <= top_k`;
- no-hit result is valid and does not claim memory absence.

- [ ] **Step 5: Run focused tests and verify RED**

Run:
```powershell
python -m pytest -q tests/test_vector_memory_index.py
```

Expected: FAIL because vector-memory package/index do not exist.

- [ ] **Step 6: Implement models and exact index**

Search algorithm is deterministic:
1. metadata filter;
2. query embedding;
3. dot product against every eligible unit vector;
4. threshold filter;
5. sort by `(-similarity, memory_id)`;
6. Top-K truncate;
7. build raw count evidence.

Do not inspect A002 `AssociationEdge`.

- [ ] **Step 7: Run focused/full gates**

Run:
```powershell
python -m pytest -q tests/test_vector_memory_index.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
git diff --check
```

Expected: all PASS.

- [ ] **Step 8: Update resume pointer and commit Task 3**

Commit:
```text
Add exact vector metadata memory index
```

### Task 4: Add frozen portable benchmark, threshold calibration, and graph-decision evaluator

**Files:**
- Create: `src/flywire_asca/vector_memory/benchmark.py`
- Create: `tests/test_vector_memory_benchmark.py`
- Modify: `tests/test_ci_contract.py`
- Modify: `docs/development/tasks/A005-semantic-vector-memory-retrieval.md`

**Interfaces:**
- Produces `GraphDecision(str, Enum)`:
  - `VECTOR_SUFFICIENT="VECTOR_SUFFICIENT"`
  - `VECTOR_NEEDS_INDEX_OR_METADATA="VECTOR_NEEDS_INDEX_OR_METADATA"`
  - `GRAPH_JUSTIFIED="GRAPH_JUSTIFIED"`
- Produces immutable benchmark case/result/report records with:
  - expected relevant memory IDs in rank order/set form as declared by the case;
  - Recall@1, Recall@K, reciprocal rank;
  - no-hit correctness;
  - metadata-filter correctness;
  - false retrieval count;
  - ambiguity-preservation flag;
  - stored/eligible/scored/above-threshold/returned counts;
  - embedding request/input counts.
- Produces `build_a005_portable_calibration_fixture()`.
- Produces `calibrate_a005_threshold(...) -> float`.
- Produces `build_a005_portable_qualification_fixture(*, frozen_threshold: float)`.
- The calibration function is backend-agnostic and reused later on a separate physical development fixture; portable fake-vector thresholds are never reused as physical thresholds.
- Produces `run_vector_memory_benchmark(...) -> VectorMemoryBenchmarkReport`.
- Produces `qualify_a005_report(report: VectorMemoryBenchmarkReport) -> list[str]`.
- Produces `decide_graph_need(report: VectorMemoryBenchmarkReport) -> GraphDecision`.

- [ ] **Step 1: Write failing calibration/qualification separation tests**

Pin:
- portable calibration and portable qualification case IDs are disjoint;
- portable qualification builder requires an explicit frozen threshold;
- calibration returns one deterministic finite threshold in [-1, 1];
- qualification runner never recalibrates/tunes threshold;
- report records the exact frozen threshold/profile;
- tests explicitly state that a fake-vector threshold is algorithm-test evidence only and is not the physical Qwen threshold.

- [ ] **Step 2: Write failing fake-geometry benchmark tests**

Controlled qualification fixture includes:
1. English paraphrase;
2. Thai paraphrase;
3. Thai query -> English memory;
4. English query -> Thai memory;
5. exact wording;
6. same-name ambiguity preserved without identity filter;
7. entity-filter disambiguation;
8. context-filter correctness;
9. similarity/confidence independence;
10. at least 256 distractor memories;
11. threshold no-hit;
12. deterministic equal-score tie ordering.

Use fake embeddings with known geometry; no external model.

- [ ] **Step 3: Pin metrics and qualification gates**

Portable qualification requires:
- Recall@1 = 1.0 for cases declaring one unique best memory;
- Recall@K = 1.0 for all declared relevant-memory cases;
- no-hit correctness = 1.0;
- metadata-filter correctness = 1.0;
- false retrieval count = 0;
- ambiguity failures = 0;
- deterministic repeated report payload;
- all cost/count invariants consistent;
- no FLOP/energy/general compute-reduction claims.

- [ ] **Step 4: Write failing graph-decision rule tests**

Decision rules are deterministic and based on report failure categories:
- `GRAPH_JUSTIFIED` only when one or more declared relation-semantic/multi-memory cases fail in a way classified as requiring explicit relation/path semantics;
- otherwise `VECTOR_NEEDS_INDEX_OR_METADATA` when semantic correctness passes but excessive vector-scored/candidate-volume criteria declared by the fixture are violated;
- otherwise `VECTOR_SUFFICIENT`.

Portable fixture is expected to exercise all three rule branches through synthetic report objects, not force the live qualification to a preferred outcome.

- [ ] **Step 5: Run focused tests and verify RED**

Run:
```powershell
python -m pytest -q tests/test_vector_memory_benchmark.py
```

Expected: FAIL because benchmark module does not exist.

- [ ] **Step 6: Implement benchmark/calibration/decision logic**

Keep raw metrics primary. Store failure-category evidence explicitly so graph decision is auditable.

- [ ] **Step 7: Add portable CI boundary tests**

Pin that GitHub Actions:
- runs the normal full pytest suite;
- retains A003 qualification;
- does not run `ollama pull`, `ollama run`, `/api/embed`, `qualify_vector_memory_a005.py`, or localhost embedding calls.

- [ ] **Step 8: Run Task 4 gates and freeze portable threshold**

Run:
```powershell
python -m pytest -q tests/test_vector_memory_benchmark.py tests/test_ci_contract.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
git diff --check
```

Also run the deterministic portable calibration path and record that threshold only as portable algorithm-test evidence. Do not label it as the physical Qwen threshold.

- [ ] **Step 9: Update resume pointer and commit Task 4**

Commit:
```text
Add A005 vector retrieval benchmark
```

### Task 5: Implement local physical embedding/vector-memory qualification

**Files:**
- Create: `scripts/qualify_vector_memory_a005.py`
- Create: `tests/test_vector_memory_qualification_cli.py`
- Modify: `docs/development/tasks/A005-semantic-vector-memory-retrieval.md`

**Interfaces:**
- CLI defaults:
  - base URL `http://127.0.0.1:11434`;
  - model `qwen3-embedding:0.6b`;
  - expected dimension `1024`;
  - profile `qwen3-embedding-0.6b-vector-memory-v1`;
  - request timeout 120 seconds.
- Physical threshold is supplied explicitly after physical development-fixture calibration; no portable fake-vector threshold is used as the physical default.
- Full digest is initially discovered after local pull and then pinned in the task/report; subsequent qualification runs use strict digest matching.
- CLI prints deterministic UTF-8 JSON and optionally writes byte-identical `--output` evidence.
- Payload includes descriptor identity, embedding profile, vector health probes, physical retrieval metrics, threshold, and graph-decision inputs/outcome.

- [ ] **Step 1: Write failing qualification CLI tests with fake adapter/index**

Pin:
- default model/profile/dimension and required explicit physical threshold;
- vector-health evidence includes dimensions, norm min/max, repeated probe count, zero/non-finite failures;
- physical retrieval result contains same-language and cross-language cases;
- payload records model digest once discovered/pinned;
- no generative Qwen fields/tools/vision;
- UTF-8 Thai output works under a simulated Windows cp1252 console;
- digest/dimension/vector-health/retrieval failure exits nonzero;
- stdout and output file bytes match.

- [ ] **Step 2: Run CLI tests and verify RED**

Run:
```powershell
python -m pytest -q tests/test_vector_memory_qualification_cli.py
```

Expected: FAIL because physical qualification script does not exist.

- [ ] **Step 3: Implement qualification CLI**

The CLI must:
1. inspect the embedding model;
2. run repeated vector-health probes in English and Thai;
3. verify every vector is finite/nonzero/dimensionally stable/unit-normalized;
4. require an explicit frozen physical threshold;
5. build the declared physical qualification fixture (never the calibration fixture);
6. search with the frozen threshold;
7. calculate physical raw metrics;
8. call the graph-decision evaluator;
9. emit deterministic JSON.

- [ ] **Step 4: Run portable gates before model installation**

Run:
```powershell
python -m pytest -q tests/test_vector_memory_qualification_cli.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
git diff --check
```

Expected: all PASS with no physical embedding model required.

- [ ] **Step 5: Commit qualification tooling before pulling the model**

Commit:
```text
Add A005 local embedding qualification runner
```

- [ ] **Step 6: Verify model absence/presence and pull only if absent**

Read `ollama list`. If `qwen3-embedding:0.6b` is absent, run:
```powershell
ollama pull qwen3-embedding:0.6b
```

Record the exact resulting full digest through the local API/tag inspection.

No model files are committed.

- [ ] **Step 7: Discover/pin digest and calibrate the physical threshold on a development-only fixture**

After first model discovery:
- record the exact digest;
- run a declared **physical development/calibration fixture** whose case IDs/content are disjoint from final physical qualification;
- call the same `calibrate_a005_threshold(...)` algorithm using real Qwen embedding scores from that development fixture;
- freeze the resulting physical threshold;
- add the exact digest and frozen physical threshold to A005 task evidence/qualification defaults;
- add regression tests that strict digest mismatch fails and the final qualification command requires/uses the frozen physical threshold;
- commit this evidence/config change **before** running the physical qualification fixture;
- from that point onward do not change the digest or threshold unless the qualification attempt is explicitly invalidated and the process restarts from a new calibration revision.

- [ ] **Step 8: Run real local physical qualification as a managed session**

Run:
```powershell
python scripts/qualify_vector_memory_a005.py --output <ignored-local-evidence-json>
```

Require:
- exit 0;
- exact digest match;
- dimension 1024;
- repeated vector health probes all finite/nonzero/unit-normalized;
- no batch count/order/dimension violations;
- physical same-language/cross-language retrieval acceptance passes;
- frozen **physical** threshold from the separate development fixture is unchanged;
- physical qualification case IDs/content are disjoint from the physical calibration fixture;
- raw metrics recorded;
- one graph-decision outcome emitted.

If the frozen threshold fails on physical qualification, do not tune it on the final fixture. Record the negative result and let the graph/index decision gate consume the failure evidence.

- [ ] **Step 9: Record local physical evidence**

Copy only non-sensitive values to the task/report. Keep the raw JSON in ignored scratch.

### Task 6: Exact branch qualification, decision report, review, integration, and A005 closure

**Files:**
- Create: `docs/development/reports/ASCA-20261009-A005-vector-memory-retrieval.md`
- Modify: `docs/development/tasks/A005-semantic-vector-memory-retrieval.md`
- Modify: `docs/development/tasks/CURRENT.md`
- Modify: `docs/development/tasks/ROADMAP.md`
- Modify: `README.md`
- Modify: `tests/test_a005_task_ledger.py`
- Modify: `tests/test_task_ledger.py`

**Interfaces:**
- Consumes Tasks 1-5, portable benchmark report, frozen threshold, physical evidence, Git/GitHub state.
- Produces A005 DONE, one graph-decision outcome, A006 disposition, and final exact main evidence.
- A006 remains `Working Set / Selective Activation` if verdict is `VECTOR_SUFFICIENT` or `VECTOR_NEEDS_INDEX_OR_METADATA`.
- If verdict is `GRAPH_JUSTIFIED`, do **not** silently overwrite A006; the closure report recommends a roadmap decision for the next session rather than creating/renumbering a graph milestone during A005 closure.

- [ ] **Step 1: Run fresh exact branch gate**

Run:
```powershell
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
git diff --check HEAD^ HEAD
git status --short --branch
git rev-parse HEAD
```

Physical qualification must correspond to the same embedding/vector-memory implementation. If behavior code changed after the last physical run, rerun physical qualification.

- [ ] **Step 2: Verify A004 and FlyWireLLM isolation read-only**

Capture:
- A004 Qwen generative model/code remains unchanged;
- FlyWireLLM has no active training runner and repo state is unchanged/clean as applicable.

Do not start/stop/mutate FlyWireLLM.

- [ ] **Step 3: Push A005 branch and require exact portable CI**

Push without force and record exact CI run for the candidate SHA.

- [ ] **Step 4: Write A005 qualification and graph-decision report**

Report:
- candidate SHA/test count/audits/A003 gate/diff;
- embedding model tag/full digest/runtime metadata;
- embedding dimension/profile/query instruction version;
- portable fake calibration evidence separately from the frozen physical Qwen threshold;
- physical calibration-vs-qualification fixture separation;
- vector-health evidence;
- portable and physical Recall@1/Recall@K/MRR/no-hit/filter/false-retrieval/ambiguity metrics;
- stored/eligible/scored/above-threshold/returned counts;
- local token/timing metadata with non-FLOP/non-energy disclaimer;
- exact branch CI;
- FlyWireLLM paused/untouched;
- explicit verdict: `VECTOR_SUFFICIENT`, `VECTOR_NEEDS_INDEX_OR_METADATA`, or `GRAPH_JUSTIFIED`;
- exact evidence supporting that verdict.

- [ ] **Step 5: Write failing closure-transition tests**

Pin:
- A005 Status DONE;
- CURRENT points to A006 PLANNED / no issue yet;
- ROADMAP A005 title is Semantic Vector Memory Retrieval and DONE;
- report includes final candidate SHA, full embedding digest, frozen physical threshold, explicit calibration/qualification separation, physical metrics, branch CI, and exactly one decision outcome;
- no graph task is auto-created by closure.

Verify RED before editing ledger state.

- [ ] **Step 6: Transition A005 DONE / A006 PLANNED and run closure gate**

Run:
```powershell
python -m pytest -q tests/test_a005_task_ledger.py tests/test_task_ledger.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
git diff --check
```

Expected: all PASS.

- [ ] **Step 7: Commit closure and require exact closure-branch CI**

Commit:
```text
Qualify A005 semantic vector memory retrieval
```

Push and require exact closure CI.

- [ ] **Step 8: Whole-branch review and one fix pass**

Review `230280bf633d20631a0da38d55bdfd7716758734..closure-head` against spec/plan, prioritizing:
- hidden graph/identity inference;
- vector safety failures;
- batch-order/dimension drift;
- threshold leakage/overfitting;
- portable CI accidentally depending on Ollama/model install;
- similarity/confidence conflation;
- graph-decision rule biased toward a preferred answer.

Fix Critical/Important findings with RED->GREEN regression tests. If embedding/index/benchmark behavior changes, rerun physical qualification before integration.

- [ ] **Step 9: Fast-forward local main only**

Require clean synchronized main and descendant ancestry, then:
```powershell
git merge --ff-only research/a005-vector-memory
```

No reset/rebase/force push.

- [ ] **Step 10: Verify merged result, push main, and require exact main CI**

Run:
```powershell
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
git diff --check origin/main..HEAD
```

Push main normally and require CI success on the exact final SHA.

- [ ] **Step 11: Fetch and verify final synchronization**

Require:
- `HEAD == origin/main`;
- ahead/behind = 0/0;
- main worktree clean.

- [ ] **Step 12: Close Issue #5 and remove clean A005 worktree**

Closure comment records:
- final main SHA/test/audit/CI evidence;
- embedding model tag/full digest;
- frozen threshold;
- physical retrieval metrics;
- graph-decision outcome;
- FlyWireLLM paused/untouched;
- A006 PLANNED.

Remove worktree only after GREEN; preserve branch/history.

## A005 Non-Goals

A005 must not:
- build/traverse a typed association graph;
- implement multi-hop relation reasoning;
- use vector similarity as identity/truth;
- use proposition confidence as a vector score;
- use Qwen3.5:4b to select or rerank memory;
- inject vector hits into a generative prompt;
- add ANN/vector-database dependencies;
- persist vectors across restarts;
- train/fine-tune embedding models;
- use a reranker;
- restart FlyWireLLM;
- claim Top-K exact search is sublinear or compute-saving;
- tune the final threshold on the qualification fixture.

## Execution Order

Execute Tasks 1-6 sequentially with RED -> GREEN -> full regression -> commit for each software checkpoint. Keep portable CI independent of Ollama/model installation. Pull the physical embedding model only after portable qualification tooling is committed. Test the calibration algorithm with fake vectors first, then calibrate/freeze the real Qwen threshold from a separate physical development fixture before final physical qualification. A005 closure must report the graph decision without silently creating a graph task.
