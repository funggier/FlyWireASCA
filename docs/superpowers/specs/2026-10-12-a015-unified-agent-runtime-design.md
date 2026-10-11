# A015 — End-to-End Unified Agent Runtime Design

Date: 2026-10-12 (Asia/Bangkok)
Repository: `funggier/ProjectASCA`
Milestone: A015
Architecture direction: Approach 3; new top-level runtime
First qualification: Stage A; long-term target: Stage C
Document status: WRITTEN_SPEC_REVIEW
Conversational design: approved by the user on 2026-10-12
Written-spec approval: not yet granted
Task/Issue activation: NOT ACTIVATED
Implementation plan: not written

## 1. Purpose and approval boundary

A caller submits ordinary Thai or English task text. The runtime interprets the
task, acquires relevant knowledge, selects or composes a strategy, executes it,
observes the result, recovers within budgets, and returns a verified terminal
result. The caller does not prepare internal policies or identifiers.

The user has approved Approach 3 and the detailed conversational design. This
document records that design with precise contracts. It does not activate A015
or authorize implementation.

The next gate is approval of this written spec. Only then may an implementation
plan be written. Task/Issue/feature-branch activation and implementation require
the later approved plan and its explicit activation step. There is no A015 Issue
number reserved by this document.

### 1.1 Research question

Can a new unified Stage A runtime preserve or improve task completion relative
to direct pinned `qwen3.5:4b`, reduce unnecessary generative-model dependence,
and keep retrieval, relation, execution, and recovery work bounded?

A valid mixed or negative result must remain publishable. Engineering validity
and research preference are separate decisions.

### 1.2 Product stages

| Stage | Capabilities | Approval scope |
| --- | --- | --- |
| A | Internal factual/relational reasoning, deterministic transformations, stored procedures, bounded in-memory simulation | This design |
| B | Read-only grounded external capabilities | Later milestone and design gate |
| C | Authorized real tool/action effects, durable effect tracking and recovery | Later milestone and design gate |

Stage A may use configured model/embedding inference services as infrastructure.
It does not expose arbitrary networking or real application/OS mutation to a
request or model-generated plan. It does not write files, control processes,
send messages, issue write APIs, or persist learned procedures during a run.
Qualification harnesses may save evidence outside the runtime.

Stage A supports declared task semantics and capabilities. It does not promise
universal open-world understanding or arbitrary-task completion.

## 2. Live design baseline and preservation

Live Git/GitHub/runtime observations made before writing this spec:

- checkout: `T:\Space\Projects\ProjectsAI\ProjectASCA`;
- local/main and GitHub/main:
  `4dca5edb24c1b64a5999f09f0fc36a5d2197c06a`;
- local working tree: clean; ahead/behind: 0/0;
- exact main CI: `38159635788`, success;
- A014 Issue #18: closed, state reason completed;
- CURRENT: A014 / DONE; ROADMAP: A001-A014 DONE; no open Issues;
- Ollama: `0.32.15`, available on the user's machine;
- generative model: `qwen3.5:4b`, digest
  `2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05ee4eefd`;
- embedding model: `qwen3-embedding:0.6b`, digest
  `ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d`,
  dimension 1024.

These observations are a design baseline, not evidence that A015 exists or has
been qualified.

### 2.1 Preserved release and frozen source

The annotated `v0.1.0` tag must remain unchanged:

- tag object: `0d2b2ebd0882d2b5e950b56e227cb4a0c5de898e`;
- peeled commit: `fd8d298c38625b2bcfc2073fa3c8f951415a9bb2`.

Release assets, checksums, historical reports and archived filenames remain
preserved. No tag move, release replacement, version promotion, reset, clean,
rebase or force-push belongs to A015.

The A011 preservation verifier must retain:

- frozen profile SHA256:
  `add06f285bf6decc7d492b987d3769dc64db4cb3d0177c8c6586d50ee5f6d46d`;
- protected path count: 67;
- protected mode/path/blob SHA256:
  `8df49f05fe54de43667ab2f8ef5de2caae9376ffedf2cb8f8d26f0e4abcca6b6`.

Preservation of A011 does not qualify current HEAD or the new runtime as A011.
FlyWireLLM is outside the work; no files, imports, checkpoints or processes of
that project are accessed or modified.

### 2.2 Historical state versus current state

The direction handoff's `7d139bd0f76d5ce40ef280f795c5f4968d9d5fb1`
describes the pre-release handoff. Release preparation subsequently produced the
preserved `fd8d298...` baseline. Repository-identity maintenance produced the
current `4dca5ed...` main. The changes from the preserved release to that main
are README and the repository rename report, not cognitive source changes.

The old repository name and local path in historical documents identify the
project at those times. The pre-A011 snapshot is historical rather than a
current task ledger. Neither is globally rewritten.

See [repository rename record](../../development/reports/ASCA-20261012-repository-rename-projectasca.md)
and [direction handoff](../../development/reports/ASCA-20261011-full-session-handoff-post-a014-a015-unified-agent-runtime-direction.md).

### 2.3 Historical conclusions

| Milestone | Conclusion retained |
| --- | --- |
| A005 | VECTOR_SUFFICIENT |
| A006 | NOT_SUPPORTED |
| A007 | SUPPORTED |
| A008 | SUPPORTED |
| A009 | SUPPORTED |
| A010 | NOT_SUPPORTED |
| A011 frozen v0.x | ENGINEERING_QUALIFIED |
| A012 | EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED |
| A013 | SIGNAL_GATED_RELATION_JUSTIFIED |
| A014 | HYBRID_STRUCTURAL_ROUTING_JUSTIFIED |

A001-A004 completion and evidence also remain unchanged.

A010's frozen ASCA/dense results were 7/8 successes, 28/27 queries, 1984/1440
vectors scored, 66/480 cumulative selected items and 12/256 peak selected items.
Smaller active context did not establish lower total retrieval work.

A014's frozen bilingual physical workload produced 32/32 downstream successes
for both hybrid and model-only. Hybrid used 9 rather than 32 model calls, with
zero false/missed activations; model-only had two false activations. Those
results motivate this research question without establishing an A015 result.

## 3. Source-grounded architecture decision

The existing components provide useful primitives but do not own the desired
human-facing end-to-end contract:

- A009 `CognitiveLoopRequest` requires prepared familiarity, root procedure and
  policies. Its recovery follows prepared retrieval scopes. Its terminal model
  is diagnostic and cannot change deterministic termination.
- A014 `run_structural_routing` accepts query text and infers StructuralNeed;
  it does not select or execute an end-to-end strategy.
- A013 `TargetFreeRelationIndex.expand` provides bounded relation expansion
  without expected target IDs.
