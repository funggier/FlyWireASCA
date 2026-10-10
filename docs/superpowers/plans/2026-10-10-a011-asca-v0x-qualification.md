# A011 ASCA v0.x System Qualification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Qualify the existing ASCA v0.x engineering system with fresh portable and local physical evidence while preserving every frozen A006-A010 research outcome.

**Architecture:** A stdlib-only qualification package validates immutable records, a reviewed profile, provenance, existing qualifier evidence, and pack publication. Two scripts orchestrate existing CLIs; the physical script first repeats the portable path on the same clean candidate. Cognitive packages and all ten existing qualifier scripts remain unchanged.

**Tech Stack:** Python >=3.11, pytest, standard-library subprocess/JSON/hashlib/pathlib/urllib, Git, existing GitHub Actions CI; local Ollama 0.32.15 with the pinned models.

**Spec:** [2026-10-10-a011-asca-v0x-qualification-design.md](../specs/2026-10-10-a011-asca-v0x-qualification-design.md), approved by the user with “โอเคครับ ทำต่อได้เลย” on 2026-10-10 at 16:11:41 +07:00. Approved spec Git blob: `c14b921f3f6b83166f2bb6e554f226636fc7ed29`.

## Global Constraints

- This is the written implementation plan review gate. A011 remains PLANNED; issue, worktree, activation, and implementation require user plan approval **and** an execution-method choice.
- Preserve Git/WIP/history: no reset, clean, rebase, force-push, or destructive checkout. Live Git/GitHub/runtime override stale prose.
- PRE-A011 is completed; Issue #11 remains CLOSED / COMPLETED. A001-A010 remain DONE.
- Keep `0.1.0.dev0`; no tag/release/stable promotion, no automatic `0.1.0`, no A012, no FlyWireLLM work.
- Engineering final states are exactly ENGINEERING_QUALIFIED, ENGINEERING_NOT_QUALIFIED, QUALIFICATION_BLOCKED. Gate states are PASS / FAIL / BLOCKED / NOT_RUN.
- Portable-only means PORTABLE_ONLY, is_final=false, engineering_verdict=null. A portable PASS never certifies the full system.
- Research outcomes remain A006=NOT_SUPPORTED, A007=SUPPORTED, A008=SUPPORTED, A009=SUPPORTED, A010=NOT_SUPPORTED. Report five separate rows; no intelligence score.
- Use Qualification Pack + Fresh System Replay + Frozen Evidence Audit; preserve the spec's exact identities, policy meanings, threshold, fingerprints, A010 counts, and dense-only sentinel.
- No A003-A010 cognitive changes, A009/A010 retrieval optimization, fixture/cue/threshold/outcome retuning, hidden retries, model pull/substitution, calibration, or runtime restart.
- A real/suspected cognitive defect stops qualification and becomes an explicit separately approved repair task. Infrastructure repairs use RED -> GREEN.
- Qualification imports only stdlib and existing contracts. Cognitive packages never import qualification. Scripts own legacy-module loading.
- Preserve existing qualifier defaults, model adapter limits, and acceptance rules. New process containment cannot impose a stricter physical deadline; durations are descriptive.
- Portable commands/tests make no Ollama/model/network calls after installation. Pytest orchestration tests inject runners and never recursively spawn real pytest.
- Frozen profile bytes and independently reviewed anchor must agree. No runtime accept-current/retune/bless-drift switch.
- Every pack binds one clean exact candidate SHA/profile hash before and after execution. Documentation metadata SHA is separate from qualified behavior SHA.
- Publication is atomic into a new directory outside the checkout. Preserve failed/blocked packs. Publication failure cannot return success.

## Review Focus

1. Shallow CI lacks the historical baseline, and Windows uses CRLF: protected identities use HEAD Git blob/mode records without fetching history (Task 3).
2. Child exits 0 with truncated/duplicate-key JSON or contradictory success fields: raw evidence and legacy acceptance must agree or FAIL (Task 4).
3. Repeat changes execution IDs, case order, sentinel, or unknown fields: only optional top-level note is excluded; other drift FAILS (Task 6).
4. Runtime disappears after preflight alongside identity drift: confirmed absence can BLOCK, but any verified hard failure dominates (Task 7).
5. Artifact paths escape through links, destination exists, or final write fails: refuse overwrite/publication, retain diagnostics, never return success (Task 5).

---

## Authority and readiness snapshot

