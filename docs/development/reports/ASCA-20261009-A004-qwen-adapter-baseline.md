# FlyWireASCA A004 Qwen Adapter Baseline Qualification

Date: 2026-10-09
Task: A004 — Local Model Adapter & Qwen3.5:4B Baseline
GitHub Issue: #4
Branch: research/a004-qwen-adapter

## Decision

The initial A004 candidate was GREEN on exact branch commit
`c7b710a36f2cdc8f97177418ccf371d995817d94` with CI run `37891675731`.
The first documentation closure commit was
`9b800698d883c5233994a3781322f6a01ff7b648` with CI run `37891872173`.

Whole-branch Native self-review then found two Important validation gaps. Both
were reproduced RED and fixed in one review pass. The reviewed implementation
is exact commit `b50a07667f96379aa6f72a9de50550764068580e`, which passed
full local qualification, a fresh physical Qwen run, and branch CI run
`37892333300`.

The generic model contract remains backend-neutral. The local Ollama adapter
and Qwen-only control baseline are qualified separately from ASCA familiarity,
memory, routing, and other cognitive mechanisms.

This report update is the final documentation layer and must itself pass exact
branch CI before fast-forward integration to `main`.

## Delivered boundary

A004 adds:

- immutable backend-neutral `ModelMessage`, `ModelRequest`,
  `ModelDescriptor`, and `ModelResponse` records;
- backend-neutral `ModelAdapter` protocol and public error hierarchy;
- standard-library JSON/HTTP Ollama transport;
- `OllamaModelAdapter` with strict tag/digest identity checks;
- explicit thinking-off text-only request mapping;
- Qwen-only machine-scored control baseline;
- local physical qualification CLI;
- roadmap migration from future A004-A010 to A005-A011.

No A003 familiarity lookup, associative recall, working-set routing, tool
calling, vision payload, or FlyWireLLM execution is implemented in this layer.

## Exact portable branch qualification

Exact candidate SHA:

`c7b710a36f2cdc8f97177418ccf371d995817d94`

Fresh local portable evidence:

- `python -m pytest -q`: **101 passed**
- `python scripts/audit_architecture_contract.py`:
  **architecture_contract_audit=PASS**
- `python scripts/qualify_repository.py`:
  **repository_qualification=PASS**
- `python scripts/run_familiarity_benchmark_a003.py --qualify`: PASS
- `git diff --check HEAD^ HEAD`: PASS
- worktree: clean

Exact portable branch CI:

- workflow: CI
- run id: `37891675731`
- head SHA: `c7b710a36f2cdc8f97177418ccf371d995817d94`
- event: push
- conclusion: **success**

GitHub Actions does not download, launch, or physically qualify Ollama/Qwen.
Physical qualification is intentionally local-machine evidence.

## Physical Qwen qualification

Physical qualification used implementation commit:

`3b8cdbb03db8cd959ce52639316a36e978d1e8f4`

Only documentation changed between that implementation commit and the exact
branch candidate above.

Observed runtime/model identity:

- backend: `ollama`
- Ollama version: `0.32.15`
- model tag: `qwen3.5:4b`
- full digest:
  `2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd`
- architecture: `qwen35`
- exact parameter count: `4,659,865,088`
- reported parameter size: `4.7B`
- quantization: `Q4_K_M`
- declared context length: `262144`
- embedding length: `2560`
- capabilities: completion, thinking, tools, vision

Qualified generation profile:

- profile: `qwen3.5-4b-thinking-off-v1`
- thinking: false
- tools: false
- vision: false
- context limit: 8192
- max output tokens: 256
- temperature: 0.0
- seed: 0
- streaming: false

Controlled Qwen-only baseline:

- case count: 6
- passed cases: 6
- pass_rate: 1.0
- prompt tokens total: 293
- generated tokens total: 16
- total duration: 2,509,991,400 ns
- prompt evaluation duration total: 1,739,271,000 ns
- generation evaluation duration total: 586,869,000 ns
- aggregate load duration: unavailable because Ollama omitted that field on
  some individual responses

Per-case normalized outputs:

- english-exact -> `blue` — PASS
- thai-exact -> `แมว` — PASS
- context-selection -> `29` — PASS
- context-middle -> `green` — PASS
- insufficient-context -> `insufficient_context` — PASS
- boolean-allowed -> `yes` — PASS

The adapter rejects nonempty returned hidden-thinking content whenever the
request used `thinking=False`. All six accepted physical baseline responses
therefore satisfied the thinking-off adapter invariant.

Token and timing values above are local Ollama observations on this machine.
They are not FLOP estimates, energy measurements, or generalized model-speed
claims.

## Qualification issue found and corrected

The first live physical run completed inference but failed while emitting the
JSON evidence because the Windows console used `cp1252` and the payload
contained Thai text.

The root cause was stdout encoding, not Qwen inference or scoring.