- A008 `run_procedure` verifies steps and child CALL completions. The root's
  COMPLETED status is not an independent check of the user's overall goal.
- The current architecture auditor enumerates legacy packages and their
  dependencies. It does not yet cover a second public namespace.

A015 therefore owns a new controller. It does not call A009
`run_cognitive_loop` as its orchestration center or alter that function's
qualified meaning. New adapters compose lower-level components.

## 4. Namespace and package boundaries

The new public namespace is:

`project_asca.agent_runtime`

The future source root is `src/project_asca/`. This document creates no package
scaffold. The existing `flywire_asca` namespace, `FlyWireASCA` distribution
identity and `0.1.0.dev0` metadata remain preserved. The current setuptools
source discovery can include both namespaces; no distribution rename or release
is required by A015.

The runtime is model-agnostic through ports. The physical experiment pins Qwen;
the model is not a mandatory core dependency.

| Unit | Owns | Depends on |
| --- | --- | --- |
| contracts | Immutable request/result, goals, evidence, plan and state types | Standard library |
| budgets and trace | Reservation ledger, deadlines, compact event evidence | Contracts |
| interpretation | Intent proposals, request bindings, GoalContract compilation | Contracts, trusted task schemas, ModelBroker port |
| context | Query construction, evidence coverage, bounded context assembly | Contracts, retrieval/routing/relation ports, ledger |
| strategy | Catalog compatibility, stored/composed plan resolution | Contracts, context, capability descriptors, ModelBroker port |
| execution | Plan validation, attempt lifecycle, action dispatch | Contracts, capability/execution ports, ledger |
| observation and verification | Observation integrity, result/postcondition checks | Contracts, trusted semantic validators, snapshot/evidence ports |
| recovery | Typed deficit analysis and bounded progress decisions | Contracts, ledger, prior context/plan/observation evidence |
| controller | Finite-state orchestration and terminal latch | The above units through their interfaces |
| adapters | Translation to qualified legacy primitives and physical transports | Explicit legacy allowlist |

Conceptual responsibilities may occupy multiple focused modules. A single
monolithic controller file is not an acceptable substitution for these
boundaries.

### 4.1 Dependency rules

- Legacy packages never import `project_asca`.
- Core runtime units depend on ports; legacy imports are concentrated in
  adapters.
- Allowed legacy primitives are contracts, familiarity, model, embedding,
  vector_memory, selective_activation, uncertainty_expansion where applicable,
  procedural_memory, relational_activation and structural_routing.
- Relation semantics may be imported from contracts. A012's target-aware
  benchmark traversal is not a runtime dependency.
- New runtime code does not directly import qualification, baseline_comparison,
  benchmark/evaluator modules or A009 controller code. Adapters bind explicit
  primitive/contract symbols from leaf modules.
- No runtime dependency on FlyWireLLM, LConnect, BConnect, shell/process-control
  libraries or an arbitrary HTTP-action executor.
- Future architectural-audit work must cover both namespaces, relative/absolute
  imports, reverse dependencies, undeclared edges and cycles. Existing legacy
  rules and frozen-source checks remain enforced.
- Implementation changes to audit infrastructure require their own regression
  checks. This spec does not change that infrastructure now.

Several current legacy package __init__ files re-export benchmark builders and
constants. Python initializes those packages even for leaf imports. This known
incidental module loading is not described as oracle isolation by module
absence. Frozen initializers are not rewritten to hide it. Adapters must not
bind/call benchmark builders, read expected IDs/labels, introspect benchmark
modules or use their fixtures as runtime configuration. The audit distinguishes
new direct dependencies from these preserved initialization edges; behavioral
leakage controls verify no forbidden fixture/oracle access occurs. The new A015
oracle/evaluator namespace is never re-exported by the runtime namespace.

## 5. Public contracts

The ordinary-text convenience API is conceptually:

`runtime.run(text) -> AgentResult`

The equivalent typed input is `AgentRequest`. Unknown request fields are
rejected rather than ignored.

### 5.1 AgentRequest

| Field | Contract |
| --- | --- |
| text | Nonblank Unicode string; original text preserved; at most 8192 UTF-8 bytes |
| request_id | Optional nonblank opaque correlation identity; generated if omitted |
| language_hint | Optional en/th; omission requires no caller language choice |

Normalization keeps a mapping to original text spans. Request IDs and language
hints never select benchmark behavior, strategy IDs, routing policies or gold
answers. Mixed-language requests may be interpreted using the supported schemas.

Forbidden public controls include StructuralNeed, relation types, procedure IDs,
retrieval/recovery/internal policies, expected target/answer IDs and benchmark
labels. Caller-supplied correlation identity is not an authorization grant.

### 5.2 Trusted runtime configuration

A runtime instance owns a versioned RuntimeProfile, public KnowledgeSnapshot,
StrategyCatalog, CapabilityRegistry, initial in-memory state and configured
ports. These are deployment/domain configuration, not per-case answers.

The same configuration is used for every request in a frozen workload.
Knowledge/catalog records may contain real internal identifiers and operation
semantics. They may not contain request-to-answer maps, benchmark family labels
or per-case controller overrides. A separate run is created for every request.

### 5.3 AgentResult

| Field | Contract |
| --- | --- |
| request_id / run_id | Correlation plus unique runtime-run identity |
| status | Exactly one terminal status |
| reason | Typed terminal reason and concise explanation |
| interpreted_goal | Accepted goal/constraints and request-span bindings |
| answer / data | Rendered text and typed result; explicitly partial if incomplete |
| verification | Immutable predicate results and supporting observation/evidence identities |
| provenance | Used entities/memories/edges, paths and snapshot fingerprints |
| final_state_ref | Present for simulated-state work; otherwise absent |
| metrics | Raw observed counts, reservations and availability flags |
| trace | Bounded ordered events or in-memory trace reference |

No stored boolean may contradict status or verification. A successful result
has nonempty applicable goal predicates, all required predicates passing and
valid provenance/identity/control evidence. A missing observation is not a pass.

A non-success result may include partial evidence. It cannot claim that the
complete task has succeeded. The answer is rendered from verified data; model
prose cannot introduce unsupported factual claims.

### 5.4 Terminal statuses

| Status | Meaning |
| --- | --- |
| SUCCEEDED | Accepted goal completed and verified |
| NEEDS_CLARIFICATION | Material ambiguity or missing user parameter; includes a focused clarification |
| UNSUPPORTED | Task requires semantics/capabilities outside the Stage A catalog |
| BOUNDED_FAILURE | Supported task cannot be completed with available evidence, validated plans or remaining resources |
| REJECTED | Invalid input or an integrity/identity/contract violation prevents safe continuation |
| CANCELLED | Cancellation accepted before successful terminal publication |

