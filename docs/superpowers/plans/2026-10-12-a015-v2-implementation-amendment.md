# A015 v2 Wire Contract and Qualification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Native is already selected. Steps use checkbox (`- [ ]`) syntax for tracking; one fresh independent whole-branch reviewer follows implementation and qualification.

**Goal:** Complete the model-facing JSON contract and qualify corrected A015 with unchanged full public data and 64 bilingual requests under the approved 12,288 context protocol.

**Architecture:** Dependency-free v2 wire and prompt modules sit beside the preserved v1 prompt source. Trusted configuration selects the version; existing goal, capability, execution and completion semantics remain authoritative. A new immutable freeze, exact-source behavior gate and evidence schema separate v2 qualification from original-checkout historical v1 replay.

**Tech Stack:** Python >=3.11, stdlib, pytest, existing Git/GitHub CI and pinned Ollama adapters; Native execution on CDQ-P through LConnect.

**Spec:** `docs/superpowers/specs/2026-10-12-a015-v2-wire-contract-design.md`. User approved the artifact at commit `48d7a8915783f07dc68f121c95e6ebe1e80645d2`, blob `4fa4a173d349f49296c537c38fa0af97a80e036c`, on 2026-10-12 23:14:50 Asia/Bangkok.

## Global Constraints

- Status: DRAFT_FOR_PLAN_REVIEW. Written-spec approval is complete; this plan still requires review before product changes or inference. Preserve Native without another execution-method selection.
- Worktree: `T:\Space\Projects\ProjectsAI\ProjectASCA\.superpowers\worktrees\a015-unified-agent-runtime`; branch `research/a015-unified-agent-runtime`. Use `C:\DATAstore\Python\Python3-14-3\python.exe` for native commands. Long-running commands use managed processes and retained logs.
- Preserve every v1 fixture, `src/project_asca/agent_runtime/prompts.py`, original raw/setup/trial/partial/report artifacts and names. Copy requests/public/oracle/certificate to v2 byte-for-byte; public.version remains `a015-public-v1`. No oracle/case/pair/family/expected answer enters runtime configuration or prompts.
- Exactly 64 requests, 32 semantic pairs, 32 EN/32 TH, 8 families of 8; repetitions=3, seed=0, existing balanced schedule, 192 trials per variant/384 overall. Normalizers and research decision rules remain unchanged. No case filtering, response-driven tuning or retry to improve an outcome.
- Only profile_id/model_context differ: `a015-stage-a-v2` / `12288`. All other frozen values remain: request_bytes=8192; model_calls=4; prompt_tokens=32768; output_per_call=1024; output_tokens=2048; context_rounds=3; queries_per_round=2; retrieval_queries=6; indexed_records=256; vectors_scored=1536; context_items=24; context_bytes=16384; relation_invocations=3; relation_hops=3; relation_visits_per_call=8; relation_edges_per_call=32; relation_visits=24; relation_edges=96; strategy_attempts=3; recovery_rounds=2; actions_per_attempt=32; actions=96; call_depth=8; transitions=64; trace_events=256; trace_bytes=262144; state_bytes=65536; deadline_seconds=180.0; model_call_seconds=120.0.
- Both variants: context_limit=12288, temperature=0, seed=0, thinking=false, output<=1024/call. Direct has one invocation and no retrieval/ranking/repair; unified retains four calls/2048 aggregate output. Existing A014 routing allowance=192.
- Generation `qwen3.5:4b` digest `2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd`; embedding `qwen3-embedding:0.6b` digest `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`, dimension=1024; Ollama=0.32.15.
- Preserve all 67 A011 paths, profile hash `add06f285bf6decc7d492b987d3769dc64db4cb3d0177c8c6586d50ee5f6d46d` and protected hash `8df49f05fe54de43667ab2f8ef5de2caae9376ffedf2cb8f8d26f0e4abcca6b6`. Preserve v0.1.0 tag `0d2b2ebd0882d2b5e950b56e227cb4a0c5de898e` / peeled `fd8d298c38625b2bcfc2073fa3c8f951415a9bb2` and release assets.
- No FlyWireLLM change, new capability, external effect, release promotion, reset/clean/rebase/force-push, Stage B/C or new milestone. A015 stays ACTIVE until final qualification/review/integration gates.
- Current-source equality remains strict. Historical v1 runs its original verifier at `c968330cf97d7a7c7893aa70fddd150ce8dd510e`; historical PASS does not qualify corrected source.
- No source, parser, prompt, capability, evaluator, frozen input or normalizer changes during the 384 trials after G4. Preserve any interrupted/invalid batch and disclose a new version before a necessary behavior change.

