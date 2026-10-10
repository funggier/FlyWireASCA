# ASCA PRE-A011 Architecture Snapshot

Date: 2026-10-10  
Repository: `funggier/FlyWireASCA`  
Purpose: canonical implemented-architecture snapshot before A011  
Research roadmap state: A001-A010 DONE; A011 PLANNED

## 1. Authority and provenance

This snapshot describes the implemented FlyWireASCA architecture after A010 and
before A011. It does not replace historical design artifacts.

The initial design predates the local-model insertion. The numbering migration is
preserved in:

`docs/development/roadmap-migrations/A004-qwen-insertion.md`

Historical milestone reports remain authoritative for their own frozen
experiments. Live Git/GitHub/runtime state remains authoritative over stale
prose.

## 2. Implemented architecture by milestone

- **A002 — Architecture Contract:** versioned typed contracts, deterministic
  validation/serialization boundaries, memory/procedure/control evidence types.
- **A003 — Familiarity System:** deterministic exact familiarity index used as
  evidence only; familiarity is not identity, truth, or semantic-routing
  authority.
- **A004 — Local Model Adapter & Qwen3.5:4B Baseline:** backend-neutral model
  adapter contract plus pinned local Ollama/Qwen baseline. Model generation is
  not allowed to control deterministic A009 retrieval/procedure verification.
- **A005 — Semantic Vector Memory Retrieval:** backend-neutral embedding
  boundary, exact vector-memory retrieval, metadata filtering, and the qualified
  `qwen3-embedding:0.6b` physical retrieval profile.
- **A006 — Working Set / Selective Activation:** bounded candidate activation
  and working-set selection. `SINGLE_BEST` is retained as the primary
  selector; exhaustive selection remains a comparison primitive.
- **A007 — Surprise, Uncertainty & Expansion:** deterministic structural
  expansion triggers and a frozen three-round bounded expansion profile with
  `SIGNAL_DRIVEN` as the retained primary policy.
- **A008 — Procedural Memory / Skill Chunking:** deterministic hierarchical
  procedures, exact outcome checkpoints, `CHUNKED` primary mode, bounded call
  depth, and no hidden automatic retry.
- **A009 — Integrated Cognitive Loop:** bounded composition of familiarity,
  vector retrieval, selective activation, structural expansion, CHUNKED
  procedure execution, and mismatch-driven outer recovery. Maximum procedure
  attempts remain 3.
- **A010 — Dense/Non-selective Baseline Comparison:** frozen comparison harness
  between the real A009 primary path and a deliberately exhaustive A005+A006
  baseline.

## 3. Current dependency direction

The pre-A011 package graph is intentionally acyclic:

```text
contracts
  |
  +--> model
  +--> embedding --> vector_memory --> selective_activation
  |                                      |
  +--> familiarity                       v
  +--> procedural_memory           uncertainty_expansion
                  \                    /
                   \                  /
                    +--> integrated_loop
                              |
                              v
                     baseline_comparison
```

The architecture audit owns enforcement of the exact allowed direct
cross-package dependency set.

## 4. Implemented versus deferred concepts

### Implemented

- typed architecture contracts and explicit evidence;
- exact familiarity estimation;
- semantic vector retrieval with metadata;
- bounded selective activation and working-set construction;
- deterministic structural uncertainty/expansion;
- reusable CHUNKED procedural units with checkpoints;
- bounded integrated recovery loop;
- backend-neutral model/embedding adapter boundaries;
- controlled dense/non-selective comparison.

### Deferred

The following remain intentionally deferred and are not silently implied by the
implemented system:

- typed associative graph traversal;
- persistent graph database;
- learned/neural familiarity;
- automatic memory consolidation;
- autonomous self-modification/learning;
- real OS/API/LConnect/BConnect action execution inside the cognitive loop;
- external knowledge/tool retrieval controlled by the cognitive loop;
- robotics/perception stack;
- hardware selective neural compute;
- general FLOP/energy/power/latency superiority claims.

## 5. Frozen research outcomes

Engineering completion and research-hypothesis support are separate.

- A006: `NOT_SUPPORTED`
- A007: `SUPPORTED`
- A008: `SUPPORTED`
- A009: `SUPPORTED`
- A010: `NOT_SUPPORTED`

A valid negative research outcome is not an engineering failure.

## 6. Evidence-driven implications

The frozen evidence supports only these bounded architectural conclusions:

- A003 familiarity remains evidence-only.
- A006 selective-convergence benefit is not promoted from its
  `NOT_SUPPORTED` result.
- A007 structural expansion remains useful on its frozen qualification
  workload.
- A008 `CHUNKED` remains the primary qualified procedure representation.
- A009 `MISMATCH_DRIVEN_RECOVERY` remains bounded and supported on its frozen
  integrated fixture.
- A010 shows substantially smaller active selected-state counts but does not
  support the declared system-level retrieval-work hypothesis.

The A010 portable primary comparison observed:

- ASCA procedure successes: 7
- dense procedure successes: 8
- dense-only successes: 1
- ASCA / dense query counts: 28 / 27
- ASCA / dense scored-vector counts: 1984 / 1440
- ASCA / dense cumulative selected counts: 66 / 480

These are controlled logical software counts, not FLOPs, RAM bytes, energy, or
general latency measurements.

## 7. Pinned physical identities

- terminal model: `qwen3.5:4b`
- terminal model digest:
  `2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd`
- embedding model: `qwen3-embedding:0.6b`
- embedding digest:
  `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`
- embedding dimension: 1024
- frozen A005 similarity threshold: `0.5037018224299838`

Physical evidence is secondary where a milestone defines a portable primary
outcome.

## 8. Pre-A011 maintenance boundary

PRE-A011 may improve documentation, lifecycle/audit infrastructure, and bounded
maintainability debt while preserving cognitive semantics and frozen evidence.

It must not optimize A009/A010 retrieval merely to improve the A010 result.

FlyWireLLM remains independent and untouched.

## 9. A011 handoff state

A011 — ASCA v0.x Qualification remains **PLANNED** and has no GitHub issue
during PRE-A011.

A011 should use this snapshot plus the qualification matrix as its initial
architecture-wide evidence map.
