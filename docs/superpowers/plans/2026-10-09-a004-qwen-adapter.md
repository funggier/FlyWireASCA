# A004 Local Model Adapter & Qwen3.5:4B Baseline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a model-agnostic inference boundary to FlyWireASCA, implement a local Ollama adapter, and qualify `qwen3.5:4b` as the first reproducible Qwen-only model-under-test baseline without coupling ASCA core to Qwen or restarting FlyWireLLM training.

**Architecture:** A004 introduces immutable generic model request/response/descriptor contracts and a `ModelAdapter` protocol, then maps those contracts to Ollama through a standard-library JSON/HTTP transport. Portable CI uses fake transport only; real Qwen inference is a separate local physical qualification that pins tag, digest, runtime metadata, generation profile, and a small Thai/English machine-scored baseline.

**Tech Stack:** Python >=3.11 standard library only, `dataclasses`, `Enum`, `Protocol`, `urllib.request`, JSON, pytest, Ollama 0.32.15 local API, `qwen3.5:4b` Q4_K_M.

**Spec:** `docs/superpowers/specs/2026-10-09-a004-qwen-adapter-design.md`

## Global Constraints

- Repository: public `funggier/FlyWireASCA`.
- Work branch: `research/a004-qwen-adapter`.
- A004 is inserted as **Local Model Adapter & Qwen3.5:4B Baseline**.
- The previous planned A004-A010 milestones shift to A005-A011; completed A001-A003 historical reports are not renumbered or rewritten.
- ASCA core remains model-agnostic.
- `qwen3.5:4b` is the first model-under-test, not an ASCA dependency.
- Target local Ollama runtime observed during design: `0.32.15`.
- Target model tag: `qwen3.5:4b`.
- Target model digest: `2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd`.
- Target runtime metadata: GGUF, family `qwen35`, reported size `4.7B`, exact `general.parameter_count = 4_659_865_088`, quantization `Q4_K_M`, declared context `262144`, embedding length `2560`.
- Default qualification profile: text-only, no tools, no images, `thinking=False`, `stream=False`, `context_limit=8192`, `max_output_tokens=256`, `temperature=0.0`, `seed=0`.
- Programmatic generation uses Ollama HTTP API; do not spawn interactive `ollama run` from production adapter code.
- Outbound default baseline request explicitly sends JSON boolean `think: false`.
- A004 adds no mandatory runtime dependency to `pyproject.toml`.
- GitHub Actions must not download or run Qwen/Ollama.
- Real model qualification runs locally only and must fail closed on target digest mismatch.
- Qwen weights/Modelfile are not copied, modified, or committed.
- No A003 familiarity trace lookup, associative recall, working-set routing, surprise policy, procedural memory, tool calling, or vision behavior belongs in the adapter.
- FlyWireLLM training is paused; A004 must not restart or mutate it.
- Token/timing metadata may be recorded but must not be converted into FLOP, energy, or generalized speed claims.
- Exact branch CI, local physical qualification, exact closure CI, final main CI, clean worktree, and sync 0/0 are required before A004 closes.

## File Structure

- `src/flywire_asca/model/__init__.py`: public model namespace exports.
- `src/flywire_asca/model/contracts.py`: generic immutable model contracts and validation.
- `src/flywire_asca/model/adapter.py`: backend-neutral `ModelAdapter` protocol.
- `src/flywire_asca/model/errors.py`: public model adapter exception hierarchy.
- `src/flywire_asca/model/ollama.py`: JSON HTTP transport, Ollama descriptor inspection, and generation mapping.
- `src/flywire_asca/model/baseline.py`: deterministic baseline case definitions, scoring, and reports.
- `scripts/qualify_qwen_a004.py`: local physical qualification CLI; never required by GitHub Actions.
- `tests/test_model_contracts.py`: generic model contract validation.
- `tests/test_ollama_adapter.py`: fake-transport unit tests for request/response/error/identity behavior.
- `tests/test_qwen_baseline.py`: baseline scoring and fake-adapter report tests.
- `tests/test_a004_task_ledger.py`: A004 roadmap/task migration and closure assertions.
- `docs/development/tasks/A004-local-model-adapter-qwen-baseline.md`: recoverable A004 task ledger.
- `docs/development/roadmap-migrations/A004-qwen-insertion.md`: old planned A004-A010 -> new A005-A011 mapping.
- `docs/development/reports/ASCA-20261009-A004-qwen-adapter-baseline.md`: final qualification evidence.

