# A009 Integrated Cognitive Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and qualify a bounded integrated cognitive controller that composes A003 familiarity, real A005 vector retrieval, A006 SINGLE_BEST working-set selection, A007 SIGNAL_DRIVEN structural expansion, and A008 CHUNKED procedural execution, then uses typed procedure-outcome mismatch as an A009-level recovery signal without hidden retry or subsystem-boundary collapse.

**Architecture:** A009 adds a typed finite-state orchestrator and immutable trace records. The initial path runs A003 once, then A007 SIGNAL_DRIVEN over an A005+A006 SINGLE_BEST scope evaluator, then executes one explicit root procedure through A008 CHUNKED. On checked procedure interruption, A009 may evaluate only the next frozen A007 scope and replay from the same immutable pre-execution snapshot with a new execution ID, repeating only until the three-scope ladder is exhausted. A004 generation is optional terminal-only diagnostic/fallback evidence and never controls recovery, procedure selection, verification, or the primary outcome.

**Tech Stack:** Python >=3.11 standard library only for A009 core, frozen dataclasses, `Enum`, `Protocol`, hashlib/json deterministic evidence, pytest, existing A003-A008 FlyWireASCA packages, existing local Ollama adapters only for local physical qualification.

**Spec:** `docs/superpowers/specs/2026-10-10-a009-integrated-cognitive-loop-design.md`

## Global Constraints

- Repository: `funggier/FlyWireASCA`.
- Work branch after activation: `research/a009-integrated-cognitive-loop`.
- Design base main before A009 spec commits: `c3feaf0b08f525276d8efa95801a161e2638821a`.
- Activation base is the exact main commit containing this plan after exact-main CI is GREEN.
- Milestone: **A009 — Integrated Cognitive Loop**.
- Do not reset, clean, rebase, or force push.
- Do not recreate or resume A008 Task 4.
- Do not modify or restart FlyWireLLM.
- Preserve historical research outcomes exactly: A006 `NOT_SUPPORTED`, A007 `SUPPORTED`, A008 `SUPPORTED`.
- Primary A006 selector is `SINGLE_BEST`; `SELECTIVE_CONVERGENCE` is diagnostic only.
- Primary A007 initial policy is `SIGNAL_DRIVEN`; its trigger vocabulary is unchanged.
- Procedure mismatch is an A009 `RecoveryCause.PROCEDURE_OUTCOME_MISMATCH`, not a new A007 `ExpansionTrigger`.
- Primary A008 execution mode is `CHUNKED`; BLIND_CHUNKED is not an A009 primary policy.
- Every A008 `run_procedure` call performs zero automatic retries.
- Every A009 replay gets a new nonblank unique execution ID and a fresh executor built from the same immutable pre-execution world snapshot.
- Recovery advances exactly one declared scope at a time and never skips a scope.
- Frozen primary A007 scope indices are exactly 0, 1, 2; no scope index 3 exists.
- Maximum A009 procedure attempts are 3.
- A009 v0.1 executes deterministic simulated procedures only; no real OS/API/LConnect/BConnect actions.
- Root procedure routing is explicit/deterministic; no natural-language procedure selection.
- A003 familiarity is evidence only; UNFAMILIAR never vetoes A005 semantic retrieval.
- A005 physical threshold remains `0.5037018224299838`; A009 does not relax it during recovery.
- A005 physical embedding identity remains `qwen3-embedding:0.6b`, digest `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`, dimension 1024.
- A004 model use policies are exactly `DISABLED` and `TERMINAL_ONLY`.
- Model output never changes retrieval scope, procedure identity, expected outcome, match result, replay eligibility, deterministic termination reason, or primary A009 outcome.
- Portable A009 qualification uses deterministic embedding/model fakes and runs in GitHub CI.
- Real Ollama/Qwen A009 physical qualification is local-only and must not be added to GitHub CI.
- Primary loop policies are exactly `NO_PROCEDURE_RECOVERY`, `MISMATCH_DRIVEN_RECOVERY`, and `ALWAYS_MAX_SCOPE`.
- Primary research outcome vocabulary is exactly `SUPPORTED`, `MIXED`, `NOT_SUPPORTED`.
- Valid MIXED or NOT_SUPPORTED evidence exits 0.
- Do not create the A009 GitHub issue before Task 1 activation.
- Issue number is taken from GitHub's create result and then written into task docs; do not hard-code it before creation.
- A010 remains PLANNED until A009 final integration is GREEN.
- Claims remain software/control/evidence claims only; no FLOP, power, energy, token-saving, general speed, or real-world autonomy claims.

## File Structure

