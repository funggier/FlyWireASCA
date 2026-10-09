# A005 Semantic Vector Memory Retrieval Design Specification

Date: 2026-10-09
Status: DESIGN FOR USER REVIEW
Planned task: A005 — Semantic Vector Memory Retrieval
Branch: research/a005-vector-memory
Base: ASCA main at 230280bf633d20631a0da38d55bdfd7716758734

## 1. Purpose

A005 tests a deliberately simpler memory architecture before introducing a
typed associative graph.

The milestone asks:

> Is embedding/vector similarity plus explicit metadata sufficient for useful,
> safe, inspectable memory retrieval in FlyWireASCA?

If the answer is yes, ASCA should not add graph complexity merely because the
project name contains "Associative".

A005 therefore implements semantic vector retrieval first and moves the
graph decision to an evidence-based decision gate after A005 qualification.

## 2. Architectural decision

A005 is **Vector + Metadata**, not Hybrid Vector + Graph.

The retrieval path is:

```text
Stored memory text
     |
     v
EmbeddingAdapter
     |
     v
validated normalized vector
     |
     +---- explicit metadata ----+
     |                           |
     v                           v
             VectorMemoryIndex


User/query text
     |
     v
EmbeddingAdapter
     |
     v
validated normalized query vector
     |
     v
metadata pre-filter
     |
     v
cosine similarity
     |
     v
minimum threshold
     |
     v
deterministic Top-K
     |
     v
VectorMemoryHit evidence bundle
```

The embedding/vector score answers only:

> "How semantically similar is this query to this stored memory text?"

It does not answer:

- whether two names refer to the same person;
- whether a proposition is true;
- whether one memory caused another;
- whether two events are temporally ordered;
- whether a retrieved item should be believed;
- whether Qwen should present it as a final answer.

## 3. What happens to the graph idea

The old planned title:

`A005 — Associative Memory & Recall`

changes to:

`A005 — Semantic Vector Memory Retrieval`.

A typed graph is explicitly **deferred, not rejected**.

After A005, the project will hold a decision gate with three possible outcomes:

1. **VECTOR_SUFFICIENT** — retrieval quality and failure profile are good enough;
   continue without a graph.
2. **VECTOR_NEEDS_INDEX_OR_METADATA** — quality is acceptable but retrieval
   scalability/selectivity needs stronger metadata or ANN/vector indexing;
   improve vector retrieval without introducing a graph.
3. **GRAPH_JUSTIFIED** — controlled failures demonstrate a need for explicit
   typed multi-hop/identity/causal/temporal relations; introduce the earlier
   typed-graph approach in a later milestone.

The graph is adopted only when benchmark evidence justifies it.

## 4. Relationship to completed ASCA subsystems

### A003 Familiarity

A003 remains valid and independent.

A005 does not require A003 Familiarity as a hard gate. That would confound the
first vector retrieval experiment.

Later control logic may use Familiarity to decide whether a vector lookup is
worth performing, but A005 first measures vector retrieval directly.

### A004 Model Adapter / Qwen3.5:4b

Qwen3.5:4b is not used to choose vector memories.

A005 retrieval must remain testable without the generative model.

Later integrated ASCA stages may turn retrieved hits into selected model
context through the A004 adapter. That later step must not retroactively define
retrieval correctness.

### A002 AssociationEdge

The A002 `AssociationEdge` contract is not removed.

A005 simply does not construct or traverse association edges.

This preserves compatibility if the later evidence-based decision gate chooses
the graph path.

## 5. Embedding model boundary

A005 introduces a backend-neutral embedding interface rather than letting
vector-memory code call Ollama directly.

Conceptually:

```python
class EmbeddingAdapter(Protocol):
    def inspect(self) -> EmbeddingDescriptor: ...
    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse: ...
```

Vector memory depends on `EmbeddingAdapter`, not on Qwen or Ollama.

This allows later replacement with:

- a different local embedding model;
- a smaller/larger Qwen embedding model;
- an accelerated backend;
- deterministic test embeddings.

## 6. First physical embedding model-under-test

The first planned local embedding model is:

`qwen3-embedding:0.6b`

Reason:

- it is an embedding-specific model rather than a chat model;
- the Ollama package is about 639 MB;
- the family is designed for multilingual semantic retrieval;
- the 0.6B model exposes a 1024-dimensional embedding representation;
- the upstream family supports 100+ languages and multilingual/cross-lingual
  retrieval;
- Qwen3 explicitly includes Thai among its supported language families.

The model is not currently installed in the observed local Ollama model list.
A005 physical qualification may pull it after implementation approval.

The repository does not vendor the weights.

A005 will record and pin the full local Ollama model digest after installation
rather than relying only on the tag.

## 7. Embedding profile

The initial A005 profile keeps variables minimal:

- model: `qwen3-embedding:0.6b`;
- vector dimension: full 1024 dimensions;
- no MRL dimensional truncation;
- document input: memory retrieval text;
- query input: fixed retrieval instruction plus query text;
- output vectors: client-validated and client-normalized to unit L2 norm;
- no reranker;
- no generative Qwen call.

The fixed query instruction is English even for Thai queries because Qwen's
embedding guidance recommends English instructions in multilingual retrieval
settings.

Proposed query template:

```text
Instruct: Retrieve stored memories that are semantically relevant to the query.
Query: <query text>
```

The instruction string is versioned as part of the embedding profile so future
changes cannot silently reuse old qualification evidence.

## 8. Generic embedding contracts

### 8.1 EmbeddingInputKind

```text
DOCUMENT
QUERY
```

This is semantic intent, not a backend-specific request field.

### 8.2 EmbeddingRequest

Immutable fields:

- `request_id: str`
- `input_kind: EmbeddingInputKind`
- `texts: tuple[str, ...]`

Blank inputs are invalid.

### 8.3 EmbeddingDescriptor

Immutable fields:

- backend name/version;
- model name;
- model digest if available;
- architecture/family;
- parameter count/size if available;
- quantization if available;
- context length if available;
- embedding dimension;
- capabilities.

### 8.4 EmbeddingVector

Immutable fields:

- `values: tuple[float, ...]`
- `dimension: int`

Contract validation requires:

- dimension > 0;
- number of values equals dimension;
- every value is finite;
- L2 norm is greater than a small epsilon;
- after adapter normalization, vector norm is approximately 1.

Zero/near-zero vectors are invalid. The initial numerical guard uses a finite
L2 norm greater than `1e-12`; normalized vectors are accepted only when their
post-normalization norm is within a small floating-point tolerance of 1.

### 8.5 EmbeddingResponse

Fields:

- request ID;
- model name/digest;
- vectors in input order;
- optional backend token/timing metadata.

Number of vectors must equal number of input texts.

## 9. Ollama embedding adapter

The physical A005 adapter uses the local Ollama `/api/embed` endpoint through
standard-library HTTP transport.

It remains separate from the A004 generative `OllamaModelAdapter` because
generation and embedding have different public contracts and failure modes.

The adapter must:

- inspect runtime/model identity;
- submit text input to `/api/embed`;
- preserve vector order;
- reject missing/malformed embeddings;
- reject non-finite values;
- reject zero/near-zero vectors;
- reject inconsistent dimensions;
- L2-normalize accepted vectors client-side;
- fail closed on strict model digest mismatch.

A successful HTTP status is not sufficient evidence that the embedding is
usable.

This guard is especially important because recent Ollama embedding bug reports
describe successful HTTP responses containing all-zero vectors under some
loads. A005 therefore validates vector norms before indexing or searching.

## 10. Memory retrieval record

A005 adds a retrieval-layer record rather than changing A002
`MemoryRecord`.

Conceptually:

```python
VectorMemoryDocument(
    memory: MemoryRecord,
    retrieval_text: str,
    entity_ids: tuple[str, ...],
    context_tags: tuple[str, ...],
    source_tags: tuple[str, ...],
)
```

The A002 memory retains proposition confidence and evidence IDs.

The vector retrieval layer adds only retrieval text and filterable metadata.

Metadata fields are immutable, sorted, unique, and explicit.

No arbitrary mutable dictionary is used as the qualification contract.

## 11. Metadata filtering

A005 query metadata filters may constrain:

- `MemoryKind`;
- entity IDs;
- context tags;
- source tags.

Filtering occurs **before** cosine scoring.

Semantics:

- empty filter means no restriction for that field;
- `allowed_memory_kinds`: the document memory kind must be a member of the
  allowed set;
- `required_entity_ids`: every requested entity ID must be present in the
  document `entity_ids`;
- `required_context_tags`: every requested context tag must be present in the
  document `context_tags`;
- `required_source_tags`: every requested source tag must be present in the
  document `source_tags`;
- filters across fields are combined with logical AND;
- metadata is a retrieval constraint, not a truth inference.

Example:

A semantic query for "Where does Somchai work?" with an entity ID for one known
Somchai may exclude another memory with the same surface name before vector
ranking.

Without an identity metadata constraint, A005 must preserve the ambiguity
rather than invent identity.

## 12. Index and search baseline

The first implementation is an in-memory exact cosine index.

Why exact search first:

- it provides a correctness oracle;
- it avoids confounding retrieval quality with ANN approximation;
- it is deterministic;
- it keeps external dependencies at zero.

For every query:

1. validate and embed the query;
2. apply metadata filters;
3. score every surviving vector by cosine similarity;
4. discard scores below `minimum_similarity`;
5. sort descending by similarity;
6. break exact score ties by `memory_id`;
7. return at most `top_k`.

