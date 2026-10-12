# A015 — Unified Agent Runtime Stage A qualification

Date: 2026-10-12 (Asia/Bangkok).
Status: physical evidence verified; A015 ACTIVE pending independent whole-branch
review and authorized integration. Engineering acceptance and research preference
are separate. No Stage B/C or new milestone activation.

## Result

The source-bound physical comparison is valid and usage-complete. Its frozen
ordered decision is **UNIFIED_RUNTIME_NOT_SUPPORTED** because the unified runtime
demonstrates zero genuine successful recovery. It correctly completes 138/144
solvable trials, but 36 controller recovery rounds are not evidence of a successful
recovery following a real prior failed observation with meaningful context/plan
change. No behavior, prompt, budget, corpus or oracle was tuned after the result.

The direct pinned-model baseline completes 0/144 solvable trials and returns
INVALID_PLAN on all 192 requests. These are protocol-compliance failures retained
with raw model outputs, not a finding that the model knows no answers. Sample
outputs echo schema descriptors, introduce extra top-level keys or supply invalid
intent/task/span structures. The direct runner rejects them under the shared
closed contract; no hidden repair or extra model call was applied.

## Authority and artifacts

- Repository: funggier/ProjectASCA; Issue [#19](https://github.com/funggier/ProjectASCA/issues/19).
- [Approved design](../../superpowers/specs/2026-10-12-a015-unified-agent-runtime-design.md), commit cccbf0fc47ca301bef8a6b7ac25398c2e1eb4447.
- [Approved plan](../../superpowers/plans/2026-10-12-a015-unified-agent-runtime.md), commit 4ca246df6976c7aa21ad07826017f167f0ee27da; user selected Native.
- [Task](../tasks/A015-unified-agent-runtime.md) and [architecture](../../architecture/A015-UNIFIED-AGENT-RUNTIME.md).
- G2 freeze commit 7fc3c0ea901bfe49f9e788065bfc7de3626c0984, aggregate 774bc3352242bee5cb588f499f6597a264c67f612feb518828058dc4c1efa882.
- G4 behavior commit c968330cf97d7a7c7893aa70fddd150ce8dd510e.
- [G4 CI 38247841795](https://github.com/funggier/ProjectASCA/actions/runs/38247841795), SUCCESS.
- Source 124 file mode/path/blob fingerprint e5d6f1f08735b8292b05bbf4b40135995af2c62b17e927a6d78c73ddd03c375b.
- [Complete physical evidence](../qualification/a015-agent-runtime-physical-v1.json).
- Payload SHA256 8036befcd0532b59e047ca6fb5c78b5f9a4f6895b2a84bad97b4ee26fc0241ad.
- Physical run ef3cc907-b320-4b5d-bf0b-45a23aed8f54:19:21:33 to20:46:51 Asia/Bangkok,2026-10-12.
- Complete reference snapshots and final same-run partial checkpoint are retained.
  The partial checkpoint remains INVALID/INCOMPLETE and is not a second run.
- Offline verifier recomputes source, hashes, ownership, goal/state checks,
  counters, denominators, raw verdicts and the decision. Fresh validation:
  valid=true, physical=true, usage_complete=true, trials384, errors[].

## Protocol and environment

Exactly32 bilingual semantic pairs /64 ordinary-text requests, three fixed
seed-0 repetitions,192 requests/variant and384 total. Pair/variant first-order
alternates by pair index and repetition. Every request starts fresh state/run
ownership. Both variants receive the identical complete public information;
runtime selects context while the direct baseline gets the complete public
payload and one generation. Private case IDs/families/expected values never enter
the runtime request or public configuration.

CDQ-P: Windows 10 build19045, Intel Core Ultra 5 245K, installed RAM34359738368
bytes, Python 3.14.6, Ollama 0.32.15. Pinned generation qwen3.5:4b digest
2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd;
embedding qwen3-embedding:0.6b digest
ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d,
dimension 1024. Fresh pre/post identity probes agree. Temperature 0, seed 0,
thinking=false and generation context8192. All complete direct prompts satisfy
the conservative bound: max 7145 prompt tokens +1024 output allowance=8169.

Unified allows at most 4 calls /2048 output tokens per run, while the direct
baseline allows1 call /1024 output tokens. This asymmetry is disclosed; observed
calls are reported separately. Query embeddings and index setup are real
inference costs, even when unified generative calls are zero.

## Completion and non-success results

| Metric / three repetitions | Unified | Direct |
| --- | ---: | ---: |
| Cost requests, all outcomes included |192|192|
| Correct solvable completions |138/144|0/144|
| English solvable completions |69/72|0/72|
| Thai solvable completions |69/72|0/72|
| Correct applicable answers |90/90|0/90|
| Correct applicable final state |48/54|0/54|
| Correct non-success controls (includes bounded failures) |48/48|0/48|
| Correct bounded failures |24/24|0/24|
| Published successes |138|0|
| False successes |0|0|
| Accepted invariant failures |0|0|
| Controller recovery rounds |36|not applicable|
| Genuine successful recoveries |0|0|
| Paired unified-only / direct-only successes |138|0|

False-success fraction is0/138 for unified; direct has no published success,
so its fraction is not applicable. A zero raw false-success count does not mean
direct succeeds. Non-success controls include12 clarification,12 unsupported
and24 bounded failures. Solvable-family results per language across repetitions:

| Family | English unified / direct | Thai unified / direct |
| --- | --- | --- |
| Simple |12/12 /0/12|12/12 /0/12|
| Factual |12/12 /0/12|12/12 /0/12|
| Relation |12/12 /0/12|12/12 /0/12|
| Procedure |12/12 /0/12|12/12 /0/12|
| Recovery-designated |9/12 /0/12|9/12 /0/12|
| Composition |12/12 /0/12|12/12 /0/12|

Each repetition is identical in these completion counts: unified46/48 and
direct0/48, with unified16/16 controls and8/8 bounded failures. Pair20 (required
reinforced packaging for order O2) stops NO_PROGRESS in both languages in all
three repetitions. The other recovery-designated completions lack the qualifying
prior failure/change chain, so they remain correct completions with genuine
recovery=false. No task was repeated outside the frozen schedule.

## Cost and timing, including rejected work

| Metric / all 192 requests per variant | Unified | Direct |
| --- | ---: | ---: |
| Actual generative invocations |0|192|
| Actual generation transport dispatches |0|192|
| Reported prompt tokens |0|358653|
| Reported output tokens |0|46976|
| Combined generative tokens |0|405629|
| Query embedding calls / inputs |216/216|not applicable|
| Query embedding prompt tokens |9015|not applicable|
| Actual retrieval queries |216|not applicable|
| Vectors scored |564|not applicable|
| Relation invocations / scanned edges |42/66|not applicable|
| Relation visit events / sum per-run unique nodes |102/66|not applicable|
| Strategy validation attempts |144|0|
| Primitive attempted / executed actions |213/207|0/0|
| End-to-end client wall total, seconds |39.223591|4909.774348|
| Median request client wall, seconds |0.201781|25.165493|
| Request wall range, seconds |0.000509-2.767868|13.289802-75.353972|

The six denied model proposals are preflight denials, not generation invocations.
The direct baseline's192 rejected proposals retain all reported tokens and time.
The sum of run context peaks (990 items /448248 bytes) and artifact peaks
(2314218 unified /1560120 direct bytes) are cumulative per-request statistics,
not one run's peak, simultaneous process RAM, or hardware memory savings.

Unified exclusive phases, seconds: RECEIVED 0.036147, INTERPRETING 0.169067,
ACQUIRING 38.246416, RESOLVING 0.128448, EXECUTING 0.280468,
OBSERVING 0.031584, VERIFYING 0.270886, RECOVERING 0.020564,
MODEL_ASSIST 0.002227. Query embedding nested wall span 37.791798 seconds is
reported separately and must not be added again to exclusive phase totals.
Control-ledger end-to-end totals39.194057 /4909.753209 differ slightly from
independently measured caller wall totals because the harness boundary differs.
Direct model-assist span 4909.608789 seconds is nested/descriptive.

Setup is excluded from task costs: cold-index client span 6.922926 seconds;
65 public document embeddings across2 calls (57 + 8 inputs),1445 prompt tokens;
common warm-up4.537835 seconds includes1 generation 17 prompt/10 output tokens
and1 embedding 8 prompt tokens. The earlier generic setup probe (wrong
render-only flag) adds1 generation 23 prompt/1 output token outside the primary
denominators. Residence before setup was empty; after warm-up both models were
resident, size_vram0. Backend load/eval durations and per-response settings remain
in raw artifacts; they are descriptive and not added to client wall measurements.

## Budgets, verification and claims boundary

All admitted work retains the same ledger and immutable goal. Limits include
six retrieval queries, three context rounds,24 items/16384 bytes of working
context, three relation invocations with 24 visits/96 edges, three strategy
validations, two recovery rounds,96 primitive executions,64 transitions,
256 trace events/262144 trace bytes and180-second deadline per unified request.
Expected bounded failure/preflight denial is distinct from a budget violation.
All accepted invariant failure counts are zero. Direct context-management counts
are not applicable; complete-public prompt visibility is recorded instead.

Stage A executes only PURE and IN_MEMORY capabilities. Request-driven file,
process, application, network, messages and persisted learned procedures are not
enabled. Configured local model/embedding inference is infrastructure. Ordinary
text support applies to the closed Stage A public-domain schemas; this is not a
general conversation agent or production deployment qualification.

Portable engineering replay is scripted and separate from physical evidence:
128 trials, unified46/48 versus direct43/48 correct solvable, controls16/16 and
bounded failures8/8 each, zero false success each. Portable response/token values
are test data. Meaningful changed-context/changed-plan recovery is demonstrated
by independent development/fault tests; physical success in recovery is absent.
No universal efficiency, FLOPs/energy, biological, AGI, real-effects replay or
general Qwen capability conclusion follows.

A006 NOT_SUPPORTED, A007/A008/A009 SUPPORTED, A010 NOT_SUPPORTED, A012
EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED, A013 SIGNAL_GATED_RELATION_JUSTIFIED
and A014 HYBRID_STRUCTURAL_ROUTING_JUSTIFIED remain historical conclusions.
A011 protects all 67 paths, profile
add06f285bf6decc7d492b987d3769dc64db4cb3d0177c8c6586d50ee5f6d46d and
mode/path/blob hash 8df49f05fe54de43667ab2f8ef5de2caae9376ffedf2cb8f8d26f0e4abcca6b6.
Release v0.1.0 tag object 0d2b2ebd0882d2b5e950b56e227cb4a0c5de898e,
peeled fd8d298c38625b2bcfc2073fa3c8f951415a9bb2 and assets are retained.
FlyWireLLM was not accessed or modified.

## Engineering gates and next action

G4 suite 1427 and exact CI 38247841795 passed before physical generation.
Evidence/mandatory offline CI addition: full suite 1428 passed in171.02s;
both architecture audits, G2 freeze, repository preservation and whitespace
checks passed. Evidence commit `42d7dffd4eca3d41245cb875e9b3781a92111566`; [evidence CI 38261192267](https://github.com/funggier/ProjectASCA/actions/runs/38261192267) was running at draft time. Subsequent review commits and exact CI are recorded in
the task checkpoint and integration handoff.

A015 remains ACTIVE until independent whole-branch review, final branch
qualification, the user's integration path, exact main/closure CI and live
Issue closure. No merge, release or next milestone is implied by the valid
negative physical result.
