# FlyWireASCA Qualification Matrix

Date: 2026-10-12
Purpose: canonical map of portable CI gates, local physical gates, frozen
outcome roles, and A011 qualification claims boundaries.

## 1. Principles

- GitHub CI is portable and Ollama-free.
- Physical model/embedding qualification is local-only.
- A valid `NOT_SUPPORTED` research outcome can still be a passing
  qualification.
- Where a milestone defines a portable primary outcome, physical evidence is
  secondary and cannot rewrite that outcome.
- Historical outcomes and pinned identities remain frozen through A011.

## 2. Milestone matrix

| Milestone | Portable CI role | Local physical gate | Frozen outcome role |
| --- | --- | --- | --- |
| A003 | familiarity benchmark qualification | none required | engineering benchmark |
| A004 | unit/fake-transport coverage | Qwen model qualifier | physical baseline |
| A005 | unit/portable vector-memory coverage | vector-memory qualifier | physical retrieval |
| A006 | unit/portable selector coverage | selective-activation qualifier | `NOT_SUPPORTED` |
| A007 | unit/portable expansion coverage | uncertainty-expansion qualifier | `SUPPORTED` |
| A008 | procedural-memory qualifier | none required | `SUPPORTED` |
| A009 | integrated-loop qualifier | integrated physical qualifier | `SUPPORTED` |
| A010 | baseline-comparison qualifier | A010 physical qualifier | `NOT_SUPPORTED` |
| A012 | relational-reasoning structure qualifier | A012 embedding replay (secondary) | `EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED` |
| A013 | target-free relational-activation qualifier | none required | `SIGNAL_GATED_RELATION_JUSTIFIED` |
| A014 | target-free structural-need routing qualifier | pinned `qwen3.5:4b` routing qualifier | `HYBRID_STRUCTURAL_ROUTING_JUSTIFIED` |

| A015 | portable engineering, bilingual freeze, new runtime audit and offline evidence verification | pinned unified/direct Stage A comparison, 384 trials | `UNIFIED_RUNTIME_NOT_SUPPORTED` |

## 3. Portable GitHub CI commands

These commands are intended to remain network/model independent after package
installation:

```text
python -m pytest -q
python scripts/audit_architecture_contract.py
python scripts/qualify_repository.py
python scripts/run_familiarity_benchmark_a003.py --qualify
python scripts/qualify_procedural_memory_a008.py
python scripts/qualify_integrated_loop_a009.py
python scripts/qualify_baseline_comparison_a010.py
python scripts/verify_a011_frozen_profile_preservation.py
python scripts/qualify_relational_reasoning_a012.py --output "$RUNNER_TEMP/a012-relational-${{ github.run_id }}-${{ github.run_attempt }}.json"
python scripts/qualify_relational_activation_a013.py --output "$RUNNER_TEMP/a013-relational-activation-${{ github.run_id }}-${{ github.run_attempt }}.json"
python scripts/qualify_structural_routing_a014.py --output "$RUNNER_TEMP/a014-structural-routing-${{ github.run_id }}-${{ github.run_attempt }}.json"
python scripts/verify_a014_physical_evidence.py docs/development/qualification/a014-structural-routing-physical-v1.json
python scripts/freeze_agent_runtime_a015.py --check
python scripts/audit_agent_runtime_contract.py
python scripts/qualify_agent_runtime_a015.py --output "$RUNNER_TEMP/a015-portable-${{ github.run_id }}-${{ github.run_attempt }}.json"
python scripts/verify_a015_physical_evidence.py docs/development/qualification/a015-agent-runtime-physical-v1.json
```

A004-A007, A009/A010, and A012 physical scripts are intentionally absent from
GitHub CI. A013 defines no mandatory physical replay because its primary variable
is deterministic activation policy after a vector seed, not embedding quality. Post-A011 CI does not rerun the A011 portable qualifier against the
new HEAD: A012 adds a cognitive package outside the frozen v0.x source universe.
Instead it verifies the literal A011 profile and all 67 protected Git blobs are
unchanged. This is preservation evidence, not a claim that the A012 HEAD is
A011-qualified.

## 4. Local-only physical commands