Because stored/query vectors are normalized, cosine similarity is their dot
product.

A005 must explicitly record how many documents were:

- stored;
- metadata-eligible;
- vector-scored;
- above threshold;
- returned.

This is important because exact brute-force vector search does **not** claim
sublinear retrieval compute.

## 13. Search query and result

### VectorMemoryQuery

Fields include:

- query ID;
- query text;
- `top_k` (strictly positive);
- `minimum_similarity` (finite and within [-1, 1]);
- optional allowed memory kinds;
- optional required entity IDs;
- optional required context tags;
- optional required source tags.

### VectorMemoryHit

Contains:

- memory ID;
- similarity score;
- memory kind;
- proposition confidence;
- evidence IDs;
- retrieval metadata needed for audit.

Similarity and proposition confidence remain separate values.

A high vector score never upgrades proposition confidence.

### VectorMemoryResult

Contains:

- query ID;
- hits in deterministic ranking order;
- stored count;
- metadata-eligible count;
- scored-vector count;
- above-threshold count;
- returned count;
- embedding model name/digest/profile.

A005 does not ask Qwen to rewrite or judge these hits.

## 14. Storage and mutation policy

A005 v0.1 keeps storage intentionally simple:

- in-memory index;
- immutable indexed documents/vectors after construction;
- no online learning;
- no autonomous memory creation;
- no memory deletion/decay policy;
- no persistence/vector database yet.

An index is built from a finite declared set of documents.

Duplicate `memory_id` values are rejected at construction. Each indexed vector
must have the same qualified dimension. Document metadata tuples must already
be canonical sorted/unique values or be normalized into that canonical form at
the retrieval-layer contract boundary.

This isolates retrieval quality before introducing storage-system behavior.

## 15. Retrieval states and evidence boundary

A005 is retrieval, not full cognitive recollection.

It therefore does not use vector similarity to manufacture:

- `SAME_PERSON`;
- causal relation;
- temporal relation;
- `CONFLICTING_RECALL`;
- factual certainty.

A no-hit result means only that the current vector/metadata/threshold profile
did not retrieve evidence.

It does not prove the memory is absent from reality.

Later ASCA control may map retrieval evidence into A002 retrieval states.

## 16. Portable benchmark design

Portable CI uses deterministic fake embedding adapters so no Ollama model is
required.

The controlled benchmark covers at least:

1. English semantic paraphrase;
2. Thai semantic paraphrase;
3. Thai query -> English memory cross-lingual retrieval;
4. English query -> Thai memory cross-lingual retrieval;
5. exact wording;
6. same-name ambiguous documents;
7. entity metadata filter disambiguation;
8. context metadata filtering;
9. proposition-confidence independence from similarity;
10. distractor corpus;
11. threshold no-hit;
12. deterministic score-tie ordering;
13. malformed/zero/non-finite/wrong-dimension vector rejection.

The fake embedding fixture is deliberately constructed so expected vector
geometry is known exactly.

## 17. Physical embedding qualification

After the software path is portable-GREEN, local qualification will:

1. install/pull `qwen3-embedding:0.6b` if absent;
2. record Ollama runtime version;
3. record full model tag/digest and descriptor metadata;
4. verify the expected embedding dimension;
5. embed controlled English and Thai document/query pairs;
6. verify every vector is finite and nonzero;
7. verify normalized vector norms;
8. run a small semantic retrieval fixture;
9. verify same-language and cross-language retrieval sanity;
10. record token/timing metadata exposed by Ollama;
11. run repeated probes sufficient to catch obvious zero-vector behavior in
    the qualification session.

A005 does not claim the physical fixture establishes universal retrieval
quality.

## 18. Physical model safety checks

Qualification fails if any accepted vector:

- contains NaN or infinity;
- has zero/near-zero norm;
- has a dimension different from the qualified model dimension;
- changes dimension across requests;
- cannot be normalized;
- arrives in the wrong batch order/count.

The implementation does not automatically restart Ollama when a bad vector is
observed. It fails visibly so the underlying runtime condition can be
investigated.

## 19. Benchmark metrics

A005 records raw metrics including:

- Recall@1;
- Recall@K;
- Mean Reciprocal Rank where meaningful;
- no-hit correctness;
- metadata-filter correctness;
- false retrieval count;
- ambiguity preservation;
- stored memory count;
- metadata-eligible count;
- vectors scored;
- candidates above threshold;
- returned candidates;
- embedding requests;
- embedding input count;
- backend token/timing metadata when available;
- retrieval latency as descriptive evidence when measured physically.

Raw metrics are primary.

A005 does not collapse them into a single "intelligence efficiency" score.

## 20. Threshold policy