Normal budget exhaustion is BOUNDED_FAILURE, not an unrecorded exception.
A budget overrun is a control violation, distinct from stopping at the limit.
Expected ambiguity/unsupported outcomes are not successes.

A terminal latch publishes one result and prevents subsequent model, retrieval,
strategy or business-action work. Cancellation/deadline is checked before each
dispatch and before publication. Resource cleanup cannot change the result.

## 6. Internal semantic contracts

### 6.1 TaskIntent and GoalContract

TaskIntent includes a supported task kind, entities, input bindings, constraints,
required result shape, request-span origins and ambiguity evidence. Stage A
supports factual lookup, relation lookup, deterministic transformation,
stored-procedure goals and finite in-memory state goals.

The interpreter tries deterministic bilingual schemas first. On an unresolved
interpretation it may request a typed model proposal. Strict parsing rejects
duplicate keys, extra fields, unknown task kinds and invalid bindings.

GoalContract contains immutable semantic predicates, request-derived parameters,
required provenance/identity conditions and the allowed effect scope. It is
compiled by trusted task templates after validating an interpretation proposal.
The model cannot supply arbitrary predicate code, replace the verifier or
declare its own success condition.

Schema validity and span bindings do not prove universal natural-language
understanding. If an accepted interpretation differs from the user's intended
meaning, the independent evaluator must detect wrong-goal success. The result
exposes the interpretation so the error remains inspectable.

### 6.2 Evidence and WorkingContext

Evidence has stable origin/snapshot identity and an explicit kind: user input,
stored fact, vector hit, relation path, catalog entry, observation or hypothesis.
A hypothesis/model proposal is never promoted to a fact by selection.

Knowledge payloads use typed domain values with provenance mappings to memory
records. Similarity is a relevance signal, not a proposition-confidence value.

WorkingContext preserves:

- the goal and necessary request bindings;
- selected memory/procedure records;
- complete required relation paths;
- relevant observations and unmet constraints;
- snapshot identity, evidence coverage and selection/drop reasons.

Memory and entity identity remain distinct from display names. Deduplication
uses stable identities. SAME_NAME does not imply SAME_PERSON. Directed edges
cannot be inverted or substituted merely because the answer would be useful.

Relation paths retain constituent memory, edge and evidence references.
The context budget accounts for their records and canonical serialized bytes,
not only a path wrapper. Required proof paths are included atomically or rejected
as insufficient. No synthetic vector score is assigned to a relation node.

### 6.3 StrategyDescriptor and ActionProposal

A StrategyDescriptor adds semantic discovery to an A008 root procedure or
registered composed strategy:

- stable strategy/root reference and version;
- bilingual description and task-kind compatibility;
- input/output schemas;
- preconditions, declared effects and goal compatibility;
- public evidence requirements;
- effect class and deterministic cost estimate.

ActionProposal/Plan includes immutable plan identity/revision, input bindings,
registered capability references and bounded ordered steps. Trusted descriptors
own action semantics and expected step-outcome templates. Model output cannot
invent a capability, set an authorization flag or weaken a postcondition.

Plans may compose select/filter/sort/group/sum/format/assert operations and
declared in-memory state operations. Data bindings reference available inputs or
prior step outputs. No arbitrary code, shell, URL dispatch, recursion or
unbounded looping is allowed. Capability schemas bound container sizes and
serialized intermediate values under the simulated-state limit.

### 6.4 Observations and verification records

Each observation is bound to run, attempt, execution, action/step identity,
capability version and state revision. It records whether an action actually
executed, its typed result or error, and its resulting snapshot reference.

Precondition-blocked actions are not recorded as executed effects.
Observation identity mismatch or missing required evidence fails closed.

VerificationRecord references the accepted GoalContract, observations and
authoritative evidence. It records predicate-level PASS/FAIL/UNRESOLVED and
does not rely on the model's claimed status.

## 7. State machine and invariants

The phase states are RECEIVED, INTERPRETING, ACQUIRING, RESOLVING, EXECUTING,
OBSERVING, VERIFYING, RECOVERING, MODEL_ASSIST and TERMINAL.

| State | Permitted next states and conditions |
| --- | --- |
| RECEIVED | INTERPRETING after input/profile validation; otherwise TERMINAL |
| INTERPRETING | ACQUIRING if knowledge is required; RESOLVING for self-contained work; MODEL_ASSIST on unresolved supported intent; TERMINAL for material ambiguity/unsupported work |
| ACQUIRING | RESOLVING after context assembly; RECOVERING for an actionable deficit; MODEL_ASSIST for a bounded query proposal; TERMINAL on integrity/resource limits |
| RESOLVING | EXECUTING after plan validation; MODEL_ASSIST for a composition proposal; RECOVERING on a repairable deficit; TERMINAL if unsupported/exhausted |
| EXECUTING | OBSERVING after bounded dispatch or interruption |
| OBSERVING | VERIFYING with action outcomes and fresh final-state evidence |
| VERIFYING | TERMINAL/SUCCEEDED when all checks pass; RECOVERING on a typed recoverable failure; otherwise TERMINAL |
| RECOVERING | ACQUIRING for context deficit; RESOLVING for a changed strategy/plan; MODEL_ASSIST for bounded repair; otherwise TERMINAL |
| MODEL_ASSIST | Return to its recorded requesting state after validated proposal; report an explicit failed proposal to that state |
| TERMINAL | No further task work |

MODEL_ASSIST never transitions directly to success. The requesting state,
purpose and input fingerprint are recorded before the call. Phase transitions
are separate from bounded primitive steps inside an execution attempt.

Global invariants:

1. One immutable request, accepted goal, initial state and profile per run.
2. One monotonic budget ledger for all attempts and model roles.
3. No expected-answer or evaluator data enters any runtime state.
4. Every dispatched action has a validated registered capability.
5. Every execution attempt has a unique execution identity.
6. Recovery carries the prior mismatch and a meaningful proposed change.
7. No real external action capability exists in the Stage A registry.
8. Success requires applicable completion verification.
9. Terminal publication is exactly once and prohibits extra attempts.
10. Unknown/failed model routing is not a confident negative route.

## 8. Interpretation, retrieval and structural routing

### 8.1 Selective path selection

An input-contained deterministic transformation can bypass knowledge retrieval
and relation routing. Familiarity, where useful, is evidence rather than a
retrieval veto or truth predicate.

For a knowledge task, context acquisition performs:

1. derive queries from the accepted goal, request text, known entity bindings and
   unmet evidence requirements;