- `src/flywire_asca/integrated_loop/__init__.py`: public A009 exports.
- `src/flywire_asca/integrated_loop/models.py`: A009 enums, immutable request/evidence/trace/result records.
- `src/flywire_asca/integrated_loop/retrieval.py`: deterministic cue tiers, A005 ExactVectorMemoryIndex scope evaluation, A006 SINGLE_BEST selection, A007 initial-policy composition.
- `src/flywire_asca/integrated_loop/procedure.py`: memory requirements, context-bound simulator wrapper/factory, fresh snapshot enforcement.
- `src/flywire_asca/integrated_loop/controller.py`: finite-state orchestration, policy behavior, bounded recovery, terminal model gate.
- `src/flywire_asca/integrated_loop/benchmark.py`: frozen deterministic fixture, policy comparison, metrics, classification.
- `scripts/qualify_integrated_loop_a009.py`: deterministic portable qualification CLI run in CI.
- `scripts/qualify_integrated_loop_a009_physical.py`: local physical A005/A004 integration qualification only.
- `tests/test_integrated_loop_models.py`: A009 model/enumeration/invariant tests.
- `tests/test_integrated_loop_retrieval.py`: A003/A005/A006/A007 scope-composition tests.
- `tests/test_integrated_loop_procedure.py`: context-bound memory requirement/snapshot/replay executor tests.
- `tests/test_integrated_loop_controller.py`: state machine/policy/recovery/model-gate tests.
- `tests/test_integrated_loop_benchmark.py`: frozen fixture/policy comparison/outcome tests.
- `tests/test_integrated_loop_qualification_cli.py`: fixture fingerprint/evidence/outcome/UTF-8 validation tests.
- `tests/test_integrated_loop_physical_cli.py`: physical script contract tests with fake adapters; no real Ollama requirement.
- `tests/test_a009_task_ledger.py`: task activation/closure evidence tests.
- `docs/development/tasks/A009-integrated-cognitive-loop.md`: recoverable A009 task ledger.
- `docs/development/reports/ASCA-20261010-A009-integrated-cognitive-loop.md`: final qualification report.

## Review Focus

1. **Replay after partial side effects:** a controller can correctly use a new execution ID while accidentally reusing the mutated simulator from the previous attempt. Task 3 must prove every attempt starts from the exact same pre-execution world-state reference and that a failed attempt's writes never leak into replay.
2. **Recovery scope skipping or duplicate evaluation:** procedure mismatch logic can jump from scope 0 directly to 2, re-evaluate scope 0, or exceed scope 2. Task 4 pins exact evaluated scope sequences for every policy and recovery family.
3. **A008 hidden retry disguised as A009 replay:** one controller call can invoke the same executor/execution ID twice. Task 4 pins unique IDs, one `run_procedure` call per attempt, and no attempt after completion.
4. **Model control leakage:** terminal model output can accidentally affect the deterministic result or authorize another replay. Task 4 runs different fake model contents against identical deterministic evidence and requires identical control trace/termination excluding the recorded model response.
5. **Research outcome drift:** the qualifier can emit a valid vocabulary value inconsistent with raw recovery/regression/coverage/scope metrics. Task 5 recomputes the classification and rejects drift/impossible count relationships.

---

### Task 1: Activate A009 and add core integrated-loop contracts

**Files:**
- Create: `src/flywire_asca/integrated_loop/__init__.py`
- Create: `src/flywire_asca/integrated_loop/models.py`
- Create: `tests/test_integrated_loop_models.py`
- Create: `tests/test_a009_task_ledger.py`
- Create: `docs/development/tasks/A009-integrated-cognitive-loop.md`
- Modify: `docs/development/tasks/CURRENT.md`
- Modify: `docs/development/tasks/ROADMAP.md`
- Modify: `README.md`
- Modify: `tests/test_task_ledger.py`
- Modify historical live-state tests only when they incorrectly freeze A009 as PLANNED after activation.