Regression test
`test_emit_handles_windows_cp1252_console_with_thai_payload` was observed
RED before the fix. The qualification CLI now writes UTF-8 bytes when stdout
offers a binary buffer and writes the evidence file with the same UTF-8 bytes.

Fix commit:

`3b8cdbb03db8cd959ce52639316a36e978d1e8f4`

After the fix:

- qualification CLI tests: 6 passed
- full suite: 101 passed
- A003 benchmark: PASS
- architecture audit: PASS
- repository qualifier: PASS
- diff check: PASS
- physical qualification rerun: PASS

## Whole-branch review and one fix pass

A fresh reviewer/subagent was not available in this harness, so the final
review was an author self-review performed as a separate pass over the entire
A004 branch. This is weaker than an independent fresh-context review and is
recorded explicitly.

Two Important findings were fixed:

1. **Public contract boundary validation.** Generic model/baseline records
   relied too heavily on Python type hints. Raw malformed role/message/content
   and scoring/result values could reach downstream logic instead of failing at
   the public contract boundary. Regression tests
   `test_public_contracts_reject_malformed_runtime_types_at_boundary` and
   `test_baseline_contract_rejects_malformed_scoring_messages_and_case_results`
   were observed RED before the fix and GREEN afterward.
2. **Non-streaming Ollama response completeness.** The adapter accepted
   `stream:false` responses without requiring `done=true` or assistant role,
   and treated returned boolean `thinking=false` as nonempty hidden thinking.
   Regression tests
   `test_generate_rejects_incomplete_or_wrong_role_nonstream_response` and
   `test_generate_accepts_explicit_false_as_no_hidden_thinking_content` were
   observed RED before the fix and GREEN afterward.

Reviewed fix commit:

`b50a07667f96379aa6f72a9de50550764068580e`

Post-review evidence:

- focused review regressions: 4 passed
- full suite: **107 passed**
- A003 familiarity qualification: PASS
- architecture audit: PASS
- repository qualifier: PASS
- diff check: PASS
- physical Qwen qualification rerun: **6/6, pass_rate 1.0**
- post-review exact branch CI run: `37892333300` — success

The post-review physical run retained the same model digest/profile and
observed 293 prompt tokens, 16 generated tokens, and
6,462,243,000 ns total duration. These timings are local-run evidence only and
are not directly comparable as a general speed claim because model load/cache
state differed between runs.

Deferred minor review notes are limited to future hardening outside A004: some
hand-crafted `ModelBaselineReport` aggregate totals are not fully
cross-validated against case-result sums; the A004-specific qualification CLI
exposes `--expected-digest` while its descriptor validator intentionally still
pins the A004 digest; a successful adapter descriptor is cached for the
lifetime of one adapter instance; and a generic future adapter could return a
response whose request/model identity is inconsistent with `inspect()` unless
that adapter validates it. None affects the qualified Ollama/Qwen A004 path.

## Model-agnostic boundary

The generic `flywire_asca.model` contracts do not encode Qwen- or
Ollama-specific fields. Ollama-specific transport/identity behavior is isolated
in the adapter implementation.

Later ASCA components can therefore use the same generic `ModelAdapter`
interface with Qwen, FlyWireLLM, or another backend.

A004 does not claim that ASCA improves Qwen. It establishes the control model
and model-facing infrastructure required to test that later.

## FlyWireLLM paused evidence

FlyWireLLM was inspected read-only before A004 branch publication:

- repository HEAD:
  `9aa8acba1ecdefcdce4678b2914fc2d2dcaacc14`
- branch: `research/l004-base50m-pretraining`
- upstream: `origin/research/l004-base50m-pretraining`
- ahead/behind: 0/0
- worktree: clean
- no FlyWireLLM training runner was present in the observed Python process list

A004 did not start, stop, restart, import, or modify the FlyWireLLM training
runtime or repository.

## Roadmap migration

The insertion of A004 shifts only future planned milestones:

- old A004 Associative Memory & Recall -> new A005
- old A005 Working Set / Selective Activation -> new A006
- old A006 Surprise, Uncertainty & Expansion -> new A007
- old A007 Procedural Memory / Skill Chunking -> new A008
- old A008 Integrated Cognitive Loop -> new A009
- old A009 Dense/Non-selective Baseline Comparison -> new A010
- old A010 ASCA v0.x Qualification -> new A011

Historical A001-A003 qualification identifiers and reports are unchanged.

## Deferred scope

A004 deliberately defers:

- Qwen fine-tuning/training;
- tool calling;
- vision;
- thinking-enabled qualification;
- ASCA memory/familiarity context injection;
- associative recall;
- paired ASCA+Qwen vs Qwen-only comparison;
- FlyWireLLM adapter implementation.

## Next milestone

A005 — Associative Memory & Recall.

A005 remains **PLANNED**. Closing A004 does not activate A005 automatically.