2. infer StructuralNeed with unchanged A014 HYBRID_RULE_THEN_MODEL;
3. search A005 memory/catalog indexes as required;
4. resolve identity and choose at most two legitimate relation seeds;
5. invoke A013 expansion only on a decided relational need with usable seeds;
6. assemble context and compute coverage/deficits.

No per-case expected IDs guide any of these steps.

### 8.2 A014 boundary

The router receives the original query text, a run-scoped generated correlation
identity and optional language hint only. Broker subrequest identities include
the run identity so repeated caller request IDs cannot accept another run's
response. It does not receive retrieved facts, graph contents,
expected relation labels or task success. Its decision is cached per run;
recovery cannot repeatedly reroute the same text to seek a preferred answer.

The five qualified relation types remain WORKS_AT, CAUSED_BY, OCCURRED_BEFORE,
PART_OF and USED_FOR. A015 does not expand A014's frozen model schema or override
strong rule decisions.

DECIDED_NON_RELATIONAL is a decision. ABSTAINED, INVALID_MODEL_OUTPUT and
MODEL_ERROR are unresolved/failure states even when StructuralNeed is empty.
The controller either proceeds on an independently supported non-relational
task, obtains an allowed recovery, or returns bounded failure. It cannot turn a
failed route into verified relation success.

A014's source remains unchanged. The injected broker-compatible ModelAdapter
records calls/errors even if A014 translates an exception into a fail-closed
result without token metadata.

### 8.3 Retrieval and expansion accounting

Identical queries against the same immutable index snapshot may be cached
within a request. Query proposals, actual searches, cache hits, embedding calls
and vectors scored have distinct counters. No cross-case answer/context cache
is allowed in qualification.

Procedure-catalog searches share the same six-query budget as memory searches.
Each actual index search reserves its eligible-vector upper bound before
dispatch. The deployment profile admits at most 256 searchable records across
memory/catalog indexes, bounding six searches at 1536 vectors.

A005 index construction/document embedding is measured as setup. It is not
silently folded into or erased from request cost.

A015 uses A013's `expand` primitive over seeds from existing retrieval output.
It does not call `run_hybrid_recall` after already searching, because that
wrapper performs another vector search. Seed count is at most two and never
exceeds A013's visited-node budget.

Each expansion keeps the existing maximum of three hops, eight visited nodes,
32 scanned edges and minimum proposition confidence 0.5. Counters include
filtered/scanned work. Per-call node deduplication does not erase repeated
visits across recovery rounds from aggregate work.

### 8.4 Context growth

Context capacities progress 8, 16, 24 items with a 16 KiB serialized ceiling.
The controller may stop earlier when goal/evidence coverage is sufficient.
Expansion is driven by a documented deficit, not by a need to reach the largest
context. Evidence needed for identity or proof cannot be dropped silently.

## 9. Strategy resolution and internal execution

The resolver first filters strategies by task/input/effect/goal compatibility.
It then ranks usable candidates by evidence coverage, declared cost and stable
identity for deterministic ordering. Ordering does not settle ambiguous entity
identity or materially different goals.

A stored procedure uses the unchanged A008 CHUNKED runner through a context-bound
executor adapter. Its preconditions may require relevant evidence selected by
the runtime. Missing evidence produces an observation/interruption and can
justify context recovery.

If no stored procedure fits, a deterministic composer may assemble registered
pure operations. A model may propose a bounded composition when deterministic
resolution is insufficient. The resulting plan is ephemeral.

The trusted compiler maps validated composed steps to an execution
representation compatible with A008 CHUNKED actions/CALLs. It derives step
ExpectedOutcome references from capability definitions, not model-supplied
"expected answer" fields. Step success is still insufficient for final success.

Plan validation checks:

- exact schema and known capability versions;
- task/goal compatibility and permitted effect class;
- available input bindings and bounded values;
- preconditions and declared result types;
- acyclic calls, maximum call depth and primitive step count;
- action/plan identity and remaining reservations.

Rejected proposals do not execute. Stored and composed plans use the same
capability semantics and completion checks. No generated plan is persisted as
a learned procedure during Stage A.

## 10. Completion verification and final answer

Verification runs after execution/observation, including for procedures whose
A008 result is COMPLETED. It reads a fresh final snapshot for simulated goals.

| Task kind | Completion checks |
| --- | --- |
| Factual | Structured claims match authoritative stored facts; entity bindings and provenance are valid |
| Relational | Correct typed direction/path/confidence and identity; required evidence is complete |
| Transformation | Output satisfies request constraints and trusted operation semantics from original inputs |
| Simulated procedure | All accepted goal postconditions hold in the fresh final state |
| Every task | Result/observation identity, capability scope, budget and control integrity |

A step marker, procedure completion flag, fluent model answer or proposed
postcondition is not evidence of overall completion. The verifier does not read
benchmark expected answers.

Unsupported claims or unresolved predicates prevent SUCCEEDED. Final text is a
deterministic rendering of verified structured values, evidence and outcome.
Optional stylistic generation is outside the Stage A qualification profile.

Offline evaluation is independent of this runtime verdict. It checks the
original task against frozen oracle values/postconditions, including
wrong-interpretation success and missing requested outputs.

## 11. Recovery and re-plan

Recovery is entered on typed causes such as MISSING_EVIDENCE,
PRECONDITION_UNSATISFIED, OBSERVED_MISMATCH or INVALID_PLAN. Backend availability
failure may yield bounded failure; there is no automatic transport retry.

Each accepted recovery must change relevant evidence, compatible strategy or
validated plan. Context/plan fingerprints and deficit resolution demonstrate
progress. An unchanged proposal or repeated unsatisfied cause without a new
remedy terminates with NO_PROGRESS.

The maximum is two recovery rounds and three strategy attempts. A strategy
attempt is a distinct resolved candidate/composition sent through validation,
even when it is rejected before execution. Candidate ranking is not an attempt.
Model proposals and failed calls have additional counters; they cannot become
unlimited because no action executed.

For each actual execution attempt:

- use a fresh in-memory executor from the same immutable initial snapshot;
- assign a new execution ID;
- preserve all prior attempt and cost evidence;
- read a new final snapshot rather than accept a previous success observation.

The three context-acquisition rounds and six queries are totals for the entire
run, not new allowances per recovery. Recovery does not reset any ledger.

Integrity violations, model/source identity drift and unresolved same-name
ambiguity do not authorize blind retry. Cancellation and terminal publication
prevent additional attempts.

The fresh-snapshot rule is specific to Stage A simulation. Future real effects
must use observation/reconciliation and the effect journal instead of assuming
the external world can be reset.