**Interfaces:**
- Produces `CognitiveLoopPhase(str, Enum)`: FAMILIARITY, INITIAL_EXPANSION, PROCEDURE_EXECUTION, RECOVERY_EXPANSION, MODEL_FALLBACK, TERMINAL.
- Produces `RecoveryCause(str, Enum)`: PROCEDURE_OUTCOME_MISMATCH.
- Produces `LoopPolicy(str, Enum)`: NO_PROCEDURE_RECOVERY, MISMATCH_DRIVEN_RECOVERY, ALWAYS_MAX_SCOPE.
- Produces `ModelUsePolicy(str, Enum)`: DISABLED, TERMINAL_ONLY.
- Produces `CognitiveTerminationReason(str, Enum)`: PROCEDURE_COMPLETED, RECOVERED_AFTER_MISMATCH, PROCEDURE_MISMATCH_EXHAUSTED.
- Produces `CognitiveTraceEventKind(str, Enum)` for the minimum event vocabulary in the spec.
- Produces immutable `CognitiveLoopRequest(loop_id: str, goal_text: str, familiarity_cue: Cue, root_procedure_id: str, policy: LoopPolicy, model_use_policy: ModelUsePolicy)`.
- Produces immutable `IntegratedScopeEvaluation(scope: ExpansionScope, retrieval_results: tuple[VectorMemoryResult, ...], working_set_result: SelectiveWorkingSetResult)`.
- Produces immutable `IntegratedExpansionResult(run: ExpansionRunResult, evaluations: tuple[IntegratedScopeEvaluation, ...])`.
- Produces immutable `CognitiveProcedureAttempt(attempt_index: int, execution_id: str, scope: ExpansionScope, working_set_memory_ids: tuple[str, ...], execution: ProcedureExecutionResult, recovery_cause: RecoveryCause | None, initial_world_state_ref: str)`.
- Produces immutable `CognitiveTraceEvent(sequence: int, kind: CognitiveTraceEventKind, refs: tuple[str, ...])`.
- Produces immutable `CognitiveLoopResult(loop_id: str, policy: LoopPolicy, familiarity: FamiliarityResult, initial_expansion: IntegratedExpansionResult, scope_evaluations: tuple[IntegratedScopeEvaluation, ...], procedure_attempts: tuple[CognitiveProcedureAttempt, ...], termination_reason: CognitiveTerminationReason, final_working_set: WorkingSet, final_world_state_ref: str | None, model_response: ModelResponse | None, trace: tuple[CognitiveTraceEvent, ...])`.

- [ ] **Step 1: Create the A009 GitHub issue now that the plan has reached task activation**

Create the issue through the GitHub connector with title:

`A009 — Integrated Cognitive Loop`

Body must summarize:
- primary `MISMATCH_DRIVEN_RECOVERY`;
- controls `NO_PROCEDURE_RECOVERY` / `ALWAYS_MAX_SCOPE`;
- SINGLE_BEST primary;
- CHUNKED primary;
- deterministic simulator only;
- A004 terminal-only model boundary;
- A006/A007/A008 historical outcomes preserved;
- FlyWireLLM untouched.

Record the actual returned issue number.

- [ ] **Step 2: Create/switch isolated A009 worktree from the exact plan-containing main commit**

Use the existing LConnect native Git worktree capability. Create branch:

`research/a009-integrated-cognitive-loop`

Do not reset/clean/rebase. The main checkout must remain preserved.

Expected: branch/worktree HEAD equals the exact main plan commit.

- [ ] **Step 3: Write failing enum/request/result invariant tests**

Pin exact enum values, frozen dataclasses, nonblank IDs/text, real existing contract types, canonical unique working-set IDs, contiguous attempt indices, unique execution IDs, attempt 0 recovery cause = None, later attempts require PROCEDURE_OUTCOME_MISMATCH, nondecreasing scope indices, no attempts after COMPLETED, trace sequence starts at 0 and is contiguous.

- [ ] **Step 4: Verify core contracts RED**

Run:
```powershell
python -m pytest -q tests/test_integrated_loop_models.py
```

Expected: import/collection FAIL because A009 package does not exist.

- [ ] **Step 5: Implement core contracts only**

Do not implement retrieval, procedure execution, controller, benchmark, or model calls.

- [ ] **Step 6: Write live A009 task-state RED tests**

Require:
- CURRENT says A009 ACTIVE;
- task ledger contains the real GitHub issue number and branch;
- ROADMAP says A009 ACTIVE;
- A010/A011 remain PLANNED;
- task ledger records A006 NOT_SUPPORTED, A007 SUPPORTED, A008 SUPPORTED;
- SINGLE_BEST + CHUNKED primary are explicit;
- no real tool execution;
- FlyWireLLM untouched;
- README current stage is A009.

- [ ] **Step 7: Verify task-state RED before docs update**

Run:
```powershell
python -m pytest -q tests/test_a009_task_ledger.py tests/test_task_ledger.py
```

Expected: FAIL because A009 is still PLANNED in repository docs.

- [ ] **Step 8: Activate task/roadmap/README using the real issue number**

Create the task ledger and update live state only. Preserve historical A006/A007/A008 reports.

- [ ] **Step 9: Run Task 1 gates**

Run:
```powershell
python -m pytest -q tests/test_integrated_loop_models.py tests/test_a009_task_ledger.py tests/test_task_ledger.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
python scripts/qualify_procedural_memory_a008.py
git diff --check
```

Expected: all PASS.

- [ ] **Step 10: Commit Task 1**

Commit:

`Activate A009 integrated cognitive loop contracts`

### Task 2: Compose A003/A005/A006/A007 retrieval and expansion

**Files:**
- Create: `src/flywire_asca/integrated_loop/retrieval.py`
- Create: `tests/test_integrated_loop_retrieval.py`
- Modify: `src/flywire_asca/integrated_loop/models.py`
- Modify: `src/flywire_asca/integrated_loop/__init__.py`
- Modify: `docs/development/tasks/A009-integrated-cognitive-loop.md`

