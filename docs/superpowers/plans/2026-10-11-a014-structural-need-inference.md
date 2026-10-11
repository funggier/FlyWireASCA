# A014 — Structural Need Inference / Query Intent Routing Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and qualify a target-free bilingual structural-need router that derives A013-compatible `StructuralNeed` from ordinary English/Thai query text and compares rule-only, model-only, and hybrid routing using downstream recall evidence.

**Architecture:** Add a post-A011 `flywire_asca.structural_routing` package above `contracts`, `model`, and `relational_activation`. Freeze a bilingual benchmark before routing-policy tuning, keep evaluator truth outside runtime/model prompts, then qualify deterministic control flow in portable CI and actual routing capability with pinned local `qwen3.5:4b` evidence bound to exact source/fixture/prompt identities.

**Tech Stack:** Python 3.11+ stdlib/dataclasses/enums/JSON/regex/unicodedata/hashlib, existing FlyWireASCA `ModelAdapter`, A013 `StructuralNeed` and `run_hybrid_recall`, pytest, GitHub Actions, local Ollama only for the mandatory physical gate.

**Spec:** `docs/superpowers/specs/2026-10-11-a014-structural-need-inference-design.md`

## Global Constraints

- Activation base is `4549951e3d2dbdbd877559d6b06ad501999e71f6`; design checkpoint is `3361a2d8ffef34b235e58d141f5b994817b49ed7`.
- Do not reset, clean, rebase, force-push, or modify A011-protected cognitive source blobs.
- Runtime routing sees query/request data only: no expected target IDs, expected relation labels, benchmark labels, graph contents, retrieval results, or post-hoc correctness.
- A014 may infer only Contract v0.1 relations. Primary benchmark relations are `WORKS_AT`, `CAUSED_BY`, `OCCURRED_BEFORE`, `PART_OF`, and `USED_FOR`.
- Never promote `SAME_NAME` to `SAME_PERSON`.
- Runtime failures and malformed model outputs fail closed to `StructuralNeed()`; they are not counted as legitimate non-relational decisions.
- GitHub CI remains network-free and Ollama-free. Scripted adapters prove engineering/control flow only, never model capability.
- Mandatory physical evidence uses pinned `qwen3.5:4b` digest `2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd`, temperature 0, seed 0, thinking disabled, and bounded output.
- The frozen bilingual benchmark is committed before rule/model routing behavior is tuned.
- Physical evidence must be bound to exact A014 runtime source, fixture, prompt, model identity, and decision logic.
- FlyWireLLM is untouched. No release/tag/version promotion is authorized.
- A valid negative or `MIXED` research result is not an engineering-process failure.
- A015 is not auto-activated by A014 closure.

## Review Focus

- Mixed Thai/English or Unicode-width variants must normalize deterministically without changing semantic keywords; Task 3 adds normalization tests.
- A direct-recall query containing a relation word (for example “cause stated directly”) must not trigger relation traversal; Task 4 adds precedence/hard-negative tests.
- Model output wrapped in prose/markdown or containing unknown/extra control fields must be rejected rather than partially parsed; Task 5 adds strict parser tests.
- A model response with the wrong request ID or a model transport exception must produce `MODEL_ERROR` and fail closed; Task 5 adds mismatch/error tests.
- Benchmark/evaluator truth must never appear in runtime dataclass fields or generated model prompts even as optional metadata; Tasks 2, 5, and 7 add introspection/leakage tests.

---

### Task 1: Activate the A014 lifecycle after plan approval

**Files:**
- Create: `docs/development/tasks/A014-structural-need-inference.md`
- Modify: `docs/development/tasks/CURRENT.md`
- Modify: `docs/development/tasks/ROADMAP.md`
- Test: `tests/test_a014_task_ledger.py`
- Test: `tests/test_task_ledger.py`

**Interfaces:**
- Consumes: approved design and this implementation plan.
- Produces: one GitHub Issue number, ACTIVE A014 task ledger, and mutable CURRENT/ROADMAP ownership.

- [ ] **Step 1: Create the A014 GitHub Issue**

Title exactly: `A014 — Structural Need Inference / Query Intent Routing Gate`.

Issue body must record the activation base, design/plan paths, target-free boundary, bilingual scope, mandatory physical gate, A011/FlyWireLLM constraints, and no A015 auto-activation.

- [ ] **Step 2: Write failing lifecycle tests**

