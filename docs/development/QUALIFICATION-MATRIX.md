# FlyWireASCA Qualification Matrix

Date: 2026-10-10
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
python scripts/qualify_asca_v0x_a011.py --expected-source-sha "$(git rev-parse HEAD)" --output-dir "$RUNNER_TEMP/a011-portable-${{ github.run_id }}-${{ github.run_attempt }}"
```

A004-A007 physical scripts and A009/A010 physical scripts are intentionally
absent from GitHub CI.

## 4. Local-only physical commands

```text
python scripts/qualify_qwen_a004.py
python scripts/qualify_vector_memory_a005.py
python scripts/qualify_selective_activation_a006.py
python scripts/qualify_uncertainty_expansion_a007.py
python scripts/qualify_integrated_loop_a009_physical.py --portable-primary-outcome SUPPORTED
python scripts/qualify_baseline_comparison_a010_physical.py --portable-primary-outcome NOT_SUPPORTED
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
locations/hashes and actual host/runtime. Later closure/handoff metadata
receives its own exact CI and does not replace the qualified physical SHA.