**Interfaces:**
- Produces immutable `IntegratedRetrievalCue(source_cue_id: str, query_id: str, query_text: str)`.
- Produces immutable `IntegratedRetrievalCueTier(tier_index: int, cues: tuple[IntegratedRetrievalCue, ...])`.
- Produces immutable `IntegratedRetrievalContext(index: ExactVectorMemoryIndex, cue_tiers: tuple[IntegratedRetrievalCueTier, ...], minimum_similarity: float)`.
- Produces `evaluate_integrated_scope(context: IntegratedRetrievalContext, scope: ExpansionScope) -> IntegratedScopeEvaluation`.
- Produces `run_initial_integrated_expansion(context: IntegratedRetrievalContext, *, profile: ExpansionProfile, policy: ExpansionPolicy) -> IntegratedExpansionResult`.
- Scope evaluator constructs one A005 `VectorMemoryQuery` per enabled cue using the scope `top_k` and context threshold, wraps outputs in `SelectiveRetrievalEvidence`, and calls A006 `select_single_best`.

- [ ] **Step 1: Write failing cue/context validation tests**

Pin:
- tier indices start at 0 and are contiguous;
- at least one tier/cue;
- source cue IDs and query IDs unique across the whole context;
- nonblank texts;
- threshold finite within [-1,1];
- context contains an `ExactVectorMemoryIndex`.

- [ ] **Step 2: Write failing A005+A006 scope evaluator tests**

Using a deterministic fake EmbeddingAdapter with a real A005 ExactVectorMemoryIndex, require:
- round 0 evaluates tier 0 only;
- round 1 evaluates tiers 0..1;
- round 2 evaluates tiers 0..2;
- query `top_k` equals scope `top_k`;
- minimum similarity is unchanged across scopes;
- returned A005 evidence is retained in `IntegratedScopeEvaluation`;
- A006 selection is exactly SINGLE_BEST;
- an UNFAMILIAR A003 result is not part of the evaluator and cannot suppress retrieval.

- [ ] **Step 3: Verify scope evaluator RED**

Run:
```powershell
python -m pytest -q tests/test_integrated_loop_retrieval.py
```

Expected: FAIL because retrieval integration APIs do not exist.

- [ ] **Step 4: Implement deterministic scope evaluator**

Do not import or call SELECTIVE_CONVERGENCE in the primary evaluator.

- [ ] **Step 5: Write failing A007 initial-policy composition tests**

Require:
- SIGNAL_DRIVEN uses the existing `run_expansion_policy`;
- evaluation record count equals executed A007 rounds;
- evaluator called once per executed scope;
- STOP does not speculatively evaluate a later scope;
- EXHAUSTED ends at scope 2;
- ALWAYS_EXPAND control evaluates exactly 0,1,2;
- no new A007 trigger kind is introduced.

- [ ] **Step 6: Implement initial integrated expansion wrapper**

Use a closure/list only to collect the exact evaluations performed by A007; do not fork A007 decision logic.

- [ ] **Step 7: Run Task 2 gates**

Run:
```powershell
python -m pytest -q tests/test_integrated_loop_retrieval.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
python scripts/qualify_procedural_memory_a008.py
git diff --check
```

Expected: all PASS.

- [ ] **Step 8: Commit Task 2**

Commit:

`Add A009 integrated retrieval expansion`

### Task 3: Add context-bound deterministic procedure attempts and snapshot-safe replay

**Files:**
- Create: `src/flywire_asca/integrated_loop/procedure.py`
- Create: `tests/test_integrated_loop_procedure.py`
- Modify: `src/flywire_asca/integrated_loop/__init__.py`
- Modify: `docs/development/tasks/A009-integrated-cognitive-loop.md`

**Interfaces:**
- Produces immutable `ActionMemoryRequirement(action_ref: str, required_memory_ids: tuple[str, ...], failure_observation_kind: ObservationKind, failure_payload_ref: str)`.
- Produces `ContextBoundProcedureExecutor` implementing A008 `ProcedureExecutor`.
- Produces `ContextBoundProcedureExecutorFactory(action_definitions: tuple[SimulatedActionDefinition, ...], completion_probes: tuple[SimulatedCompletionProbe, ...], initial_state: SimulatedWorldState, requirements: tuple[ActionMemoryRequirement, ...], failure_overrides: tuple[SimulatedFailureOverride, ...] = ())`.
- Factory method: `create(*, available_memory_ids: tuple[str, ...], execution_id: str) -> ContextBoundProcedureExecutor`.
- Executor delegates successful actions/completion probes/world-state evidence to a fresh `DeterministicProcedureSimulator`.
- Missing required memory returns a deterministic observation using the requirement's failure kind/payload and performs zero action writes.

- [ ] **Step 1: Write failing memory-requirement validation tests**