Add tests asserting:
- A014 task exists and says `Status: ACTIVE`;
- CURRENT says `Current task: A014` and `Status: ACTIVE`;
- ROADMAP has one A014 row with `ACTIVE`;
- task records the actual created Issue number;
- A013 historical ledger no longer owns mutable CURRENT/ROADMAP.

- [ ] **Step 3: Run lifecycle tests and verify RED**

Run:
`python -m pytest -q tests/test_a014_task_ledger.py tests/test_task_ledger.py tests/test_a013_task_ledger.py`

Expected: FAIL because A014 lifecycle metadata does not yet exist.

- [ ] **Step 4: Write lifecycle metadata**

Create/update the listed task docs only. Do not add runtime source in this task.

- [ ] **Step 5: Run lifecycle tests and A011 preservation**

Run:
`python -m pytest -q tests/test_a014_task_ledger.py tests/test_task_ledger.py tests/test_a013_task_ledger.py && python scripts/verify_a011_frozen_profile_preservation.py && git diff --check`

Expected: all PASS.

- [ ] **Step 6: Commit**

Commit message:
`docs(a014): activate structural need inference gate`

### Task 2: Define target-free structural-routing contracts

**Files:**
- Create: `src/flywire_asca/structural_routing/__init__.py`
- Create: `src/flywire_asca/structural_routing/models.py`
- Create: `tests/test_structural_routing_models.py`

**Interfaces:**
- Consumes: `flywire_asca.contracts.RelationType`, `flywire_asca.relational_activation.StructuralNeed`.
- Produces:
  - `RoutingPolicy` = `RULE_ONLY | MODEL_ONLY | HYBRID_RULE_THEN_MODEL`
  - `RoutingInferenceStatus` = `DECIDED_RELATIONAL | DECIDED_NON_RELATIONAL | ABSTAINED | INVALID_MODEL_OUTPUT | MODEL_ERROR`
  - `RoutingInferenceSource` = `RULE | MODEL | FAIL_CLOSED`
  - `StructuralRoutingDecision` = `HYBRID_STRUCTURAL_ROUTING_JUSTIFIED | RULE_ROUTING_SUFFICIENT | MODEL_ROUTING_PREFERRED | STRUCTURAL_ROUTING_NOT_SUPPORTED | MIXED`
  - `StructuralRoutingRequest(request_id: str, query_text: str, language_hint: str | None = None)`
  - `StructuralRoutingResult(request_id: str, policy: RoutingPolicy, status: RoutingInferenceStatus, source: RoutingInferenceSource, structural_need: StructuralNeed, model_invoked: bool, rule_evidence_ids: tuple[str, ...], model_name: str | None, model_digest: str | None, raw_model_output: str | None, prompt_tokens: int | None, generated_tokens: int | None, total_duration_ns: int | None)`

- [ ] **Step 1: Write failing model-contract tests**

Tests must assert:
- request rejects blank IDs/text;
- language hint accepts only `None`, `"en"`, `"th"`;
- no dataclass field name contains `target`, `expected`, `answer`, `benchmark`, or `label`;
- relational status requires active `StructuralNeed`;
- non-relational/abstained/invalid/error statuses carry empty `StructuralNeed`;
- `MODEL_ERROR` is distinct from `DECIDED_NON_RELATIONAL`;
- token/timing values are nonnegative or `None`;
- model identity/output fields are present only when a model was invoked.

- [ ] **Step 2: Run tests and verify RED**

Run:
`python -m pytest -q tests/test_structural_routing_models.py`

Expected: import/module failure.

- [ ] **Step 3: Implement the contracts**

Keep validation deterministic and stdlib-only. Canonicalize rule evidence IDs lexically. Do not add benchmark-specific fields.

- [ ] **Step 4: Run tests and verify GREEN**

Run:
`python -m pytest -q tests/test_structural_routing_models.py`

Expected: PASS.

- [ ] **Step 5: Commit**

Commit message:
`feat(a014): add target-free structural routing contracts`

### Task 3: Freeze the bilingual benchmark before router tuning

**Files:**
- Create: `src/flywire_asca/structural_routing/benchmark_fixture.py`
- Create: `tests/test_structural_routing_fixture.py`

