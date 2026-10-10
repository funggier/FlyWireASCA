# A011 — ASCA v0.x System Qualification Design

Date: 2026-10-10
Repository: `funggier/FlyWireASCA`
Document state: WRITTEN SPEC / AWAITING USER REVIEW
Milestone state: PLANNED
GitHub Issue: not created
Package version: `0.1.0.dev0`

## 1. Intent, authority, and approval boundary

A011 answers whether the implemented ASCA v0.x architecture is coherent,
reproducible, identity-stable, and supported by traceable portable and local
physical evidence. It is a system qualification/certification layer over
A003-A010. It does not introduce a research hypothesis or optimize cognition.

เอกสารนี้ออกแบบการรับรองระบบที่มีอยู่ โดยแยกความถูกต้องทางวิศวกรรมออกจาก
ผลการทดลองเดิม ผลวิจัยที่ไม่สนับสนุนสมมติฐานยังคงเป็นหลักฐานที่ถูกต้องได้
การผ่าน portable อย่างเดียวไม่ถือว่ารับรองระบบครบ และการรับรองไม่ใช่การออก release

The conversational design uses the four sections in the
[previous full handoff](../../development/reports/ASCA-20261010-full-session-handoff-post-pre-a011-a011-design-gate.md).
The user subsequently said: “อนุมัติให้ทำไปเลยครับ”. This authorizes writing this
spec and the requested advance task/handoff documentation. It does not approve
this previously nonexistent written spec or a future implementation plan.

Live source baseline used to write the spec:

- main/local/origin exact SHA: `c1498e8e30a23fb67965239d13f0531d5326079e`;
- exact CI: [38038307095](https://github.com/funggier/FlyWireASCA/actions/runs/38038307095),
  completed/success, push/main, exact baseline SHA;
- main clean; exact ahead/behind 0/0;
- PRE-A011 Issue #11: CLOSED / COMPLETED;
- A011: PLANNED, no issue; all 11 existing issues enumerated with pagination;
- local Ollama: `0.32.15`; pinned model tags/digests and embedding metadata
  dimension verified on the user's machine.

Git/GitHub/runtime are authoritative over stale narrative. The PRE-A011 report
starts with its historical ACTIVE/pre-review state; its later closure sections,
Issue #11, and live CURRENT/ROADMAP establish completion. Do not resume PRE-A011.

The selected approach is **Qualification Pack + Fresh System Replay + Frozen
Evidence Audit**. Report-only aggregation lacks fresh replay; a new benchmark
would mix qualification with new research. Neither alternative is A011's scope.

## 2. Four-part design

1. **Result semantics:** engineering verdict and research evidence are separate.
2. **Qualification pack:** repository/architecture integrity, frozen identities,
   fresh portable replay, fresh physical replay, and final manifest.
3. **Source boundaries:** add qualification schema/classification and orchestration;
   reuse existing qualifiers without changing cognitive semantics.
4. **Execution/failure flow:** complete both evidence paths, reject drift and
   malformed evidence, distinguish verified external blockers from failures,
   and preserve every milestone's existing claims boundary.

## 3. Engineering verdict and research outcomes

The only final engineering states are:

| State | Meaning |
| --- | --- |
| `ENGINEERING_QUALIFIED` | Every mandatory integrity, frozen-audit, portable, physical, and evidence-consistency gate passed. |
| `ENGINEERING_NOT_QUALIFIED` | At least one verified system, identity, replay, schema, or evidence failure exists. |
| `QUALIFICATION_BLOCKED` | No verified hard failure exists, but an identified external/local prerequisite prevents completion. |

Research outcomes are reported individually:

| Milestone | Frozen outcome | Evidence role |
| --- | --- | --- |
| A006 | `NOT_SUPPORTED` | Frozen physical selective-activation hypothesis |
| A007 | `SUPPORTED` | Frozen physical structural-expansion hypothesis |
| A008 | `SUPPORTED` | Frozen portable procedural-memory hypothesis |
| A009 | `SUPPORTED` | Frozen portable integrated-loop primary hypothesis; physical evidence secondary |
| A010 | `NOT_SUPPORTED` | Frozen portable comparison primary hypothesis; physical evidence secondary |

No aggregate ASCA intelligence score, weighted research score, or automatic
conversion of NOT_SUPPORTED to an engineering failure is permitted.

A changed frozen outcome is a hard failure even if the new outcome appears
more favorable. A006/A010 remaining NOT_SUPPORTED is expected evidence.

### 3.1 Gate states and incomplete packs

Internal gate states are `PASS / FAIL / BLOCKED / NOT_RUN`. These are not
additional final engineering states.

A portable-only pack has `scope=PORTABLE_ONLY`, `is_final=false`,
`engineering_verdict=null`, and an explicit portable status. It can pass CI
without Ollama. It cannot claim ENGINEERING_QUALIFIED or represent unexecuted
physical observations as fresh evidence.

A full-system pack has `scope=FULL_SYSTEM`, `is_final=true`, and exactly one
allowed final engineering verdict. Mandatory gates must appear exactly once.
A missing/duplicated/unknown gate cannot be silently treated as passed.

### 3.2 Classification precedence

Apply this order after validating evidence:

1. Any verified FAIL -> ENGINEERING_NOT_QUALIFIED.
2. Otherwise, a verified external blocker preventing required gates ->
   QUALIFICATION_BLOCKED.
3. Otherwise, all mandatory gates PASS -> ENGINEERING_QUALIFIED.
4. Unexplained missing evidence, NOT_RUN without a recorded cause, or an
   internally inconsistent pack -> ENGINEERING_NOT_QUALIFIED.

A blocker cannot mask an already observed hard failure. Downstream gates not run
because of a hard failure record the causal gate, and the final result remains
ENGINEERING_NOT_QUALIFIED. Downstream gates prevented by a verified external
blocker record that blocker.

## 4. Architecture and dependency boundary

New package:

`src/flywire_asca/qualification/`

It contains immutable qualification records, strict profile/evidence validation,
normalization rules, deterministic classification, and serialization. It may
depend on the existing contracts package and standard library. Existing cognitive
packages must never import qualification. No new reverse edge or cycle is allowed.

New entry points:

- `scripts/qualify_asca_v0x_a011.py`: portable pack orchestration.
- `scripts/qualify_asca_v0x_a011_physical.py`: fresh full-system orchestration,
  including local portable replay followed by physical replay.

Canonical frozen profile, created during approved implementation:

`docs/development/qualification/a011-v0x-profile-v1.json`

Final milestone report, created only when supported by qualification evidence:

`docs/development/reports/ASCA-20261010-A011-v0x-qualification.md`

The orchestration layer invokes existing qualifier CLIs with explicit argument
arrays and captures their output. The package does not import scripts or
reimplement retrieval, selection, expansion, procedures, model inference,
recovery, or comparison algorithms.

Existing A004-A010 qualifier CLIs already expose JSON output paths. Use their
existing validators and success meanings. A003, pytest, architecture audit, and
repository qualification use their existing command/exit/output contracts.
A small backward-compatible infrastructure exposure is allowed only if an
existing interface cannot expose required evidence. Any such change needs
characterization evidence and cannot alter defaults or qualification semantics.

The architecture audit may add the explicit qualification-to-contracts edge
and new package vocabulary. Lifecycle tests may change only during later
approved activation/closure. These are infrastructure changes, not permission
to change A003-A010 behavior.

## 5. Frozen profile and independent trust anchor

The production profile is a reviewed list of expected identities and evidence
roles. It is not generated from observed runtime values during qualification.

Its schema contains:

- schema version and profile ID;
- preserved package version and cognitive policy identities;
- mandatory portable/physical gate IDs and evidence roles;
- terminal/embedding identities, dimension, and A005 threshold;
- frozen fixture versions/fingerprints and milestone outcomes;
- A010 exact portable primary counts and sentinel identity;
- allowed deterministic-payload metadata exclusions;
- source baseline and historical evidence references.

The implementation freezes the profile bytes and an independently reviewed
expected SHA-256 anchor in qualification infrastructure. Validators verify the
profile against that anchor before using it. Runtime output cannot rewrite the
profile, the anchor, or expected outcomes. A changed profile requires an explicit
new review decision; A011 has no accept-current, recalibrate, or bless-drift mode.

The anchor protects against accidental replacement. Git provenance and review
protect changes to both the profile and anchor; it is not a cryptographic
third-party certification claim.

### 5.1 Required exact identities

| Identity | Frozen value |
| --- | --- |
| Terminal model | `qwen3.5:4b` |
| Terminal digest | `2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd` |
| Embedding model | `qwen3-embedding:0.6b` |
| Embedding digest | `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d` |
| Embedding dimension | `1024` |
| A005 threshold | `0.5037018224299838` |
| A006 physical fingerprint | `e51fea2e58186e94d7affc964509e96d96fc656759677d7dcc073e5b36b91035` |
| A007 physical fingerprint | `59f95ef115534fe24e59570cb281c0564ab75aadf364f4c26feba0d4078213c9` |
| A008 portable fingerprint | `f52fbd4ab018386ff3cbfb62a68cc44a4b40e54ec4fd9a3b2e885dd2c5663fc6` |
| A009 fixture/version | `a009-deterministic-v1` |
| A009 deterministic fingerprint | `2f92b5092de346f62879ac2cbb9f96d6de5d6f919e12d0693345c8228b01ab2a` |
| A010 fixture/version | `a010-deterministic-v1` |
| A010 deterministic fingerprint | `69d20542cd1e7e5c25a0fb61b9060f622379206b519da3cec7624e00bb6e5d4c` |

The additional A006/A008 fingerprints above were read directly from the frozen
existing qualifiers at the source baseline. They introduce no new fixture.

Model generation remains terminal/non-controlling. Existing A004 baseline
settings and acceptance rules remain frozen as implemented at the source
baseline. A005 runs qualification, never `--calibrate`. A011 passes the exact
frozen threshold and model identities; user-supplied alternatives are rejected.

### 5.2 Cognitive policies that remain unchanged

- A003 familiarity: evidence only, not truth/identity/routing authority.
- A006 primary selector: SINGLE_BEST.
- A007 primary expansion policy: SIGNAL_DRIVEN.
- A008 primary representation: CHUNKED; zero hidden automatic retry.
- A009 recovery: MISMATCH_DRIVEN_RECOVERY at the outer controller; fresh
  execution state on each attempt; at most three procedure attempts.
- A004 generation cannot control deterministic retrieval/procedure verification.
- A010 uses the existing dense exhaustive control and existing classification.

### 5.3 A010 portable primary counts

| Metric | ASCA | Dense |
| --- | ---: | ---: |
| Primary cases | 9 | 9 |
| Procedure successes | 7 | 8 |
| Query count | 28 | 27 |
| Scored-vector count | 1984 | 1440 |
| Cumulative selected count | 66 | 480 |
| Peak selected count | 12 | 256 |
| Procedure attempts | 14 | 9 |

Shared successes: 7. Dense-only successes: 1. ASCA-only successes: 0.
The `selective-routing-miss-sentinel` remains present and remains dense-only.
Fresh physical counts are secondary and are not substituted for these portable
primary counts.

## 6. Qualification pack contracts

The normalized records have these responsibilities:

| Record | Required content |
| --- | --- |
| Profile identity | Profile/schema version, profile SHA-256, expected frozen identities, source provenance. |
| Source identity | Exact Git commit, repository identity, clean-state check, protected-source fingerprint. |
| Gate evidence | Gate ID, scope, status, command/arguments, start/end UTC, exit code, raw artifact hashes, validator errors, causal blocker/failure. |
| Frozen check | Identity name, expected value, observed value or explicit absence, match status, evidence reference. |
| Research evidence | Milestone, expected outcome, observed outcome where executed, primary/secondary role, historical/fresh provenance. |
| Replay identity | Fixture identities, stable payload digest, qualifier source identity, attempt/run association. |
| Physical environment | Machine identity, Python/Ollama versions, endpoint, model descriptors/digests, observed embedding dimension. |
| Final manifest | Scope/finality, engineering verdict, mandatory gate coverage, errors/blockers, separate research summary, claims boundary. |

Validation is strict: reject unsupported schema versions, unknown control fields,
duplicate JSON keys/gate IDs/milestones, invalid enums, missing required fields,
wrong primitive types, nonfinite numbers, malformed digests, contradictory
PASS plus errors, and inconsistent scope/finality/verdict combinations.
Boolean values cannot stand in for integer counts or embedding dimensions.

The threshold is compared to the exact stored value after strict numeric parsing;
do not round it, relax it with a tolerance, or silently normalize drift.

Output artifacts:

- `qualification.json`: machine-readable normalized pack/final manifest;
- `qualification.md`: readable report derived from that same validated manifest;
- one raw output/log artifact per executed gate;
- a frozen profile copy and artifact index with SHA-256 digests.

Raw evidence and the manifest must agree; rendered prose cannot override them.
The raw-evidence index hashes the profile copy and child artifacts, not itself,
the containing manifest, or the derived report. This avoids circular hashes.
The final manifest/report hashes can be recorded by an external publication
record after writing. Paths are relative to the pack root and resolve to
existing indexed artifacts.
No absent raw artifact can be accepted merely because a summary says PASS.

A unique output directory prevents overwrite of an earlier run. Write the
manifest/report atomically after validation. Record write failures as command
failures; never report success when the required artifacts were not produced.
Output defaults outside the source checkout; an explicit output directory must
not overwrite tracked repository files.

### 6.1 Normalized schema v1

The top-level pack has exactly these keys: `schema_version` (integer 1),
`profile`, `source`, `scope`, `is_final`, `portable_status`,
`engineering_verdict`, `gates`, `frozen_checks`, `research_evidence`,
`replay_identity`, `physical_environment`, `errors`, `blockers`,
`artifact_index`, and `claims_boundary`.

- `scope` is PORTABLE_ONLY or FULL_SYSTEM; `portable_status` is PASS, FAIL,
  BLOCKED, or NOT_RUN. `physical_environment` is null in portable scope or when collection was not
  possible because a recorded prerequisite blocker or earlier hard failure
  stopped the physical path. That absence requires a causal evidence reference.
- `profile` records ID/schema/hash and the expected identity source.
  `source` records exact commit, repository, protected-content hash, and
  before/after clean-state checks.
- Every gate records `gate_id`, `scope`, `status`, `command`, `started_at`,
  `finished_at`, `exit_code`, `artifacts`, `errors`, and `cause_ids`.
  Command is an argument array or an explicit A011 internal-validator identity;
  unexecuted gates have null execution fields and a required causal reference.
- Frozen checks record `identity`, `expected`, `observed`, `status`, and
  `evidence_refs`. Observed absence is explicit and cannot count as a match.
- Research records appear once for A006-A010 and contain `milestone`,
  `expected_outcome`, `observations`, and `historical_refs`. Each observation
  has `outcome`, `role`, `freshness`, and `evidence_ref`; no unexecuted gate
  creates an observation.
- Errors/blockers have stable reason `code`, `gate_id`, `message`, and
  `evidence_refs`. Causal references resolve to an existing gate/reason.
- Artifact entries contain relative path, kind, SHA-256, and byte length.
  Replay identity binds fixture/payload digests to the profile and source.
- Versioned nested records reject unknown keys under their documented schema;
  optional content is represented with explicit null or empty lists, rather
  than unrecognized extension fields.

Required gate IDs in PORTABLE_ONLY are P00-P09 from Section 8. FULL_SYSTEM
requires those same ten portable gates plus H00-H07 from Section 9.
This complete set is stored in the trusted profile; it cannot shrink at runtime.
Output scope, finality, coverage, verdict, and errors must agree before publication.

## 7. Source identity, freshness, and reproducibility

A pack is tied to one exact qualification commit and profile hash. Each child
process uses the same checkout/interpreter and captures that context.
Verify clean source state and source identity before and after the pack.
A changed source checkout, wrong commit/profile, or modified protected cognitive
content is a hard failure.

The protected cognitive fingerprint covers the existing A003-A010 packages,
their frozen fixtures/profiles, and existing qualifier semantics at the source
baseline. Normal A011 qualification additions are separate. Any narrowly allowed
infrastructure exposure is reviewed and characterized explicitly; it is not
silently excluded from provenance.

Full physical orchestration runs a fresh portable pack locally on the same
candidate commit/profile, then the mandatory physical gates. GitHub CI remains
independent portable evidence. A previous milestone report or a previous machine
run cannot replace a mandatory fresh A011 replay.

Research summary distinguishes:

- frozen expectations;
- historical evidence provenance;
- fresh portable observations;
- fresh physical observations.

Portable-only output cannot fabricate fresh A006/A007 physical observations.
A009/A010 physical observations cannot rewrite portable primary outcomes.

Repeated deterministic A008/A009/A010 replay uses the same frozen fixtures and
existing validators. The stable digest includes semantic payload, fingerprints,
case IDs/order, counts, outcomes, and policy identities. For the existing A008/A009/A010 portable JSON payloads at this baseline, the
only excluded payload field is an optional top-level `note`. Their execution IDs
and all semantic fields remain included. A011 envelope timestamps, process wall
durations, run-directory paths, and pack IDs are outside the child semantic
payload digest; their raw artifact hashes are still recorded. Unknown child
payload fields are rejected rather than silently dropped. Adding an exclusion
requires written review and cannot be used to conceal changed behavior.

Do not hash an entire physical pack and demand byte-for-byte equality: timing,
run IDs, and runtime observations vary. Preserve existing physical acceptance
rules, exact pinned identities, fixture identities, and outcome roles instead.

Later documentation-only commits may reference the qualified behavior SHA
without relabeling it. If source/qualifier/profile behavior changes after replay,
rerun affected qualification before claiming that new behavior qualified.
Exact CI for a documentation commit does not replace physical behavior evidence.

## 8. Fresh portable replay

The portable orchestrator runs these existing gates:

| Gate ID | Command |
| --- | --- |
| P00_PROFILE_SOURCE | A011 trusted-profile and clean-source precheck |
| P01_TESTS | `python -m pytest -q` |
| P02_ARCHITECTURE | `python scripts/audit_architecture_contract.py` |
| P03_REPOSITORY | `python scripts/qualify_repository.py` |
| P04_A003 | `python scripts/run_familiarity_benchmark_a003.py --qualify` |
| P05_A008 | `python scripts/qualify_procedural_memory_a008.py` |
| P06_A009 | `python scripts/qualify_integrated_loop_a009.py` |
| P07_A010 | `python scripts/qualify_baseline_comparison_a010.py` |
| P08_FROZEN_AUDIT | A011 profile/source/fingerprint/outcome/count audit |
| P09_PACK_VALIDATION | A011 normalized coverage, replay, and artifact consistency |

A008/A009/A010 receive unique `--output` paths. Their existing validators and
JSON success fields must agree with exit code 0. Other commands require their
documented success marker where one exists and successful exit; pytest output
and complete logs are retained.

P00 rejects an untrusted profile or dirty/wrong source context before child
commands run. P08/P09 reject drift, missing data, and unsupported evidence. They
perform repeated deterministic replay checks of the existing frozen
qualification cases; they do not create a new benchmark or alternate workload.

All portable gates run without Ollama and without model/network calls after
installation. Tests of orchestration inject fake process/evidence providers;
they do not invoke the real full pytest command from inside pytest, preventing
recursive test execution.

CI keeps the existing standalone gates and adds the A011 portable gate.
Duplicated portable command execution is acceptable qualification overhead.
Do not optimize away mandatory gate coverage during A011.

Portable CLI exit codes: 0 for complete portable PASS, 1 for portable
failure/malformed evidence, 2 for a verified external prerequisite blocker.
Even exit 0 yields a nonfinal portable pack with a null engineering verdict.

## 9. Fresh local physical replay

The physical entry point first validates the profile/source and runs the fresh
local portable path. It then performs bounded live prerequisite inspection:

- endpoint/runtime reachable;
- required model tags present;
- exact terminal and embedding digests;
- embedding metadata dimension;
- observed embedding dimension validated by the existing A005 qualifier.

Runtime metadata is preflight evidence, not a substitute for executing qualifiers.

Mandatory physical gates:

| Gate ID | Command |
| --- | --- |
| H00_PREREQUISITES | A011 runtime availability and frozen-identity precheck |
| H01_A004 | `python scripts/qualify_qwen_a004.py` |
| H02_A005 | `python scripts/qualify_vector_memory_a005.py` |
| H03_A006 | `python scripts/qualify_selective_activation_a006.py` |
| H04_A007 | `python scripts/qualify_uncertainty_expansion_a007.py` |
| H05_A009 | `python scripts/qualify_integrated_loop_a009_physical.py --portable-primary-outcome SUPPORTED` |
| H06_A010 | `python scripts/qualify_baseline_comparison_a010_physical.py --portable-primary-outcome NOT_SUPPORTED` |
| H07_FULL_VALIDATION | A011 profile, physical identity, fresh-evidence coverage, and final classification |

Run physical qualifiers sequentially with existing frozen settings and explicit
output files. A004/A005 model adapters inspect live identities; check the returned
descriptors rather than trusting an echoed expected-digest CLI argument.
Inspect pinned runtime identities again at completion to detect mid-run drift.

No auto-pull, model substitution, automatic retry, calibration, model training,
runtime restart, or preference-changing recovery is performed by A011.
A manual rerun is a new pack and preserves the previous failed/blocked pack.

Endpoint location may be supplied for local runtime access, but model tags,
digests, dimension, threshold, fixtures, and cognitive policies cannot be
overridden. Existing qualifier timeout settings remain unchanged. Process
containment must not impose a new, stricter qualification deadline. Existing
adapter/qualifier limits remain authoritative and any external containment
limit is recorded separately. An interrupted or incomplete process cannot pass;
its cause is classified under Section 10 rather than a new speed target.

Physical CLI exit codes: 0 for ENGINEERING_QUALIFIED, 1 for
ENGINEERING_NOT_QUALIFIED, 2 for QUALIFICATION_BLOCKED.
Timing remains descriptive except where an existing qualifier already defines
a timing rule. A003/A008 require no invented physical gate.

## 10. Failure and blocker taxonomy

| Observation | Classification |
| --- | --- |
| Endpoint unavailable / required model tag absent, confirmed by preflight | BLOCKED external prerequisite |
| Tag exists but digest/dimension differs | FAIL frozen identity |
| Fixture/fingerprint/threshold/outcome/count drift | FAIL frozen evidence |
| Existing qualifier reports failed acceptance or invalid experiment | FAIL qualification |
| Malformed/unparseable/contradictory output or missing raw evidence | FAIL evidence validity |
| Source/profile changes or packs refer to different candidates | FAIL provenance |
| Known external runtime disappearance during physical execution, with recorded verification | BLOCKED unless another hard failure already exists |
| Unknown exception, unexplained timeout, or unclassified nonzero process exit | FAIL; do not infer external blockage from free-text output |

Structured reason codes distinguish at least PROFILE_DRIFT, IDENTITY_DRIFT,
REPLAY_DRIFT, EVIDENCE_INVALID, SOURCE_MISMATCH, QUALIFIER_FAILED,
PREREQUISITE_UNAVAILABLE, and MODEL_MISSING. Diagnostic messages provide details;
classification cannot depend on guessing a keyword in an error string.

On a real/suspected cognitive defect, stop qualification, retain the failure
pack, and request an explicit repair task. Do not hide a repair inside A011,
rewrite prior results, or resume qualification as though a failure never occurred.
Infrastructure defects within A011 can be fixed under its approved plan with
RED -> GREEN evidence. Cognitive repairs require separate scope and approval.

## 11. Verification design for later TDD

Tests must exercise decisions rather than merely echo manifest construction:

- expected valid portable and full-system packs;
- correct finality and absence of full certification in portable-only mode;
- failure/blocker precedence, including simultaneous failure and unavailable model;
- missing/duplicate/unknown gates and unexplained NOT_RUN;
- every pinned value mutation, including A006/A010 outcomes and A010 counts;
- changed profile bytes against the independently frozen anchor;
- missing sentinel/case-order drift;
- invalid types, duplicate JSON keys, NaN/infinity, malformed digests/schema;
- clean-source/provenance mismatch and mid-run source/runtime drift;
- missing raw files, hash mismatch, contradictory success/exit fields;
- real existing qualifier outputs normalized through fake-runner integration;
- deterministic repeat mismatches without retuning any fixture;
- physical preflight unavailability versus wrong installed model identity;
- output publication failure/overwrite protection;
- no Ollama/model calls in portable tests and no recursive pytest spawning;
- backward-compatible qualifier exposure only if needed and characterized;
- qualification dependency direction and cognitive boundary preservation.

Production frozen artifacts are never mutated for a test. Deliberate mutation
uses independent temporary copies/test evidence. Keep all failures visible.

## 12. Advance task decomposition and delivery boundaries

The [planned task](../../development/tasks/A011-asca-v0x-qualification.md)
records scope-sized candidate work items and their required evidence.
It is an advance task inventory, not an implementation plan.

After this written spec is approved, invoke writing-plans to decide concrete
files, RED/GREEN commands, commits, dependency order, and execution handoffs.
Only after plan review and execution-method selection may issue creation,
isolated worktree creation, activation, and implementation begin.

Expected implementation responsibilities:

- qualification records/classifier;
- independently frozen profile and strict validation;
- existing-evidence adapters and portable orchestration;
- portable CI integration;
- physical preflight/orchestration;
- pack/report serialization and provenance;
- fresh system qualification and frozen-evidence audit;
- whole-change review, exact branch/main CI, and closure metadata.

This design does not assign an A012 or authorize a subsequent optimization task.

## 13. Acceptance and milestone closure

A011 can reach DONE only when:

1. this written spec is explicitly approved;
2. the written implementation plan is reviewed/approved and execution selected;
3. A011 issue creation/worktree/activation follows those gates;
4. portable qualification passes from a clean checkout without Ollama;
5. mandatory physical qualifiers reproduce the pinned local profile;
6. all frozen identities, deterministic fingerprints/counts, and outcomes match;
7. mutation, malformed-evidence, incomplete-coverage, and provenance tests fail closed;
8. a validated full-system pack gives a coherent final engineering verdict;
9. the target engineering completion verdict is ENGINEERING_QUALIFIED;
10. whole-change review completes, with Critical/Important findings resolved
    using appropriate RED -> GREEN evidence;
11. exact feature-branch CI is GREEN for the reviewed candidate;
12. reviewed behavior integrates to main without history destruction;
13. exact reviewed/integration main CI is GREEN;
14. final report records evidence roles, physical applicability, and claims boundaries;
15. issue closure and CURRENT/ROADMAP/task state agree;
16. final main is clean and synchronized;
17. package remains 0.1.0.dev0, FlyWireLLM is untouched, and no release is promoted.

A valid ENGINEERING_NOT_QUALIFIED/BLOCKED pack is a correctly classified result,
but does not close A011 as successfully engineering-qualified. Record the
failure/blocker and next action without manufacturing GREEN.
CI/review/integration are live publication/closure gates; the offline portable
runner does not query GitHub to claim their completion.

## 14. Version, release, and claims boundaries

Keep `0.1.0.dev0`. No tag, release, stable promotion, or automatic `0.1.0`
promotion belongs to A011. A later release-readiness decision requires explicit
user authorization.

Do not claim intelligence superiority, general FLOP/energy/power/RAM-byte/
latency savings, biological equivalence, consciousness, or AGI.
A011 is a project-internal qualification of a declared architecture profile;
it is not certification by an external standards body.

Do not change cues, fixtures, thresholds, dense-only sentinel, cognitive
semantics, A009/A010 retrieval scheduling, or historical conclusions.
No real OS/API/LConnect/BConnect action execution is added to cognition.
No graph database, learned familiarity, memory consolidation, autonomous
self-modification, or FlyWireLLM work is added.

The defensible claim is that the declared ASCA v0.x engineering profile is
coherent and reproducible under pinned portable/physical qualification contracts
while preserving its positive and negative component research outcomes.

## 15. Review and resume gate

The author must self-review this spec for incomplete markers, contradictions,
ambiguity, and scope; fix findings before committing. Commit/push it, require
exact CI for that spec commit, and then stop for the user's written-spec review.

User approval of the conversational design does not skip this gate.
The immediate next stage after written-spec approval is writing-plans.