Pin:
- nonblank unique action refs;
- each requirement has at least one unique nonblank memory ID;
- valid ObservationKind;
- nonblank failure payload;
- at most one requirement per action ref;
- every requirement action ref exists in simulator action definitions.

- [ ] **Step 2: Write failing missing-memory behavior tests**

Require:
- available memory -> delegate action runs and writes state;
- absent required memory -> no delegate action write;
- returned observation uses declared failure kind/payload;
- observation ID is deterministic from execution ID + canonical primitive path + stable suffix;
- A008 verify_outcome sees the mismatch naturally;
- no A008 code is modified.

- [ ] **Step 3: Verify procedure integration RED**

Run:
```powershell
python -m pytest -q tests/test_integrated_loop_procedure.py
```

Expected: FAIL because A009 procedure integration does not exist.

- [ ] **Step 4: Implement context-bound executor/factory**

Do not add real tools or side-effecting external transports.

- [ ] **Step 5: Write failing fresh-snapshot replay tests**

Create two executors from the same factory:
- attempt 0 mutates then interrupts;
- attempt 1 starts from the exact original world state, not attempt 0's mutated state;
- initial world-state refs equal;
- executor instances differ;
- execution IDs differ;
- missing-memory failure in one executor does not contaminate another;
- deterministic equivalent attempts with the same inputs produce equal logical evidence.

- [ ] **Step 6: Run Task 3 gates**

Run:
```powershell
python -m pytest -q tests/test_integrated_loop_procedure.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/qualify_procedural_memory_a008.py
git diff --check
```

Expected: all PASS.

- [ ] **Step 7: Commit Task 3**

Commit:

`Add A009 context-bound procedure replay`

### Task 4: Implement the bounded integrated cognitive controller

**Files:**
- Create: `src/flywire_asca/integrated_loop/controller.py`
- Create: `tests/test_integrated_loop_controller.py`
- Modify: `src/flywire_asca/integrated_loop/models.py`
- Modify: `src/flywire_asca/integrated_loop/__init__.py`
- Modify: `docs/development/tasks/A009-integrated-cognitive-loop.md`

**Interfaces:**
- Produces `MemoryContextProvider(Protocol)` with `resolve(memory_id: str) -> str | None` for bounded terminal model prompt assembly.
- Produces `run_cognitive_loop(request: CognitiveLoopRequest, *, familiarity_index: ExactFamiliarityIndex, retrieval_context: IntegratedRetrievalContext, expansion_profile: ExpansionProfile, procedure_library: ProcedureLibrary, procedure_executor_factory: ContextBoundProcedureExecutorFactory, model_adapter: ModelAdapter | None = None, memory_context_provider: MemoryContextProvider | None = None) -> CognitiveLoopResult`.
- Attempt execution IDs are deterministic: `<loop_id>:procedure-attempt:<attempt_index>`.
- Primary/NO_RECOVERY initial expansion policy is SIGNAL_DRIVEN.
- ALWAYS_MAX_SCOPE initial expansion policy is ALWAYS_EXPAND.
- Recovery evaluates `profile.scopes[current_index + 1]` only.
- Terminal model request ID is deterministic: `<loop_id>:terminal-model`.

- [ ] **Step 1: Write failing easy-path and familiarity tests**

Require:
- familiarity assessed exactly once;
- UNFAMILIAR still proceeds to retrieval;
- easy success executes one CHUNKED attempt;
- no recovery scope;
- no model call;
- termination PROCEDURE_COMPLETED;
- trace event order exact and contiguous.

- [ ] **Step 2: Write failing mismatch-driven round-one/round-two recovery tests**

Pin exact sequences:
- initial final scope 0 + mismatch -> scope 1 replay;
- if scope 1 succeeds: evaluated scope sequence 0,1 and attempts 0,1;
- if scope 1 mismatches and scope 2 succeeds: evaluated sequence 0,1,2 and attempts 0,1,2;
- every attempt execution ID unique/deterministic;
- every replay has PROCEDURE_OUTCOME_MISMATCH cause;
- successful attempt stops further execution.

- [ ] **Step 3: Write failing persistent/max-scope boundedness tests**

Require:
- persistent mismatch never evaluates scope >2;
- at most three procedure attempts;
- initial scope 2 mismatch creates zero replay;
- no attempt after completed attempt;
- final reason PROCEDURE_MISMATCH_EXHAUSTED.

- [ ] **Step 4: Write failing policy-control tests**

Require:
- NO_PROCEDURE_RECOVERY terminates after first mismatch regardless of wider scopes;
- ALWAYS_MAX_SCOPE evaluates all 0,1,2 then executes exactly one procedure attempt at scope 2;
- MISMATCH_DRIVEN never evaluates a forced wider scope before an actual A008 interruption;
- no policy modifies A007 trigger enums.