**Interfaces:**
- Consumes: `build_a013_deterministic_fixture()`, `StructuralNeed`.
- Produces:
  - `StructuralRoutingBenchmarkCase`
  - `build_a014_frozen_fixture() -> tuple[StructuralRoutingBenchmarkCase, ...]`
  - `runtime_input_fingerprint(case) -> str`
  - `evaluator_metadata_fingerprint(case) -> str`
  - `a014_fixture_fingerprint(cases) -> str`
  - literal `EXPECTED_A014_CASE_IDS`, `EXPECTED_A014_RUNTIME_INPUT_FINGERPRINTS`, `EXPECTED_A014_EVALUATOR_FINGERPRINTS`, and `EXPECTED_A014_FIXTURE_FINGERPRINT` populated from the first frozen commit and thereafter treated as immutable qualification anchors.

The case type stores A013 runtime fixture data plus:
- `routing_case_id`;
- `base_a013_case_id`;
- `language: "en" | "th"`;
- `query_text`;
- evaluator-only expected `StructuralNeed`;
- evaluator-only A013 expected-target/outcome metadata.

Runtime fingerprint includes only `request_id/query_text/language_hint`; evaluator fingerprint holds truth separately.

**Frozen query matrix (exact text):**

| Base semantic | English | Thai |
| --- | --- | --- |
| ownership-workplace-one-hop | `Where does Ada work?` | `Ada สังกัดบริษัทใด?` |
| causal-one-hop | `What caused the observed outage?` | `ต้นตอของเหตุขัดข้องที่สังเกตพบคืออะไร?` |
| temporal-one-hop | `Which event happened after event Alpha?` | `เหตุการณ์ถัดจาก Alpha คือเหตุการณ์ใด?` |
| part-of-two-hop | `Which whole system is this sensor part of?` | `เซนเซอร์นี้เป็นส่วนหนึ่งของระบบใด?` |
| used-for-one-hop | `What is the caliper used for?` | `คาลิเปอร์มีหน้าที่อะไร?` |
| same-name-disambiguated-ownership | `Identify this Alex's employer.` | `Alex คนนี้ทำงานที่ไหน?` |
| cycle-control | `Which larger assembly is this component part of?` | `ชิ้นส่วนนี้สังกัดชุดประกอบใด?` |
| low-confidence-edge-control | `What caused this observed failure?` | `ต้นตอของความขัดข้องนี้คืออะไร?` |
| relation-allowlist-control | `What purpose does this component serve?` | `ชิ้นส่วนนี้ใช้ทำอะไร?` |
| missing-target-control | `Who employs this person?` | `บุคคลนี้ทำงานที่ไหน?` |
| vector-direct-control | `What fact is stated directly?` | `ข้อเท็จจริงที่ระบุไว้โดยตรงคืออะไร?` |
| vector-direct-context-control | `What context is stated directly?` | `บริบทที่ระบุไว้โดยตรงคืออะไร?` |
| vector-direct-procedure-control | `What procedure is stated directly?` | `ขั้นตอนที่ระบุไว้โดยตรงคืออะไร?` |
| vector-direct-causal-control | `What cause is stated directly?` | `สาเหตุที่ระบุไว้โดยตรงคืออะไร?` |
| vector-direct-episodic-control | `What event is stated directly?` | `เหตุการณ์ที่ระบุไว้โดยตรงคืออะไร?` |
| vector-direct-spatial-control | `What location is stated directly?` | `ตำแหน่งที่ระบุไว้โดยตรงคืออะไร?` |

This yields 32 valid routing cases: 12 relation-positive, 8 structural fail-closed controls, 12 direct/non-structural controls.

- [ ] **Step 1: Write fixture tests with the exact matrix and expected category counts**

Tests must also assert:
- every base A013 valid case appears exactly twice;
- EN/TH ordering is deterministic;
- invalid A013 contract case is excluded from valid routing fixture and represented by one separate invalid-request control;
- runtime fingerprints change when query text changes;
- evaluator fingerprints change when expected need changes;
- runtime fingerprints do not serialize expected relation labels/targets.

- [ ] **Step 2: Run tests and verify RED**

Run:
`python -m pytest -q tests/test_structural_routing_fixture.py`

Expected: FAIL because fixture module does not exist.

- [ ] **Step 3: Implement and freeze the fixture**

Generate the first hashes with a one-off local inspection command, then paste them as literal constants. Do not add routing rules yet.

- [ ] **Step 4: Run fixture tests and verify GREEN**

Run:
`python -m pytest -q tests/test_structural_routing_fixture.py`