## Review Focus

1. **Backend response drift / malformed JSON:** missing nested `message.content`, non-integer token/timing values, or unexpected response shape must raise `ModelProtocolError`, not silently produce an empty response; pin in Task 2.
2. **Model tag drift behind the same name:** strict qualification must compare the full current digest from `/api/tags` and raise `ModelIdentityMismatchError` before generation when it differs; pin in Task 2.
3. **Thinking accidentally enabled:** every thinking-off request must contain JSON boolean `think: false`, and any returned nonempty thinking field during strict baseline qualification is a qualification failure; pin in Tasks 2 and 4.
4. **Portable CI accidentally requiring Ollama:** all unit/baseline CI tests must run with fake adapters/transports and no localhost service; pin in Task 3 CI-contract tests.
5. **Timeout/unreachable endpoint behavior:** socket timeout/URL errors must map to deterministic `ModelTimeoutError`/`ModelUnavailableError` without retries hidden inside A004; pin in Task 2.

---

### Task 1: Add generic model contracts, activate A004, and migrate the roadmap

**Files:**
- Create: `src/flywire_asca/model/__init__.py`
- Create: `src/flywire_asca/model/contracts.py`
- Create: `src/flywire_asca/model/adapter.py`
- Create: `src/flywire_asca/model/errors.py`
- Create: `tests/test_model_contracts.py`
- Create: `tests/test_a004_task_ledger.py`
- Create: `docs/development/tasks/A004-local-model-adapter-qwen-baseline.md`
- Create: `docs/development/roadmap-migrations/A004-qwen-insertion.md`
- Modify: `docs/development/tasks/CURRENT.md`
- Modify: `docs/development/tasks/ROADMAP.md`
- Modify: `README.md`
- Modify: `tests/test_task_ledger.py`

**Interfaces:**
- Produces `ModelRole(str, Enum)` with exactly `SYSTEM="system"`, `USER="user"`, `ASSISTANT="assistant"`.
- Produces immutable `ModelMessage(role: ModelRole, content: str)`.
- Produces immutable `ModelRequest(request_id: str, messages: tuple[ModelMessage, ...], max_output_tokens: int = 256, context_limit: int = 8192, temperature: float = 0.0, seed: int | None = 0, thinking: bool = False)`.
- Produces immutable `ModelDescriptor(backend_name: str, backend_version: str, model_name: str, model_digest: str | None, architecture: str | None, parameter_count: int | None, parameter_size: str | None, quantization: str | None, context_length: int | None, embedding_length: int | None, capabilities: tuple[str, ...])`.
- Produces immutable `ModelResponse(request_id: str, model_name: str, model_digest: str | None, content: str, finish_reason: str | None, prompt_tokens: int | None, generated_tokens: int | None, total_duration_ns: int | None, load_duration_ns: int | None, prompt_eval_duration_ns: int | None, eval_duration_ns: int | None)`.
- Produces `ModelAdapter(Protocol)`:
  - `inspect(self) -> ModelDescriptor`
  - `generate(self, request: ModelRequest) -> ModelResponse`
- Produces exceptions: `ModelAdapterError`, `ModelUnavailableError`, `ModelNotFoundError`, `ModelIdentityMismatchError`, `ModelProtocolError`, `ModelTimeoutError`.

- [ ] **Step 1: Write failing generic contract tests**

Pin:
- all public record types are frozen dataclasses;
- blank request/message/model/backend identifiers are rejected;
- `ModelRequest.messages` is nonempty;
- `max_output_tokens > 0`, `context_limit > 0`;
- `temperature` is finite and nonnegative;
- `seed` is `int | None` but rejects bool;
- `thinking` is strictly bool;
- descriptor capability tuple is sorted/unique and metadata counts/durations are nonnegative when present;
- `ModelResponse.content` may be empty at contract level, because protocol validation belongs to the adapter/qualification layer;
- no generic contract imports or names Ollama/Qwen.