- [ ] **Step 5: Write failing model-gate/leakage tests**

Using a fake ModelAdapter:
- DISABLED never calls model;
- TERMINAL_ONLY calls model exactly once only after deterministic exhaustion;
- success path never calls model;
- model request contains goal, familiarity state, final scope, working-set IDs/text, failing procedure/step/call path, expected and observed payload refs;
- request contains no tool schema;
- two different fake model response contents produce identical deterministic control trace and termination reason;
- model response request_id mismatch fails closed;
- model cannot authorize a new procedure attempt.

- [ ] **Step 6: Verify controller RED**

Run:
```powershell
python -m pytest -q tests/test_integrated_loop_controller.py
```

Expected: FAIL because controller does not exist.

- [ ] **Step 7: Implement finite-state controller minimally**

Reuse A003/A007/A008 APIs directly. Do not duplicate their decision/verifier logic.

- [ ] **Step 8: Run Task 4 gates**

Run:
```powershell
python -m pytest -q tests/test_integrated_loop_controller.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
python scripts/qualify_procedural_memory_a008.py
git diff --check
```

Expected: all PASS.

- [ ] **Step 9: Commit Task 4**

Commit:

`Add A009 bounded cognitive controller`

### Task 5: Add frozen A009 benchmark, deterministic qualifier, physical CLI contract, and CI

**Files:**
- Create: `src/flywire_asca/integrated_loop/benchmark.py`
- Create: `scripts/qualify_integrated_loop_a009.py`
- Create: `scripts/qualify_integrated_loop_a009_physical.py`
- Create: `tests/test_integrated_loop_benchmark.py`
- Create: `tests/test_integrated_loop_qualification_cli.py`
- Create: `tests/test_integrated_loop_physical_cli.py`
- Modify: `.github/workflows/ci.yml`
- Modify: `tests/test_ci_contract.py`
- Modify: `docs/development/tasks/A009-integrated-cognitive-loop.md`

**Interfaces:**
- Produces immutable `IntegratedLoopBenchmarkCase` containing frozen A003 traces/cue, deterministic A005 documents/vectors/cue tiers, A008 procedure library/action simulator definitions, action-memory requirements, initial world snapshot, required success/failure labels, and model-fallback label.
- Produces immutable `IntegratedLoopPolicyCaseResult`.
- Produces immutable `IntegratedLoopBenchmarkCaseResult`.
- Produces immutable `IntegratedLoopBenchmarkReport`.
- Produces `build_a009_deterministic_fixture() -> tuple[IntegratedLoopBenchmarkCase, ...]`.
- Produces `run_a009_benchmark(cases: Iterable[IntegratedLoopBenchmarkCase]) -> IntegratedLoopBenchmarkReport`.
- Produces `classify_a009_hypothesis(report: IntegratedLoopBenchmarkReport) -> str`.
- Produces `qualify_a009_report(report: IntegratedLoopBenchmarkReport) -> list[str]`.
- Deterministic fixture scope literal: `deterministic_integrated_cognitive_loop_a009`.
- Fixture version literal: `a009-deterministic-v1`.

- [ ] **Step 1: Write failing frozen fixture-family tests**

Require exact declared families:
- easy-familiar-success;
- unfamiliar-semantic-success;
- structural-expansion-success;
- procedure-recovery-round-one;
- procedure-recovery-round-two;
- persistent-procedure-mismatch;
- max-scope-mismatch;
- same-name-ambiguity-preserved;
- model-terminal-fallback;
- invalid-contract.

Require deterministic fake embedding identity and a real A005 ExactVectorMemoryIndex in valid cases.

- [ ] **Step 2: Write failing policy-comparison/recovery tests**

For every valid case run:
- NO_PROCEDURE_RECOVERY;
- MISMATCH_DRIVEN_RECOVERY;
- ALWAYS_MAX_SCOPE.

Pin raw scope/attempt counts, genuine mismatch recovery definition, regression definition, final-state correctness, unique execution IDs, same-name preservation, model call counts.

- [ ] **Step 3: Write failing CHUNKED/FLAT diagnostic tests**

For declared deterministic success cases with the same final working set:
- ordered primitive action refs equal;
- final world state equal;
- success/failure classification equal.

Diagnostic cannot alter primary classification.

- [ ] **Step 4: Write failing primary-outcome classification tests**

Pin:
- SUPPORTED only when all exact spec conditions hold;
- MIXED when recovery exists but any support condition fails;
- NOT_SUPPORTED when no genuine recovery exists;
- impossible count relationships fail validation rather than being classified.

- [ ] **Step 5: Verify benchmark RED**

Run:
```powershell
python -m pytest -q tests/test_integrated_loop_benchmark.py
```

Expected: FAIL because benchmark does not exist.

- [ ] **Step 6: Implement deterministic benchmark and freeze fixture fingerprint**