```text
python scripts/qualify_qwen_a004.py
python scripts/qualify_vector_memory_a005.py
python scripts/qualify_selective_activation_a006.py
python scripts/qualify_uncertainty_expansion_a007.py
python scripts/qualify_integrated_loop_a009_physical.py --portable-primary-outcome SUPPORTED
python scripts/qualify_baseline_comparison_a010_physical.py --portable-primary-outcome NOT_SUPPORTED
python scripts/qualify_relational_reasoning_a012_physical.py
python scripts/qualify_structural_routing_a014_physical.py --expected-source-sha <exact-implementation-sha> --output docs/development/qualification/a014-structural-routing-physical-v1.json
python scripts/qualify_agent_runtime_a015_physical.py --fixture fixtures/a015/stage-a-v1 --repetitions 3 --seed 0 --output docs/development/qualification/a015-agent-runtime-physical-v1.json
```

These commands require the pinned local Ollama/model prerequisites and are
**local-only**.

## 5. Pinned local identities

### A004 terminal model

- tag: `qwen3.5:4b`
- digest:
  `2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd`

### A005 embedding model

- tag: `qwen3-embedding:0.6b`
- digest:
  `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`
- dimension: 1024
- minimum similarity threshold: `0.5037018224299838`

## 6. Frozen outcome preservation

- A006: `NOT_SUPPORTED`
- A007: `SUPPORTED`
- A008: `SUPPORTED`
- A009: `SUPPORTED`
- A010: `NOT_SUPPORTED`

A valid `NOT_SUPPORTED` result means the experiment/qualification evidence is
valid while the tested hypothesis is not supported. It must not be converted
into a CI failure merely because the scientific result is negative.

## 7. Claims boundary

Portable logical counts do not establish hardware FLOPs, energy, power, RAM
bytes, bandwidth, or general latency. Local physical timing remains descriptive
unless a milestone defines a statistical timing protocol.

The qualification matrix documents evidence topology; it does not itself add a
new ASCA research claim.

## 8. A011 system qualification topology

A011 is an engineering qualification layer over the existing milestones.
Research evidence remains five separate milestone outcomes; a valid negative
outcome is preserved, and no aggregate intelligence score is defined.

| Scope | Mandatory gates | Final state |
| --- | --- | --- |
| Portable CI/local | P00-P09: profile/source, tests, architecture, repository, A003/A008/A009/A010, frozen repeat audit, pack validation | PORTABLE_ONLY; is_final=false; engineering_verdict=null |
| Full local system | Fresh local P00-P09 plus H00-H07: metadata prerequisites, A004/A005/A006/A007/A009/A010, completion audit | FULL_SYSTEM; is_final=true; one engineering verdict |

The portable workflow retains every preexisting standalone gate, binds the pack
to its actual Git HEAD (including a PR merge checkout), and uploads the indexed
pack with actions/upload-artifact@v4 and if:always(). Missing artifacts fail the
upload. It does not invoke physical models.

Full local command:

```text
python scripts/qualify_asca_v0x_a011_physical.py --expected-source-sha <exact-git-head-40hex> --output-dir <new-outside-checkout-directory>
```

The full command runs fresh portable and sequential physical replay on one clean
candidate/profile. A005 receives the frozen threshold 0.5037018224299838.
Metadata inspection and source capture run before and after the physical path.
Confirmed missing runtime/model prerequisites yield QUALIFICATION_BLOCKED only
when no verified hard failure exists. Identity/profile/source drift, malformed
evidence, and unexplained child failure yield ENGINEERING_NOT_QUALIFIED.
Every mandatory gate PASS is required for ENGINEERING_QUALIFIED.

The reviewed frozen profile is
docs/development/qualification/a011-v0x-profile-v1.json; its literal SHA256 is
add06f285bf6decc7d492b987d3769dc64db4cb3d0177c8c6586d50ee5f6d46d.
Protected Git mode/path/blob records are shallow-checkout safe and hash to
8df49f05fe54de43667ab2f8ef5de2caae9376ffedf2cb8f8d26f0e4abcca6b6.
A011 adds no calibration, workload, threshold/model override, hidden retry,
model pull/restart, or new physical process deadline. It changes no cognitive
semantics and makes no external certification, FLOPs, energy, or general speed
claim. Exact candidate/main CI and fresh physical evidence are recorded in the
A011 task and final report; this topology document alone is not completion proof.

