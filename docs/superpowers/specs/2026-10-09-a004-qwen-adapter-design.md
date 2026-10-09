# A004 Local Model Adapter and Qwen3.5:4B Baseline Design Specification

Date: 2026-10-09
Status: DESIGN FOR USER REVIEW
Planned task: A004 — Local Model Adapter & Qwen3.5:4B Baseline
Branch: research/a004-qwen-adapter
Base: ASCA main at 1079e8eb6c11027e83de2e96547e1ac094fc9e16

## 1. Purpose

A004 introduces the first model-facing boundary for FlyWireASCA and qualifies
Qwen3.5:4b through local Ollama as the initial model-under-test.

The model is not part of ASCA core. ASCA remains model-agnostic.

A004 has two purposes:

1. define a stable model adapter contract that later ASCA components can call
   without knowing the backend implementation;
2. establish a reproducible Qwen-only baseline that later ASCA+Qwen
   experiments can compare against.

FlyWireLLM is no longer the near-term model-under-test. It remains an optional
future adapter candidate after its separate training work resumes and
qualifies.

## 2. Live runtime baseline

The local machine was inspected before this design.

Observed Ollama runtime:

- version: `0.32.15`
- host: local Ollama service
- model tag: `qwen3.5:4b`
- model digest:
  `2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd`
- format: GGUF
- family: `qwen35`
- metadata parameter size: `4.7B`
- quantization: `Q4_K_M`
- declared model context length: 262,144
- embedding length: 2,560
- reported capabilities: completion, vision, tools, thinking

The tag name `4b` is treated as the model name, while qualification records
the runtime-reported parameter size `4.7B` rather than claiming exactly four
billion parameters.

A manual CLI probe also established an important invocation constraint:
`--think false` can be parsed as prompt text in the observed CLI invocation.
A004 therefore does not rely on that spelling. Programmatic requests use the
HTTP API with a boolean `think: false`; manual diagnostics use
`--think=false`.

A direct local HTTP probe of `/api/chat` then verified the intended baseline
mapping on the real runtime using `think: false`, `stream: false`,
`num_ctx: 8192`, `num_predict: 8`, `temperature: 0`, and `seed: 0`. The model
returned content `OK`, `thinking: null`, `done_reason: stop`,
`prompt_eval_count: 16`, `eval_count: 2`, and populated duration metadata.
This is design evidence only; A004 qualification will repeat the probe through
the implemented adapter rather than treating this manual check as final
qualification.

## 3. Architecture choice

The selected architecture is:

```text
ASCA components
      |
      v
ModelAdapter protocol
      |
      +-------------------------+
      |                         |
      v                         v
OllamaModelAdapter        Future adapters
      |                    (FlyWireLLM,
      v                     other local/cloud
qwen3.5:4b                 models)
```

The adapter is an infrastructure boundary. It must not contain familiarity,
memory retrieval, working-set selection, surprise control, procedural memory,
or other cognitive policy.

That separation allows later comparisons such as:

```text
Prompt -> Qwen-only adapter
```

versus:

```text
Prompt
  -> ASCA familiarity / recall / selective state
  -> selected context
  -> same Qwen adapter
```

The same model backend can therefore be used on both sides of an experiment.

## 4. Roadmap migration

A004 is inserted before Associative Memory & Recall so that later cognitive
subsystems have a qualified model boundary available without depending on it.

The planned roadmap becomes:

- A001 — Repository & Research Foundation — DONE
- A002 — ASCA Architecture Contract — DONE
- A003 — Familiarity System — DONE
- A004 — Local Model Adapter & Qwen3.5:4B Baseline
- A005 — Associative Memory & Recall
- A006 — Working Set / Selective Activation
- A007 — Surprise, Uncertainty & Expansion
- A008 — Procedural Memory / Skill Chunking
- A009 — Integrated Cognitive Loop
- A010 — Dense / Non-selective Baseline Comparison
- A011 — ASCA v0.x Qualification

Completed historical evidence is not rewritten merely because task numbers
after A003 shift. A004 adds a roadmap-migration note mapping the old planned
A004-A010 names to new A005-A011 names.

## 5. Generic model contract

A004 adds a model namespace independent from Ollama.

### 5.1 ModelRequest

Proposed immutable fields:

- `request_id: str`
- `messages: tuple[ModelMessage, ...]`
- `max_output_tokens: int`
- `context_limit: int`
- `temperature: float`
- `seed: int | None`
- `thinking: bool`

A004 v0.1 is text-only. A request therefore contains no image payload and no
tool schema.

### 5.2 ModelMessage

Fields:

- `role: ModelRole` where v0.1 permits `system`, `user`, `assistant`
- `content: str`

Blank content is invalid.

### 5.3 ModelResponse

Proposed immutable fields:

- `request_id: str`
- `model_name: str`
- `model_digest: str | None`
- `content: str`
- `finish_reason: str | None`
- `prompt_tokens: int | None`
- `generated_tokens: int | None`
- `total_duration_ns: int | None`
- `load_duration_ns: int | None`
- `prompt_eval_duration_ns: int | None`
- `eval_duration_ns: int | None`

Timing/token fields are backend evidence. They are not normalized FLOP or
energy metrics.

### 5.4 ModelAdapter protocol

The stable interface is conceptually:

```python
class ModelAdapter(Protocol):
    def generate(self, request: ModelRequest) -> ModelResponse: ...
    def inspect(self) -> ModelDescriptor: ...
```

ASCA components depend on this protocol, never directly on Ollama APIs.

## 6. ModelDescriptor and reproducibility

`ModelDescriptor` records the model/runtime identity observed by the adapter:

- backend name;
- backend version;
- model tag/name;
- model digest when available;
- architecture/family;
- reported parameter size;
- quantization;
- declared context length;
- capability flags.

For the A004 qualified Qwen baseline, tag and full digest are both recorded.

If `qwen3.5:4b` later resolves to a different digest, the adapter may still
operate, but the old A004 qualification must not be silently reused. A new
qualification snapshot is required.

The repository does not vendor or redistribute Qwen weights.

## 7. Ollama adapter transport

The production A004 adapter uses the local Ollama HTTP API rather than spawning
the interactive CLI.

Reasons:

- structured request/response data;
- explicit boolean `think: false`;
- token/timing metadata is available directly;
- no terminal control sequences or spinner output;
- easier deterministic testing with a fake HTTP transport;
- avoids CLI argument ambiguity observed during design probing.

The first implementation uses the Python standard library HTTP client so A004
does not add a mandatory runtime dependency.

Default endpoint:

`http://127.0.0.1:11434`

The endpoint is configurable at adapter construction time for tests and future
local deployments.

A004 does not expose the local Ollama service to external networks.

## 8. Baseline generation profile

The qualification profile is intentionally conservative:

- model: `qwen3.5:4b`
- expected digest:
  `2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd`
- text-only
- tools: disabled / no tool definitions
- vision: disabled / no image payload
- thinking: `false`
- streaming: `false`
- context limit: 8,192 tokens
- maximum generated tokens: 256
- temperature: 0.0
- seed: 0 when supported by the backend options
- keep-alive: bounded local value, not part of semantic correctness

The model itself advertises a much larger context window, but A004 deliberately
uses 8K. Later ASCA experiments should demonstrate selective context use rather
than hide retrieval cost inside a huge model context.

A separate later experiment may qualify thinking-enabled operation. It must not
replace the thinking-off baseline.

## 9. Ollama request mapping

For the text-only v0.1 adapter, ASCA model messages map to Ollama chat-style
messages.

The outbound request must explicitly set:

- `model`;
- `messages`;
- `stream: false`;
- `think: false` for the default baseline;
- options containing the configured context/output/generation controls.

No tools or images are sent.

Backend responses are converted into `ModelResponse`; ASCA callers do not
receive raw Ollama dictionaries.

Unknown extra Ollama response fields are ignored rather than leaked into the
public contract.

## 10. Error model

A004 distinguishes at least:

- `ModelUnavailableError`: local endpoint unavailable;
- `ModelNotFoundError`: requested model tag absent;
- `ModelIdentityMismatchError`: strict qualification expected one digest but
  the tag resolves to another;
- `ModelProtocolError`: malformed/unsupported backend response;
- `ModelTimeoutError`: request exceeded the configured timeout.

Exceptions must not silently turn into empty model responses.

Qualification fails closed on model/digest mismatch.

Routine adapter use outside qualification may opt out of strict digest pinning,
but the observed descriptor is still returned/recorded.

## 11. Testability and transport isolation

Network logic is isolated behind a minimal internal transport boundary.

Most tests do not run Qwen. They use deterministic fake Ollama HTTP responses
to verify:

- request mapping;
- explicit `think: false`;
- context/output/seed/temperature options;
- response normalization;
- error translation;
- model-descriptor parsing;
- digest mismatch behavior.

A smaller integration/qualification suite targets the real local Ollama/Qwen
runtime.

This keeps CI portable: GitHub Actions does not need to download a multi-GB
model.

## 12. Portable CI vs local model qualification

A004 uses two evidence layers.

### Portable repository CI

GitHub Actions runs:

- unit/contract tests;
- fake-transport adapter tests;
- architecture audit;
- repository qualifier;
- no real Qwen download/inference.

### Local physical qualification

A dedicated local command validates the actual machine:

1. Ollama API reachable;
2. runtime version captured;
3. `qwen3.5:4b` installed;
4. full digest captured and matches the qualification target;
5. model descriptor matches required family/quantization metadata;
6. thinking-off generation request succeeds;
7. response contains nonempty text and model/token/timing evidence;
8. baseline fixture passes.

The local qualification artifact is committed as evidence, while raw model
weights are not.

## 13. Qwen-only baseline fixture