Use canonical JSON + SHA-256. Freeze exact fingerprint only after the fixture is internally valid and before accepting the first final qualification result.

- [ ] **Step 7: Write failing portable qualification CLI tests**

Pin:
- scope/version/fingerprint/case IDs;
- exact policies;
- primary SINGLE_BEST + CHUNKED declarations;
- max scopes = 3 / max procedure attempts = 3;
- output includes raw policy metrics, validity errors, experiment_valid, primary outcome;
- stdout UTF-8 bytes equal `--output` bytes;
- valid MIXED/NOT_SUPPORTED exits 0;
- invalid evidence exits nonzero;
- validator recomputes primary outcome and rejects drift;
- duplicate execution IDs/scope skipping/model-control leakage evidence rejected.

- [ ] **Step 8: Implement deterministic qualification CLI**

No network/Ollama calls.

- [ ] **Step 9: Write physical CLI contract tests with fake adapters**

Pin that physical script:
- targets qwen3-embedding:0.6b exact digest/dimension;
- keeps threshold 0.5037018224299838;
- targets A004 qwen3.5:4b only for TERMINAL_ONLY fallback cases;
- validates model/embedding identity before accepting evidence;
- records physical metadata separately from portable primary outcome;
- can be exercised under fake adapters in tests without real Ollama.

- [ ] **Step 10: Implement physical local-only script**

Do not add the physical script to CI.

- [ ] **Step 11: Add deterministic A009 qualification to GitHub CI and extend CI contract tests**

CI must run:

```powershell
python scripts/qualify_integrated_loop_a009.py
```

CI must not run:
- `qualify_integrated_loop_a009_physical.py`;
- Ollama HTTP/CLI commands;
- A005/A006/A007 physical scripts.

Preserve existing full pytest, architecture audit, repository qualifier, A003 qualification, and A008 deterministic qualification.

- [ ] **Step 12: Run Task 5 gates**

Run:
```powershell
python -m pytest -q tests/test_integrated_loop_benchmark.py tests/test_integrated_loop_qualification_cli.py tests/test_integrated_loop_physical_cli.py tests/test_ci_contract.py
python scripts/qualify_integrated_loop_a009.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
python scripts/qualify_procedural_memory_a008.py
git diff --check
```

Expected: all engineering gates PASS. A009 primary hypothesis may validly report SUPPORTED/MIXED/NOT_SUPPORTED.

- [ ] **Step 13: Commit Task 5**

Commit:

`Add A009 integrated loop qualification`

### Task 6: Exact branch qualification, physical evidence, report, and closure transition

**Files:**
- Create: `docs/development/reports/ASCA-20261010-A009-integrated-cognitive-loop.md`
- Modify: `docs/development/tasks/A009-integrated-cognitive-loop.md`
- Modify: `docs/development/tasks/CURRENT.md`
- Modify: `docs/development/tasks/ROADMAP.md`
- Modify: `README.md`
- Modify: `tests/test_a009_task_ledger.py`
- Modify: `tests/test_task_ledger.py`
- Modify qualification tests only when review/evidence validation requires it.

- [ ] **Step 1: Run fresh portable qualification and branch engineering gate**

Run from the clean candidate:
```powershell
python scripts/qualify_integrated_loop_a009.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
python scripts/qualify_procedural_memory_a008.py
git diff --check
git status --short --branch
git rev-parse HEAD
```

Record exact raw metrics, fingerprint, and primary outcome.

- [ ] **Step 2: Push branch normally and require exact candidate SHA CI**

Require the CI run to include deterministic A009 qualification and conclude success on the exact branch SHA.

- [ ] **Step 3: Inspect local physical runtime prerequisites read-only**

Check:
- Ollama reachable;
- qwen3-embedding:0.6b installed with exact pinned digest/dimension;
- qwen3.5:4b installed with the current A004-qualified identity expected by the script.

Do not pull/replace models automatically to chase a result.

- [ ] **Step 4: Run local physical A009 qualification when prerequisites match**

Run:
```powershell
python scripts/qualify_integrated_loop_a009_physical.py --output <evidence-path>
```

If exact prerequisites do not match, record the physical qualification as not executed with the concrete identity mismatch/prerequisite evidence; do not falsify GREEN physical evidence.

Physical evidence cannot rewrite the deterministic primary outcome.

- [ ] **Step 5: Verify isolation and historical-result preservation**

Read-only confirm:
- A006 historical result remains NOT_SUPPORTED;
- A007 historical result remains SUPPORTED;
- A008 historical result remains SUPPORTED;
- A007 trigger enum unchanged;
- A008 retry semantics unchanged;
- FlyWireLLM was not modified by this branch;
- no real tool execution path was added to A009.

- [ ] **Step 6: Write A009 qualification report**