## Review Focus

1. A valid-looking model response combines literal/reference alternatives, boolean numeric values, excessive nesting or extra closed keys; reject it before execution. Owner: Task 2.
2. Thai/codepoint spans or compound/semicolon clauses bind only part of the request; reject omissions and retain exact separators. Owner: Task 2.
3. A relation wrapper lacks directed public constituents, or a textual state claim is presented as executed effects; independently reject false completion. Owner: Task 2.
4. Setup/warm-up uses default8192 while metadata claims12288, or a reduced v1 admission budget changes its historical transport setting; verify actual dispatched settings. Owners: Tasks 1 and 4.
5. A resealed evidence file mixes versions/approval anchors, invents setup cost, alters counters/answer/references, or hides unknown usage; reject qualification. Owner: Task 4.

---

## Completed prerequisites and file responsibilities

The first five independent-review corrections are already complete at `55aa42d0febecdbc0014ffef3853b9105e9471f2`, with exact byte preservation finalized at `48d7a8915783f07dc68f121c95e6ebe1e80645d2`. Watched RED→GREEN regressions, 1454 full-suite passes, portable/audit/freeze/A011/history checks and exact CI `38274882155` SUCCESS are recorded. Corrected source fingerprint `8500fe9e5dbf7fca7858d3653ca45b577d27be0e5d8df9e90923fd997c9e99f8` is NOT_G4_V2. Do not repeat that correction pass.

`agent_runtime/wire_v2.py` owns immutable notation and structural validation; `prompts_v2.py` owns role assembly. Existing parser/semantic owners retain trusted grounding and execution checks. `evaluation/fixture.py` and `freeze.py` own offline versioned workload/lock assembly; `source.py` owns Git anchors and dependency closure; `evidence.py`/`codec.py` own closed metadata and replay; `physical.py` owns actual setup and trial dispatch. Core modules never read frozen fixture files.

All paths below are repository-relative. Commands run from this worktree; `python` in command blocks denotes the native interpreter specified above. Each code task records its own RED/GREEN output, commit and brief in the existing private execution ledger. Full verification is required at G2/G4/final gates; do not rerun the full suite after every small edit when targeted checks suffice.

### Task 1: Versioned wire, prompt and trusted context dispatch

**Files:**
- Create: `src/project_asca/agent_runtime/wire_v2.py`, `src/project_asca/agent_runtime/prompts_v2.py`.
- Modify: `src/project_asca/agent_runtime/profile.py`, `src/project_asca/agent_runtime/contracts.py`, `src/project_asca/agent_runtime/broker.py`, `src/project_asca/agent_runtime/interpretation.py`, `src/project_asca/agent_runtime/strategy.py`.
- Modify: `src/project_asca/evaluation/direct.py` for trusted version selection.
- Test: `tests/agent_runtime/test_wire_v2.py`, `tests/agent_runtime/test_profile_v2.py`, `tests/agent_runtime/test_model_adapter.py`.

