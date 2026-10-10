# ASCA A010 - Dense / Non-selective Baseline Comparison

Date: 2026-10-10
Repository: `funggier/FlyWireASCA`
Task: A010 â€” Dense/Non-selective Baseline Comparison
GitHub Issue: #10
Branch: `research/a010-dense-nonselective-baseline-comparison`

## 1. Result

Primary A010 hypothesis outcome: `NOT_SUPPORTED`

The frozen deterministic A010 workload does **not** support the declared
system-level hypothesis that ASCA_PRIMARY preserves dense-baseline deterministic
task coverage while also reducing all three declared logical-work dimensions:
A005 query count, A005 scored-vector count, and cumulative selected working-set
items.

The result is a valid negative research outcome, not a process failure.

ASCA did keep far less selected active state on this fixture, but the A009
progressive/recovery path re-evaluates already-enabled cue tiers at wider
scopes. On the frozen fixture this produced more logical retrieval queries and
more exact-index vector scores than the one-shot dense exhaustive baseline.
The frozen routing-miss sentinel also produced one dense-only procedure success.

No fixture, threshold, ranking rule, procedure requirement, or classifier was
retuned after observing this result.

## 2. Frozen portable identity

- qualification scope: `deterministic_dense_nonselective_baseline_a010`
- fixture version: `a010-deterministic-v1`
- fixture fingerprint:
  `69d20542cd1e7e5c25a0fb61b9060f622379206b519da3cec7624e00bb6e5d4c`
- primary ASCA policy: `MISMATCH_DRIVEN_RECOVERY`
- A006 primary selector: `SINGLE_BEST`
- A007 initial policy: `SIGNAL_DRIVEN`
- primary procedure mode: `CHUNKED`
- dense top-k policy: `max(1,index.document_count)`
- dense activation policy: existing A006 `select_exhaustive()`

The portable fixture contains 12 ordered cases and fixed corpus-size classes of
16, 64, and 256 memories.

## 3. Primary compared systems

### ASCA_PRIMARY

ASCA_PRIMARY delegates to the real A009 controller:

`A003 familiarity â†’ A005 retrieval â†’ A006 SINGLE_BEST â†’ A007 SIGNAL_DRIVEN â†’ A008 CHUNKED â†’ A009 MISMATCH_DRIVEN_RECOVERY`.

A010 does not fork or replace the A009 primary controller.

### DENSE_EXHAUSTIVE

DENSE_EXHAUSTIVE uses the same A005 index, memory corpus, cue texts,
minimum-similarity threshold, explicit A008 root procedure, action-memory
requirements, and immutable initial world state.

It:

1. enables all declared cue tiers immediately;
2. uses `top_k=max(1,index.document_count)` for every query;
3. merges returned evidence with the existing A006 `select_exhaustive()`;
4. executes the same A008 root procedure once in `CHUNKED` mode;
5. performs no mismatch-driven replay because all declared retrieval scope is
   already available.

A009 `ALWAYS_MAX_SCOPE` remains a secondary wide-selective control and is not
treated as the dense baseline.

## 4. Frozen deterministic case families

The ordered cases are:

1. `easy-local-many-distractors`
2. `unfamiliar-semantic-many-distractors`
3. `structural-expansion-required`
4. `procedure-recovery-one-scope`
5. `procedure-recovery-two-scopes`
6. `persistent-missing-memory`
7. `selective-routing-miss-sentinel`
8. `same-name-identity`
9. `tie-heavy-distractors`
10. `structural-expansion-ablation`
11. `familiarity-disabled-equivalence`
12. `invalid-contract`

The `selective-routing-miss-sentinel` is intentionally capable of producing
a dense-only success. It prevents a benchmark made only of ASCA-friendly cases.

## 5. Frozen aggregate evidence

| Metric | Value |
| --- | ---: |
| Case count | 12 |
| Valid case count | 11 |
| Invalid-contract case count | 1 |
| Primary comparison case count | 9 |
| ASCA procedure success count | 7 |
| Dense procedure success count | 8 |
| Shared success count | 7 |
| Dense-only success count | 1 |
| ASCA-only success count | 0 |
| ASCA query count | 28 |
| Dense query count | 27 |
| ASCA scored-vector count | 1984 |
| Dense scored-vector count | 1440 |
| ASCA cumulative selected count | 66 |
| Dense cumulative selected count | 480 |
| ASCA peak selected count | 12 |
| Dense peak selected count | 256 |
| ASCA procedure attempt count | 14 |
| Dense procedure attempt count | 9 |
| designated parity reduction count | 7 |
| identity failure count | 0 |
| duplicate execution-ID failure count | 0 |
| post-completion extra-attempt failure count | 0 |
| ASCA deterministic repeat match | true |
| Dense deterministic repeat match | true |

These are logical software/control counts.

In particular:

- `scored-vector count` is the number reported by the exact A005 software
  index, not FLOPs;
- selected counts are working-set item counts, not RAM bytes;
- procedure attempts are not converted into a weighted cost;
- A010 defines no synthetic scalar efficiency score.

## 6. Why the primary hypothesis is NOT_SUPPORTED

A010 requires all three declared logical-work dimensions to be strictly lower
for ASCA before a positive system-level efficiency result can be
`SUPPORTED`:

1. A005 query count;
2. A005 scored-vector count;
3. cumulative selected working-set items.

The frozen fixture shows:

- queries: ASCA 28 vs dense 27;
- scored vectors: ASCA 1984 vs dense 1440;
- cumulative selected items: ASCA 66 vs dense 480.

Therefore ASCA reduces selected active state substantially on this workload but
does not reduce logical retrieval work under the declared comparison contract.

Additionally, dense has one success that ASCA does not have on the frozen
routing-miss sentinel:

- ASCA successes: 7;
- dense successes: 8;
- dense-only successes: 1.

Because the required multi-dimensional retrieval reduction is absent, the
classifier returns `NOT_SUPPORTED`, rather than `MIXED`.

## 7. What the result does and does not mean

The negative result is specifically about this A010 hypothesis and this frozen
comparison workload.

It does **not** mean:

- bounded selective activation is nonfunctional;
- A007 expansion stopped working;
- A008 CHUNKED procedures stopped working;
- A009 mismatch recovery stopped working;
- dense processing is generally superior;
- future ASCA retrieval scheduling cannot improve.

A useful architectural observation is exposed by A010: the current A009
recovery representation can save active-state size while paying repeated
retrieval work because wider scope evaluations re-run prior enabled cue tiers.
A future milestone may investigate incremental/cached retrieval without
rewriting this A010 outcome.

## 8. Portable qualification evidence

Qualified implementation candidate:

- SHA:
  `234bc090dc068447c1830fa79337745b7796f25f`
- exact feature-branch CI:
  `38014300995`
- conclusion: `success`
- local full suite: `515 passed`

Portable A010 qualification:

- experiment validity: `true`
- errors: none
- primary outcome: `NOT_SUPPORTED`
- frozen fingerprint: exact match
- deterministic repeat: ASCA `true`, dense `true`
- identity failures: 0
- duplicate execution IDs: 0
- post-completion extra attempts: 0

Existing portable qualification gates remained GREEN:

- architecture contract audit;
- repository qualification;
- A003 familiarity qualification;
- A008 procedural-memory qualification;
- A009 integrated-loop qualification.

## 9. Physical integration evidence

Physical integration validity: `true`

Pinned A005 physical identity:

- model: `qwen3-embedding:0.6b`
- digest:
  `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`
- embedding dimension: 1024
- similarity threshold: `0.5037018224299838`
- physical fixture: `a010-physical-v1`

Observed physical comparison:

| Metric | ASCA | Dense |
| --- | ---: | ---: |
| Procedure success | true | true |
| Final state correct | true | true |
| Procedure attempts | 1 | 1 |
- ASCA physical query/scored-vector | 1 / 3
- Dense physical query/scored-vector | 3 / 9
| Cumulative selected count | 3 | 3 |
| Peak selected count | 3 | 3 |
| Observed runner duration, ns | 145013000 | 158247300 |

The physical case is deliberately small and is **secondary** evidence. It shows
that on this particular physical case the early selective path used fewer
queries/vector scores than dense, but it cannot change the frozen portable
A010 primary outcome.

Observed timing is descriptive only. A010 does not define a statistical timing
benchmark and makes no general latency claim.

## 10. Historical result preservation

A010 answers a different system-level comparison question and does not rewrite
earlier frozen results:

- A006 selective-convergence hypothesis: `NOT_SUPPORTED`;
- A007 structural-expansion hypothesis: `SUPPORTED`;
- A008 procedural-memory hypothesis: `SUPPORTED`;
- A009 integrated-loop hypothesis: `SUPPORTED`;
- A010 dense/non-selective comparison hypothesis: `NOT_SUPPORTED`.

This combination is internally consistent: A009 can demonstrate bounded
integration/recovery while A010 can still find that the current integrated path
does not beat the declared dense baseline on the A010 multi-dimensional
logical-work objective.

## 11. Claims boundary

A010 may report exactly what it measured:

- deterministic task-success coverage;
- dense-only/ASCA-only success counts;
- A005 logical query and scored-vector counts;
- selected working-set item counts;
- procedure attempt/recovery counts;
- identity preservation;
- deterministic repeat evidence;
- pinned physical embedding identity and secondary observed metadata.

A010 does not claim:

- lower FLOPs;
- lower energy or power;
- lower RAM use in bytes;
- lower hardware memory bandwidth;
- general latency superiority;
- general model-token savings;
- superiority over dense LLM architectures;
- open-domain reasoning superiority;
- biological efficiency;
- AGI or consciousness.

## 12. FlyWireLLM boundary

FlyWireLLM was untouched.

A010 does not import FlyWireLLM code, read or modify its checkpoints, restart
training, or use it as an embedding/generative model.

## 13. Closure candidate state

At this report stage:

- portable qualification: GREEN;
- physical qualification: GREEN;
- exact feature-branch CI: GREEN;
- primary outcome: `NOT_SUPPORTED`;
- GitHub Issue #10: OPEN;
- A010 repository status: ACTIVE;
- whole-branch review: pending;
- reviewed main integration: pending;
- exact final-main CI: pending;
- A011: PLANNED with no GitHub issue.

A010 must remain ACTIVE until review findings are resolved and reviewed behavior
is integrated into main with exact final-main CI evidence.