Expected: PASS with 32 valid bilingual cases and stable literal fingerprints.

- [ ] **Step 5: Commit the frozen benchmark before policy tuning**

Commit message:
`test(a014): freeze bilingual structural routing benchmark`

After this commit, query text or evaluator labels may not be changed to improve policy scores without an explicit benchmark revision.

### Task 4: Implement the conservative deterministic rule router

**Files:**
- Create: `src/flywire_asca/structural_routing/rules.py`
- Create: `tests/test_structural_routing_rules.py`

**Interfaces:**
- Consumes: `StructuralRoutingRequest`.
- Produces:
  - `normalize_routing_text(text: str) -> str`
  - `route_by_rules(request: StructuralRoutingRequest) -> StructuralRoutingResult`

**Rule precedence and cue contract:**

1. Normalize NFKC, casefold Latin text, collapse whitespace, preserve Thai text.
2. Strong direct-recall negative markers win before relation cues:
   - English: `"stated directly"`, `"directly stated"`
   - Thai: `"ระบุไว้โดยตรง"`, `"บอกไว้โดยตรง"`
3. Strong positive cues:
   - `WORKS_AT`: English `where ... work`, `works at`, `work for`; Thai `ทำงานที่`, `ทำงานให้`
   - `CAUSED_BY`: English `what caused`, `caused by`, `cause of`; Thai `สาเหตุของ`, `เกิดจาก`
   - `OCCURRED_BEFORE`: English `happened after`, `happened before`, `occurred after`, `occurred before`; Thai `เกิดหลัง`, `เกิดก่อน`
   - `PART_OF`: English `part of`; Thai `เป็นส่วนหนึ่งของ`
   - `USED_FOR`: English `used for`; Thai `ใช้ทำอะไร`, `ใช้สำหรับ`
4. Multiple matched relation types produce the sorted union and `DECIDED_RELATIONAL`.
5. No strong positive/negative cue produces `ABSTAINED` and empty `StructuralNeed`.
6. Rule-positive results set `requires_path_provenance=True`.

Evidence IDs are stable semantic IDs such as `rule:direct:stated-directly` and `rule:relation:works-at`, never case IDs.

- [ ] **Step 1: Write rule tests**

Include:
- each relation cue in EN/TH;
- direct-negative precedence using `What cause is stated directly?` and its Thai counterpart;
- paraphrase abstentions from the frozen matrix such as `Identify this Alex's employer.`, `Ada สังกัดบริษัทใด?`, and `คาลิเปอร์มีหน้าที่อะไร?`;
- NFKC/full-width and repeated-whitespace normalization;
- mixed Thai/English text;
- no `SAME_NAME`/`SAME_PERSON` inference.

- [ ] **Step 2: Run tests and verify RED**

Run:
`python -m pytest -q tests/test_structural_routing_rules.py`

Expected: FAIL because rule router does not exist.

- [ ] **Step 3: Implement minimal rule router**

Use compiled stdlib regex/string checks only. Do not import the benchmark fixture.

- [ ] **Step 4: Run tests and verify GREEN**

Run:
`python -m pytest -q tests/test_structural_routing_rules.py`

Expected: PASS.

- [ ] **Step 5: Commit**

Commit message:
`feat(a014): add conservative bilingual rule router`

### Task 5: Implement the strict model router and parser

**Files:**
- Create: `src/flywire_asca/structural_routing/model_router.py`
- Create: `tests/test_structural_routing_model_router.py`

**Interfaces:**
- Consumes: `StructuralRoutingRequest`, existing `ModelAdapter`.
- Produces:
  - `A014_ROUTER_SYSTEM_PROMPT: str`
  - `router_prompt_fingerprint() -> str`
  - `build_router_model_request(request: StructuralRoutingRequest) -> ModelRequest`
  - `parse_router_model_response(request: StructuralRoutingRequest, response: ModelResponse, *, policy: RoutingPolicy) -> StructuralRoutingResult`
  - `route_by_model(request: StructuralRoutingRequest, adapter: ModelAdapter, *, policy: RoutingPolicy) -> StructuralRoutingResult`

The model request uses:
- `request_id=f"a014-router:{request.request_id}"`;
- temperature `0.0`;
- seed `0`;
- thinking `False`;
- context limit `8192`;
- max output tokens `192`.