Record:
- exact branch SHA and CI run;
- portable test/gate results;
- fixture version/fingerprint/case IDs;
- raw per-policy scope/attempt/recovery/regression/final-state metrics;
- primary SUPPORTED/MIXED/NOT_SUPPORTED outcome;
- CHUNKED/FLAT diagnostic;
- model-control isolation evidence;
- physical qualification status/evidence;
- claims boundary;
- historical A006/A007/A008 outcomes preserved;
- FlyWireLLM untouched.

- [ ] **Step 7: Write closure-transition tests RED**

Require:
- A009 task Status DONE;
- ROADMAP A009 DONE;
- CURRENT A010 PLANNED/no issue;
- README current stage reflects A009 result;
- report exact SHA/CI/fingerprint/outcome;
- exactly one primary outcome;
- no A010 issue;
- historical A006/A007/A008 results unchanged.

Verify RED before docs transition.

- [ ] **Step 8: Transition task/roadmap/README and run closure gate**

Run:
```powershell
python -m pytest -q tests/test_a009_task_ledger.py tests/test_task_ledger.py
python scripts/qualify_integrated_loop_a009.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
python scripts/qualify_procedural_memory_a008.py
git diff --check
```

Expected: all PASS.

- [ ] **Step 9: Commit closure candidate and require exact closure-branch CI**

Commit:

`Qualify A009 integrated cognitive loop`

Push normally and require exact SHA CI success.

### Task 7: Whole-branch review, post-review qualification, and main integration

**Files:**
- Modify only files required by review findings or integration evidence.

- [ ] **Step 1: Perform whole-branch review from activation base to closure candidate**

Prioritize:
- snapshot reuse after interrupted attempt;
- duplicate execution IDs;
- scope skip/duplicate/overflow;
- hidden retry inside one A008 attempt;
- model-control leakage;
- A003 familiarity incorrectly vetoing retrieval;
- SELECTIVE_CONVERGENCE accidentally promoted;
- A007 trigger mutation;
- CHUNKED replaced by BLIND/FLAT on primary path;
- benchmark fixture/result leakage;
- outcome validator accepting impossible relationships;
- physical evidence changing portable primary outcome;
- overclaiming scope/dispatch counts as compute/energy savings.

- [ ] **Step 2: Fix Critical/Important findings with RED→GREEN tests**

If controller/benchmark/qualification semantics change, rerun deterministic A009 qualification and preserve/freeze identity only when the fixture itself was proven invalid.

- [ ] **Step 3: Run post-review full branch gate**

Run:
```powershell
python scripts/qualify_integrated_loop_a009.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
python scripts/qualify_procedural_memory_a008.py
git diff --check
```

- [ ] **Step 4: Commit review fixes/evidence and require exact post-review branch CI**

Record reviewer limitation honestly if only author self-review is available.

- [ ] **Step 5: Verify main integration preconditions**

Require:
- main checkout clean;
- main == origin/main before integration;
- A009 branch head descends from exact activation base;
- A009 worktree clean;
- A009 GitHub issue still open.

- [ ] **Step 6: Fast-forward local main only**

Use ff-only integration. No merge commit, rebase, reset, clean, or force push.

- [ ] **Step 7: Verify merged main before push**

Run:
```powershell
python scripts/qualify_integrated_loop_a009.py
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
python scripts/qualify_procedural_memory_a008.py
git diff --check origin/main..HEAD
```

- [ ] **Step 8: Push main and require exact final-main CI**

Do not close the A009 issue until exact merged-main CI succeeds.

- [ ] **Step 9: Record tested main-integration evidence**

Any documentation-only main evidence commit must itself pass fresh local gates and exact-main CI before issue closure.

- [ ] **Step 10: Final synchronization and issue closure**

Require:
- final HEAD == origin/main;
- ahead/behind 0/0;
- main clean;
- exact final-main CI success;
- CURRENT A010 PLANNED/no issue;
- FlyWireLLM untouched.

Close the A009 GitHub issue with final SHA/CI/test count/fingerprint/primary outcome/key recovery and boundedness metrics.

- [ ] **Step 11: Cleanup**

Remove the clean A009 worktree and delete the local `research/a009-integrated-cognitive-loop` branch non-force. Preserve remote history unless explicitly requested otherwise.

## Execution Order

Execute Tasks 1-7 sequentially using Native/inline execution, TDD RED→GREEN, fresh full regression, and commit evidence at each task boundary.

Before Task 1 implementation:
- verify exact main/CI synchronization after this plan is committed and pushed;
- create no issue before activation;
- then use the native Git worktree tool to isolate the A009 branch.

The deterministic fixture and fingerprint must be frozen before accepting the first final A009 hypothesis result. Experiment validity remains separate from SUPPORTED/MIXED/NOT_SUPPORTED. A010 remains PLANNED until reviewed A009 behavior is integrated and exact final-main evidence is GREEN.