## 12. Runtime budgets and enforcement

Profile identity: `a015-stage-a-v1`.

| Resource | Maximum / rule |
| --- | --- |
| Request text | 8192 UTF-8 bytes |
| Generative calls | 4 total, across all purposes and failures |
| Model context | 8192 tokens per call, including output allowance |
| Prompt-token reservations | 32768 total upper bound |
| Generated-token allowance | 1024 per call; 2048 total |
| Context rounds | 3 total |
| Actual retrieval queries | 6 total; at most 2 per round, including catalog |
| Eligible indexed records | 256 total across searchable memory/catalog indexes |
| Vectors scored | 1536 total |
| Active context | At most 24 items and 16384 serialized bytes; levels 8/16/24 |
| Relation invocations | 3 total |
| Relation work per invocation | 3 hops / 8 visited nodes / 32 scanned edges |
| Aggregate relation work | At most 24 visit events / 96 scanned edges |
| Strategy attempts | 3 total |
| Recovery rounds | 2 total |
| Primitive actions | 32 per execution attempt / 96 total |
| Procedure call depth | 8; no recursion |
| Controller transitions | 64 phase transitions |
| Trace | 256 compact events / 262144 serialized bytes |
| Simulated state/intermediate data | 65536 serialized bytes; bounded capability input schemas |
| End-to-end deadline | 180 seconds from receipt |
| Single model call | 120 seconds, clamped to remaining deadline |

Limits are independent; reaching one can stop a run before another is exhausted.
A plan that exceeds an action/data/call-depth limit is rejected before dispatch.
Pure capabilities must bound their inputs and operations; arbitrary evaluation
and unbounded allocation are not supported.

### 12.1 Reservation semantics

A single ledger reserves worst-case admitted work before dispatch:

- model-call slot, request-specific output allowance, prompt upper bound and
  remaining deadline;
- vector upper bound from eligible index records;
- relation and context capacity;
- strategy/primitive-action counts.

Actual reported work is reconciled afterward. A014's existing 192-output-token
request remains unchanged and participates in the same output ledger. Other
roles request only their allocated remaining allowance, capped at 1024.

A failed/timeout call consumes its call slot. Unknown actual token use remains
unknown and its reservation stays charged. There is no refund based on assuming
that an exception meant no model computation occurred.

Physical prompts require a defensible pinned-template/tokenizer upper bound.
Before dispatch, prompt upper bound plus requested output fits the context
limit. Arbitrary byte counts are not represented as exact token counts.
Inability to establish a safe bound blocks physical cost qualification; silent
provider truncation cannot be used to make a prompt fit.

Reported use above the admitted allowance is a port/control violation, recorded
explicitly. Reservations bound admitted work; the controller does not claim
that it can physically undo an uncooperative backend's computation.

### 12.2 Time, cancellation and late results

Generation and embedding transports use deadline-aware timeouts. The synchronous
legacy adapter is used through an injected transport/adapter boundary rather
than edited. Cancellation is checked before each dispatch and after return.

The controller publishes a bounded terminal result at deadline through a port
that can return control. Late responses are discarded and cannot publish
success. Backend abort is best effort and its support/outcome is recorded.
No daemon/process termination is part of request cancellation.

If physical backend work remains unobserved after a timeout, usage is unknown
and the cost comparison is incomplete. The trace records that condition instead
of reporting zero residual computation.

### 12.3 Trace bounds

A primitive step event contains its dispatch and observation evidence together;
separate redundant records are not required. State snapshots/contexts use hashes
and referenced bounded artifacts instead of full repeated copies. Trace
capacity is reserved before the next operation. Overflow terminates explicitly
rather than dropping evidence required for verification.

## 13. Selective model assistance

Every model call goes through ModelBroker, including A014. Purposes are INTENT,
STRUCTURAL_ROUTING, QUERY_PROPOSAL, PLAN_PROPOSAL and PLAN_REPAIR. There is no
separate quota for a purpose and no hidden retry.

| Purpose | Permitted inputs |
| --- | --- |
| Intent | Raw user text and trusted task schemas |
| Structural routing | A014 fixed prompt, raw query and optional language hint |
| Query proposal | Accepted goal and bounded evidence deficit; no gold targets |
| Plan proposal/repair | Accepted goal, bounded context/observations and public capability schemas |

The broker records run/subrequest identity, purpose, prompt fingerprint,
configured model/digest, raw bounded output, parse status, requested/observed
tokens, timings and errors.

Strict schemas reject duplicate keys, extra fields, invalid capability references,
attempted authorization/policy overrides and unknown types. Retrieved text is
data, not a source of system instructions. Model plans cannot access the corpus
oracle, environment secrets or arbitrary tools.

Physical model and embedding identities are probed freshly before and after a
qualification batch, with call-response identity validation. A cached legacy
descriptor alone is not fresh proof of the deployed digest.

## 14. Future capability, authorization and effect seams

The Stage A design keeps these interfaces distinct:

| Interface | Stage A behavior | Future behavior |
| --- | --- | --- |
| CapabilityRegistry | PURE / IN_MEMORY descriptors | Read/write external capabilities, schemas, effect and retry classes |
| AuthorizationPort | Enforces Stage A scope from trusted configuration | Host/user grants scoped to capabilities/resources |
| ActionProposal / ExecutionPort | Validate then dispatch internal operation | Authorized external execution |
| ObservationPort | Typed results and in-memory snapshots | External observations, freshness and outcome reconciliation |
| EffectJournalPort | Action/effect identities represented in in-memory trace | Durable proposed/dispatched/observed/unknown/compensated records |
| Cancellation / RetryPolicy | Bounded cooperative control; no hidden retry | Capability-specific retry and deadline semantics |
| PostconditionVerifier | Internal goal checks | Fresh verification of external effects |
| CompensationPort | No real compensation executor | Explicit rollback/compensation where the capability supports it |

Only minimal types and the pure/in-memory path are required in Stage A. A real
tool transport, durable journal database, approval UI, generic retry engine and
rollback framework are not implemented in this milestone.

Execution-attempt identities remain unique. A future logical operation/
idempotency identity must remain stable across retries of the same effect;
creating a new attempt does not authorize repeating a real write.

For Stage C, an unknown outcome is reconciled before retry. The model cannot
mint grants or choose effect classification. Compensation is explicit and may
be unavailable; the architecture does not promise universal rollback. Additional
confirmation applies only where the future authorized deployment policy requires
it, not automatically to every action.

## 15. Frozen bilingual benchmark contract

Workload identity: `a015-bilingual-stage-a-v1`.