Strict JSON accepts exactly:
- `requires_relation: bool`
- `required_relations: list[str]`
- `requires_path_provenance: bool`

No confidence field, target field, case ID, or extra field is accepted.

- [ ] **Step 1: Write parser/prompt tests**

Tests must assert:
- prompt contains query text and fixed relation vocabulary only;
- prompt does not contain any target/expected/benchmark metadata;
- exact valid relational and non-relational JSON parses;
- unknown relation, extra field, prose prefix/suffix, markdown fences, duplicate contradictory fields, or inconsistent boolean/list combinations yield `INVALID_MODEL_OUTPUT`;
- wrong response request ID yields `MODEL_ERROR`;
- adapter exception yields `MODEL_ERROR`;
- model identity/tokens/timing/raw output are preserved as evidence;
- Thai query is passed unchanged in the user message.

- [ ] **Step 2: Run tests and verify RED**

Run:
`python -m pytest -q tests/test_structural_routing_model_router.py`

Expected: FAIL because model router does not exist.

- [ ] **Step 3: Implement strict prompt, JSON parser, and adapter wrapper**

Use `json.loads` only; require top-level object and exact key set. Map relation strings through Contract v0.1 enum values. Never strip markdown fences or salvage substrings.

- [ ] **Step 4: Run tests and verify GREEN**

Run:
`python -m pytest -q tests/test_structural_routing_model_router.py`

Expected: PASS.

- [ ] **Step 5: Commit**

Commit message:
`feat(a014): add strict model structural router`

### Task 6: Implement policy orchestration

**Files:**
- Create: `src/flywire_asca/structural_routing/runner.py`
- Modify: `src/flywire_asca/structural_routing/__init__.py`
- Create: `tests/test_structural_routing_runner.py`

**Interfaces:**
- Consumes: `route_by_rules`, `route_by_model`, `ModelAdapter | None`.
- Produces:
  - `run_structural_routing(request: StructuralRoutingRequest, *, policy: RoutingPolicy, model_adapter: ModelAdapter | None = None) -> StructuralRoutingResult`

Policy behavior:
- `RULE_ONLY`: rule result; abstention remains fail-closed; never calls model.
- `MODEL_ONLY`: requires adapter and invokes exactly once for every valid request.
- `HYBRID_RULE_THEN_MODEL`: use strong rule positive/negative directly; call model exactly once only after rule `ABSTAINED`.
- Missing adapter when a model call is required returns `MODEL_ERROR` fail-closed, not an exception that is mistaken for a negative decision.

- [ ] **Step 1: Write policy-call-count tests**

Use a counting scripted adapter. Verify exact call counts, source/status values, and no model override of strong rule results.

- [ ] **Step 2: Run tests and verify RED**

Run:
`python -m pytest -q tests/test_structural_routing_runner.py`

Expected: FAIL because policy runner does not exist.

- [ ] **Step 3: Implement orchestration**

No benchmark imports.

- [ ] **Step 4: Run tests and verify GREEN**

Run:
`python -m pytest -q tests/test_structural_routing_runner.py`

Expected: PASS.

- [ ] **Step 5: Commit**

Commit message:
`feat(a014): orchestrate rule model and hybrid routing`

### Task 7: Wire inferred need into the existing A013 downstream recall path

**Files:**
- Create: `src/flywire_asca/structural_routing/evaluation.py`
- Create: `tests/test_structural_routing_downstream.py`

**Interfaces:**
- Consumes: frozen benchmark cases, `run_structural_routing`, A013 `HybridRecallRequest`, `RelationalActivationPolicy.SIGNAL_GATED_RELATION`, `run_hybrid_recall`.
- Produces:
  - `RoutingPolicyCaseResult`
  - `evaluate_routing_case(case: StructuralRoutingBenchmarkCase, *, policy: RoutingPolicy, model_adapter: ModelAdapter | None) -> RoutingPolicyCaseResult`

The routing request receives only case runtime input. Evaluator truth is consulted only after the routing result exists.

- [ ] **Step 1: Write leakage and downstream tests**

Tests assert:
- evaluator expected need/targets are not arguments to routing/model functions;
- inferred need alone is inserted into A013 `HybridRecallRequest`;
- direct controls remain direct when routing says non-relational;
- relation-positive cases can recover only through inferred relation need;
- fail-closed controls preserve A013 identity/provenance/budget behavior;
- a deliberately wrong inferred relation causes downstream failure and is measured, not repaired with evaluator truth.