- [ ] **Step 2: Run focused tests and verify RED**

Run:
```powershell
python -m pytest -q tests/test_model_contracts.py
```

Expected: import/collection FAIL because the model package does not exist.

- [ ] **Step 3: Implement generic contracts/protocol/errors only**

Use standard-library validation and frozen/slotted dataclasses. Keep backend-specific field names out of the generic public records.

- [ ] **Step 4: Write failing roadmap/task migration tests**

Pin:
- CURRENT points to A004 ACTIVE and GitHub Issue #4;
- ROADMAP contains A001-A011 exactly once with A001-A003 DONE, A004 ACTIVE, A005-A011 PLANNED;
- A004 title is `Local Model Adapter & Qwen3.5:4B Baseline`;
- migration doc maps:
  - old A004 Associative Memory & Recall -> new A005;
  - old A005 Working Set / Selective Activation -> new A006;
  - old A006 Surprise, Uncertainty & Expansion -> new A007;
  - old A007 Procedural Memory / Skill Chunking -> new A008;
  - old A008 Integrated Cognitive Loop -> new A009;
  - old A009 Dense/non-selective comparison -> new A010;
  - old A010 ASCA v0.x Qualification -> new A011;
- historical A001-A003 reports remain unchanged references;
- README states ASCA is model-agnostic and Qwen3.5:4b is the current model-under-test.

- [ ] **Step 5: Run task/roadmap tests and verify RED**

Run:
```powershell
python -m pytest -q tests/test_a004_task_ledger.py tests/test_task_ledger.py
```

Expected: FAIL because A004 task/migration and new roadmap do not exist yet.

- [ ] **Step 6: Create GitHub Issue #4 and activate A004 ledger**

Issue title:
`A004 — Local Model Adapter & Qwen3.5:4B Baseline`

Issue scope mirrors this plan. Record the returned issue number in CURRENT and A004 task doc.

- [ ] **Step 7: Migrate roadmap and README**

Create the migration doc rather than rewriting historical reports. Update README stale current-stage text and state:
- ASCA remains model-agnostic;
- current local model-under-test is `qwen3.5:4b`;
- FlyWireLLM is a future adapter candidate, not an A004 dependency.

- [ ] **Step 8: Run Task 1 gates**

Run:
```powershell
python -m pytest -q tests/test_model_contracts.py tests/test_a004_task_ledger.py tests/test_task_ledger.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
git diff --check
```

Expected: all PASS.

- [ ] **Step 9: Commit Task 1**

Commit:
```text
Add A004 model contracts and roadmap migration
```

### Task 2: Implement Ollama JSON transport and model adapter with fake-transport tests

**Files:**
- Create: `src/flywire_asca/model/ollama.py`
- Create: `tests/test_ollama_adapter.py`
- Modify: `src/flywire_asca/model/__init__.py`
- Modify: `docs/development/tasks/A004-local-model-adapter-qwen-baseline.md`

**Interfaces:**
- Produces internal `JsonTransport(Protocol)` with:
  - `request_json(self, method: str, path: str, payload: dict[str, object] | None, timeout_seconds: float) -> dict[str, object]`.
- Produces `UrllibJsonTransport(base_url: str)` implementing `JsonTransport`.
- Produces `OllamaModelAdapter(model_name: str, *, base_url: str = "http://127.0.0.1:11434", expected_digest: str | None = None, timeout_seconds: float = 120.0, keep_alive: str = "5m", transport: JsonTransport | None = None)`.
- `inspect() -> ModelDescriptor` calls:
  - GET `/api/version`;
  - GET `/api/tags`;
  - POST `/api/show` with `{"model": model_name}`.
- `generate(request: ModelRequest) -> ModelResponse` performs identity inspection/cache first, then POST `/api/chat`.

- [ ] **Step 1: Write failing descriptor-inspection tests with fake transport**

Fake responses must prove:
- `backend_name == "ollama"`;
- version from `/api/version`;
- full digest selected by exact model tag from `/api/tags`;
- architecture/parameter count/context/embedding from `/api/show.model_info`;
- parameter-size/quantization from `/api/show.details`;
- capabilities sorted/unique;
- missing tag raises `ModelNotFoundError`;
- strict digest mismatch raises `ModelIdentityMismatchError`.