**Interfaces:**
- Consumes: `RuntimeProfile`, `ModelPrompt`, `ModelPurpose`, `BrokerModelRequest` and existing model-port transport.
- Produces in `profile.py`: `wire_version_for_profile(profile: RuntimeProfile) -> str` returning `a015-wire-v2` only for the trusted v2 profile; `generation_context(profile: RuntimeProfile) -> int` returning12288 for v2 and8192 for existing v1/development profiles.
- Produces in `wire_v2.py`: immutable `WIRE_TEXT_V2: str` and `WIRE_SCHEMA_V2: Mapping[str, object]` with version `a015-wire-v2`, closed=true, exact grammar text and role-output declarations from spec `3.
- Produces in `prompts_v2.py`: `template_v2(role: str) -> tuple[str, str]` (system/hash), `render_role_prompt_v2(purpose: ModelPurpose, payload: Mapping) -> ModelPrompt`, `template_bundle_v2() -> Mapping[str, Mapping]`. DIRECT assembly consumes `template_v2("DIRECT")`.
- Existing `BrokerModelRequest` accepts pinned transport contexts8192/12288 only. Existing v1 profiles retain lower development admission limits; the v2 profile requires model_context exactly12288. Other resource ceilings remain v1 ceilings; the physical freeze later requires exact values.

- [ ] **Step 1: Add failing prompt/profile/transport tests.** Pin assertions:
```python
system, digest = template_v2("DIRECT")
assert len(system.encode("utf-8")) == 4118
assert digest == "09a639d9979b3e72b71c9fc21fc08af5a02d6bf3014cb091dba7077c10f5d300"
assert WIRE_SCHEMA_V2["version"] == "a015-wire-v2"
assert generation_context(RuntimeProfile()) == 8192
assert generation_context(RuntimeProfile(model_context=4096)) == 8192
v2 = RuntimeProfile(profile_id="a015-stage-a-v2", model_context=12288)
assert wire_version_for_profile(v2) == "a015-wire-v2"
assert generation_context(v2) == 12288
```
  `test_v2_dispatch_records_actual_context` uses the existing fake transport to assert both request.context_limit and emitted Ollama options.num_ctx equal12288, with temperature0/seed0/thinkingfalse/output<=1024. Reject v2 contexts12287/16384 and a v1 profile requesting12288. Test all five exact template IDs and role whitelists, unknown-role rejection, immutable schema, unchanged v1 prompt/template bytes and unchanged A014 routing.
- [ ] **Step 2: Run RED.** `python -m pytest tests/agent_runtime/test_wire_v2.py tests/agent_runtime/test_profile_v2.py tests/agent_runtime/test_model_adapter.py -q`. Expected failures concern missing v2 APIs/context dispatch; retain the output.
- [ ] **Step 3: Implement constants and assembly.** Copy exact approved `complete-wire-v2.txt` text, stripping only its final LF. DIRECT system is the exact spec core plus LF plus that3935-byte text. Other roles carry this complete notation and their own declared output restriction; QUERY remains a declared existing contract, without a new runtime query path. Use only trusted control/configuration to choose v2; preserve original `prompts.py`. Keep schema/template correspondence in one immutable definition.
- [ ] **Step 4: Implement context dispatch.** Add the two exact profile helpers and use `generation_context(control.profile)` when constructing broker requests. Existing adapters already forward context_limit; exercise them without modifying legacy code. Preserve lowered v1 admission behavior and all output/call/deadline ceilings.
- [ ] **Step 5: Run GREEN.** Repeat Step 2; run `python -m pytest tests/agent_runtime/test_broker.py tests/agent_runtime/test_routing_adapter.py tests/a015/test_direct.py -q` and both architecture/runtime audits. Compare v1 prompt and seven fixture Git blobs with original G2. Expected: PASS, no physical calls.
- [ ] **Step 6: Commit.** Stage only the listed deliverable/test paths; `git commit -m "feat(a015): add versioned complete wire and context dispatch"`. Record SHA and focused verification.

### Task 2: Strict wire/parser/semantic correspondence

**Files:**
- Modify: `src/project_asca/agent_runtime/wire_v2.py`, `src/project_asca/agent_runtime/broker.py`, `src/project_asca/agent_runtime/goals.py`, `src/project_asca/agent_runtime/interpretation.py`, `src/project_asca/agent_runtime/plans.py`, `src/project_asca/agent_runtime/strategy.py`, `src/project_asca/agent_runtime/capabilities.py`, `src/project_asca/agent_runtime/state.py`.
- Modify: `src/project_asca/evaluation/direct.py` and `src/project_asca/agent_runtime/verification.py` only where advertised type/answer correspondence requires it.
- Test: `tests/agent_runtime/test_wire_v2.py`, `tests/agent_runtime/test_review_regressions.py`, `tests/a015/test_v2_direct.py`.

**Interfaces:**
- Consumes: Task 1 version helpers; existing `strict_json_object(raw)`, `validate_parameters(task, parameters, schemas)`, `validate_intent_proposal(raw, request, schemas)`, `parse_plan_proposal(raw)`, `validate_plan(...)`, `bind_answer(proposal, goal, records, configuration)` and `verify_completion(...)`. Preserve their existing signatures.
- Produces in `wire_v2.py`: `validate_role_output_v2(role: str, raw: Mapping[str, object]) -> Mapping[str, object]`, returning the immutable closed response or raising ValueError. Call it after strict decoding and before shared interpretation/plan/direct validation for trusted v2 consumers.
- This validator checks shape/types/bounds/role alternatives; existing trusted validators independently check grounding, capability registration/effects/preconditions, reference ownership and postconditions. A shape-valid response never grants success.

- [ ] **Step 1: Write failing structural cases.** Hand-author development JSON examples from the public contract, without `deterministic_intent` or oracle-derived goals. Define local pytest fixtures in the listed test files for these explicit inputs. Assertions for `test_v2_closed_unions_and_limits`:
```python
assert validate_role_output_v2("QUERY_PROPOSAL", {"queries": ["temperature"]})["queries"]
for bad in ({"queries": []}, {"queries": ["a", "b", "c"]},
            {"queries": ["a"], "extra": 1}):
    with pytest.raises(ValueError):
        validate_role_output_v2("QUERY_PROPOSAL", bad)