There are exactly 64 ordinary-text requests: 32 semantic tasks, each expressed
once in English and once in Thai. Translations are paired observations, not 64
independent semantic tasks.

| Family | Semantic pairs | EN | TH | Oracle expectation |
| --- | ---: | ---: | ---: | --- |
| Direct/simple transformation | 4 | 4 | 4 | Complete with applicable deterministic operations |
| Factual/context retrieval | 4 | 4 | 4 | Correct grounded result |
| Relation-dependent question | 4 | 4 | 4 | Correct typed relation/path result |
| Stored/compound procedure | 4 | 4 | 4 | Correct result and final state |
| Genuine recovery | 4 | 4 | 4 | Initial real mismatch then verified recovery |
| No stored procedure / composition | 4 | 4 | 4 | Resolve or construct a bounded strategy |
| Ambiguity / capability controls | 4 | 4 | 4 | Correct clarification or unsupported terminal |
| Explicit bounded failure | 4 | 4 | 4 | Correct bounded failure and reason |
| Total | 32 | 32 | 32 | 64 requests |

The first six families have 48 solvable requests. Controls comprise:

- two ambiguity semantic pairs: four NEEDS_CLARIFICATION requests;
- two out-of-Stage-A capability semantic pairs: four UNSUPPORTED requests;
- four explicit-failure semantic pairs: eight BOUNDED_FAILURE requests.

Thus bounded-failure correctness has denominator 8, while correct non-success
terminal behavior has denominator 16. The expectation includes required status
and reason category, not merely "did not succeed".

Genuine recovery must arise from real context/precondition/observation deficits,
not a case-ID failure switch. The composition family has no matching stored root
for its complete task; model assistance may be appropriate but is not forced if
deterministic composition solves it.

Engineering fault controls are separate from these 64 requests. They cover
malformed input/output, wrong identities/digests, forged provenance, unsupported
effects, missing observations, cyclic/oversized plans, budget overrun attempts,
cancellation and post-terminal work. They do not inflate task-success metrics.

### 15.1 Freeze artifact and timing

The future freeze artifact contains:

- the exact ordered 64 bilingual texts and opaque case identities;
- paired-task/family metadata accessible only to the evaluator;
- complete public facts, relations, catalog, capabilities and initial state;
- separate oracle answers/postconditions/statuses/reasons;
- canonical schemas, runtime profile and both prompt templates;
- seeds/order schedule and pinned physical identities;
- evaluator and normalizer definitions.

The implementation plan must place an explicit freeze commit before controller,
interpreter/ranking tuning or any physical performance experiment against the
workload. The semantic coverage and counts are fixed by this spec. Exact corpus
serialization/texts are implementation deliverables at that freeze gate, not a
permission to change counts/families after results.

Development fixtures are separate. After freeze, a change to requests, public
data, oracle, budgets or prompts creates a new disclosed workload/profile
version; old results remain available. Harness-only model responses are not used
to train a per-case answer map.

The runtime receives AgentRequest and the same public configuration for all
cases. It never receives evaluator metadata or an expected terminal/answer.
Generated run IDs are unrelated to case IDs. Public procedures may describe
their real semantics; benchmark matching annotations are not public knowledge.

## 16. Direct pinned-model baseline

Variant identities are UNIFIED_RUNTIME and DIRECT_PINNED_MODEL.

The direct baseline receives:

- the same ordinary task text;
- the complete public knowledge/relations, procedure semantics and capability
  catalog used by Stage A;
- the same initial simulated state and supported completion/output contract;
- no gold answers, per-case expected target IDs or ASCA-selected context.

Its frozen system prompt requests a strictly typed answer, intent/bindings and/or
bounded pure plan. One model call proposes the complete solution. The harness
performs no model repair call, ASCA retrieval, ranking or recovery.

The same mechanical plan validator, capability semantics, pure executor and
completion predicates are available to both variants. A direct plan may select
a public stored root by ID or list registered pure steps. Mechanical root lookup
does not perform ASCA strategy selection.

The model proposes its interpretation; the common validation layer validates
bindings and instantiates trusted goal templates from the original text. It
does not supply a preinterpreted gold goal or an ASCA-selected strategy. This
keeps the completion contract comparable without moving ASCA orchestration into
the baseline.

Execution tasks run the direct model's validated plan once. Evaluation does not
count a textual claim of "done" as state completion. Invalid JSON, invalid plans
or failed verification receive an explicit non-success result without hidden
repair. Raw claimed-success/rejected-proposal counts are reported separately
from published false success.

### 16.1 Information and context fairness

All public baseline material must fit in the pinned 8192-token context together
with the requested output allowance. This is verified before workload freeze.
No needed facts are removed per case and no evaluator chooses a helpful subset.

If the proposed corpus cannot fit, its common public fixture is reduced before
freeze, preserving coverage/counts and applying the same data to both variants.
If that is impossible without changing the approved design, return to design
review. It is not acceptable to silently truncate the direct baseline.

Both variants use the same model/digest, temperature 0, seed 0, thinking false,
8192 context and at most 1024 output tokens per call. A014 keeps its qualified
192-token role request. Both have the same 180-second request deadline and
120-second per-call ceiling.

The unified runtime may use up to four calls with a 2048-output-token aggregate
allowance. The baseline is one-shot. This aggregate-budget difference is
reported; the experiment is not represented as equal-call-budget inference.

Direct retrieval/relation counters are zero by construction. Its internal
working-context manager is N/A, not zero memory. Both variants report prompt
record counts/bytes/tokens; runtime context items/bytes are a separate metric.

## 17. Portable and physical qualification

### 17.1 Portable engineering qualification

Portable deterministic ports test contracts, controller transitions, semantic
operations, observations, verification, bounded recovery and leakage prevention.
They do not establish real Qwen token savings or generation success.

Required controls include:

- procedure COMPLETED with unmet root goal does not become SUCCEEDED;
- wrong-goal/model claims are inspectable and evaluator-detectable;
- same-name entities remain distinct through retrieval and recovery;
- route failure/abstention is not converted to a decided negative;
- relation paths remain valid under context assembly;
- blocked actions have no executed-effect evidence;
- attempts use fresh simulated state and distinct execution IDs;
- retry/re-plan costs stay in the same ledger;
- rejected actions, cancelled runs and terminal runs do no extra task work;
- new runtime never imports A015 oracle/evaluator data, and adapters never read
  legacy expected labels or call fixture builders despite incidental package
  initialization;
- renamed namespace audit preserves all legacy/frozen constraints.

Tests assert meaningful observable invariants and failures. They do not merely
duplicate the implementation's control statements.

### 17.2 Physical execution protocol