- [ ] **Step 2: Run tests and verify RED**

Run:
`python -m pytest -q tests/test_structural_routing_downstream.py`

Expected: FAIL because evaluation module does not exist.

- [ ] **Step 3: Implement downstream evaluator composition**

Reuse A013 vector/relation fixture semantics; do not alter A013 runtime source.

- [ ] **Step 4: Run tests and verify GREEN**

Run:
`python -m pytest -q tests/test_structural_routing_downstream.py`

Expected: PASS.

- [ ] **Step 5: Commit**

Commit message:
`feat(a014): evaluate inferred routing through a013 recall`

### Task 8: Add aggregate metrics, architecture decision, and portable qualifier

**Files:**
- Create: `src/flywire_asca/structural_routing/benchmark.py`
- Create: `scripts/qualify_structural_routing_a014.py`
- Create: `tests/test_structural_routing_benchmark.py`
- Create: `tests/test_structural_routing_qualification_cli.py`

**Interfaces:**
- Consumes: `evaluate_routing_case`, frozen fixture.
- Produces:
  - `StructuralRoutingBenchmarkReport`
  - `run_a014_benchmark(*, adapters_by_policy: Mapping[RoutingPolicy, ModelAdapter | None]) -> StructuralRoutingBenchmarkReport`
  - `classify_a014_architecture(report: StructuralRoutingBenchmarkReport) -> StructuralRoutingDecision`
  - `benchmark_report_payload(report) -> dict[str, object]`
  - portable qualifier CLI.

Report fields include the spec metrics separately per policy plus integrity totals.

Portable scripted adapter returns deterministic schema-valid outputs keyed only by request text to exercise all branches. Portable output must say `evidence_role="engineering_control_flow"` and must not claim the physical architecture result.

- [ ] **Step 1: Write aggregation/decision tests**

Pin all five decision branches with synthetic reports and verify the exact predeclared inequalities from the spec.

- [ ] **Step 2: Write portable qualifier tamper tests**

Reject:
- fixture/case-order/runtime/evaluator fingerprint drift;
- raw case-evidence drift;
- prompt fingerprint drift;
- invalid decision vocabulary;
- leakage/integrity failures;
- scripted adapter being labeled as physical/model-capability evidence.

- [ ] **Step 3: Run tests and verify RED**

Run:
`python -m pytest -q tests/test_structural_routing_benchmark.py tests/test_structural_routing_qualification_cli.py`

Expected: FAIL because benchmark/qualifier modules do not exist.

- [ ] **Step 4: Implement aggregate benchmark and portable qualifier**

The portable qualifier validates deterministic machinery but does not freeze a real-model architecture outcome.

- [ ] **Step 5: Run tests and qualifier**

Run:
`python -m pytest -q tests/test_structural_routing_benchmark.py tests/test_structural_routing_qualification_cli.py && python scripts/qualify_structural_routing_a014.py`

Expected: PASS, with portable engineering evidence role explicitly identified.

- [ ] **Step 6: Commit**

Commit message:
`test(a014): add portable structural routing qualification`

### Task 9: Add mandatory physical qualifier and source-bound evidence verifier

**Files:**
- Create: `scripts/qualify_structural_routing_a014_physical.py`
- Create: `scripts/verify_a014_physical_evidence.py`
- Create: `tests/test_structural_routing_physical_contract.py`
- Create later during execution: `docs/development/qualification/a014-structural-routing-physical-v1.json`

**Interfaces:**
- Consumes: existing `OllamaModelAdapter`, A014 benchmark/classifier.
- Produces:
  - `a014_source_manifest() -> tuple[(mode, path, blob_sha), ...]`
  - `a014_source_manifest_fingerprint() -> str`
  - physical JSON with exact source SHA, manifest fingerprint, fixture fingerprint, prompt fingerprint, pinned model identity, raw model outputs, per-policy metrics, and derived `StructuralRoutingDecision`.
  - verifier that checks committed evidence against current source/fixture/prompt and raw aggregate recomputation.

Source manifest scope is exact Git-tracked files:
- `src/flywire_asca/structural_routing/**/*.py`
- `scripts/qualify_structural_routing_a014.py`
- `scripts/qualify_structural_routing_a014_physical.py`

The evidence JSON itself is excluded from the source manifest.

- [ ] **Step 1: Write physical-contract tests**