for raw in ('{"x":1,"x":2}', '{"x":NaN}', '[]', '{"x":1e999}'):
    with pytest.raises(ValueError):
        strict_json_object(raw)
```
  Parametrize INTENT/DIRECT/PLAN alternatives: exact three transform sources, six operations with operation-specific fields, output enum/length, exact I/IS and paired stops; reject missing group key/value, wrong select fields, descriptive source strings, extra literal reference, reference plus value, empty/nonblank violations, boolean N/offsets, J depth9/array257/bytes65537 and unknown closed keys. J depth is measured within each J value, not by counting its enclosing intent/envelope.
- [ ] **Step 2: Write failing trusted correspondence controls.** `test_v2_spans_preserve_every_clause` uses explicit EN/TH codepoint spans, compound thresholds, semicolon requests and literal/tab/quoted separators; dropped original clauses or unbound material values must raise/reject. Missing factual fields remain valid request-grounded intent and end MISSING_EVIDENCE. Descending requests remain UNSUPPORTED. `test_v2_plan_bindings_and_state_types` rejects duplicate/forward step IDs, absent context/request references, wrong resolved types, extra capability inputs, version other than"1", unsupported assert comparisons and new/wrong-type state fields. State-sum exact keys/finite operands/own postcondition are pinned.
- [ ] **Step 3: Write failing shared-completion controls.** `test_v2_relation_constituents_and_state_claims` hand-authors a DIRECT S1→PumpAssembly→Plant path with e4/e5 and evidence:e4/e5; assert valid directed completion, then reject reversed/missing/invented/low-confidence constituents, repeated nodes/edges and incomplete requested predicates. A structured STATE_GOAL answer fails; an executed registered plan must have observations and matching postcondition verification. `test_v2_answer_shape_and_role_stop` asserts PLAN roles accept only R, INTENT only I/IS, direct paired/justified stops, exact fact/transform outputs and rejection of extra single-output claims, including sort+sum list-and-sum requirements.
- [ ] **Step 4: Run RED.** `python -m pytest tests/agent_runtime/test_wire_v2.py tests/a015/test_v2_direct.py -q`. Retain failures proving actual v2 gaps; existing corrected regressions remain GREEN.
- [ ] **Step 5: Implement correspondence.** Add structural v2 checks at the declared consumer boundaries; fix only shared semantic discrepancies exposed by these controls. Keep finite typed comparison and capability assert eq/ge/le, optional field only for filter/sort, existing snapshot/evidence semantics and state-field types. No hidden repair, new capability or response-specific allowance.
- [ ] **Step 6: Run GREEN.** Repeat Step 4; run `python -m pytest tests/agent_runtime tests/a015 -q` and both audits/A011 preservation. Expected: all old/new controls PASS; cancellation/publication, replay-reference and counter/answer corrections remain intact.
- [ ] **Step 7: Commit.** Stage explicit Task 2 paths; `git commit -m "fix(a015): enforce complete v2 wire correspondence"`. Record RED/GREEN and unchanged v1 identities.

### Task 3: Immutable v2 workload and actual G2 freeze

**Files:**
- Create: `fixtures/a015/stage-a-v2/requests.json`, `fixtures/a015/stage-a-v2/public.json`, `fixtures/a015/stage-a-v2/oracle.json`, `fixtures/a015/stage-a-v2/token-bound-certificate.json`, `fixtures/a015/stage-a-v2/profile.json`, `fixtures/a015/stage-a-v2/schemas.json`, `fixtures/a015/stage-a-v2/freeze.lock.json`.
- Modify: `src/project_asca/evaluation/fixture.py`, `src/project_asca/evaluation/freeze.py`, `src/project_asca/evaluation/source.py`; `scripts/freeze_agent_runtime_a015.py`.
- Test: `tests/a015/test_v2_freeze.py`, `tests/a015/test_freeze.py`.

**Interfaces:**
- Consumes: `WIRE_SCHEMA_V2`, `template_bundle_v2()`, existing `FrozenWorkload` and `bounds_from_workload(workload)`.
- Produces in `fixture.py`: `workload_version(workload: FrozenWorkload) -> str` ("v1"/"v2"; reject mixed/unknown trusted profile/schema/lock identities); extend `render_direct_prompt(text: str, public: Mapping, *, version: str = "v1") -> ModelPrompt`.
- Extend `validate_freeze(workload, bounds, *, approval_metadata: Mapping | None = None) -> FreezeValidation`. Retain v1 lock serialization. V2 validation carries workload_id, approval_metadata and component_blobs in addition to existing fields; `write_freeze_lock(root, validation) -> str` remains immutable first-write.
- First v2 freeze CLI requires `--approval-record .superpowers/sdd/2026-10-12-a015-unified-agent-runtime/v2-approval-record.json` pointing to a retained private JSON approval record; later `--check` reads the immutable lock. The record is written from actual approved Git anchors before first freeze, with no inference. V2 approval_metadata has original_spec_commit/blob, original_plan_commit/blob, amendment_spec_commit/blob and amendment_plan_commit/blob. Original commits are cccbf0fc/4ca246df; amendment spec is the exact approved48d7a891/blob above. Amendment plan is the actual user-reviewed plan commit/blob recorded after approval, never a guessed/self-containing SHA.
- V2 source policy retains all existing runtime/adapters/evaluator/protocol scripts and static legacy initializer/import closure, includes both v1/v2 seven-file fixture sets and explicit guard/thin verifier scripts, and excludes docs/tests/generated artifacts from their own behavior fingerprint.
- `verify_frozen_anchors(root, commit, workload, *, freeze_commit: str | None = None) -> None` preserves original checks. For v2 it requires an actual supplied G2 ancestor whose exact lock/component blobs match, plus original/amendment ancestry and byte-preserved approved artifacts.

- [ ] **Step 1: Write failing preservation/identity/bound tests.**
```python
for name in ("requests.json", "public.json", "oracle.json", "token-bound-certificate.json"):
    assert (v2_root / name).read_bytes() == (v1_root / name).read_bytes()