## 9. A011 reviewed integration evidence

Engineering qualification on exact integration/main `f83bf1febbb6ac0bdcba3d8bf05dc8d437edc5ac`: FULL_SYSTEM, is_final=true, ENGINEERING_QUALIFIED;18 gates/94 frozen checks
PASS,86 indexed artifacts independently audited, errors/blockers empty.
Exact push/main [CI38058896880](https://github.com/funggier/FlyWireASCA/actions/runs/38058896880) SUCCESS.
Fresh repaired-feature e96d71b and main physical packs are separate; portable
CI packs remain nonfinal/null verdict.

[Evidence report](reports/ASCA-20261010-A011-v0x-qualification.md) records
exact sources, review/TDD repairs, frozen identities/counts/outcomes, pack
locations/hashes and actual host/runtime. Later closure/handoff metadata receives its own exact CI and does not replace
the qualified physical SHA.

## 10. A012 relational-reasoning decision topology

A012 is a new research layer outside the frozen A011 v0.x source universe. Its
portable primary experiment compares the real A005 Vector + Metadata primitive
with deterministic bounded traversal over explicit Contract v0.1 typed edges.
The frozen fixture contains 12 cases: 6 relation-dependent positives, 1 direct
vector control, 4 fail-closed controls, and 1 invalid-contract control.

Portable frozen result: `EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED` for the declared
A012 workload. Vector success is 5/11 valid cases; bounded-relation success is
11/11; relation-only recoveries are 6; regressions, identity failures,
provenance failures, budget violations, and duplicate-visit failures are 0.
Fixture SHA256 is
`dcabd86117f22e35c18fe605c8411da143962f112645a78c9124ec5987179aea`.

Development physical replay with pinned `qwen3-embedding:0.6b` also observes
`EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED`: vector success 2/11, relation-aware
success 6/11, relation-only recoveries 4, with deterministic repeat and zero
regression, identity, provenance, budget, or duplicate-visit failures. Some
negative controls are retrieved directly by the physical embedding at the frozen
A005 threshold, so physical counts are descriptive secondary evidence rather
than a replacement fixture.

This does not replace A005 Vector + Metadata, justify a persistent graph
database, or establish general graph superiority. Physical A012 embedding replay
is secondary and cannot rewrite the frozen portable decision. A011 remains
historical qualification of exact integration `f83bf1febbb6ac0bdcba3d8bf05dc8d437edc5ac`.


## 11. A013 selective relational-activation decision topology

A013 is a post-A011 research layer built above the A005 vector-retrieval and
A012 relation semantics without modifying the A011-protected cognitive source
blobs. It removes the A012 benchmark-only expected-target oracle from runtime
control by introducing target-free bounded neighborhood expansion.

The frozen portable mixed workload contains 17 cases: 16 valid and 1 invalid
contract control. Among valid cases, 6 are relation-dependent positives, 4 are
structural fail-closed controls, and 6 are direct-vector/non-structural
controls. All three policies share the same vector retrieval input:

- `VECTOR_ONLY`
- `ALWAYS_RELATION`
- `SIGNAL_GATED_RELATION`

Portable frozen result: `SIGNAL_GATED_RELATION_JUSTIFIED` for the declared
A013 workload. Vector-only succeeds on 10/16 valid cases; always-relation and
signal-gated both succeed on 16/16. Both relation policies recover all 6
relation-dependent misses with zero regressions. Signal-gated activation
reduces relation invocations from 16 to 10, scanned edges from 16 to 11, and
relation visited nodes from 29 to 18 while preserving all 6 direct-vector
controls. False/missed structural activation, identity failures, provenance
failures, budget violations, and duplicate-visit failures are all zero.
Fixture SHA256 is
`fcd805a5229bfad43f8eed6999be37ae61168dda1a8560f04370b3df0262baa5`.

This result assumes an explicit typed `StructuralNeed` contract. A013 does not
claim that a model can infer structural need from unconstrained natural
language, does not justify a persistent graph database, and does not establish
general latency, FLOP, energy, RAM, or production-safety superiority.

## 12. A014 structural-need routing decision topology

A014 is a post-A011, target-free routing layer above `contracts`, `model`, and
`relational_activation`. Runtime/model routing receives ordinary English/Thai
query text only and must not receive evaluator targets, expected relation labels,
benchmark labels, graph contents, retrieval results, or post-hoc correctness.

Portable GitHub CI validates frozen bilingual fixture integrity, strict model
output parsing, deterministic rule/model/hybrid control flow, downstream A013
composition, and evidence derivation. Portable scripted adapters are engineering
control-flow evidence only and do **not** establish a physical architecture
decision.

The mandatory local physical gate uses pinned `qwen3.5:4b` digest
`2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd`
with temperature 0, seed 0, thinking disabled, bounded output, exact source
manifest binding, frozen fixture/prompt fingerprints, and retained raw model
outputs. One of the predeclared A014 decisions is derived from that physical
evidence. A negative or `MIXED` decision remains a valid research result when
experiment integrity is valid.

After Task 11 creates and locally verifies the source-bound physical JSON,
GitHub CI verifies that committed evidence against the exact frozen source,
fixture, prompt, model identity, raw per-case records, recomputed policy metrics,
and derived decision. GitHub CI remains Ollama-free; it never runs the physical
model qualifier.
Frozen A014 physical architecture decision: `HYBRID_STRUCTURAL_ROUTING_JUSTIFIED`. On 32 valid
English/Thai cases, RULE_ONLY succeeds on 27/32, MODEL_ONLY on 32/32, and
HYBRID_RULE_THEN_MODEL on 32/32. Hybrid records zero false/missed activations
and invokes the model on 9/32 cases versus 32/32 for model-only. This establishes
a routing/control-flow trade-off for the frozen workload, not general latency,
FLOP, energy, RAM, token, or production-safety superiority.
## 12. A015 unified runtime Stage A

A015 is a separate post-A011 runtime gate. Stage A permits PURE and IN_MEMORY
capabilities with no real external actions. Ordinary English/Thai text is bound
to closed public schemas; model/embedding inference is configured infrastructure.
The new top-level controller owns observation, independent verification and
bounded recovery. A001-A014 outcomes and all67 A011 protected paths are retained.

Portable engineering uses scripted ports to qualify contracts, provenance,
terminal control, semantic operations, changed-context/changed-plan recovery and
budget accounting. It does not establish physical model capability or savings.

The physical comparison freezes64 requests /32 bilingual pairs and three
repetitions,384 trials /192 per variant. Each repetition has48 solvable and16
non-success controls, including8 bounded failures. Direct uses one model call
with the complete identical public information and1024 output tokens. Unified
permits4 calls /2048 output tokens, at most6 retrieval queries across3 rounds,
24 context items /16384 bytes,3 relation invocations /24 visits /96 scanned
edges,3 strategy validations /2 recovery rounds /96 primitive executions and
180 seconds per request. Failed work and null usage retain costs.

The ordered decision requires genuine successful recovery after a real failed
observation with meaningful context or plan change. The verified physical
outcome is UNIFIED_RUNTIME_NOT_SUPPORTED: unified138/144 solvable completions,
48/48 controls and24/24 bounded failures, zero false success/invariant failures,
but zero genuine successful recovery despite36 controller recovery rounds.
Direct returns192 INVALID_PLAN proposals and completes0/144; retained outputs
show protocol failures, not general absence of model knowledge.
Unified generation calls/tokens0; direct192 calls,358653 prompt and46976 output
tokens. Unified query embedding calls216 /9015 prompt tokens remain separate;
setup and latency are measured separately. No universal efficiency, FLOPs,
energy, process-RAM or real-effects safety claim follows.

[Report](reports/ASCA-20261012-A015-unified-agent-runtime.md),
[architecture](../architecture/A015-UNIFIED-AGENT-RUNTIME.md),
[physical artifact](qualification/a015-agent-runtime-physical-v1.json).
The offline verifier recomputes raw verdicts/counters/outcome and source identity,
and is unconditional in CI. CI remains Ollama-free and never reruns physical
generation. A valid negative research outcome permits engineering qualification
only after independent whole-branch review, exact CI and authorized integration.
