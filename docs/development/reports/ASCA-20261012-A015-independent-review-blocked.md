# A015 independent whole-branch review — BLOCKED

Date: 2026-10-12 (Asia/Bangkok).
Reviewed BASE4ca246df6976c7aa21ad07826017f167f0ee27da..HEAD5b33baaf9f9e3978fc3e15261ef7fdc0e7ac6ebe.
Method: independent fresh-context subagent review under selected Native workflow.
No Critical or Minor findings. Six Important findings block integration.

1. interpretation.py153-167 drops subsequent thresholds, explicit semicolon,
   simultaneous format/sum and descending modifiers while returning VERIFIED.
   Independent development examples: keep2,5,8,12 above3 and below10 returns
   [5,8,12]; reversing threshold order returns[2,5,8]; semicolon formatting
   returns comma. Remedy: preserve every recognized constraint or stop honestly.
2. verification.py258-277 single-output transform accepts extra_claim alongside
   value22 and renderer publishes it as verified. Remedy: closed permitted output
   shape including deliberate scalar/raw-map representations.
3. controller.py103-122/direct.py96-106 can publish success after cancellation or
   deadline arriving during rendering. Remedy: explicit synchronized final
   publication arbitration; one coherent terminal result/trace.
4. evidence.py139-141/196-212 accepts a resealed forged terminal execution ID or
   unresolved observation_ref. Remedy: resolve every execution/control/candidate/
   observation/receipt link, ordering and uniqueness; exact matching terminal
   verification and independent recovery provenance.
5. evidence.py119-212 accepts resealed fabricated retrieval/vector counters and
   invented rendered answers. Remedy: derive supported counters from raw event/
   snapshot records, keep unavailable work unknown, and rerender publication.
6. Frozen prompts.py5/18-21 omits strict source union, group key/select fields and
   relation-path data shape required by parsers. Portable scripted proposals use
   internal interpreter knowledge and do not establish full model-facing schema.
   Remedy: preserve v1; corrected full wire contract requires a disclosed new
   freeze/version and affected qualification, never silent prompt tuning.

Reviewer ran88 focused tests, both audits, G2 freeze and A01167-path guard; all
passed. No src/flywire_asca or pyproject changes. Original384 records inspected:
unified138 solvable successes, zero genuine recoveries; direct192 INVALID_PLAN
and192 invocations. Reviewer made no project/Git/evidence changes.

Declined to judge: causal model capability/prompt omissions; independent upstream
GGUF tokenizer proof reconstruction; full suite (root owns it); pending main CI,
release assets and Issue closure. Root must rule separately before integration.

Root full suite at5b33baa:1381 passed/49 clone setup errors. Exact GitHub CI
38262031184 passed. Failure root cause: Windows test clones of newly tracked
long snapshot paths do not inherit repo-local core.longpaths. Actual existing
failures serve as regression evidence; explicit clone config is being corrected.

A015 remains ACTIVE, review BLOCKED. First5 defects are in the single Native
fix pass, with independent development RED->GREEN. Finding6 needs a concrete
written v2 contract/context-fit amendment and review before frozen protocol
changes. Existing v1 evidence and conclusions are historical observations with
these review limitations; they do not qualify corrected behavior. No model
inference, new frozen inputs, merge, Issue closure or release is authorized by
this report.

## Consolidated Native fix verification

The first five Important findings are corrected and verified through development
RED→GREEN regressions. The sixth stays BLOCKED for the complete v2 wire/protocol
amendment. This is one consolidated author fix pass; the executing-plans workflow
does not dispatch a second reviewer for the same covered corrections.

| Finding | Corrected behavior | Reproduced regression |
| --- | --- | --- |
| 1 semantic clauses | All recognized numeric thresholds retained; named/quoted separators exact; unsupported descending and format-plus-sum stop honestly | compound filters EN/TH, semicolon, tab and quoted separator, unsupported modifiers, model-dropped threshold |
| 2 extra output claims | Single-output mapping has exactly its permitted output key or equals the trusted raw map | extra_claim candidate fails verification and does not render as verified; direct proposal rejects |
| 3 publication race | Builtin cancellation serializes with terminal publication; cancellation/deadline rechecked after rendering | cancel/deadline during render in unified/direct; concurrent cancel observes committed terminal |
| 4 execution provenance | Every action observation resolves with exact run/execution/step ownership; receipt/plan/context/state replay; exactly one terminal matching verification | rebuilt evidence with forged execution or unresolved observation fails |
| 5 cost/answer replay | Counters derive from raw events/references, vector eligibility derives from public documents; unknown usage flagged; exact verified rendering replay | rebuilt zero retrieval/vector counters and invented answer fail; counter+reported+trace zero vector work also fails |

Returned embedding token usage is retained even when its identity is rejected.
Unknown embedding or scoring usage remains unavailable. Builtin Cancellation
provides cross-thread publication arbitration; a third-party cancelled()-only
token supplies a final poll without a synchronization contract for its writer.

Actual Native checks on CDQ-P after the last separator correction:
python -X utf8 -m pytest -q ->1454 passed in227.09s.
Both architecture audits, repository qualification, A003/A008/A009/A010 portable
checks, A01167-path preservation, A012/A013/A014 portable qualification,
A014 offline evidence replay, unchanged A015 G2 freeze, A015128-trial scripted
engineering qualification and historical v1 replay all returned exit0.
A015 portable retains46/48 unified and43/48 direct solvable completions, zero
false successes; scripted results are not physical comparison evidence.

Windows regression history: the original49 clone errors were reduced to11
checkout errors plus5 false source-gate failures. Read-only reproduction in a
failed temporary clone showed normal Git status reporting long files changed,
while git -c core.longpaths=true status was clean. Git clone now persists
core.longpaths=true through its own -c option, including the shallow provenance
fixture; later status checks use the same setting. Protected production source
and frozen A011 profile remain unchanged. Final full suite is GREEN.

Historical replay checks the exact preserved payload8036befc and behaviorc968330
in a detached temporary local clone with the original verifier. It returns
VALID_UNDER_ORIGINAL_V1_CONTRACT and current_source_qualified=false. Current
evidence verification keeps strict source equality and stronger replay; no
legacy source omission or identity waiver is used to make old evidence pass.

Final/current physical qualification, complete v2 wire contract, approved
new freeze/settings, final integration/main CI, Issue#19 closure and release
remain unfulfilled. A015 stays ACTIVE and integration remains BLOCKED.
Written v2 review: [complete contract and context amendment](../../superpowers/specs/2026-10-12-a015-v2-wire-contract-design.md).
That static proof admits0/64 at8192 and64/64 at12288; no new inference has run.

## Root rulings on declined review scope

Causal model capability and prompt-omission attribution remain unclaimed:
v1 observations do not isolate those causes; a separately approved complete
protocol is required. Upstream tokenizer proof reconstruction is not claimed;
root reproduced the frozen conservative method and all64 v1 bounds, with an
explicit v2 admission gap. Root owns and completed the full suite and portable/
preservation checks; exact feature CI is checked after commit. Main, release
assets and Issue closure remain outside this unintegrated checkpoint.

No Critical or Minor findings were reported, so no deferred minors exist.