The primary model-comparison evidence requires real pinned generation and
embedding on the user's machine. Three repetitions produce 192 request results
per variant, 384 in total. Each repetition keeps all 64 requests.

A deterministic seed-0 order schedule balances which variant runs first:
canonical EN/TH pair order, alternating first variant by pair index and
repetition. Both translations and both variants start fresh runs and initial
world states. There is no cross-request answer, learned-procedure or working-
context cache.

Record warm-up and model residence/cache conditions. Use a documented common
warm-up before timed batches. Build the unified index once per declared setup;
report document embeddings and setup time separately. Warm-up outputs cannot
become task evidence. Report a setup/cold-start measurement separately from
steady request latency rather than mixing the two into one number.

Physical generation need not be bit-identical even at temperature 0. Retain all
replicates, success variation and raw outputs; no cherry-picking or retrying a
failed request outside the defined runtime.

Record machine/OS, Ollama version, full model/embedding descriptors, digest,
dimension, source identities, setup/workload/prompt fingerprints and timing
method. Probe physical identity before and after the batch. Model drift or
uncontrolled source/data drift blocks acceptance of the experiment.

### 17.3 Evidence artifacts

The harness saves a source-bound JSON evidence payload plus bounded prompt/output
and trace artifacts. It includes:

- specification/workload/profile/schema versions and canonical hashes;
- runtime/evaluator source mode/path/blob fingerprint and source commit;
- exact model/embedding identities and backend environment;
- all raw case/variant/repetition records;
- runtime terminal results, interpreted goals and verifier evidence;
- offline oracle verdicts and aggregate counters;
- real model-call records and setup metadata.

The source universe for that fingerprint is declared in the freeze manifest:
runtime/adapters, evaluator/normalizers, prompt/schema/profile and public/oracle
fixture inputs. Generated evidence/report files are outside their own source
fingerprint, avoiding circular identity. A packaging/evidence commit records the
behavior commit and preserves the exact mode/path/blob fingerprint.

The offline evidence verifier recomputes aggregates and outcomes from raw
records, validates reference identities/bounds and rejects tampered or
inconsistent evidence. Evidence validity is not inferred from a success flag.
Raw physical evidence is preserved even for negative/mixed research outcomes.

CI remains Ollama-independent: portable tests, architecture audit, A011
preservation, existing historical qualifications and verification of committed
physical evidence. Saving a physical artifact is not permission to change
historical A005-A014 results.

## 18. Metrics and denominators

All metrics include failed/rejected/timed-out attempts; unavailable values remain
null with availability flags.

| Group | Raw measurements |
| --- | --- |
| Completion | Runtime status, oracle task success, answer correctness, final-state correctness, false success |
| Non-success | Clarification correctness, unsupported correctness, bounded-failure correctness including reason |
| Generative model | Attempted/dispatched/completed/error calls by purpose, requested/reported prompt/output tokens, prompt fingerprints and model identity |
| Embedding/retrieval | Query proposals, actual queries, cache hits, document/query embedding calls, vectors scored, setup cost |
| Context | Selected/current/peak item counts and canonical bytes, evidence-kind counts, drop/coverage reasons |
| Relations | Activation decision, invocations, scanned edges, visit events and unique visited identities, path evidence |
| Strategy/execution | Candidates resolved, strategy/plan validation attempts, root procedure attempts, primitive actions actually executed, blocked dispatches, depth |
| Recovery | Rounds, re-plan proposals, meaningful context/plan changes, genuine successful recovery |
| Timing | Exclusive phase durations, broker/embedding spans, end-to-end client wall time, setup and backend-reported durations |
| Integrity | Identity/provenance/control/budget violations, rejections, unknown usage, duplicate execution IDs, post-terminal work |

Counter derivation is explicit: a model invocation starts when the broker calls
ModelAdapter.generate, including an error/timeout return. Preflight-denied
proposals are counted separately and are not invocations. Actual generation
requests dispatched by the transport are also recorded, so admitted invocations
are not confused with confirmed backend computation. Aggregate generative cost
uses all invocation attempts and all available token metadata; unknown usage
blocks a positive cost comparison.

A recovery round is a controller-admitted repair cycle; a re-plan proposal is a
separate event within it. Primitive-action count includes only operations whose
executor actually ran, while blocked dispatches have their own counter.

Primary rates per repetition:

- task completion: correct completed requests / 48 solvable requests;
- bounded-failure correctness: correct bounded failures / 8 explicit failures;
- non-success terminal correctness: correct status/reason / 16 controls;
- false success: raw count and count / all published SUCCEEDED results.

Report answer and final-state correctness separately where applicable. Also
report task/family/language and paired semantic-task results. Across three
repetitions the denominators are 144 solvable, 24 bounded-failure and 48
non-success controls per variant. Cost comparison uses all 192 requests per
variant, with family/language breakdowns, not only successes.

Exclusive phase timers include controller overhead without double-counting
nested model spans. End-to-end wall time is measured independently. Backend
durations are descriptive; they are not directly summed into client phase
durations. Report median/range and raw repetitions.

Expected stopping at a budget is not a budget violation. Safe rejection of
forged identity is distinct from accepting wrong identity. Fault controls have
their own expected behavior, outside primary task denominators.

No synthetic efficiency score, inferred FLOPs/energy claim or comparison of
logical context count with actual process RAM is made.

## 19. Predeclared architecture decision

Evidence validation precedes outcome classification. If records, identities,
required physical metrics or fingerprints cannot be trusted, the comparison is
INVALID/INCOMPLETE and no positive research outcome is assigned. Portable-only
results cannot substitute for the physical model comparison.

A valid comparison can produce these outcomes:

### UNIFIED_RUNTIME_JUSTIFIED

All of the following hold across paired physical trials:

1. Unified published false-success count is zero.
2. Unified controls are correct in all 48 non-success trials, including all 24
   bounded-failure trials.
3. No accepted provenance, identity, budget/control or post-terminal violation.
4. No baseline-only success on a solvable paired trial; unified completion is
   no lower in each language and family.
5. At least one English and one Thai genuine successful recovery are observed
   in each repetition, with failed prior observation and meaningful changed
   context/plan evidence.
6. Unified total generative calls over all 192 requests are strictly fewer than
   direct baseline calls.
7. Unified total reported prompt plus output tokens are no greater than direct
   baseline totals; usage is complete for this comparison.
8. All declared retrieval/relation/execution/recovery limits hold.

This supports the runtime for the frozen Stage A workload, not universal
superiority or automatic savings in every resource.

### UNIFIED_RUNTIME_NOT_SUPPORTED