Use a fake adapter only to test:
- pinned model mismatch rejection;
- evidence source SHA/manifest binding;
- fixture/prompt binding;
- raw-output preservation;
- recomputation detects tampered metrics/decision;
- missing physical evidence causes verifier nonzero after CI integration is enabled.

- [ ] **Step 2: Run tests and verify RED**

Run:
`python -m pytest -q tests/test_structural_routing_physical_contract.py`

Expected: FAIL because physical scripts do not exist.

- [ ] **Step 3: Implement physical runner and verifier**

Physical runner must call `adapter.inspect()` before scoring and require exact tag/digest. No model pull/restart or hidden retry.

- [ ] **Step 4: Run contract tests and verify GREEN**

Run:
`python -m pytest -q tests/test_structural_routing_physical_contract.py`

Expected: PASS.

- [ ] **Step 5: Commit physical machinery before running Ollama**

Commit message:
`test(a014): add source-bound physical qualification`

### Task 10: Integrate architecture audit, qualification matrix, and portable CI

**Files:**
- Modify: `scripts/audit_architecture_contract.py`
- Modify: `tests/test_architecture_audit.py`
- Modify: `docs/development/QUALIFICATION-MATRIX.md`
- Modify: `.github/workflows/ci.yml`
- Create/modify: A014 CI tests as needed.

**Interfaces:**
- Consumes: all A014 portable/physical verification commands.
- Produces architecture allowance:
  `structural_routing -> {contracts, model, relational_activation}`

- [ ] **Step 1: Write failing architecture tests**

Assert:
- declared A014 dependencies pass;
- `structural_routing -> integrated_loop|baseline_comparison|qualification` fails;
- reverse `relational_activation -> structural_routing` fails;
- cross-package cycles fail.

- [ ] **Step 2: Run tests and verify RED**

Run:
`python -m pytest -q tests/test_architecture_audit.py`

Expected: FAIL until structural_routing is declared.

- [ ] **Step 3: Update audit, matrix, and CI**

CI order after A013 in this task:
1. A014 portable qualifier writes `$RUNNER_TEMP/a014-structural-routing-...json`;
2. upload portable evidence with `if: always()`;
3. existing whitespace check.

Do not run Ollama in CI. Do not add the committed-physical-evidence verifier to CI until Task 11 has created and locally verified the evidence file.

- [ ] **Step 4: Run focused integration gates**

Run:
`python -m pytest -q tests/test_architecture_audit.py tests/test_structural_routing_qualification_cli.py tests/test_structural_routing_physical_contract.py && python scripts/audit_architecture_contract.py && python scripts/qualify_structural_routing_a014.py && git diff --check`

Expected: PASS. At this point CI intentionally contains only the A014 portable gate; the physical-evidence verifier is deferred to Task 11.

- [ ] **Step 5: Commit**

Commit message:
`ci(a014): integrate structural routing qualification gates`

### Task 11: Run development qualification, mandatory physical comparison, and freeze exact evidence

**Files:**
- Create: `docs/development/qualification/a014-structural-routing-physical-v1.json`
- Modify after local evidence verification: `.github/workflows/ci.yml`
- Modify only if evidence reveals a real bug: relevant tests/source via strict RED-to-GREEN repair; any source/fixture/prompt change invalidates the first physical run and requires a fresh run.

**Interfaces:**
- Consumes: stable A014 implementation HEAD from Tasks 1-10.
- Produces: source-bound real-model evidence and the actual A014 architecture decision.

- [ ] **Step 1: Run full pre-physical qualification on the exact implementation tree**

Run:
- `python -m pytest -q`
- `python scripts/audit_architecture_contract.py`
- `python scripts/qualify_repository.py`
- `python scripts/run_familiarity_benchmark_a003.py --qualify`
- `python scripts/qualify_procedural_memory_a008.py`
- `python scripts/qualify_integrated_loop_a009.py`
- `python scripts/qualify_baseline_comparison_a010.py`
- `python scripts/verify_a011_frozen_profile_preservation.py`
- `python scripts/qualify_relational_reasoning_a012.py`
- `python scripts/qualify_relational_activation_a013.py`
- `python scripts/qualify_structural_routing_a014.py`
- `python -m compileall -q src scripts`
- `git diff --check`

Expected: all engineering gates PASS.

- [ ] **Step 2: Record the exact implementation SHA**