A cosine threshold is a retrieval parameter, not a probability of truth.

The initial threshold must be calibrated only from declared development
fixtures and then frozen before qualification fixtures are scored.

Qualification must not tune the threshold on the same cases it reports as
final evidence.

If no robust threshold can separate relevant/irrelevant physical cases, that
is a valid negative result for the vector-only experiment.

## 21. Qwen3.5:4b integration boundary

A005 does not feed retrieved memories to Qwen3.5:4b yet.

That separation gives two independent artifacts:

- A004: qualified generative control model;
- A005: qualified semantic memory retriever.

A later integration milestone can compose them:

```text
query
 -> vector memory retrieval
 -> bounded hits
 -> selected model context
 -> Qwen3.5:4b
```

At that point retrieval quality can be separated from answer-generation
quality.

## 22. Relationship to selective compute

Vector-only retrieval should not be credited with compute savings merely
because it returns top-K.

The exact in-memory baseline still scores every metadata-eligible vector.

A005 therefore reports `scored_vector_count`.

Possible future reductions include:

- stronger metadata pruning;
- ANN/vector database;
- A003 Familiarity gating;
- caching;
- typed graph routing.

Those are future hypotheses, not A005 claims.

## 23. Evidence-based graph decision gate

At A005 closure, the report must explicitly evaluate whether the earlier typed
graph approach is justified.

Evidence supporting **VECTOR_SUFFICIENT** includes:

- strong semantic/cross-lingual retrieval;
- acceptable ambiguity behavior with metadata;
- low false retrieval under fixed threshold;
- no benchmark cases requiring explicit relation paths.

Evidence supporting **VECTOR_NEEDS_INDEX_OR_METADATA** includes:

- retrieval quality is adequate;
- failures are mainly scalability/filtering/candidate-volume issues rather than
  missing relation semantics.

Evidence supporting **GRAPH_JUSTIFIED** includes reproducible cases where:

- required evidence is distributed across multiple memories and cannot be
  recovered by useful top-K semantic similarity;
- same-name/entity ambiguity cannot be resolved safely with available metadata;
- causal/temporal/ownership/path semantics are required;
- vector similarity repeatedly retrieves semantically similar but relationally
  wrong memories.

No graph milestone is created merely because one was originally planned.

## 24. Planned package boundaries

Proposed layout:

```text
src/flywire_asca/embedding/
    __init__.py
    contracts.py
    adapter.py
    errors.py
    ollama.py

src/flywire_asca/vector_memory/
    __init__.py
    models.py
    index.py
    benchmark.py

scripts/
    qualify_vector_memory_a005.py

tests/
    test_embedding_contracts.py
    test_ollama_embedding_adapter.py
    test_vector_memory_index.py
    test_vector_memory_benchmark.py
    test_a005_task_ledger.py
```

Embedding and vector-memory packages remain separate so a future storage/index
implementation can change without changing embedding backends.

## 25. Acceptance criteria

A005 can close only when:

- the roadmap title is migrated to Semantic Vector Memory Retrieval;
- generic embedding contracts do not depend on Ollama/Qwen;
- fake embedding/unit tests require no external model;
- in-memory exact cosine retrieval is deterministic;
- metadata filters are deterministic and audited;
- similarity remains separate from proposition confidence;
- same-name ambiguity is preserved without identity metadata;
- identity metadata can constrain retrieval without vector-inferred identity;
- zero/non-finite/wrong-dimension vectors fail closed;
- portable English/Thai/cross-lingual benchmark passes its declared gates;
- real local `qwen3-embedding:0.6b` physical qualification passes;
- full embedding model digest/profile is recorded;
- A004 Qwen generative baseline remains intact;
- FlyWireLLM remains paused/untouched;
- exact branch/final-main CI pass;
- main synchronizes 0/0 and is clean;
- the closure report records one explicit graph-decision outcome:
  VECTOR_SUFFICIENT, VECTOR_NEEDS_INDEX_OR_METADATA, or GRAPH_JUSTIFIED.

## 26. Non-goals

A005 does not:

- build or traverse a typed association graph;
- implement multi-hop relation reasoning;
- implement ANN/vector-database acceleration;
- persist vectors across process restarts;
- train/fine-tune embedding models;
- use a reranker;
- invoke Qwen3.5:4b to judge retrieval;
- integrate retrieval hits into a model prompt;
- use vector similarity as identity or truth;
- restart FlyWireLLM training;
- claim vector Top-K alone reduces compute.

## 27. Success definition

A005 succeeds when FlyWireASCA has a safe, inspectable, multilingual
Vector + Metadata memory retriever and enough controlled evidence to decide
whether a typed associative graph is actually necessary.

A negative result is also success if it cleanly demonstrates why vector-only
retrieval is insufficient and justifies the next architectural step.