With trustworthy evidence, the unified runtime publishes false success, fails
a required non-success control, accepts a runtime invariant violation, completes
none of the solvable tasks, or demonstrates no genuine successful recovery.
The engineering/research failure is recorded rather than tuned out of the
workload.

### DIRECT_MODEL_PREFERRED

The comparison is valid and safe, but the direct baseline dominates solvable
task success: at least one baseline-only success and no unified-only success,
with all direct non-success controls correct and direct calls and combined
tokens no greater than unified. This label follows the NOT_SUPPORTED safety/
capability checks above.

### MIXED

All remaining valid trade-offs, including preserved completion with higher
model-token cost, reduced model calls with a completion regression, or improved
completion without lower model dependence.

Latency, vectors scored, embedding work and context/relation costs remain
separate measured conclusions for every outcome. They do not overwrite the
predeclared model-dependence/completion decision.

## 20. Component reuse and historical boundaries

| Component | A015 treatment | Boundary preserved |
| --- | --- | --- |
| A003 familiarity | Reuse optional exact familiarity evidence | Not task truth or a retrieval veto |
| A004 model adapter | Reuse through broker/deadline-aware transport | Frozen adapter contracts/source retained |
| A005 vector memory | Reuse index, embedding and hit/metric primitives | VECTOR_SUFFICIENT remains historical |
| A006 working set | Adapt vector selector through a local adapter; new heterogeneous context merger | NOT_SUPPORTED retained; no false relation-vector evidence |
| A007 expansion | Adapt deficit/structural-trigger concepts in new contracts | Existing enums/qualified behavior unchanged |
| A008 procedures | Reuse CHUNKED library/runner behind executor and strategy catalog | No hidden retry; independent root goal verification |
| A009 loop | Supersede top-level orchestration only in new path; historical/baseline reference | Existing SUPPORTED controller remains unchanged |
| A010 comparison | Baseline-only evidence and cost-accounting caution | NOT_SUPPORTED and all counts retained |
| A011 qualification | Preserve source guard/evidence infrastructure | No claim of automatic A015 qualification |
| A012 relations | Reuse typed semantics; target-aware traversal stays evaluator/baseline-only | No expected target IDs in runtime |
| A013 activation | Reuse target-free bounded expansion primitive | Bounds, direction, identity and provenance retained |
| A014 routing | Reuse hybrid query-text-only inference through broker | Original schema/rules/failure statuses retained |

The reused A006 vector-selection path is SINGLE_BEST; A015 does not promote
SELECTIVE_CONVERGENCE. A006's local vector-selection budgets are not replaced
with a combined A015 budget object. Its contract does not accept relation/model control budgets.
Global ledger checks surround adapters; local primitives keep their semantics.

A009 terminal-only model behavior remains isolated on its historical path.
A015's new selective proposal policy does not rewrite what A009 proved.

## 21. Acceptance and claims boundary

A015 implementation engineering evidence must establish:

- ordinary EN/TH text is sufficient input; internal controls are not required;
- new controller owns the lifecycle and can reach a verified terminal result;
- supported pure/simulated work, stored procedures and validated compositions
  execute through declared capabilities;
- meaningful recovery and bounded failure are inspectable;
- independent completion and offline oracle checks are both present;
- all call/query/context/relation/action/recovery costs are accounted;
- Stage A exposes no real external action;
- historical source, outcomes, release and tag identities are preserved;
- portable tests, current architecture audit, A011 guard, exact-commit CI and
  source-bound physical evidence checks pass as applicable.

Engineering checks do not force a positive research label. No claim of human
cognition, AGI, biological surprise, lower FLOPs/energy, universal speed,
production safety or safe replay of real side effects follows from this spec.

## 22. Written-spec review and next gate

This document is the concrete artifact for written-spec review. It contains
design contracts and acceptance requirements, not an ordered implementation
plan.

Approval of this spec permits writing the implementation plan. It does not
create an Issue, change CURRENT/ROADMAP to ACTIVE, create a runtime package,
install dependencies or run a new physical A015 benchmark.

The later plan must explicitly preserve the workload freeze timing, activation
gate, isolated implementation scope, testing, whole-change review and final
integration/evidence gates. Actual Issue/branch identities come from live
creation results at that authorized step.

### 22.1 Author self-review

Review method: inline author self-review, not independent peer review.

The document was checked for:

- complete coverage of the approved Approach 3 / Stage A direction;
- public/internal contract separation and evaluator leakage;
- state/terminal/proposal boundaries;
- global versus per-attempt budgets and unknown-usage accounting;
- procedure completion versus overall goal completion;
- independent offline correctness checks;
- fair executable direct-model completion and context visibility;
- legacy incidental benchmark loading versus forbidden fixture/oracle access;
- explicit 48/8/8 workload denominators and three-repetition accounting;
- Stage B/C interfaces without Stage B/C implementation;
- preservation and process gates.

Material clarifications include reserving output space inside the 8192-token
context, counting rejected strategy attempts, charging catalog queries to the
same retrieval budget, retaining reservations on unknown usage, and separating
expected bounded stops from budget overruns. Self-review also identified legacy
package initializers that load benchmark modules transitively; the dependency
rules now prohibit fixture/oracle use explicitly without editing frozen source.
These make the conversational
design precise without enlarging its product scope.

## 23. Source references

- [CURRENT](../../development/tasks/CURRENT.md)
- [ROADMAP](../../development/tasks/ROADMAP.md)
- [Qualification matrix](../../development/QUALIFICATION-MATRIX.md)
- [Pre-A011 snapshot](../../architecture/ASCA-PRE-A011-SNAPSHOT.md)
- [A009 design](2026-10-10-a009-integrated-cognitive-loop-design.md)
- [A009 controller](../../../src/flywire_asca/integrated_loop/controller.py)
- [A009 report](../../development/reports/ASCA-20261010-A009-integrated-cognitive-loop.md)
- [A013 runner](../../../src/flywire_asca/relational_activation/runner.py)
- [A013 report](../../development/reports/ASCA-20261011-A013-selective-relational-activation.md)
- [A014 runner](../../../src/flywire_asca/structural_routing/runner.py)
- [A014 model router](../../../src/flywire_asca/structural_routing/model_router.py)
- [A014 report](../../development/reports/ASCA-20261011-A014-structural-need-inference.md)
- [A014 completed handoff](../../development/reports/ASCA-20261011-full-session-handoff-a014-completed.md)
- [Model contracts](../../../src/flywire_asca/model/contracts.py)
- [Procedure runner](../../../src/flywire_asca/procedural_memory/runner.py)
- [Architecture auditor](../../../scripts/audit_architecture_contract.py)
- [A011 preservation verifier](../../../scripts/verify_a011_frozen_profile_preservation.py)