Commit any remaining non-evidence changes first. Physical qualification must point to this exact SHA.

- [ ] **Step 3: Run the mandatory local physical qualifier**

Run:
`python scripts/qualify_structural_routing_a014_physical.py --expected-source-sha <exact-implementation-sha> --output docs/development/qualification/a014-structural-routing-physical-v1.json`

Expected:
- exact pinned `qwen3.5:4b` identity;
- 32 valid bilingual cases;
- raw model output retained for every model invocation;
- all three policy metrics reported;
- one of the five predeclared architecture decisions derived;
- timing/token fields descriptive only.

Do not treat a negative/mixed decision as runner failure if experiment integrity is valid.

- [ ] **Step 4: Verify committed-evidence integrity**

Run:
`python scripts/verify_a014_physical_evidence.py docs/development/qualification/a014-structural-routing-physical-v1.json`

Expected: PASS on exact source/fixture/prompt/model/raw aggregates.

- [ ] **Step 5: Add the committed physical-evidence verifier to CI**

Modify `.github/workflows/ci.yml` so A014 portable upload is followed by:
`python scripts/verify_a014_physical_evidence.py docs/development/qualification/a014-structural-routing-physical-v1.json`

This step occurs only after Step 4 proves the evidence file is valid locally. Ollama remains absent from CI.

- [ ] **Step 6: Commit exact physical evidence and CI verifier**

Commit message:
`evidence(a014): freeze physical structural routing result`

- [ ] **Step 7: Run full qualification again including physical-evidence verifier**

Repeat Step 1 plus:
`python scripts/verify_a014_physical_evidence.py docs/development/qualification/a014-structural-routing-physical-v1.json`

Expected: all PASS and source binding remains valid after the evidence-only commit.

### Task 12: Final review, exact GitHub qualification, integration, and closure

**Files:**
- Create after integration: `docs/development/reports/ASCA-20261011-A014-structural-need-inference.md`
- Create after integration: `docs/development/reports/ASCA-20261011-full-session-handoff-a014-completed.md`
- Modify after integration: `docs/development/tasks/A014-structural-need-inference.md`
- Modify after integration: `docs/development/tasks/CURRENT.md`
- Modify after integration: `docs/development/tasks/ROADMAP.md`
- Modify after integration: `README.md`
- Modify historical A014 task-ledger test to become self-contained at closure.

**Interfaces:**
- Consumes: exact local qualification, physical evidence, whole-branch review, and the user’s integration choice required by `superpowers:finishing-a-development-branch`.
- Produces: merged/closed A014 only after exact CI evidence; no A015 activation.

- [ ] **Step 1: Run whole-branch review package**

Use the freshest available reviewer/subagent if available; otherwise ledger a self-review as weaker than an independent reviewer. Fix Important/Critical findings only via RED→GREEN tests; report deferred Minor findings.

- [ ] **Step 2: Re-run full branch verification after review fixes**

Same complete gate set as Task 11 Step 6.

- [ ] **Step 3: Push feature branch and require exact feature-head CI GREEN**

Record exact SHA, run ID, and A014 portable artifact digest. The committed physical verifier must pass on GitHub without Ollama.

- [ ] **Step 4: Use `superpowers:finishing-a-development-branch`**

Present the required integration menu. The project’s normal historical path is PR to `main`, but do not silently merge without the required user choice.

- [ ] **Step 5: If PR integration is chosen, create PR and require exact PR CI GREEN**

Normal merge only. No squash/rebase/force push.

- [ ] **Step 6: Require exact integration/main CI GREEN**

Record merge SHA, exact main CI run, and artifact digests.

- [ ] **Step 7: Write final report/handoff and closure metadata**

Report:
- actual physical decision and all policy metrics;
- exact frozen fixture/prompt/model/source hashes;
- raw evidence path/hash;
- portable vs physical evidence distinction;
- repair/failure history;
- exact GitHub SHA/run/artifact chain;
- A005-A013 historical boundaries;
- claims boundary;
- FlyWireLLM untouched;
- no A015 auto-activation.

- [ ] **Step 8: Commit closure metadata on main and require exact closure CI GREEN**

Only after that:
- post final exact evidence to the A014 Issue;
- close it as completed;
- verify `main == origin/main`, ahead/behind `0/0`, clean worktree, no open A014 PR/Issue, and CURRENT says A014 DONE with no A015 active.