- [ ] **Step 2: Write failing request-mapping tests**

For the default baseline request assert outbound `/api/chat` payload contains exactly the semantic controls:
- `model: "qwen3.5:4b"`;
- ordered `messages` role/content objects;
- `stream: false`;
- `think: false`;
- `keep_alive: "5m"`;
- `options.num_ctx: 8192`;
- `options.num_predict: 256`;
- `options.temperature: 0.0`;
- `options.seed: 0`;
- no `tools`, `images`, or vision fields.

A request with `thinking=True` must map to JSON boolean true, proving the field is not encoded as a string.

- [ ] **Step 3: Write failing response/error tests**

Pin:
- valid chat response maps content, `done_reason`, prompt/eval counts, and nanosecond duration fields;
- returned response `model_digest` equals the inspected descriptor digest;
- missing/blank `message.content` raises `ModelProtocolError` in `generate`;
- malformed descriptor numeric values raise `ModelProtocolError`;
- transport socket timeout -> `ModelTimeoutError`;
- connection/refused/DNS `URLError` -> `ModelUnavailableError`;
- HTTP non-2xx response -> `ModelProtocolError` carrying status context but not raw sensitive response bodies;
- invalid/non-object JSON response -> `ModelProtocolError`;
- no automatic retry occurs in A004;
- when strict baseline request has `thinking=False`, fake response with nonempty `message.thinking` raises `ModelProtocolError`.

- [ ] **Step 4: Run focused tests and verify RED**

Run:
```powershell
python -m pytest -q tests/test_ollama_adapter.py
```

Expected: FAIL because adapter/transport do not exist.

- [ ] **Step 5: Implement transport and adapter minimally**

Use `urllib.request.Request/urlopen`; serialize request JSON as UTF-8 and parse UTF-8 JSON object responses. Translate `TimeoutError`, `socket.timeout`, and `urllib.error.URLError` deterministically into the public exception hierarchy.

Cache a successfully inspected descriptor per adapter instance; do not cache an inspection failure.

- [ ] **Step 6: Run focused and full gates**

Run:
```powershell
python -m pytest -q tests/test_ollama_adapter.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
git diff --check
```

Expected: all PASS without requiring Ollama to be running.

- [ ] **Step 7: Update resume pointer and commit Task 2**

Mark generic contract/roadmap and adapter implementation DONE; Qwen baseline ACTIVE.

Commit:
```text
Add local Ollama model adapter
```

### Task 3: Add Qwen-only machine-scored baseline and portable CI coverage

**Files:**
- Create: `src/flywire_asca/model/baseline.py`
- Create: `tests/test_qwen_baseline.py`
- Modify: `.github/workflows/ci.yml`
- Modify: `tests/test_ci_contract.py`
- Modify: `docs/development/tasks/A004-local-model-adapter-qwen-baseline.md`

**Interfaces:**
- Produces `BaselineScoring(str, Enum)` with `EXACT_NORMALIZED="exact_normalized"`, `ALLOWED_NORMALIZED="allowed_normalized"`.
- Produces immutable `ModelBaselineCase(case_id: str, messages: tuple[ModelMessage, ...], scoring: BaselineScoring, expected_answers: tuple[str, ...])`.
- Produces immutable `ModelBaselineCaseResult(case_id: str, passed: bool, normalized_output: str, prompt_tokens: int | None, generated_tokens: int | None, total_duration_ns: int | None)`.
- Produces immutable `ModelBaselineReport(profile_name: str, model_name: str, model_digest: str | None, case_results: tuple[ModelBaselineCaseResult, ...], case_count: int, passed_case_count: int, pass_rate: float, prompt_tokens_total: int | None, generated_tokens_total: int | None, total_duration_ns: int | None)`.
- Produces `normalize_baseline_answer(text: str) -> str` using NFKC + strip/collapse whitespace + casefold.
- Produces `build_qwen_a004_baseline_cases() -> tuple[ModelBaselineCase, ...]`.
- Produces `run_model_baseline(adapter: ModelAdapter, cases: Iterable[ModelBaselineCase], *, profile_name: str) -> ModelBaselineReport`.
- Produces `qualify_qwen_a004_report(report: ModelBaselineReport) -> list[str]`.

