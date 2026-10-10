# A011 — ASCA v0.x System Qualification

Date: 2026-10-10 (Asia/Bangkok).

Engineering result: `ENGINEERING_QUALIFIED`. Scope: `FULL_SYSTEM`; is_final=true; exit0. Fresh exact integration replay passed all18 mandatory gates and94 frozen checks;86 indexed artifacts were independently validated. Errors/blockers are empty.

This project-internal qualification is separate from five frozen research outcomes. The work adds a qualification layer over the existing system; it changes no cognitive source, frozen workload, threshold, model identity or research result.

## Exact source and CI

| Phase | Exact SHA | Evidence |
| --- | --- | --- |
| Activation base | `e8f75a862e0cb0d28b7e4efe25a77fa088ad646f` | [38042756382](https://github.com/funggier/FlyWireASCA/actions/runs/38042756382) success |
| Historical candidate | `f36080155957e30a0a9ab6be2270a67330a151e0` | [38048466684](https://github.com/funggier/FlyWireASCA/actions/runs/38048466684) success; historical full pack |
| Independent review head | `ba7b150cba8f4738415745678db5977f898dcde1` | [38048998834](https://github.com/funggier/FlyWireASCA/actions/runs/38048998834) success; review range starts at activation base |
| Repaired/qualified feature | `e96d71b033212668bc3ce98873903618c9c44bcf` | [38058426606](https://github.com/funggier/FlyWireASCA/actions/runs/38058426606) success; new full replay |
| PR13 checks | `e96d71b033212668bc3ce98873903618c9c44bcf` | [38058683663](https://github.com/funggier/FlyWireASCA/actions/runs/38058683663) success; PR merge checkout portable |
| Qualified integration/main | `f83bf1febbb6ac0bdcba3d8bf05dc8d437edc5ac` | [38058896880](https://github.com/funggier/FlyWireASCA/actions/runs/38058896880) success; independent new full replay |

[PR13](https://github.com/funggier/FlyWireASCA/pull/13) used merge_method=merge and retained all10 feature commits. Feature and integration Git trees agree at `a97c287539f7d44e765bb534017cb1f834e3d1e6`. Main was clean and exactly synchronized with origin/main (0/0) before/after qualification.

Later closure documentation/lifecycle-test commits are metadata. They receive their own exact main CI; the physical-qualified integration identity above is retained. This report's containing metadata SHA is discoverable with Git log for this path, rather than a self-referential SHA written into the file.

## Gate coverage

| Mandatory gate | Repaired feature | Integration/main |
| --- | --- | --- |
| P00_PROFILE_SOURCE | PASS | PASS |
| P01_TESTS | PASS | PASS |
| P02_ARCHITECTURE | PASS | PASS |
| P03_REPOSITORY | PASS | PASS |
| P04_A003 | PASS | PASS |
| P05_A008 | PASS | PASS |
| P06_A009 | PASS | PASS |
| P07_A010 | PASS | PASS |
| P08_FROZEN_AUDIT | PASS | PASS |
| P09_PACK_VALIDATION | PASS | PASS |
| H00_PREREQUISITES | PASS | PASS |
| H01_A004 | PASS | PASS |
| H02_A005 | PASS | PASS |
| H03_A006 | PASS | PASS |
| H04_A007 | PASS | PASS |
| H05_A009 | PASS | PASS |
| H06_A010 | PASS | PASS |
| H07_FULL_VALIDATION | PASS | PASS |

Portable replay covers full pytest, architecture/repository audits, A003/A008/A009/A010 and two independent frozen A008/A009/A010 observations. Local full replay freshly repeats portable qualification, then metadata preflight, A004/A005/A006/A007/A009 physical/A010 physical and completion/source/pack audit. Existing standalone CI gates remain present. CI makes no model calls.

## Fresh physical environment and provenance

| Field | Observed |
| --- | --- |
| hostname | `CDQ-P` |
| platform | `Windows-10-10.0.19045-SP0` |
| python_version | `3.14.6` |
| ollama_version | `0.32.15` |
| endpoint | `http://127.0.0.1:11434` |

| Model | Tag | Digest | Dimension |
| --- | --- | --- | --- |
| Terminal | `qwen3.5:4b` | `2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd` | null |
| Embedding | `qwen3-embedding:0.6b` | `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d` | 1024 |

A005 observed model and vector-health dimension are both1024; observed threshold is `0.5037018224299838` with physical_frozen_threshold_v1. Before/after runtime descriptors match. No pull, substitution, calibration, restart or hidden retry occurred.

| Replay | Source-before UTC | Source-after UTC |
| --- | --- | --- |
| Repaired feature | 2026-10-10T14:08:53.988647+00:00 | 2026-10-10T14:10:51.174476+00:00 |
| Integration/main | 2026-10-10T14:16:13.086883+00:00 | 2026-10-10T14:18:11.331635+00:00 |

## Preserved research evidence

| Milestone | Frozen/fresh outcome | Fresh roles | Indexed raw references |
| --- | --- | --- | --- |
| A006 | NOT_SUPPORTED | PHYSICAL_PRIMARY | `raw/H03_A006/output.json` |
| A007 | SUPPORTED | PHYSICAL_PRIMARY | `raw/H04_A007/output.json` |
| A008 | SUPPORTED | PORTABLE_PRIMARY | `raw/P05_A008/output.json` |
| A009 | SUPPORTED | PORTABLE_PRIMARY + PHYSICAL_SECONDARY | `raw/P06_A009/output.json`; `raw/H05_A009/output.json` |
| A010 | NOT_SUPPORTED | PORTABLE_PRIMARY + PHYSICAL_SECONDARY | `raw/P07_A010/output.json`; `raw/H06_A010/output.json` |

References above are relative to each full pack root. Historical reports/task provenance are separately retained in research_evidence.historical_refs; they are never relabelled as fresh replay. A006/A010 negative outcomes are valid evidence and do not turn engineering qualification into a scientific positive result. No ASCA intelligence score is defined.

## Frozen evidence audit

Profile: `asca-v0x-a011-v1`; SHA256 `add06f285bf6decc7d492b987d3769dc64db4cb3d0177c8c6586d50ee5f6d46d`. Exact reviewed7481 bytes match the independently literal anchor. Protected67 Git mode/path/blob identities match `8df49f05fe54de43667ab2f8ef5de2caae9376ffedf2cb8f8d26f0e4abcca6b6`. Qualification supports shallow history and Windows CRLF without fetching a historical baseline object.

| Milestone | Preserved fixture fingerprint |
| --- | --- |
| A006 | `e51fea2e58186e94d7affc964509e96d96fc656759677d7dcc073e5b36b91035` |
| A007 | `59f95ef115534fe24e59570cb281c0564ab75aadf364f4c26feba0d4078213c9` |
| A008 | `f52fbd4ab018386ff3cbfb62a68cc44a4b40e54ec4fd9a3b2e885dd2c5663fc6` |
| A009 | `2f92b5092de346f62879ac2cbb9f96d6de5d6f919e12d0693345c8228b01ab2a` |
| A010 | `69d20542cd1e7e5c25a0fb61b9060f622379206b519da3cec7624e00bb6e5d4c` |

| Portable milestone | Preserved full semantic SHA256 |
| --- | --- |
| A008 | `4883b4eba174a2edc8c753297e02903c940f0b0fc38a71f80d5b76541b49e7c3` |
| A009 | `5fb0c8b803b0c15888907ca388aa8f705d904351a9f23da43cdf7a285c9052b7` |
| A010 | `8e57b744e96294565551061728ff90b4ddba43b66051237124378f981db185d5` |

Only optional top-level note is excluded from portable semantics. Case order/IDs, execution identities, unknown fields, counts and sentinels remain audited. Policy identities are preserved: EVIDENCE_ONLY, SINGLE_BEST, SIGNAL_DRIVEN, CHUNKED, MISMATCH_DRIVEN_RECOVERY; max_procedure_attempts3; hidden_automatic_retry0.

A010 retains12 total cases /9 primary cases and all ablations:

| Primary metric | ASCA | Dense |
| --- | --- | --- |
| Successes | 7 | 8 |
| Queries | 28 | 27 |
| Scored vectors | 1984 | 1440 |
| Cumulative selected | 66 | 480 |
| Peak selected | 12 | 256 |
| Procedure attempts | 14 | 9 |

Shared successes7; dense-only1; ASCA-only0. Dense-only sentinel `selective-routing-miss-sentinel`: ASCA_PRIMARY=false, DENSE_EXHAUSTIVE=true. The original ASCA_ALWAYS_MAX_SCOPE ablation remains in complete raw evidence and the semantic digest. No fixture, cue, threshold, sentinel or retrieval retuning occurred.

## Independent whole-change review and verified repair

Native implementation plus one completed fresh-context independent reviewer `/root/a011_whole_change_review_resumed` (gpt-6-astra/high). Exact range `e8f75a862e0cb0d28b7e4efe25a77fa088ad646f..ba7b150cba8f4738415745678db5977f898dcde1`. First attempt ended at usage limit without findings; the resumed reviewer completed the review. Critical0 / Important2 / Minor0. Declined to judge: none. Root retained both Important grades.

- I1: qualification accepted missing A005 benchmark or missing/contradictory A009/A010 physical details despite success flags. Require actual emitted structures, strict acceptance primitives, original legacy acceptance and summary/metadata agreement.
- I2: confirmed transport loss after version/tags but before /show fabricated dimension drift from an unobserved null. Retain an explicit transport-loss observation, classify absence as BLOCKED, and preserve observed wrong-digest/malformed-response FAIL precedence.

One author TDD fix pass: 21 failed, 2 passed, 55 deselected in13.12s -> 78 passed in43.71s; 952 passed in77.72s. Independent review tests: 398 passed in66.41s. Architecture/repository/whitespace PASS. No second independent review is claimed. Regression tests cover adapter detail mutations, final full-pack publication and partial metadata loss/mixed hard failures.

The actual historical f360801 physical details were present/consistent; the review defects do not establish a failed historical run. That pack was retained and was not reused to qualify repairs or main. Fresh repaired-feature and integration packs above are the applicable qualification evidence. No cognitive defect was found that required an out-of-scope repair.

## Retained pack locations and hashes

Full packs are outside both checkouts and remain distinct:

Repaired feature: `T:\Space\Projects\ProjectsAI\FlyWireASCA-qualification-evidence\a011-e96d71b-reviewed-1791641331086`.

Integration/main: `T:\Space\Projects\ProjectsAI\FlyWireASCA-qualification-evidence\a011-f83bf1f-main-1791641770439`.

| Full pack | File | SHA256 |
| --- | --- | --- |
| Repaired feature | artifact-index.json | `daffd0300237d5e07ccb26eeb9b386fde2eb0cf697bbd199d702ef465ffca14c` |
| Repaired feature | qualification.json | `4c831003728604e9efca81ad0d7d5d2e74eec2b4bd7b52e6f5af9ed5c3cf155d` |
| Repaired feature | qualification.md | `76d675ddb7819052db2ffe2f3649cab55349fb1f585c8f4cea42c98a641ece98` |
| Integration/main | artifact-index.json | `0685306d087395c679c165369b0547c4ca610068e54b2972633555c9904509fa` |
| Integration/main | qualification.json | `73491f44d1feb0d1d19b4adb4a20ed5d8684e4cc651d771e11c70afed4a8d6cc` |
| Integration/main | qualification.md | `304e20b8c2f364891d2c47f7470f5ead69378e37ff9ed7e1c04166f9c2f2f908` |

Each pack retains profile.json, source snapshots, runtime/preflight.json and runtime/completion.json, per-gate stdout/stderr/process/output/validation evidence, frozen repeat observations and artifact-index.json. Manifest/report/index are publication metadata;86 raw/profile/source/runtime artifacts are indexed. Readback verified strict manifest, artifact hashes/links, raw acceptance and completed gate coverage.

| Portable CI | Artifact ID | Raw artifacts | Finality |
| --- | --- | --- | --- |
| [38058426606](https://github.com/funggier/FlyWireASCA/actions/runs/38058426606) | 11671998484 | 52 | PORTABLE_ONLY; is_final=false; verdict=null |
| [38058896880](https://github.com/funggier/FlyWireASCA/actions/runs/38058896880) | 11671649254 | 52 | PORTABLE_ONLY; is_final=false; verdict=null |

| CI pack | File | SHA256 |
| --- | --- | --- |
| 38058426606 | qualification.json | `e75853c42ef73691e7001f6dd227def768ce4241ffe400b8367783fc12601d3a` |
| 38058426606 | qualification.md | `794dd53bc3b6d1392079db6e2171ef53fb287afc92722234246fcdd08de13c68` |
| 38058426606 | artifact-index.json | `92efa24be3068d71828a31e5f9eff1552359e843321484dfcd6dda89aad57741` |
| 38058896880 | qualification.json | `79d4e348d511ce12ee28b845a90d2d04557fd235b9ec813b882fdc9a214517de` |
| 38058896880 | qualification.md | `f728e4b641e2bf4ec41e4be0cdf4a0eed5b13bba55ef4abf25e57a6019b0c399` |
| 38058896880 | artifact-index.json | `bce1a57ea19b52a6cc61c162b9701e0f0a6e22f97fea4fc5616aa755e009d1bc` |

Both CI archives were downloaded and independently decoded/hash/coverage/source audited, with10 PASS gates and34 frozen checks each. CI evidence does not replace physical replay.

Execution/review/raw audit logs and all13 ordered rulings remain at `T:\Space\Projects\ProjectsAI\FlyWireASCA-worktrees\a011-asca-v0x-qualification\.superpowers\sdd\2026-10-10-a011-asca-v0x-qualification`. Their exhaustive decisions/costs are copied into the final session handoff. Deferred minors: none. The feature branch/worktree and failed injected diagnostic packs are preserved; no cleanup destroys evidence.

## Closure and claims boundaries

Engineering implementation/integration and physical evidence gates are complete. At this report's first publication, GitHub Issue12 completion is pending the closure metadata commit's exact main CI. The live completion response is recorded in the final handoff after that gate; no requested GitHub operation alone establishes CLOSED.

*GitHub completion verified:* Issue12 CLOSED/COMPLETED at `2026-10-10T14:33:14Z`; independent live fetch confirmed. Closure metadata `4053cb42bb50a683965d83bee20cbffb25668f02`/[38059824196](https://github.com/funggier/FlyWireASCA/actions/runs/38059824196) SUCCESS; main clean/exactorigin0/0.

[Full session handoff](ASCA-20261010-full-session-handoff-a011-completed.md) records the exhaustive rulings, approvals and resume instructions. Its containing metadata SHA/own exact CI are resolved from Git/live state after publication.

PRE-A011 remains DONE / Issue11 CLOSED-COMPLETED; A001-A010 remain DONE. Package version remains `0.1.0.dev0`. No FlyWireLLM change, A012, tag/release or0.1.0 promotion is part of this work.

Declared pack boundaries:

- Project-internal qualification of the declared ASCA v0.x profile.
- A006-A010 research outcomes are reported separately by milestone.
- No external certification or aggregate intelligence/performance claim.

Local timings are descriptive; qualification does not establish hardware FLOPs, energy/power, general latency improvement, broad intelligence or external certification. A future change or milestone requires its own explicit scope/design approval and applicable fresh evidence.

Closure verification: lifecycle RED2 failed/14 passed -> GREEN16; explicit publication-gate layout preserved the original external closure requirement. Repository guard RED1/951 exposed unfinished engineering-checklist presentation; reconciled ledger/repository37 PASS and full952 PASS in79.42s. Existing repository qualifier/assertions remain unchanged. Architecture/repository/cached whitespace PASS; exact closure metadata main CI is required before GitHub completion.