Planning baseline: clean/synchronized main `0ca486b136da127ce69543f8c5c9258b6663ece6`, exact push/main CI [38039978481](https://github.com/funggier/FlyWireASCA/actions/runs/38039978481), completed/success.

Written-spec publication: `6eb5fb1399bc21a05599b92d9aa8b312df70c9e1`, exact CI [38039670308](https://github.com/funggier/FlyWireASCA/actions/runs/38039670308), success. All-state paginated issue inspection finds #1-#11 closed/completed and no A011 issue.

Read-only runtime inspection at 2026-10-10T09:15:16.837Z matched terminal/embedding digests and embedding metadata dimension 1024. Unchanged A008/A009/A010 portable CLIs were inspected and repeated without changing workloads. No fresh A011 physical replay is claimed.

Activation base is the **live reviewed plan publication HEAD**, not a historical SHA above. Recheck its exact CI and source state in Task 1.

## File and responsibility map

All module paths below expand under `src/flywire_asca/qualification/`.

| File | Responsibility |
| --- | --- |
| `__init__.py` | Explicit exports, no execution at import |
| `records.py` | Immutable records, enums, gate constants, tagged errors |
| `manifest.py` | Strict JSON codec, schema/causal/coverage consistency |
| `classifier.py` | Portable status, full verdict, CLI exit mapping |
| `profile.py` | Literal trust anchors, frozen-profile loader |
| `provenance.py` | Clean source snapshots and protected Git-tree digest |
| `process.py` | Command specification, injectable process runner |
| `evidence.py` | Normalize existing child evidence, repeat identity |
| `artifacts.py` | New-directory artifacts, index, atomic JSON/Markdown |
| `portable.py` | P00-P09 orchestration |
| `physical.py` | Read-only runtime probe, H00-H07 orchestration |

Other exact files:

| File | Responsibility |
| --- | --- |
| `scripts/_a011_legacy_evidence.py` | Allowlisted legacy validators, no inference at import |
| `scripts/qualify_asca_v0x_a011.py` | Portable CLI |
| `scripts/qualify_asca_v0x_a011_physical.py` | Full CLI |
| `docs/development/qualification/a011-v0x-profile-v1.json` | Reviewed profile, created in Task 3 |
| `tests/qualification/conftest.py` | Qualification-only fake runner/runtime/evidence factories |
| `tests/qualification/test_records.py`, `test_manifest.py`, `test_classifier.py` | Record/schema/classification tests |
| `tests/qualification/test_profile.py`, `test_provenance.py` | Frozen profile and Git identity |
| `tests/qualification/test_process.py`, `test_evidence.py` | Existing evidence adapters |
| `tests/qualification/test_artifacts.py` | Publication integrity |
| `tests/qualification/test_portable.py`, `test_physical.py` | Runner decisions |
| `tests/qualification/test_ci_contract.py` | CI topology |
| `.github/workflows/ci.yml` | Add A011 portable gate/upload, retain old steps |
| `scripts/audit_architecture_contract.py`, `tests/test_architecture_audit.py` | Qualification dependency edge/direction |
| `tests/test_task_ledger.py` | Mutable lifecycle at activation/closure |
| `docs/development/tasks/A011-asca-v0x-qualification.md`, `CURRENT.md`, `ROADMAP.md` | Lifecycle/evidence ledger |
| `docs/development/QUALIFICATION-MATRIX.md` | Extend topology, preserve historical outcomes |
| `docs/development/reports/ASCA-20261010-A011-v0x-qualification.md` | Final evidence-backed report |

Existing cognitive sources, ten frozen qualifier scripts, and historical milestone-test semantics are unchanged.

## Shared record contract

Use frozen dataclasses with recursively immutable values: copy mappings into immutable mappings, sequences into tuples. Check exact primitive types before conversion; bool cannot be an int. JSON maps tuples to arrays. `JsonValue` means null/bool/int/finite float/string/immutable string-key mapping/tuple of JsonValue; `JsonObject` is that mapping type.

These fields are the exact v1 nested keys; no extension keys:

| Record | Fields and types |
| --- | --- |
| `Reason` | code:str, gate_id:str, message:str, evidence_refs:tuple[str,...] |
| `ProfileIdentity` | id:str, schema_version:int, sha256:str, expected_sha256:str, expected_identity_source:str |
| `SourceSnapshot` | commit:str\|None, clean:bool\|None, protected_sha256:str\|None, profile_sha256:str\|None, captured_at:str |
| `SourceIdentity` | repository:str, commit:str\|None, protected_sha256:str\|None, before:SourceSnapshot, after:SourceSnapshot |
| `GateEvidence` | gate_id:str, scope:Scope, status:GateStatus, command:tuple[str,...]\|None, started_at:str\|None, finished_at:str\|None, exit_code:int\|None, artifacts:tuple[str,...], errors:tuple[Reason,...], cause_ids:tuple[str,...] |
| `FrozenCheck` | identity:str, expected:JsonValue, observed:JsonValue, status:GateStatus, evidence_refs:tuple[str,...] |
| `ResearchObservation` | outcome:ResearchOutcome, role:EvidenceRole, freshness:Freshness, evidence_ref:str |
| `ResearchEvidence` | milestone:str, expected_outcome:ResearchOutcome, observations:tuple[ResearchObservation,...], historical_refs:tuple[str,...] |
| `ReplayObservation` | milestone:str, run_index:int, fixture_version:str, fixture_fingerprint:str, payload_sha256:str, qualifier_blob:str, source_commit:str, profile_sha256:str, evidence_ref:str |
| `ReplayIdentity` | pack_id:str, source_commit:str\|None, profile_sha256:str, observations:tuple[ReplayObservation,...] |
| `PhysicalEnvironment` | hostname:str, platform:str, python_version:str, ollama_version:str\|None, endpoint:str, terminal:JsonObject\|None, embedding:JsonObject\|None, evidence_refs:tuple[str,...] |
| `ArtifactRecord` | path:str, kind:str, sha256:str, byte_length:int |
| `QualificationPack` | schema_version:int, profile:ProfileIdentity, source:SourceIdentity, scope:Scope, is_final:bool, portable_status:GateStatus, engineering_verdict:EngineeringVerdict\|None, gates:tuple[GateEvidence,...], frozen_checks:tuple[FrozenCheck,...], research_evidence:tuple[ResearchEvidence,...], replay_identity:ReplayIdentity, physical_environment:PhysicalEnvironment\|None, errors:tuple[Reason,...], blockers:tuple[Reason,...], artifact_index:tuple[ArtifactRecord,...], claims_boundary:tuple[str,...] |

Additional enums: `Scope={PORTABLE_ONLY,FULL_SYSTEM}`; `ResearchOutcome={SUPPORTED,NOT_SUPPORTED}`; `EvidenceRole={PHYSICAL_PRIMARY,PORTABLE_PRIMARY,PHYSICAL_SECONDARY}`; `Freshness={FRESH_PORTABLE,FRESH_PHYSICAL}`. Historical provenance is historical_refs, never a fabricated fresh observation.

Terminal/embedding environment objects each contain exactly model:str, digest:str, dimension:int|None. Terminal dimension is null; embedding dimension is 1024 when inspected. Keep complete runtime descriptors in indexed raw evidence.

Missing snapshot fields require failed/blocked state and a causal source/prerequisite reason. PASS requires exact 40-hex commit, 64-hex hashes, clean=true before/after, matching profile, and one candidate. UTC start/end must parse and finish cannot precede start.

The claims_boundary tuple must retain three statements: project-internal declared-profile qualification; separate A006-A010 research outcomes; no external certification or aggregate intelligence/performance claim. The report prints these statements directly.

Reason codes: PROFILE_DRIFT, IDENTITY_DRIFT, REPLAY_DRIFT, EVIDENCE_INVALID, SOURCE_MISMATCH, QUALIFIER_FAILED, PREREQUISITE_UNAVAILABLE, MODEL_MISSING, ARTIFACT_WRITE_FAILED. The last is an infrastructure failure.

## Gate and child-evidence decisions

P00-P09 commands/IDs exactly follow the spec. P05/P06/P07 run once; P08 repeats A008/A009/A010 in separate paths and checks first/repeat hashes against frozen semantic digests. Repeats belong to P08, not new gate IDs.

Commands use `sys.executable`, absolute script paths, argument arrays, repo cwd, shell=False. JSON children use unique --output paths. Retain stdout/stderr bytes, output JSON, exit and UTC times; stdout/file JSON must canonically agree.

| Child | Additional PASS contract |
| --- | --- |
| pytest | Exit0, complete nonempty completion log; no invented marker |
| architecture | Exact architecture_contract_audit=PASS line, no FAIL line |
| repository | Exact repository_qualification=PASS line, no FAIL line |
| A003 | One strict stdout JSON object under --qualify; existing CLI report validator; no invented marker/--output |
| A008/A009/A010 | experiment_valid true, errors empty, existing validate_qualification_payload empty; frozen scope/version/fingerprint/outcome/full semantic hash |
| A004 | qualified true, errors empty, observed frozen model, existing generation/baseline acceptance |
| A005 | mode=qualification, experiment_valid/retrieval_qualified true, errors empty, exact threshold, threshold_origin=physical_frozen_threshold_v1; model and vector_health.dimension both1024 |
| A006/A007 | experiment_valid true, errors empty, existing validate_physical_experiment(experiment) empty; descriptors/frozen profiles/fingerprints/hypothesis_outcome exact |
| A009/A010 physical | physical_prerequisites_valid AND physical_integration_valid true, errors empty; physical fixture version, portable_primary_outcome and observed metadata exact |

A004-A007 retain 120-second adapter timeout defaults. A009/A010 retain their adapter defaults. No new physical subprocess deadline. Endpoint is fixed http://127.0.0.1:11434: A009/A010 physical CLIs expose no base-url option, so this plan adds no endpoint override or legacy API change.

## Task dependency and evidence map

| Task | Independently reviewable result | Inventory coverage |
| --- | --- | --- |
| 1 | Issue/worktree/ledger activation after approval | G06 |
| 2 | Records/schema/classifier, dependency audit | Q01 |
| 3 | Profile anchor and shallow-safe source identity | Q02; Q03 provenance |
| 4 | Process/evidence adapters | Q03 |
| 5 | Validated pack/report publication | Q07 |
| 6 | Ollama-free portable pack/repeat audit | Q04 |
| 7 | Physical pack and blocker semantics | Q06 |
| 8 | Exact portable CI integration | Q05 |
| 9 | Fresh candidate qualification | Q08 |
| 10 | Whole-change review/repairs/integration | Q09/Q10 |
| 11 | Report/issue/ledger closure/full handoff | Q11 |

Tasks 2-8 end with focused tests/commits. Tasks 9-11 are operational evidence tasks; no artificial tests echo metadata.

### Task 1: Gate-authorized activation

**Files:** Modify `docs/development/tasks/A011-asca-v0x-qualification.md`, `CURRENT.md`, `ROADMAP.md`, `tests/test_task_ledger.py`.

**Interfaces:** Consumes approved spec/plan and method choice; produces actual issue number, branch/worktree, activation-base SHA and ACTIVE ledger. Never guess #12.

- [ ] **Step 1 — Verify authorization/readiness.** Record explicit plan approval and Native/Subagent-driven choice. Require live main clean/sync, exact latest CI success, Issue #11 closed/completed, A011 PLANNED, and paginated all-state absence of A011 issue. Inspect/reconcile an existing issue rather than duplicating it.
- [ ] **Step 2 — Create issue.** Title `A011 — ASCA v0.x System Qualification / Certification Layer`; structured GitHub body links spec/plan and lists Q01-Q11, frozen outcomes, non-scope, gates and completion evidence.
- [ ] **Step 3 — Isolate.** Invoke using-git-worktrees; suggested branch `qualification/a011-asca-v0x`, worktree `T:\Space\Projects\ProjectsAI\FlyWireASCA-worktrees\a011-asca-v0x-qualification`. Check destination/branch, preserve WIP and capture actual base.
- [ ] **Step 4 — RED lifecycle.** Rename mutable test to `test_current_points_to_active_a011_with_actual_issue`; assert CURRENT/A011 task ACTIVE, actual returned issue in both, ROADMAP A011 ACTIVE. Replace PRE-A011's mutable PLANNED pin with `test_pre_a011_stays_completed_during_a011_lifecycle`: PRE DONE/#11 completed, A001-A010 DONE, roadmap A001-A011 once.

Run `python -m pytest tests/test_task_ledger.py -q`; expected RED against still-PLANNED docs, without weakening historical assertions.

- [ ] **Step 5 — GREEN activation.** Update three ledger docs with actual ACTIVE/issue/branch/base, G05/G06 evidence and Task2 next action. Rerun ledger, full pytest, architecture/repository audits; PASS.
- [ ] **Step 6 — Commit.** Stage exact three docs plus test_task_ledger.py, cached whitespace PASS, commit `docs(a011): activate approved system qualification`. Record RED/GREEN/issue/SHA. Original main remains outside feature execution.

### Task 2: Strict records, manifest, classifier and dependency boundary

**Files:** Create package __init__.py/records.py/manifest.py/classifier.py; create tests/qualification/conftest.py/test_records.py/test_manifest.py/test_classifier.py. Modify audit dependency dictionary and tests/test_architecture_audit.py.

**Interfaces — produces:**
- `QualificationError(code: str, message: str)`, enums/records above.
- `PORTABLE_GATE_IDS: tuple[str,...]`, `PHYSICAL_GATE_IDS: tuple[str,...]` from Appendix A.
- `strict_json_object(raw: bytes) -> dict[str, JsonValue]`: duplicate-key/UTF-8/nonfinite/trailing/root rejection.
- `decode_pack(raw: bytes) -> QualificationPack`; `encode_pack(pack: QualificationPack) -> bytes`.
- `manifest_issues(pack: QualificationPack) -> tuple[Reason,...]`: coverage/causes/scope/roles/verdict; coherent failure packs are valid.
- `classify_full(gates: tuple[GateEvidence,...], errors: tuple[Reason,...], blockers: tuple[Reason,...]) -> EngineeringVerdict`.
- `classify_portable(gates: tuple[GateEvidence,...], errors: tuple[Reason,...], blockers: tuple[Reason,...]) -> GateStatus`.
- `pack_exit_code(pack: QualificationPack) -> int`:0 pass/qualified,1 fail,2 confirmed blocked.

**Test helper contract:** conftest defines `make_pack(scope: Scope = Scope.FULL_SYSTEM) -> QualificationPack`, `replace_gate(pack: QualificationPack, gate_id: str, status: GateStatus, reason: Reason | None = None) -> QualificationPack`; complete coherent records, with artifacts materialized in Task5. Test functions receive these as pytest fixtures, not undefined globals.

- [ ] **Step 1 — Write decision tests.**

```python
def test_negative_research_outcomes_do_not_fail_engineering(make_pack):
    pack = make_pack()
    assert [r.expected_outcome.value for r in pack.research_evidence] == [
        "NOT_SUPPORTED", "SUPPORTED", "SUPPORTED", "SUPPORTED", "NOT_SUPPORTED"]
    assert classify_full(pack.gates, pack.errors, pack.blockers).value == "ENGINEERING_QUALIFIED"

def test_portable_pass_never_has_final_verdict(make_pack):
    pack = make_pack(Scope.PORTABLE_ONLY)
    assert pack.is_final is False and pack.engineering_verdict is None
    assert classify_portable(pack.gates, pack.errors, pack.blockers).value == "PASS"
    assert pack_exit_code(pack) == 0
```

Also pin `test_verified_failure_dominates_simultaneous_blocker` (A006 identity FAIL plus confirmed H00 BLOCKED => NOT_QUALIFIED), `test_all_pass_full_is_qualified`, `test_confirmed_blocker_with_caused_not_run_is_blocked`, `test_unexplained_not_run_is_failure`. Schema tests: `test_missing_duplicate_unknown_gate_is_rejected`, `test_pass_with_errors_and_bad_cause_is_rejected`, `test_unknown_nested_field_is_rejected`, `test_bool_counts_duplicate_keys_nonfinite_and_bad_hash_are_rejected`, `test_records_deep_copy_and_freeze_nested_values`, `test_scope_finality_and_physical_freshness_cannot_contradict`.

- [ ] **Step 2 — RED.** `python -m pytest tests/qualification/test_records.py tests/qualification/test_manifest.py tests/qualification/test_classifier.py -q`; missing API/behavior fails, no test syntax error.
- [ ] **Step 3 — Implement.** FAIL precedes confirmed BLOCKED; missing/duplicate/unknown gates or unexplained NOT_RUN fail closed. NOT_RUN has null execution fields and cause referencing an earlier failed/blocked gate; reject cycles. BLOCKED uses only independently proved PREREQUISITE_UNAVAILABLE/MODEL_MISSING. PASS has no errors. Negative research outcome never implies engineering failure.
- [ ] **Step 4 — RED/GREEN dependency audit.** Add `test_audit_rejects_qualification_to_cognitive_dependency`, `test_audit_rejects_cognitive_to_qualification_dependency`, `test_audit_allows_qualification_to_contracts` with temporary repo/import copies. RED shows new unregistered package was invisible; add `"qualification": frozenset({"contracts"})`; all audit tests GREEN.
- [ ] **Step 5 — Verify/commit.** Focused tests above plus `python -m pytest tests/test_architecture_audit.py -q`, architecture audit PASS. Stage only Task2 files, cached whitespace PASS, commit `feat(a011): define strict qualification records and verdicts`.

### Task 3: Frozen profile and exact source provenance

**Files:** Create package profile.py/provenance.py; create `docs/development/qualification/a011-v0x-profile-v1.json`; create tests/qualification/test_profile.py/test_provenance.py.

**Interfaces — consumes:** Task2 records/error/strict JSON.
**Produces:**
- `FrozenProfile(raw: bytes, sha256: str, values: JsonObject)`: validated/deep immutable.
- Literal `EXPECTED_PROFILE_SHA256 = "add06f285bf6decc7d492b987d3769dc64db4cb3d0177c8c6586d50ee5f6d46d"` in profile.py, never derived from current file at runtime.
- `load_frozen_profile(raw: bytes) -> FrozenProfile`: exact canonical bytes/schema/identities/trusted hash.
- `capture_source(repo_root: Path, profile_path: Path, protected_paths: tuple[str,...]) -> SourceSnapshot`.
- `source_issues(before: SourceSnapshot, after: SourceSnapshot, expected_commit: str, profile: FrozenProfile) -> tuple[Reason,...]`.
- `protected_tree_sha256(repo_root: Path, paths: tuple[str,...]) -> str`: HEAD mode/path/blob algorithm in Appendix A.

- [ ] **Step 1 — Profile RED.** `test_reviewed_profile_hash_is_literal_and_exact` asserts 7481 canonical bytes/hash add06...; `test_every_frozen_identity_mutation_is_rejected` parameterizes tags/digests/dimension/threshold, every fingerprint/outcome/policy, every A010 count/sentinel, gates/source hash/semantic digests. `test_profile_bytes_cannot_bless_changed_values` mutates temporary copies and asserts PROFILE_DRIFT. `test_profile_rejects_unknown_keys_bool_dimension_and_nonfinite_threshold` rejects malformed input.
- [ ] **Step 2 — Provenance RED.** `test_shallow_checkout_needs_only_head_blobs`: depth1 temporary clone passes without c149... object. `test_crlf_checkout_keeps_protected_git_identity`: clean CRLF returns identical digest. `test_missing_mode_blob_or_extra_cognitive_path_is_source_mismatch`, `test_dirty_or_changed_head_profile_is_source_mismatch`, `test_mid_run_source_change_is_failure`: SOURCE_MISMATCH, never qualified.

Assertions: `assert len(raw) == 7481`; `assert hashlib.sha256(raw).hexdigest() == EXPECTED_PROFILE_SHA256`; drift uses `with pytest.raises(QualificationError)` and `assert exc.value.code == "PROFILE_DRIFT"`; provenance uses `assert issues[0].code == "SOURCE_MISMATCH"` and `assert snapshot.protected_sha256 == "8df49f05fe54de43667ab2f8ef5de2caae9376ffedf2cb8f8d26f0e4abcca6b6"` for clean shallow/CRLF inputs.

Run `python -m pytest tests/qualification/test_profile.py tests/qualification/test_provenance.py -q`; expected missing API/profile then identity RED.

- [ ] **Step 3 — Implement profile.** Serialize Appendix A as UTF-8 sorted compact JSON **without newline/BOM**, verify reviewed byte hash. Explicit implementation-time freeze, never a runtime generator. Profile has 67 protected paths/hash `8df49f05fe54de43667ab2f8ef5de2caae9376ffedf2cb8f8d26f0e4abcca6b6`.
- [ ] **Step 4 — Implement provenance.** Read git status --porcelain=v1 --untracked-files=all, rev-parse HEAD and HEAD tree entries via argument arrays. Reject dirty/source/profile changes, missing path/mode/blob drift, or additional committed Python files under the old cognitive/contract package tree outside new qualification. Candidate SHA binds A011 additions. Use Git blobs, not raw CRLF bytes; never fetch/check out old baseline. Capture before/after even on failures where obtainable.
- [ ] **Step 5 — GREEN/commit.** Same focused tests and architecture audit PASS; hashlib verifies 7481 bytes/add06...; stage exact Task3 files, cached whitespace PASS, commit `feat(a011): freeze profile and verify candidate provenance`.

### Task 4: Explicit processes and existing-evidence adapters

**Files:** Create package process.py/evidence.py and `scripts/_a011_legacy_evidence.py`; create tests/qualification/test_process.py/test_evidence.py; extend conftest.

**Interfaces — consumes:** Task2 strict JSON/records, Task3 FrozenProfile.
**Produces:**
- `CommandSpec(gate_id: str, argv: tuple[str,...], cwd: Path, output_path: Path | None, timeout_seconds: float | None)`.
- `ProcessEvidence(command: CommandSpec, started_at: str, finished_at: str, exit_code: int | None, stdout: bytes, stderr: bytes, execution_error: str | None)`.
- `ProcessRunner` protocol `run(command: CommandSpec) -> ProcessEvidence`; `SubprocessRunner` implementation.
- `LegacyValidator = Callable[[dict[str, JsonValue]], tuple[str,...]]`.
- `AdapterResult(status: GateStatus, payload: JsonObject | None, errors: tuple[Reason,...], frozen_checks: tuple[FrozenCheck,...], observation: ResearchObservation | None, semantic_sha256: str | None)`.
- `normalize_child(gate_id: str, evidence: ProcessEvidence, output_bytes: bytes | None, profile: FrozenProfile, validator: LegacyValidator | None) -> AdapterResult`.
- `semantic_payload_sha256(payload: JsonObject, milestone: str, profile: FrozenProfile) -> str`: strict top keys, only top-level note omitted; nested semantics retained.
- Script-only `load_legacy_validators(repo_root: Path) -> Mapping[str, LegacyValidator]`: allowlist A008/A009/A010 validate_qualification_payload; A006/A007 validate_physical_experiment on experiment member. Unique module names, no main call.

**New test helpers:** conftest defines `FakeRunner` recording commands and returning queued ProcessEvidence; `portable_payload(milestone: str) -> dict[str,JsonValue]` invokes unchanged script `run_qualification()` and existing validator with no child/network; `physical_payload(gate_id: str) -> dict[str,JsonValue]` creates qualification-test-only fake raw evidence.

For physical fixtures, reuse patterns without modifying old tests: test_qwen_qualification_cli.py FakeAdapter; test_vector_memory_qualification_cli.py _fake_adapter_class; test_selective_activation_qualification_cli.py and test_uncertainty_expansion_qualification_cli.py _valid_physical_payload; test_integrated_loop_physical_cli.py FakePhysicalEmbeddingAdapter/FakePhysicalModelAdapter; test_baseline_comparison_physical.py FakePhysicalEmbeddingAdapter. Define local helpers in new conftest, not production imports of test modules. Fake evidence is never fresh physical hardware evidence.

- [ ] **Step 1 — Process RED.** `test_subprocess_uses_argument_array_same_cwd_and_no_shell` spies on subprocess.run, asserts shell=False/cwd/byte capture/one call. `test_nonzero_and_launch_error_preserve_diagnostics` never fabricates exit0. `test_physical_process_has_no_new_deadline` asserts timeout None. No real nested pytest.
- [ ] **Step 2 — Adapter RED.**
  - `test_real_portable_payloads_retain_frozen_outcomes`: A008/A009 PASS/SUPPORTED, A010 PASS/NOT_SUPPORTED; actual aggregate_metrics preserved.
  - `test_zero_exit_truncated_duplicate_key_or_missing_output_fails`: EVIDENCE_INVALID/FAIL.
  - `test_exit_success_flag_and_validator_must_all_agree`: nonzero/false/errors/validator error FAIL.
  - `test_stdout_and_json_artifact_must_agree`: canonical conflict FAIL.
  - `test_a003_uses_json_exit_contract_without_invented_marker`: valid stdout object accepted only at exit0; malformed root/junk rejected.
  - `test_a005_checks_observed_vector_health_dimension`: descriptor1024 + actual health768 => IDENTITY_DRIFT.
  - `test_a009_a010_require_both_physical_validity_flags`: missing/false either flag FAIL.
  - `test_qualification_package_does_not_load_scripts_or_cognitive_modules`: AST/import trap preserves dependency boundary.

Assertions: process spy `assert kwargs["shell"] is False`, `assert kwargs["cwd"] == repo_root`, `assert physical_command.timeout_seconds is None`; invalid evidence `assert result.status is GateStatus.FAIL`; A008/A009/A010 valid `assert result.status is GateStatus.PASS`; frozen drift `assert any(e.code == "IDENTITY_DRIFT" for e in result.errors)`. A003 has `assert "--qualify" in evidence.command.argv` and `assert "--output" not in evidence.command.argv`.

Run `python -m pytest tests/qualification/test_process.py tests/qualification/test_evidence.py -q`; missing API/acceptance RED.

- [ ] **Step 3 — Implement processes.** One call/command, no shell/retry. Preserve stdout/stderr/output bytes; strict UTF-8 JSON. Explicit interpreter/path args handle Windows spaces. Unknown launch/timeout/nonzero is hard failure pending separately verified external absence.
- [ ] **Step 4 — Implement adapters/bridge.** Honor child table. A004/A005 CLI already invokes typed descriptor/report validators: do not recreate cognition. Add schema/identity/success consistency. Inject A006/A007 pure experiment validators. Physical exception payloads are diagnostic variants and never PASS. Blocker classification never guesses message keywords.
- [ ] **Step 5 — GREEN/commit.** Focused tests and existing CLI test command below PASS without source edits:

``
python -m pytest tests/test_qwen_qualification_cli.py tests/test_vector_memory_qualification_cli.py tests/test_selective_activation_qualification_cli.py tests/test_uncertainty_expansion_qualification_cli.py tests/test_procedural_memory_qualification_cli.py tests/test_integrated_loop_qualification_cli.py tests/test_integrated_loop_physical_cli.py tests/test_baseline_comparison_qualification_cli.py tests/test_baseline_comparison_physical.py -q
``
Stage exact Task4 files, cached whitespace PASS; commit `feat(a011): normalize existing qualifier evidence`.

### Task 5: Artifact integrity and atomic publication

**Files:** Create package artifacts.py/tests/qualification/test_artifacts.py; extend manifest.py with artifact-aware checks.

**Interfaces — consumes:** Task2 records/codec/manifest_issues, Task3 profile.
**Produces:**
- `ArtifactStore.create(repo_root: Path, output_dir: Path | None) -> ArtifactStore`: exclusive new root; default system-temp/flywire-asca-a011/UUID; reject inside checkout.
- `ArtifactStore.root: Path`; `write_raw(relative_path: str, data: bytes, kind: str) -> ArtifactRecord`; `index() -> tuple[ArtifactRecord,...]`.
- `artifact_issues(pack: QualificationPack, root: Path) -> tuple[Reason,...]`: relative refs, regular nonlinked files, bytes/hash/index consistency.
- `render_pack_markdown(pack: QualificationPack) -> str`: from validated pack only.
- `publish_pack(store: ArtifactStore, pack: QualificationPack) -> tuple[Path,Path]`: validated atomic qualification.json/qualification.md/artifact-index.json, raises QualificationError.

- [ ] **Step 1 — Integrity RED.** `test_missing_raw_file_or_hash_length_mismatch_fails`, `test_manifest_refs_resolve_to_indexed_relative_files`, `test_index_never_hashes_itself_manifest_or_report`, `test_source_profile_or_candidate_mix_fails`: EVIDENCE_INVALID/SOURCE_MISMATCH, publication refused.
- [ ] **Step 2 — Publication RED.** `test_existing_directory_or_inside_checkout_is_refused`: bytes untouched. `test_link_and_parent_path_escape_is_rejected`: ../, absolute, symlink/junction where supported, hardlink (link count>1). `test_write_failure_never_returns_passing_publication`: injected os.replace failure => ARTIFACT_WRITE_FAILED, no success. `test_report_is_derived_from_validated_manifest`: nonfinal portable wording, five research rows, no score.

Assertions: `assert artifact_issues(pack, store.root)` for missing/hash/path inputs; `with pytest.raises(QualificationError)` for publication refusal; `assert original_path.read_bytes() == original_bytes`; injected write failure `assert exc.value.code == "ARTIFACT_WRITE_FAILED"`; `assert all(a.path not in {"qualification.json", "qualification.md", "artifact-index.json"} for a in store.index())`.

Run `python -m pytest tests/qualification/test_artifacts.py -q`; missing API/safety RED.

- [ ] **Step 3 — Implement store/index.** Exclusive root and raw file creation; refuse links/linked ancestors/path escape and prior-file overwrite. Index profile copy, raw logs/JSON/internal audit/probe outputs by bytes SHA256. Manifest/report/index do not index themselves. Retain obtainable diagnostics after failure.
- [ ] **Step 4 — Implement publication.** Same-directory temporary files/atomic replace; one immutable validated pack feeds JSON/Markdown. Missing/write-failed artifacts => caller exit1 with tagged diagnostic even if manifest cannot be written. Do not report passing publication before all files finish.
- [ ] **Step 5 — GREEN/commit.** Same focused command and record/manifest tests PASS; exact Task5 files/cached whitespace; commit `feat(a011): publish validated qualification artifacts`.

### Task 6: Portable pack and frozen repeat audit

**Files:** Create package portable.py, `scripts/qualify_asca_v0x_a011.py`, tests/qualification/test_portable.py; extend conftest/evidence.py/manifest.py only as interfaces require.

**Interfaces — consumes:** Task2-5 APIs.
**Produces:**
- `RunContext(repo_root: Path, expected_commit: str, profile_path: Path, store: ArtifactStore, runner: ProcessRunner, validators: Mapping[str,LegacyValidator])` in portable.py.
- `run_portable(context: RunContext) -> QualificationPack`: writes raw evidence, returns validated nonfinal pack; CLI publishes.
- CLI `main(argv: Sequence[str] | None = None) -> int`: optional --repo-root, required --expected-source-sha (40hex), optional --profile (reviewed default), optional --output-dir; no identity/threshold/fixture override.
- Manifest `validate_completed_evidence(pack: QualificationPack, final_gate_id: str, artifact_root: Path) -> tuple[Reason,...]`: P09 validates completed P00-P08; H07 validates P00-P09/H00-H06. Only these two fixed phases allowed, then final manifest validation requires validator gate once.

- [ ] **Step 1 — Happy-path RED.** `test_portable_runs_all_ten_gates_without_ollama`: FakeRunner/real deterministic payloads, ordered P00-P09, exact candidate/profile, PORTABLE_ONLY/is_final false/verdict None/PASS/exit0, no fresh A006/A007. Calls include full pytest once, A008/A009/A010 twice; A003 --qualify/no --output.
- [ ] **Step 2 — Replay RED.** `test_repeat_changes_execution_id_case_order_sentinel_or_unknown_field_fail`: independent second-copy mutations => P08 FAIL/REPLAY_DRIFT or EVIDENCE_INVALID. `test_only_optional_top_level_note_is_ignored`: changed note same digest, any other new key rejected. `test_a010_primary_nine_is_distinct_from_total_twelve`: aggregate_metrics.case_count12, primary_case_count9, all exact counts and dense-only sentinel preserved.
- [ ] **Step 3 — Flow RED.** `test_p00_rejects_dirty_wrong_source_or_profile_before_child_calls`: no child calls, caused NOT_RUN. `test_mid_run_source_drift_cannot_publish_pass`; `test_missing_raw_or_bad_gate_coverage_fails_p09`; `test_pytest_tests_never_spawn_real_nested_pytest`: fake runner completes, actual subprocess trap never fires.

Assertions: `assert tuple(g.gate_id for g in pack.gates) == PORTABLE_GATE_IDS`; `assert pack.engineering_verdict is None`; `assert pack.portable_status is GateStatus.PASS`; second-payload drift `assert pack.portable_status is GateStatus.FAIL`; `assert semantic_payload_sha256(first, milestone, profile) == semantic_payload_sha256(note_changed, milestone, profile)`; `assert payload["aggregate_metrics"]["case_count"] == 12`; `assert payload["aggregate_metrics"]["primary_case_count"] == 9`; precheck failure `assert runner.commands == []`.

Run `python -m pytest tests/qualification/test_portable.py -q`; missing API/contract RED.

- [ ] **Step 4 — Implement P00-P08.** Check profile/source before children. On verified fail/blocker stop later execution with cause-linked NOT_RUN. Capture unique per-gate logs/JSON. P08 repeats only frozen workloads; first/repeat digest must both match Appendix A. Record ReplayObservation with qualifier Git blob/candidate/profile. Five research expectations/historical refs always exist; add only actually executed fresh observations.
- [ ] **Step 5 — Implement P09/CLI.** Validate completed evidence, create indexed internal-audit JSON and P09 PASS/FAIL, classify portable, validate full manifest/artifacts. Before/after source surrounds all execution. A profile failure uses independently fixed gate/outcome vocabulary and expected hash plus observed file hash/raw diagnostics; it never reads expectations from contaminated profile. Absent source measurements remain explicit null with cause. Publication error exit1; verified external blocker exit2; unexplained absence exit1.
- [ ] **Step 6 — GREEN/commit/real replay.** Focused tests/full pytest/audits PASS; exact Task6 files/cached whitespace; commit `feat(a011): replay portable system qualification`. From clean **committed** checkout, run portable CLI outside pytest using actual SHA/new outside output dir; exit0 and validated nonfinal pack. Record pack path/hash/behavior SHA.

### Task 7: Physical prerequisites and full-system replay

**Files:** Create package physical.py, `scripts/qualify_asca_v0x_a011_physical.py`, tests/qualification/test_physical.py.

**Interfaces — consumes:** RunContext/run_portable, runner/adapters/store/profile/manifest/classifier.
**Produces:**
- `RuntimeSnapshot(available: bool, hostname: str, platform: str, python_version: str, endpoint: str, ollama_version: str | None, terminal: JsonObject | None, embedding: JsonObject | None, reasons: tuple[Reason,...], raw: JsonObject)`.
- `RuntimeProbe` protocol `inspect() -> RuntimeSnapshot`; `OllamaRuntimeProbe(endpoint: str = "http://127.0.0.1:11434")`.
- `runtime_issues(snapshot: RuntimeSnapshot, profile: FrozenProfile) -> tuple[Reason,...]`.
- `run_full(context: RunContext, probe: RuntimeProbe) -> QualificationPack`.
- Physical CLI `main(argv: Sequence[str] | None = None) -> int`: same four options as portable; fixed endpoint, no identity/timeout/calibrate/retry override.

Probe uses bounded read-only GET /api/version, GET /api/tags, POST /api/show(model name), five-second request inspection limits; no generation/embedding/pull/restart. Confirmed refusal/unreachability => PREREQUISITE_UNAVAILABLE; missing required tag => MODEL_MISSING; malformed reachable response => EVIDENCE_INVALID; present wrong digest/dimension => IDENTITY_DRIFT. Inspect/preserve all models even if one missing.

- [ ] **Step 1 — Preflight RED.** `test_runtime_missing_or_model_absent_is_confirmed_blocker`: H00 BLOCKED, no physical calls, caused H01-H06 NOT_RUN, full BLOCKED/exit2. `test_installed_wrong_digest_dimension_is_failure`: FAIL/exit1. `test_missing_terminal_and_wrong_embedding_digest_is_failure`: both findings preserved, NOT_QUALIFIED.
- [ ] **Step 2 — Full RED.** `test_full_runs_fresh_local_portable_then_six_physical_qualifiers`: same SHA/profile, sequential H01-H06, A005 --threshold 0.5037018224299838/no --calibrate, A009 SUPPORTED/A010 NOT_SUPPORTED arguments, qualified/exit0. `test_physical_secondary_never_overwrites_portable_primary`: separate A009/A010 portable-primary/physical-secondary roles.
- [ ] **Step 3 — Mid-run RED.** `test_confirmed_runtime_disappearance_after_h00_is_blocked`: after-failure probe indexed. `test_unknown_timeout_or_nonzero_is_failure_not_keyword_blocker`: connection/model words but healthy probe =>FAIL. `test_verified_child_identity_drift_dominates_later_runtime_loss`: NOT_QUALIFIED. `test_completion_probe_detects_mid_run_identity_drift`: H07 FAIL. `test_no_auto_retry_pull_calibration_restart_or_new_deadline`: one child each, allowed metadata endpoints only.

Assertions: complete `assert pack.engineering_verdict is EngineeringVerdict.ENGINEERING_QUALIFIED`; absence-only `assert pack.engineering_verdict is EngineeringVerdict.QUALIFICATION_BLOCKED`; any observed hard failure `assert pack.engineering_verdict is EngineeringVerdict.ENGINEERING_NOT_QUALIFIED`; `assert tuple(g.gate_id for g in pack.gates) == PORTABLE_GATE_IDS + PHYSICAL_GATE_IDS`; `assert "--calibrate" not in a005_command.argv`; `assert a005_command.timeout_seconds is None`.

Run `python -m pytest tests/qualification/test_physical.py -q`; missing API/classification RED.

- [ ] **Step 4 — Implement full flow.** Build one full pack/store from fresh run_portable; never import a prior pack as fresh. Portable failure prevents physical execution with causal NOT_RUN; H07 still classifies. H00 inspects all identities. For nonzero child, verify structured evidence first: actual identity/acceptance contradictions remain FAIL. Transport-only incomplete evidence can BLOCK only with independent contemporaneous absence proof; otherwise FAIL. No message-keyword inference.
- [ ] **Step 5 — Implement H07/publication.** Completion probe/source snapshot detect drift. Validate 18 mandatory gates, raw refs/observations, A005 actual vector dimension, all identities/outcomes/roles. Internal audit then final gate/classifier. All PASS =>QUALIFIED; hard fail=>NOT_QUALIFIED; confirmed blocker only=>BLOCKED. Physical bytes/timing need not be identical.
- [ ] **Step 6 — GREEN/commit.** Focused tests/full pytest/audits PASS with no live model calls from tests. Exact Task7 files/cached whitespace; commit `feat(a011): qualify pinned local physical system`.

### Task 8: Portable CI integration

**Files:** Modify `.github/workflows/ci.yml`, `docs/development/QUALIFICATION-MATRIX.md`; create tests/qualification/test_ci_contract.py.

**Interfaces:** Consumes clean-source portable CLI; produces exact branch CI plus pack retention, no physical/model call.

- [ ] **Step 1 — RED topology.** `test_ci_retains_every_existing_standalone_gate` checks pytest/audit/repository/A003/A008/A009/A010/whitespace; `test_ci_adds_nonfinal_a011_and_uploads_even_on_failure` requires portable step/upload-artifact@v4/if:always(); `test_ci_has_no_physical_model_or_calibration_command` rejects physical/pull/calibrate. Stdlib inspection, no YAML runtime dependency.
- [ ] **Step 2 — Confirm RED.** `python -m pytest tests/qualification/test_ci_contract.py -q`; absent A011 step/upload fails.
- [ ] **Step 3 — Add gate after old qualifiers, before whitespace.**

```yaml
- name: Qualify A011 portable system
  run: python scripts/qualify_asca_v0x_a011.py --expected-source-sha "$(git rev-parse HEAD)" --output-dir "$RUNNER_TEMP/a011-portable-${{ github.run_id }}-${{ github.run_attempt }}"
- name: Upload A011 portable qualification pack
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: a011-portable-${{ github.run_id }}-${{ github.run_attempt }}
    path: ${{ runner.temp }}/a011-portable-${{ github.run_id }}-${{ github.run_attempt }}/
    if-no-files-found: error
```

Use Git HEAD for PR merge-checkout identity, not an assumed feature head; retain fetch-depth2. Old history is unnecessary. Missing pack/upload failure cannot be qualification success.

- [ ] **Step 4 — GREEN/exact CI.** Focused tests/full suite/audits PASS; commit `ci(a011): retain portable system qualification evidence`; push feature non-force/tags=false. Require latest exact run for that 40hex commit; inspect A011/upload and pack source/finality/hash. Unrelated green CI is insufficient.

### Task 9: Fresh candidate qualification and frozen-evidence audit

**Files:** A011 evidence ledger after recording behavior SHA; actual raw evidence outside checkout. No new research workload.

**Interfaces:** Consumes clean committed feature/exact CI; produces qualified behavior SHA, pack root/hashes, gate/identity audit, physical environment.

- [ ] **Step 1 — Freeze actual candidate.** Require clean worktree and exact successful branch CI for live SHA. Read profile/protected hashes and live runtime. New output directory example `T:\Space\Projects\ProjectsAI\FlyWireASCA-qualification-evidence\a011-<actual-candidate-sha>-<new-run-id>`; substitute observed SHA/new UUID.
- [ ] **Step 2 — Full replay outside pytest.** Run physical CLI --expected-source-sha actual candidate --output-dir new root. Use LConnect background-process APIs for long work, retain raw files and communicate progress. Fresh local portable then physical sequentially; no automatic retry/new deadline.
- [ ] **Step 3 — Audit exact evidence.** Exit0/schema1/FULL_SYSTEM/is_final true/ENGINEERING_QUALIFIED; all18 gates once/PASS; same clean source before/after; profile add06.../protected8df...; intact raw hashes/refs; exact model digests/dimension/threshold; five frozen outcomes; portable fingerprints/digests; A010 nine primary/twelve total/all counts/dense-only sentinel.
- [ ] **Step 4 — Retain failure honestly.** Exit1/2 stops successful closure. Confirmed prerequisite blocker records cause/resume. Cognitive defect requires separate explicit repair task. Infrastructure repair returns to owning TDD task and new candidate/pack, never alters frozen anchor to force GREEN.
- [ ] **Step 5 — Publish evidence ledger.** Record qualified behavior SHA, exact branch CI URL/ID, pack root/manifest/report/index hashes, physical host/runtime, gate table/outcomes. Documentation-only commit stays distinct from qualified behavior.

### Task 10: Whole-change review and reviewed integration

**Files:** Infrastructure findings in owning task; review/evidence ledger in A011 task/report draft. Preserve full history.

**Interfaces:** Consumes fresh qualification; produces reviewed behavior SHA/findings/method, exact reviewed branch CI, integration SHA/exact main CI.

- [ ] **Step 1 — Whole-change review.** Invoke requesting-code-review. Follow G05 method: Subagent-driven task reviews plus final whole-branch review, or Native implementation plus one fresh whole-branch reviewer. Review actual activation base..candidate against spec/plan. Record reviewer/method/exactSHA/severity/physical applicability. Self-review is never independent review.
- [ ] **Step 2 — Resolve Critical/Important.** Reproducer RED, minimal infrastructure repair, GREEN. Behavior/profile/qualifier changes require affected fresh portable/physical evidence/new qualified candidate. Cognitive defect stays outside A011. Preserve old packs/reviews.
- [ ] **Step 3 — Exact reviewed branch.** Non-force push/tags=false, latest exact CI for final reviewed branch SHA. Later docs commits record reviewed/qualified behavior separately.
- [ ] **Step 4 — Integrate.** Invoke finishing-a-development-branch; normal PR merge preserving feature commits. Reviewed-plan execution authorizes evidence-driven integration after gates; respect a later explicit user integration instruction. No reset/rebase/squash/force/WIP destruction; preserve branch/worktree through final verification.
- [ ] **Step 5 — Exact integration/main.** Read merge SHA live, sync main non-destructively, require exact push/main CI and clean/sync0/0. Run fresh full-system pack on clean integration/main before saying that exact integration SHA qualified. Failure/blocker stops closure. Record feature qualified/reviewed, integration qualified and metadata SHAs separately.

### Task 11: Evidence closure and full-session handoff

**Files:** Create `docs/development/reports/ASCA-20261010-A011-v0x-qualification.md`; update A011 task/CURRENT/ROADMAP/matrix and mutable tests/test_task_ledger.py. Create full session handoff named for actual closure date.

**Interfaces:** Consumes reviewed integration/main full pack; produces coherent DONE/closed-completed/exact final main CI/clean sync, no release.

- [ ] **Step 1 — Final report.** From validated pack, state qualified/scope/profile,18-gate table,frozen audits,five research rows/separate provenance roles,exactSHA/CI,actual physical environment/raw locations/hashes,review/repairs,claims boundaries. CI metadata never replaces physical evidence; no intelligence/FLOPs/energy/general speed claim.
- [ ] **Step 2 — RED closure lifecycle.** Only mutable ledger assertions expect A011 DONE, actual issue, PRE-A011 DONE/#11 completed, A001-A010 DONE, roadmap once. `python -m pytest tests/test_task_ledger.py -q` RED against ACTIVE docs.
- [ ] **Step 3 — GREEN docs.** Coherent A011/CURRENT/ROADMAP; terminal CURRENT points to completed A011, no invented A012. Preserve behavior/review/integration identities. Ledger/full pytest/audits/cached whitespace PASS; exact docs/tests commit/push and exact main CI.
- [ ] **Step 4 — Close actual issue completed.** After evidence/exact-main gates, GitHub state=closed/state_reason=completed. Verify live response/state; reconcile if closure fails, never assert CLOSED merely from requested operation.
- [ ] **Step 5 — Final handoff/repository.** Include approvals/method/allSHAs/exactruns/physical locations+hashes/review/Issue/runtime/frozen values/limitations/next authorized gate. Metadata-only handoff commit gets exact CI; containing SHA discovered from Git, no self-SHA loop. Main clean/exact origin sync0/0, no version/tag/release/FlyWireLLM change.

## Execution method and cost boundary

No method was supplied with written-spec approval. Stop after publishing this plan for user review and choice:

- **Native:** this agent implements all tasks with executing-plans; one fresh whole-change reviewer after fresh qualification. Recommended because records/adapters/artifacts/runners share tight interfaces and one author can keep causal/source identity consistent.
- **Subagent-driven:** subagent-driven-development, fresh implementer/reviewer for each Task2-8 plus final whole-change review. More independent checkpoints/context cost. Operational/physical/integration gates remain sequential.

Generic header recommendation does not override user choice. Do not spawn workers/create issue/worktree/activate/start TDD before plan approval and method selection.

## Plan self-review

| Check | Result |
| --- | --- |
| Spec coverage | PASS — Sections1-3 Tasks1-2;4 Tasks2/4;5/7 Task3;6 Tasks2/5;8 Tasks6/8;9-10 Task7;11 Tasks2-8;12-15 Tasks1/9-11 |
| Step completeness | PASS — paths/APIs/named assertions/RED-GREEN/commits/operational evidence |
| Type/interface consistency | PASS — shared records, earlier outputs consumed later; legacy loading script-only |
| Review Focus | PASS — five conditions tested by Tasks3/4/6/7/5 |
| Scope/proportion | PASS — no implementation bodies; reviewed data appendix; no cognitive/benchmark expansion |
| Unresolved Critical/Important | 0 |

Author self-review, not independent implementation review. Writing this plan creates no production code/profile/tests/workflow.

## Appendix A: Reviewed future profile and anchors

JSON below combines spec values with read-only planning identity refinements; it is **not** a production profile file yet. Task3 serialization:

```python
json.dumps(values, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
```

No newline/BOM. Exact bytes **7481**, SHA256 **add06f285bf6decc7d492b987d3769dc64db4cb3d0177c8c6586d50ee5f6d46d**.

Protected-tree algorithm: HEAD records for67 paths, each exactly `{"path":path,"mode":mode,"blob":blob_sha}`; sorted by path, same sorted compact UTF-8 JSON array serialization. Expected SHA256 **8df49f05fe54de43667ab2f8ef5de2caae9376ffedf2cb8f8d26f0e4abcca6b6**. Observed from unchanged baseline c149...; still identical at planning HEAD. No historical baseline object is needed during qualification.

Semantic hashes were observed by running unchanged A008/A009/A010 CLIs twice and canonicalizing payloads with only optional top-level note omitted. They are qualification identities, not a new experiment.

```json
{
  "schema_version": 1,
  "profile_id": "asca-v0x-a011-v1",
  "package_version": "0.1.0.dev0",
  "source_baseline": "c1498e8e30a23fb67965239d13f0531d5326079e",
  "terminal": {
    "model": "qwen3.5:4b",
    "digest": "2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd"
  },
  "embedding": {
    "model": "qwen3-embedding:0.6b",
    "digest": "ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d",
    "dimension": 1024
  },
  "a005_threshold": 0.5037018224299838,
  "policies": {
    "familiarity": "EVIDENCE_ONLY",
    "selector": "SINGLE_BEST",
    "expansion": "SIGNAL_DRIVEN",
    "procedure": "CHUNKED",
    "recovery": "MISMATCH_DRIVEN_RECOVERY",
    "max_procedure_attempts": 3,
    "hidden_automatic_retry": 0
  },
  "research_outcomes": {
    "A006": "NOT_SUPPORTED",
    "A007": "SUPPORTED",
    "A008": "SUPPORTED",
    "A009": "SUPPORTED",
    "A010": "NOT_SUPPORTED"
  },
  "evidence_roles": {
    "A006": "PHYSICAL_PRIMARY",
    "A007": "PHYSICAL_PRIMARY",
    "A008": "PORTABLE_PRIMARY",
    "A009": "PORTABLE_PRIMARY_PHYSICAL_SECONDARY",
    "A010": "PORTABLE_PRIMARY_PHYSICAL_SECONDARY"
  },
  "fixture_fingerprints": {
    "A006": "e51fea2e58186e94d7affc964509e96d96fc656759677d7dcc073e5b36b91035",
    "A007": "59f95ef115534fe24e59570cb281c0564ab75aadf364f4c26feba0d4078213c9",
    "A008": "f52fbd4ab018386ff3cbfb62a68cc44a4b40e54ec4fd9a3b2e885dd2c5663fc6",
    "A009": "2f92b5092de346f62879ac2cbb9f96d6de5d6f919e12d0693345c8228b01ab2a",
    "A010": "69d20542cd1e7e5c25a0fb61b9060f622379206b519da3cec7624e00bb6e5d4c"
  },
  "a010_primary_counts": {
    "primary_case_count": 9,
    "asca_success_count": 7,
    "dense_success_count": 8,
    "shared_success_count": 7,
    "dense_only_success_count": 1,
    "asca_only_success_count": 0,
    "asca_query_count": 28,
    "dense_query_count": 27,
    "asca_scored_vector_count": 1984,
    "dense_scored_vector_count": 1440,
    "asca_cumulative_selected_count": 66,
    "dense_cumulative_selected_count": 480,
    "asca_peak_selected_count": 12,
    "dense_peak_selected_count": 256,
    "asca_procedure_attempt_count": 14,
    "dense_procedure_attempt_count": 9
  },
  "a010_dense_only_sentinel": "selective-routing-miss-sentinel",
  "portable_gate_ids": [
    "P00_PROFILE_SOURCE",
    "P01_TESTS",
    "P02_ARCHITECTURE",
    "P03_REPOSITORY",
    "P04_A003",
    "P05_A008",
    "P06_A009",
    "P07_A010",
    "P08_FROZEN_AUDIT",
    "P09_PACK_VALIDATION"
  ],
  "physical_gate_ids": [
    "H00_PREREQUISITES",
    "H01_A004",
    "H02_A005",
    "H03_A006",
    "H04_A007",
    "H05_A009",
    "H06_A010",
    "H07_FULL_VALIDATION"
  ],
  "protected_source": {
    "algorithm": "sorted-git-mode-path-blob-json-sha256-v1",
    "sha256": "8df49f05fe54de43667ab2f8ef5de2caae9376ffedf2cb8f8d26f0e4abcca6b6",
    "paths": [
      "scripts/qualify_baseline_comparison_a010.py",
      "scripts/qualify_baseline_comparison_a010_physical.py",
      "scripts/qualify_integrated_loop_a009.py",
      "scripts/qualify_integrated_loop_a009_physical.py",
      "scripts/qualify_procedural_memory_a008.py",
      "scripts/qualify_qwen_a004.py",
      "scripts/qualify_selective_activation_a006.py",
      "scripts/qualify_uncertainty_expansion_a007.py",
      "scripts/qualify_vector_memory_a005.py",
      "scripts/run_familiarity_benchmark_a003.py",
      "src/flywire_asca/__init__.py",
      "src/flywire_asca/baseline_comparison/__init__.py",
      "src/flywire_asca/baseline_comparison/ablations.py",
      "src/flywire_asca/baseline_comparison/benchmark.py",
      "src/flywire_asca/baseline_comparison/dense.py",
      "src/flywire_asca/baseline_comparison/models.py",
      "src/flywire_asca/contracts/__init__.py",
      "src/flywire_asca/contracts/benchmark.py",
      "src/flywire_asca/contracts/codec.py",
      "src/flywire_asca/contracts/control.py",
      "src/flywire_asca/contracts/enums.py",
      "src/flywire_asca/contracts/memory.py",
      "src/flywire_asca/contracts/procedure.py",
      "src/flywire_asca/contracts/validation.py",
      "src/flywire_asca/embedding/__init__.py",
      "src/flywire_asca/embedding/adapter.py",
      "src/flywire_asca/embedding/contracts.py",
      "src/flywire_asca/embedding/errors.py",
      "src/flywire_asca/embedding/ollama.py",
      "src/flywire_asca/familiarity/__init__.py",
      "src/flywire_asca/familiarity/benchmark.py",
      "src/flywire_asca/familiarity/exact.py",
      "src/flywire_asca/familiarity/models.py",
      "src/flywire_asca/familiarity/normalization.py",
      "src/flywire_asca/integrated_loop/__init__.py",
      "src/flywire_asca/integrated_loop/benchmark.py",
      "src/flywire_asca/integrated_loop/controller.py",
      "src/flywire_asca/integrated_loop/models.py",
      "src/flywire_asca/integrated_loop/procedure.py",
      "src/flywire_asca/integrated_loop/retrieval.py",
      "src/flywire_asca/model/__init__.py",
      "src/flywire_asca/model/adapter.py",
      "src/flywire_asca/model/baseline.py",
      "src/flywire_asca/model/contracts.py",
      "src/flywire_asca/model/errors.py",
      "src/flywire_asca/model/ollama.py",
      "src/flywire_asca/procedural_memory/__init__.py",
      "src/flywire_asca/procedural_memory/benchmark.py",
      "src/flywire_asca/procedural_memory/library.py",
      "src/flywire_asca/procedural_memory/models.py",
      "src/flywire_asca/procedural_memory/runner.py",
      "src/flywire_asca/procedural_memory/simulator.py",
      "src/flywire_asca/procedural_memory/verifier.py",
      "src/flywire_asca/selective_activation/__init__.py",
      "src/flywire_asca/selective_activation/baselines.py",
      "src/flywire_asca/selective_activation/benchmark.py",
      "src/flywire_asca/selective_activation/models.py",
      "src/flywire_asca/selective_activation/selector.py",
      "src/flywire_asca/uncertainty_expansion/__init__.py",
      "src/flywire_asca/uncertainty_expansion/benchmark.py",
      "src/flywire_asca/uncertainty_expansion/controller.py",
      "src/flywire_asca/uncertainty_expansion/models.py",
      "src/flywire_asca/uncertainty_expansion/runner.py",
      "src/flywire_asca/vector_memory/__init__.py",
      "src/flywire_asca/vector_memory/benchmark.py",
      "src/flywire_asca/vector_memory/index.py",
      "src/flywire_asca/vector_memory/models.py"
    ]
  },
  "portable_payloads": {
    "A008": {
      "fixture_version": "a008-deterministic-v1",
      "qualification_scope": "deterministic_procedural_memory_a008",
      "required_top_level_keys": [
        "aggregate_metrics",
        "case_ids",
        "cases",
        "chunk_reuse_counts",
        "claims_boundary",
        "controls",
        "errors",
        "experiment_valid",
        "fixture_fingerprint",
        "fixture_version",
        "max_call_depth",
        "modes",
        "primary_architecture",
        "primary_hypothesis_outcome",
        "qualification_scope",
        "reused_procedure_ids"
      ],
      "allowed_optional_keys": [
        "note"
      ],
      "excluded_semantic_keys": [
        "note"
      ],
      "semantic_sha256": "4883b4eba174a2edc8c753297e02903c940f0b0fc38a71f80d5b76541b49e7c3"
    },
    "A009": {
      "fixture_version": "a009-deterministic-v1",
      "qualification_scope": "deterministic_integrated_cognitive_loop_a009",
      "required_top_level_keys": [
        "aggregate_metrics",
        "case_ids",
        "cases",
        "claims_boundary",
        "errors",
        "experiment_valid",
        "fixture_fingerprint",
        "fixture_version",
        "max_procedure_attempts",
        "max_scope_count",
        "policies",
        "primary_hypothesis_outcome",
        "primary_procedure_mode",
        "primary_selector",
        "qualification_scope"
      ],
      "allowed_optional_keys": [
        "note"
      ],
      "excluded_semantic_keys": [
        "note"
      ],
      "semantic_sha256": "5fb0c8b803b0c15888907ca388aa8f705d904351a9f23da43cdf7a285c9052b7"
    },
    "A010": {
      "fixture_version": "a010-deterministic-v1",
      "qualification_scope": "deterministic_dense_nonselective_baseline_a010",
      "required_top_level_keys": [
        "aggregate_metrics",
        "case_ids",
        "cases",
        "claims_boundary",
        "dense_top_k_policy",
        "errors",
        "experiment_valid",
        "fixture_fingerprint",
        "fixture_version",
        "primary_asca_policy",
        "primary_hypothesis_outcome",
        "primary_procedure_mode",
        "qualification_scope",
        "variants"
      ],
      "allowed_optional_keys": [
        "note"
      ],
      "excluded_semantic_keys": [
        "note"
      ],
      "semantic_sha256": "8e57b744e96294565551061728ff90b4ddba43b66051237124378f981db185d5"
    }
  },
  "historical_refs": [
    "docs/development/reports/ASCA-20261009-A006-working-set-selective-activation.md",
    "docs/development/reports/ASCA-20261009-A007-surprise-uncertainty-expansion.md",
    "docs/development/tasks/A008-procedural-memory-skill-chunking.md",
    "docs/development/tasks/A009-integrated-cognitive-loop.md",
    "docs/development/tasks/A010-dense-nonselective-baseline-comparison.md"
  ]
}
```