- [ ] **Step 1: Write failing baseline contract/scoring tests**

Pin:
- case IDs are nonblank;
- messages nonempty;
- expected answers are nonempty/canonical sorted unique after normalization;
- exact-normalized scoring requires exactly one expected answer;
- report counts/rates are internally consistent;
- duration/token totals are `None` if any case lacks the corresponding backend metric, rather than inventing zero.

- [ ] **Step 2: Write failing controlled-case fixture tests**

The built-in fixture contains exactly these stable prompt-only controls:
1. English exact instruction: output only `BLUE`;
2. Thai exact instruction: output only `แมว`;
3. supplied-context selection: given `alpha=17, beta=29`, output only `29`;
4. supplied-context transformation: given `red | green | blue`, output only the middle item `green`;
5. insufficient-context control: when the prompt explicitly lacks the requested value, output only `INSUFFICIENT_CONTEXT`;
6. allowed-normalized case accepting `yes` or `true` for a supplied Boolean statement.

No case depends on current world knowledge or web access.

- [ ] **Step 3: Write failing fake-adapter execution tests**

Use a deterministic fake `ModelAdapter` to prove:
- all six cases pass;
- report `pass_rate == 1.0`;
- model tag/digest propagate from adapter responses/descriptors;
- token/duration totals are summed only when complete;
- one wrong output yields deterministic failure;
- the scorer never inspects hidden thinking/reasoning text.

- [ ] **Step 4: Run focused tests and verify RED**

Run:
```powershell
python -m pytest -q tests/test_qwen_baseline.py
```

Expected: FAIL because baseline module does not exist.

- [ ] **Step 5: Implement baseline module**

Keep prompt generation and scoring deterministic. Do not include wall-clock timing from Python; use backend-reported metadata only.

`qualify_qwen_a004_report` requires:
- `profile_name == "qwen3.5-4b-thinking-off-v1"`;
- `case_count == 6`;
- `pass_rate == 1.0`;
- `passed_case_count == case_count`;
- nonblank model name;
- nonblank model digest.

- [ ] **Step 6: Add portable CI contract tests**

GitHub Actions should continue running the ordinary full unit suite, audits, A003 benchmark, and whitespace checks. Add no real-Qwen command.

Pin with tests that:
- workflow contains no `ollama pull`, `ollama run`, `qualify_qwen_a004.py`, or localhost model invocation;
- fake-transport/baseline tests are covered by the existing full `pytest` step;
- A003 qualification gate remains present.

- [ ] **Step 7: Run Task 3 gates**

Run:
```powershell
python -m pytest -q tests/test_qwen_baseline.py tests/test_ci_contract.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
git diff --check
```

Expected: all PASS without relying on local Ollama.

- [ ] **Step 8: Update resume pointer and commit Task 3**

Mark Qwen baseline software/portable CI DONE and local physical qualification ACTIVE.

Commit:
```text
Add Qwen-only baseline scoring
```

### Task 4: Implement and run local physical Qwen qualification

**Files:**
- Create: `scripts/qualify_qwen_a004.py`
- Create: `tests/test_qwen_qualification_cli.py`
- Modify: `docs/development/tasks/A004-local-model-adapter-qwen-baseline.md`

**Interfaces:**
- CLI defaults:
  - base URL `http://127.0.0.1:11434`;
  - model `qwen3.5:4b`;
  - expected digest `2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd`;
  - profile `qwen3.5-4b-thinking-off-v1`;
  - request timeout 120 seconds.
- `build_qualification_payload(descriptor: ModelDescriptor, report: ModelBaselineReport) -> dict[str, object]`.
- CLI prints one JSON object to stdout and exits 0 only when descriptor identity, thinking-off smoke generation, and baseline acceptance all pass.
- `--output PATH` optionally writes the exact same UTF-8 JSON plus newline to a local evidence file.

- [ ] **Step 1: Write failing CLI unit tests without real Ollama**

