# FlyWireASCA Qualification Matrix

Date: 2026-10-10  
Purpose: canonical map of portable CI gates, local physical gates, frozen
outcome roles, and claims boundaries before A011.

## 1. Principles

- GitHub CI is portable and Ollama-free.
- Physical model/embedding qualification is local-only.
- A valid `NOT_SUPPORTED` research outcome can still be a passing
  qualification.
- Where a milestone defines a portable primary outcome, physical evidence is
  secondary and cannot rewrite that outcome.
- Historical outcomes and pinned identities are not retuned during PRE-A011.

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