assert {k for k in v1_profile if v1_profile[k] != v2_profile[k]} == {"profile_id", "model_context"}
assert v2_profile["profile_id"] == "a015-stage-a-v2"
assert v2_profile["model_context"] == 12288
assert max(v.direct_prompts, key=lambda r: r["upper_tokens"])["upper_tokens"] == 9795
assert v.max_prompt_upper_bound + 1024 == 10819
assert sum(r["upper_tokens"] + 1024 <= 12288 for r in v.direct_prompts) == 64
assert sum(r["upper_tokens"] + 1024 <= 8192 for r in v.direct_prompts) == 0
```
  `v1_root/v2_root` are local temporary test fixture directories; `v` is the declared FreezeValidation. Check all64 user payloads equal exactly original text plus full public canonical JSON, full public bytes5351, certificate hash `f68470eb8b0c5bf9e3ee4d4b40b5bdeb06cc614ba151eec71c4eb84fe7ee2bdf`, all exact template IDs and direct digest from Task 1.
- [ ] **Step 2: Write failing lock/anchor controls.** `test_v2_freeze_rejects_mixed_or_mutated_components` rejects wrong profile/schema/workload, changed prompt/certificate/normalizer/resources, omitted imported evaluator dependency and altered approved spec/plan blobs. `test_v2_lock_has_no_self_commit_cycle` asserts first lock write is stable/immutable, raw component Git blobs and canonical hashes are recorded, and actual G2 SHA is supplied after commit rather than embedded into its own lock.
- [ ] **Step 3: Run RED.** `python -m pytest tests/a015/test_v2_freeze.py tests/a015/test_freeze.py -q`. Missing v2 assembly/lock/anchor behavior must account for failures.
- [ ] **Step 4: Implement offline versioned assembly.** Copy the four original files byte-for-byte. Set only approved profile delta and new exact schema. Assemble all64 prompts from production v2 constants; include canonical/Git component hashes, five assembled role templates, direct prompt hashes/bounds, unchanged A014 router identity, source policy, approved anchors, order/seed and context/settings in v2 lock aggregate. Exclude lock from its own aggregate and include it in final behavior identity. Existing v1 defaults and freeze checks remain unchanged. Run `python scripts/freeze_agent_runtime_a015.py --fixture fixtures/a015/stage-a-v2 --approval-record .superpowers/sdd/2026-10-12-a015-unified-agent-runtime/v2-approval-record.json` once to write the immutable production lock from that exact approval record.
- [ ] **Step 5: Run GREEN and G2 readiness.** Repeat Step 3; run `python scripts/freeze_agent_runtime_a015.py --fixture fixtures/a015/stage-a-v2 --check` and the original default freeze check, full pytest, both audits, repository qualification, A011 and original historical replay. Static serialization makes no generation/embedding call. If any approved exact wire/prompt hash/bound changes, stop for a concrete amended design review before freeze.
- [ ] **Step 6: Commit G2-v2.** Stage only Task 3 deliverables; `git commit -m "feat(a015): freeze approved bilingual v2 protocol"`. Push/read back the exact immutable lock/component Git blobs, record the actual freeze SHA in the private checkpoint, then validate its approved ancestry. Record exact-commit CI. No primary inference yet.

### Task 4: Closed v2 evidence, truthful setup and current-source CI

**Files:**
- Modify: `src/project_asca/evaluation/evidence.py`, `src/project_asca/evaluation/codec.py`, `src/project_asca/evaluation/source.py`, `src/project_asca/evaluation/physical.py`, `src/project_asca/evaluation/portable.py`.
- Modify: `scripts/verify_a015_physical_evidence.py`, `scripts/qualify_agent_runtime_a015.py`, `scripts/qualify_agent_runtime_a015_physical.py`, `.github/workflows/ci.yml`.
- Test: `tests/a015/test_v2_evidence.py`, `tests/a015/test_physical_contract.py`, `tests/a015/test_physical_cli.py`, `tests/a015/test_evidence.py`.
- Reuse unchanged: `scripts/verify_agent_runtime_a015_history.py`. Preserve every original evidence/report blob.

**Interfaces:**
- Consumes: Task 3 version, immutable G2 lock and `verify_frozen_anchors(..., freeze_commit=actual_g2)`; unchanged strict `source_fingerprint(root, commit, universe) -> SourceFingerprint`.
- Add flat `PhysicalRunMetadataV2` with all original metadata fields plus required amendment_spec_commit/blob, amendment_plan_commit/blob, workload_id, profile_id, wire_version, model_context and settings. Define it independently of the v1 dataclass so default interruption does not reorder required fields. Keep original spec/plan fields and original anchors; freeze_commit names actual G2-v2.
- Preserve `build_evidence(trials, metadata) -> PhysicalEvidence`, `decode_evidence(raw, *, reference_contents) -> PhysicalEvidence`, `load_evidence(output) -> PhysicalEvidence` and `verify_evidence(e, *, root)` signatures. Dispatch only closed schemas `a015-physical-evidence-v1` / `a015-physical-evidence-v2`; unknown/mixed versions reject. V2 metadata and replay bind exact workload/profile/wire/templates/source/settings/approvals.
- Preserve `run_physical_comparison(workload, *, output, repetitions, seed)`. Explicit `--fixture fixtures/a015/stage-a-v2` selects v2; repetitions3/seed0 remain fixed. G4 sidecar `.superpowers/sdd/2026-10-12-a015-unified-agent-runtime/v2-g4.json`, selected by `A015_G4_RECORD`, carries actual exact behavior SHA/source fingerprint/successful CI and actual G2/approved anchors, checked before setup.
- Extend portable CLI `--fixture` with preserved v1 default. Portable records remain scripted engineering evidence, never physical qualification.

- [ ] **Step 1: Write failing evidence/version/source controls.** Extend existing isolated source-repo/test-evidence helpers for v2 and persist `core.longpaths` before clone checkout. Assertions:
```python
assert evidence.schema == "a015-physical-evidence-v2"
assert evidence.metadata.model_context == 12288
assert verify_evidence(evidence, root=source_repo).valid
assert not verify_evidence(resealed_mixed_version, root=source_repo).valid
assert not verify_evidence(resealed_wrong_context, root=source_repo).valid
assert not verify_evidence(resealed_missing_dependency, root=source_repo).valid
```
  `test_v2_resealed_review_faults` independently reseals altered verification execution_id, unresolved/misattributed action observation_ref, counters, rendered answer and terminal assertions; every case is invalid. Unknown invoked generation/embedding/scoring usage remains incomplete; interrupted or partial schedules cannot qualify. Helpers build only scripted development artifacts, retaining the existing replay checks.
- [ ] **Step 2: Write failing setup/dispatch tests.** `test_v2_setup_uses_profile_before_ports_and_warmup` spies on setup/warm controls, BrokerModelRequest and transport: all generation dispatches use12288 and pinned settings; document/index/warm costs stay separately recorded. Assert v2 setup contains no invented `historical_setup_probe`. The old Task3 generic1-call/23-input/1-output probe remains historical v1 data only. Record actual warm-up request parameters/response usage; metadata labels alone cannot pass. Misstated settings/identity/unknown warm usage fail readiness/qualification.
- [ ] **Step 3: Run RED.** `python -m pytest tests/a015/test_v2_evidence.py tests/a015/test_physical_contract.py tests/a015/test_physical_cli.py -q`. Expected: v2 metadata/anchor/warm-up behavior is missing, not unrelated environment failures.
- [ ] **Step 4: Implement versioned evidence and setup.** Load trusted configuration before creating setup controls/ports; pass cfg.profile to setup/warm controls and explicit context12288 to warm-up BrokerModelRequest. Capture fresh backend/model metadata, declared maximum, dispatched settings and actual usage. Reuse independently derived counters, receipt/reference replay and answer rendering; do not bypass current-source equality. V1 decoder remains available, with qualification at original checkout only.
- [ ] **Step 5: Separate CI proof contexts.** Move the existing historical command to a `historical-a015-v1` job using original-checkout helper and recorded limitations. Current-source job runs v1/v2 freeze checks, tests/audits and v2 portable controls. Before primary v2 evidence exists, record current physical qualification as pending; no empty-artifact PASS. Task 5 activates the unconditional current-source physical verifier after the actual saved batch.
- [ ] **Step 6: Run GREEN/G4 readiness.** Repeat Step 3; run full pytest, both audits, repository/A011 guards, both freeze checks, v2 portable CLI and unchanged historical helper. Verify source policy contains thin verifier and all static dependencies. Original v1 on corrected checkout must still fail strict source equality; original checkout validates only the historical contract.
- [ ] **Step 7: Commit.** Stage explicit Task 4 paths; `git commit -m "feat(a015): bind v2 evidence and native protocol settings"`. Push exact SHA and inspect CI. This commit or a subsequent necessary portable-only fix becomes the clean G4 candidate; do not call it G4 until Task 5 gate passes.

### Task 5: Exact G4 gate and fixed384 physical qualification

**Files:**
- Create ignored G4/preflight/checkpoint records in the existing private execution ledger.
- Create: `docs/development/qualification/a015-agent-runtime-physical-v2.json` and its raw content-reference directory; retain same-run partial artifacts at their generated distinct paths.
- Create: `docs/development/reports/ASCA-20261012-A015-v2-qualification.md`.
- Modify: `.github/workflows/ci.yml` only after the completed saved v2 batch, to activate unconditional current-source evidence verification. No model-facing/source change.

**Interfaces:**
- Consumes: exact G2 checkpoint, clean source/approved anchors, successful exact feature CI, v2 CLI and strict offline verifier from Task 4.
- Produces: actual G4 SHA/fingerprint/CI/preflight record, fixed384 raw trials, complete settings/usage/replay validation and a factual research outcome. No future SHA or positive outcome is assumed.

- [ ] **Step 1: Confirm G4 readiness.** Reuse verified outputs unless a new change requires rerunning them. Require full suite, corrected controls, complete wire correspondence, all64 static admissions, leakage/audits/A011/release/v1 history guards and both freeze checks. On CDQ-P recheck Ollama0.32.15, both model digests/dimension and fresh declared context maximum>=12288; recorded262144 alone is not a live allocation proof.
- [ ] **Step 2: Freeze actual behavior gate.** Require a clean selected source and exact-commit GREEN CI. Record actual G4 SHA, full source mode/path/blob fingerprint, actual G2 lock/blob ancestry and approved original/amendment artifacts. Recheck current HEAD/remote/source before writing `A015_G4_RECORD`. G4 record is external to its own source universe; it is not a guessed/self-containing commit.
- [ ] **Step 3: Start exactly one primary batch as a managed native process.** Set `A015_G4_RECORD` to the retained sidecar, then run:
```text
python scripts/qualify_agent_runtime_a015_physical.py --fixture fixtures/a015/stage-a-v2 --repetitions 3 --seed 0 --output docs/development/qualification/a015-agent-runtime-physical-v2.json
```
  Common warm-up/index/setup is separately observed; both variants' task requests use12288. Save one checkpoint after every request. Retain failures/timeouts and unknown usage; no task retry, early case omission or response-driven change. Send concise progress updates while monitoring managed session status.
- [ ] **Step 4: Validate the saved complete batch.** Postflight identity/source must equal preflight, trials384/192each, schedule/seed/pairs/languages/families and original decision denominators must match. Run `python scripts/verify_a015_physical_evidence.py docs/development/qualification/a015-agent-runtime-physical-v2.json`. Expected: valid=true, usage_complete=true, trials384 and no errors; actual outcome may be mixed/negative. On interrupted/invalid evidence, retain raw/partial artifacts, leave ACTIVE and record the concrete blocker.
- [ ] **Step 5: Publish factual v2 evidence/report and current CI hook.** Report exact source/G2/G4/approval/workload/template/certificate/settings identities, all usage/costs/failures and per-language/family/paired denominators, genuine recovery and predeclared outcome. Disclose complete schema/five corrections and8192→12288 delta without a causal v1/v2 superiority claim. Preserve original reports and mark v1 historical with review limitations in the new report. Add unconditional `verify_a015_physical_evidence.py ...physical-v2.json` to the current-source CI job.
- [ ] **Step 6: Commit artifacts with source unchanged.** Verify strict equality to G4 before/after `git commit -m "docs(a015): record source-bound v2 physical qualification"`, push and inspect exact CI. Evidence/docs/CI packaging must not change the selected behavior universe. Physical completion alone does not close A015.

### Task 6: Fresh whole-branch review and authorized integration

**Files:**
- Create the independent v2 whole-branch review report under `docs/development/reports/`.
- Update after valid review/integration: `docs/architecture/A015-UNIFIED-AGENT-RUNTIME.md`, `docs/development/QUALIFICATION-MATRIX.md`, `docs/development/tasks/A015-unified-agent-runtime.md`, `docs/development/tasks/CURRENT.md`, `docs/development/tasks/ROADMAP.md` and `README.md` where the existing workflow requires them.
- Issue#19 actions occur only within the original authorized integration workflow.

**Interfaces:**
- Consumes: actual implementation, approved spec/plan, both freezes, completed v2 evidence/report and current exact CI.
- Produces: independent acceptance or concrete blockers, normal authorized integration, exact integrated-head CI and honest final task status.

- [ ] **Step 1: Request one fresh independent whole-branch review.** Native implementer remains the root. Use the reviewer/model required by the execution skill; inspect actual whole-branch code/spec/plan/evidence and all six original findings. No extra pre-G4 independent-review gate or repeated agent review of the already completed first-five correction pass.
- [ ] **Step 2: Resolve findings with evidence discipline.** Portable tests must demonstrate any necessary fix. A selected-source change invalidates current-source qualification of the old batch; preserve it and require a disclosed approved new freeze/G4/full384 version before closure. A docs-only correction keeps strict source equality and does not trigger repeated tests without a concrete need.
- [ ] **Step 3: Verify final feature acceptance.** Require no Blocking/Important findings, full checks as needed after actual changes, exact final-head CI, strict G4 source equality, valid complete v2 physical replay, approved ancestry and unchanged v1/A011/v0.1.0.
- [ ] **Step 4: Integrate through the already authorized normal workflow.** Inspect live main/upstream first; preserve concurrent work. No force push, release or tag move. Run/read exact integrated-head CI and source/evidence equality before DONE.
- [ ] **Step 5: Close only verified engineering work.** Mark A015 DONE/close Issue#19 only after these gates, stating the actual research outcome even when negative. Otherwise retain ACTIVE with the earliest unmet gate. Deliver concise commit/CI/evidence links and any concrete blocker; no new milestone activation.

## Plan self-review and handoff

Root self-review completed against all nine spec sections: preservation/budgets→global constraints and Tasks1/3; complete wire/trusted semantics→Tasks1/2; exact static proof→Task3; G2/G4/closed evidence/source/actual setup→Tasks3–5; separate original-checkout history/current CI→Task4; fixed384/report/research/integration→Tasks5/6. Each Review Focus has an explicit owning test. Later tasks use the exact signatures/types declared above; v1 defaults remain compatible. The plan is comparable in length to the spec and contains decisions/assertions rather than implementation bodies.

The approved spec bytes remain untouched. This plan is reviewable before implementation; its actual reviewed Git commit/blob will become the amendment-plan anchor. Native persists. The next gate is human plan review, then task-by-task execution starting at Task1.