Monkeypatch/fake the adapter to pin:
- default model/tag/digest/profile;
- qualification JSON includes runtime version, model digest, architecture, exact parameter count, parameter size, quantization, declared context/embedding lengths, capabilities, case results, aggregate token/duration metadata, and generation profile;
- JSON contains explicit `"thinking": false`, `"tools": false`, `"vision": false`, `"context_limit": 8192`, `"max_output_tokens": 256`, `"temperature": 0.0`, `"seed": 0`;
- JSON contains no keys implying FLOP, energy, or generalized hardware-compute reduction;
- fake digest mismatch exits nonzero;
- fake baseline failure exits nonzero;
- output file bytes match stdout payload bytes.

- [ ] **Step 2: Run CLI tests and verify RED**

Run:
```powershell
python -m pytest -q tests/test_qwen_qualification_cli.py
```

Expected: FAIL because qualification script does not exist.

- [ ] **Step 3: Implement qualification CLI**

Use `OllamaModelAdapter(expected_digest=...)`. Call `inspect()` before baseline execution and enforce:
- model name exact match;
- full digest exact match;
- architecture `qwen35`;
- parameter count `4_659_865_088`;
- quantization `Q4_K_M`;
- declared context >= 8192;
- required `completion` and `thinking` capability flags present.

Run all six controlled cases with default thinking-off requests.

The adapter contract must reject any case response whose returned `message.thinking` is nonempty while its request used `thinking=False`. Therefore physical qualification proves the thinking-off invariant across every baseline generation, not only a separate smoke prompt.

- [ ] **Step 4: Run unit/full portable gates**

Run:
```powershell
python -m pytest -q tests/test_qwen_qualification_cli.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
git diff --check
```

Expected: all PASS without requiring live Qwen.

- [ ] **Step 5: Commit physical-qualification tooling before using live model**

Commit:
```text
Add local Qwen A004 qualification runner
```

- [ ] **Step 6: Run real local physical qualification**

Because CPU inference can exceed individual tool-call timeouts, start the qualification command as a managed local process/session rather than relying on one short synchronous tool call.

Run conceptually:
```powershell
python scripts/qualify_qwen_a004.py --output <local-evidence-json>
```

Require:
- process exit 0;
- descriptor identity matches the pinned target;
- six controlled cases pass;
- `pass_rate == 1.0`;
- all six requests were sent with `thinking=false` and no accepted response contained nonempty hidden thinking;
- thinking-off profile recorded;
- token/timing metadata present when supplied by Ollama;
- no tools/images used.

If one of the six prompts is not robust enough for the exact model, treat it as a fixture-design failure, not permission to loosen scoring silently. Reproduce, fix the case/prompt under TDD, and rerun the complete physical qualification.

- [ ] **Step 7: Record local physical evidence**

Do not commit an absolute local filesystem path. Copy only the non-sensitive JSON evidence values needed for the final A004 report.

Update A004 Current Action to exact branch qualification.

### Task 5: Exact branch qualification, evidence, fast-forward integration, and A004 closure

**Files:**
- Create: `docs/development/reports/ASCA-20261009-A004-qwen-adapter-baseline.md`
- Modify: `docs/development/tasks/A004-local-model-adapter-qwen-baseline.md`
- Modify: `docs/development/tasks/CURRENT.md`
- Modify: `docs/development/tasks/ROADMAP.md`
- Modify: `tests/test_a004_task_ledger.py`
- Modify: `tests/test_task_ledger.py`

**Interfaces:**
- Consumes: Tasks 1-4, local physical qualification JSON, Git/GitHub state.
- Produces: final A004 qualification report, A004 DONE, A005 PLANNED, final exact main evidence.

- [ ] **Step 1: Run fresh exact local branch gate**

Run on clean branch HEAD:
```powershell
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
git diff --check HEAD^ HEAD
git status --short --branch
git rev-parse HEAD
```

Physical Qwen qualification must already have passed on the same implementation code. If the branch changed adapter/baseline/qualification code afterward, rerun physical qualification before publication.

- [ ] **Step 2: Verify paused FlyWireLLM state read-only**

Capture:
- no active training runner process;
- repository branch/HEAD/worktree/sync state.