A004 does not attempt to prove ASCA usefulness yet. It establishes the model
control to be reused later.

The controlled Qwen-only fixture includes machine-scoreable cases in both Thai
and English, for example:

- exact constrained answer;
- simple factual transformation using only information in the prompt;
- short JSON extraction/selection;
- Thai instruction following;
- English instruction following;
- a deliberately missing-information case where the expected behavior is to
  say that the supplied context is insufficient.

The fixture should avoid volatile world knowledge so results do not depend on
model cutoff or web access.

The same cases can later be extended with ASCA-provided context for paired
comparison.

## 14. Baseline scoring

A004 records:

- case count;
- exact/structured task pass count;
- pass rate;
- prompt tokens;
- generated tokens;
- total duration;
- load duration;
- prompt evaluation duration;
- generation evaluation duration;
- model tag and digest;
- runtime version;
- generation profile.

The baseline report separates correctness metrics from performance metadata.

Timing values are local-machine observations, not general model speed claims.

Token/timing values are not converted into FLOP or energy claims.

## 15. Determinism policy

LLM generation cannot be assumed byte-identical across all runtimes/hardware,
even with temperature 0 and a seed.

Therefore qualification does not require identical raw prose across repeated
runs except where the task itself requires an exact constrained token/string.

Machine-scored fixture cases use one of:

- exact normalized string match;
- parsed JSON/schema/value checks;
- explicit allowed answer set.

The benchmark records the full generation profile and model digest so drift is
detectable.

## 16. ASCA/Qwen separation

No A003 familiarity behavior is moved into the model adapter.

The Qwen adapter does not:

- look up familiarity traces;
- retrieve associative memory;
- choose working-set items;
- expand compute on surprise;
- learn procedures;
- mutate ASCA memory.

Later integrated flow is expected to look like:

```text
input
  -> ASCA components produce selected state/context
  -> ModelRequest
  -> ModelAdapter
  -> Qwen
  -> ModelResponse
  -> ASCA evaluation/control
```

The model remains replaceable.

## 17. FlyWireLLM status

The previously active FlyWireLLM training process was checked after the user's
pause instruction and is no longer running.

A004 must not restart it.

FlyWireLLM remains an independent repository and future adapter candidate. No
A004 acceptance criterion depends on FlyWireLLM.

## 18. Planned package boundaries

Proposed layout:

```text
src/flywire_asca/model/
    __init__.py
    contracts.py
    errors.py
    adapter.py
    ollama.py
    baseline.py

scripts/
    qualify_qwen_a004.py

tests/
    test_model_contracts.py
    test_ollama_adapter.py
    test_qwen_baseline.py
    test_a004_task_ledger.py
```

The exact filenames may be adjusted in the implementation plan if needed, but
the component boundaries above are part of this design.

## 19. Roadmap/document updates

When A004 implementation is activated:

- `ROADMAP.md` is migrated to A004-A011 numbering;
- `CURRENT.md` points to A004 ACTIVE;
- a roadmap migration document records the old-to-new mapping;
- README current-stage text is corrected from the stale A001 wording;
- project boundary text states that Qwen3.5:4b is the current model-under-test
  while ASCA remains model-agnostic;
- completed A001-A003 historical qualification reports are not rewritten.

## 20. Acceptance criteria

A004 can close only when:

- generic model contracts are independent from Ollama;
- Ollama adapter unit tests use fake transport and pass without Ollama;
- outbound baseline requests explicitly disable thinking;
- no tools/images are sent by the text-only baseline;
- model descriptor/digest parsing is tested;
- strict digest mismatch fails closed;
- portable GitHub CI passes without downloading Qwen;
- local Ollama physical qualification passes for `qwen3.5:4b`;
- the observed qualification digest is recorded;
- Qwen-only Thai/English controlled baseline passes its declared scoring gates;
- token/timing/model metadata is captured as evidence;
- no FLOP/energy claim is inferred from those metrics;
- FlyWireLLM remains stopped and untouched;
- exact branch CI and final main CI pass;
- main synchronizes 0/0 and is clean;
- A005 — Associative Memory & Recall remains PLANNED.

## 21. Non-goals

A004 does not:

- train or fine-tune Qwen;
- modify Qwen weights or Modelfile;
- expose Ollama externally;
- implement RAG;
- implement associative memory;
- integrate A003 familiarity into prompts yet;
- enable tools or vision;
- qualify thinking-enabled Qwen;
- benchmark Qwen against FlyWireLLM;
- claim ASCA improves Qwen;
- claim hardware energy/FLOP savings.

## 22. Success definition

A004 succeeds when FlyWireASCA can address a stable model-independent adapter
contract, the real local `qwen3.5:4b` can be qualified through that contract,
and a reproducible Qwen-only control baseline exists for later ASCA-vs-control
experiments.

That success means the test harness is ready for cognitive integration. It does
not yet demonstrate that ASCA improves the model.