Do not start, stop, or mutate FlyWireLLM.

- [ ] **Step 3: Push A004 branch and require exact portable CI**

Push without force. Require GitHub Actions success on the exact candidate SHA.

- [ ] **Step 4: Write A004 qualification report**

Report:
- final candidate SHA;
- Ollama runtime version;
- Qwen tag/full digest;
- architecture, exact parameter count, parameter-size label, quantization, context/embedding lengths, capabilities;
- exact generation profile;
- physical six-case result and pass rate;
- per-case normalized pass/fail;
- prompt/generated token totals;
- backend timing totals where present;
- explicit local-machine/non-FLOP/non-energy disclaimer;
- portable full test/audit/A003 gate/diff results;
- exact branch CI run ID;
- FlyWireLLM paused/untouched evidence;
- roadmap migration mapping;
- deferred tools/vision/thinking-on/integration scope.

- [ ] **Step 5: Write failing closure-transition tests**

Pin:
- A004 Status DONE;
- CURRENT points to A005 / PLANNED / no issue yet;
- ROADMAP marks A004 DONE and A005-A011 PLANNED;
- closure report contains final candidate SHA, Qwen full digest, physical baseline `pass_rate: 1.0`, exact branch CI run ID, and FlyWireLLM paused evidence.

Verify RED before changing ledger state.

- [ ] **Step 6: Transition A004 DONE / A005 PLANNED and run closure gate**

Run:
```powershell
python -m pytest -q tests/test_a004_task_ledger.py tests/test_task_ledger.py
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
Qualify A004 Qwen adapter baseline
```

Push branch and require exact CI success.

- [ ] **Step 8: Whole-branch review and one fix pass**

Review `base-main..closure-head` against the approved spec/plan, prioritizing:
- accidental Ollama/Qwen coupling in generic contracts;
- hidden model download/network requirement in portable CI;
- missing strict digest/thinking-off failure behavior;
- overclaiming token/timing data;
- roadmap/history corruption.

Fix Critical/Important findings with RED->GREEN regression tests, rerun full/physical qualification if adapter/baseline behavior changes, and require exact CI on the reviewed final branch SHA.

- [ ] **Step 9: Fast-forward local main only**

Preconditions:
- local main clean;
- fetched `origin/main` equals local main;
- reviewed A004 branch is a descendant of main.

Run:
```powershell
git merge --ff-only research/a004-qwen-adapter
```

No rebase/reset/force push.

- [ ] **Step 10: Verify merged result and push main**

Run:
```powershell
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
git diff --check origin/main..HEAD
```

If adapter/baseline implementation is unchanged since the last physical qualification, the report may reference that same local physical result; otherwise rerun physical qualification before pushing main.

Push `main` normally and require exact GitHub Actions success on the final main SHA.

- [ ] **Step 11: Fetch and verify final synchronization**

Require:
- `HEAD == origin/main`;
- ahead/behind = 0/0;
- worktree clean.

- [ ] **Step 12: Close Issue #4 and remove clean A004 worktree**

Issue closure comment records:
- final main SHA;
- local test/audit/A003 qualification results;
- physical Qwen model tag/digest/profile/pass rate;
- branch/final-main CI run IDs;
- sync 0/0;
- FlyWireLLM paused/untouched;
- A005 PLANNED.

Remove the clean worktree without deleting branch/history only after final GREEN evidence.

## A004 Non-Goals

A004 must not:
- fine-tune/train Qwen;
- alter Qwen weights/Modelfile;
- expose Ollama externally;
- add RAG or ASCA memory context to model prompts;
- invoke A003 familiarity inside the adapter;
- enable tools or vision;
- qualify thinking-enabled behavior;
- benchmark Qwen against FlyWireLLM;
- restart FlyWireLLM training;
- claim ASCA improves Qwen;
- infer FLOP/energy savings from token, logical-work, or duration metadata.

## Execution Order

Execute Tasks 1-5 sequentially with RED -> GREEN -> full regression -> commit for each software checkpoint. Keep portable CI independent of Ollama. Physical Qwen qualification is mandatory before A004 closure. Do not activate A005 until A004 final main CI, physical qualification evidence, and synchronization are GREEN.
