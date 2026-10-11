# Full Session Handoff â€” Post-A014 / A015 Unified Agent Runtime Direction

Date: 2026-10-11
Repository: `funggier/FlyWireASCA`
Local repo: `T:\Space\Projects\ProjectsAI\FlyWireASCA`
Handoff role: authoritative session-transition context for the next architectural milestone
A014 status: DONE / CLOSED
A015 status: NOT YET ACTIVATED

## 1. Read this first

The next session must treat live Git, GitHub, and runtime state as authoritative.
If any prose in this handoff conflicts with live state, investigate and explain
the mismatch before changing anything.

Do not:

- reset or clean the worktree;
- rebase or force-push;
- rewrite A005-A014 historical conclusions;
- weaken the A011 frozen-source preservation guard;
- modify FlyWireLLM;
- create a release/tag/version bump unless explicitly authorized;
- silently activate A015 before the architectural design/spec/plan gates are
  satisfied.

The user has already chosen the architectural direction described below:
**Approach 3 â€” build a new unified agent runtime rather than merely wrapping
the existing A009 loop. Do not reopen the Approach 1/2/3 choice unless live
evidence exposes a blocking contradiction.**

## 2. Live state at handoff creation

Verified on 2026-10-11:

- local `main`:
  `7d139bd0f76d5ce40ef280f795c5f4968d9d5fb1`;
- `origin/main`:
  `7d139bd0f76d5ce40ef280f795c5f4968d9d5fb1`;
- ahead/behind: `0/0`;
- worktree: clean;
- A014 Issue #18: closed with reason `completed`;
- A014 exact closure CI:
  run `38153588947`, GREEN;
- A014 closure artifact:
  `a014-structural-routing-38153588947-1`;
- artifact digest:
  `sha256:669db68c5954fe53bca42cd621bae616ebb784120db04c70b7a3c2702c57db0a`;
- `CURRENT.md`: A014 / DONE;
- `ROADMAP.md`: A001-A014 DONE;
- no A015 row exists;
- no A015 task is active.

The historical remote branch
`origin/research/a014-structural-need-inference` still exists. It is not an
active development branch and must not be mistaken for current work.

## 3. Why the project is moving to end-to-end work now

A005-A014 progressively established increasingly useful pieces of the
architecture without claiming more than the evidence supported.

The most important recent chain is:

1. A009 demonstrated a bounded integrated cognitive loop with selective
   retrieval, CHUNKED procedure execution, mismatch-driven recovery, and
   terminal model fallback.
2. A010 deliberately compared that path with a dense/non-selective baseline and
   found the broad system-efficiency hypothesis `NOT_SUPPORTED`. ASCA used a
   much smaller active working set, but under that frozen workload it issued
   slightly more retrieval queries and more vector scores, and dense retained
   one success that ASCA missed.
3. A012 showed that explicit typed relational traversal is justified for the
   relation-dependent workload.
4. A013 showed that relation traversal should not be always-on:
   `SIGNAL_GATED_RELATION_JUSTIFIED`.
5. A014 removed the requirement that a caller manually supplies that structural
   signal. Ordinary English/Thai query text can now be routed into an
   A013-compatible `StructuralNeed` with a hybrid rules-then-model policy.

A014 produced a particularly important physical result on 32 valid bilingual
cases using pinned `qwen3.5:4b`:

| Metric | RULE_ONLY | MODEL_ONLY | HYBRID_RULE_THEN_MODEL |
| --- | ---: | ---: | ---: |
| downstream success | 27/32 | 32/32 | 32/32 |
| false activations | 0 | 2 | 0 |
| missed activations | 9 | 0 | 0 |
| exact relation-set matches | 23/32 | 30/32 | 32/32 |
| model invocations | 0 | 32 | 9 |
| prompt tokens | 0 | 6435 | 1817 |
| generated tokens | 0 | 1134 | 345 |
| observed model-call duration | 0 | ~127.706 s | ~20.760 s |

The hybrid policy therefore matched model-only downstream success while reducing
model invocations by 23/32 = 71.875%, and it removed model-only's two false
activations.

The duration numbers are descriptive physical-run observations, not a universal
latency claim. The token and invocation counts are stronger evidence for the
specific frozen workload.

This result is why the next step is justified: the project has enough evidence
that selective control can materially reduce unnecessary LLM use while
preserving success on the A014 workload. The next question is whether those
pieces can become one usable autonomous runtime rather than a collection of
qualified subsystems.

## 4. What is still missing after A014

A014 does **not** yet provide a product-style runtime where the user types a
normal request and the system autonomously carries it to completion.

The qualified post-A014 path is roughly:

`ordinary EN/TH text`
â†’ A014 structural routing
â†’ inferred `StructuralNeed`
â†’ A013 signal-gated relation-aware recall

A009 is still a separate frozen integrated loop. Its
`CognitiveLoopRequest` expects prepared fields such as:

- `goal_text`;
- `familiarity_cue`;
- `root_procedure_id`;
- loop/model policies;
- prepared retrieval/procedure context supplied by collaborators.

Therefore the caller still has to know too much about the internal architecture.
There is no single public runtime entry point equivalent to:

`run("normal user message") -> final completed result`

There is also no qualified path yet for controlled real-world tool/OS/API side
effects.

## 5. User's final product intent

The user wants the long-term system to reach **C: real end-to-end autonomous
execution**.

The desired eventual experience is:

> The user types ordinary Thai or English text only. The system determines what
> the request requires, obtains the relevant knowledge, reasons and retrieves
> selectively, chooses or constructs an execution strategy, runs it, observes
> results, recovers when necessary, invokes the model only where it adds value,
> uses external tools when authorized, verifies completion, and returns the
> final result without the user manually supplying internal policies or IDs.

The user explicitly chose to pursue **Approach 3**:

**Build a new unified agent runtime subsystem, rather than simply wrapping A009
or mutating A009 into a natural-language endpoint.**

The reason is strategic: A005-A014 already demonstrate enough feasibility that
the next architecture should be designed around the intended end state instead
of accumulating adapters around a historically frozen research loop.

Historical A009/A011-A014 components remain valuable as qualified reference
implementations, controls, reusable primitives, and regression oracles. They do
not have to remain the permanent top-level runtime architecture.

## 6. Required staged strategy: target C, prove A first

Although the final product target is C, the next implementation must first
prove **Stage A**.

### Stage A â€” internal end-to-end autonomous runtime

Input:

- ordinary user text;
- request identity;
- optional language hint or automatically inferred language.

The user must **not** have to provide:

- `StructuralNeed`;
- relation types;
- procedure ID;
- retrieval cue tiers;
- loop/recovery policy;
- expected answer/target IDs;
- benchmark labels.

The unified runtime should autonomously perform enough of the following to reach
a final internal result:

1. normalize/understand the request;
2. determine request/task intent;
3. decide what memory/retrieval is needed;
4. perform vector retrieval;
5. infer structural/relation needs;
6. perform bounded relation expansion only when justified;
7. assemble a bounded working context;
8. resolve/select an executable procedure or strategy;
9. execute internal procedures;
10. observe result/mismatch;
11. recover/re-plan within explicit budgets;
12. invoke the model selectively when deterministic paths are insufficient;
13. determine terminal success/failure;
14. produce a final answer/result plus inspectable trace/provenance.

**Stage A must have no real external side effects.**

No file deletion, process control, network mutation, email sending, real API
writes, or OS/tool mutations belong in the first proof.

This is not a retreat from C. Stage A isolates the core architecture so that
end-to-end correctness and efficiency can be measured before tool safety and
external-state nondeterminism are introduced.

### Future Stage B â€” read-only grounded tools

After Stage A is qualified, a later milestone may add read-only external
capabilities such as:

- reading files;
- querying repositories;
- fetching current information;
- inspecting system state;
- other non-mutating observations.

### Future Stage C â€” controlled real actions

The final target may add mutating tools/actions such as:

- editing/writing files;
- running commands;
- changing system state;
- calling write APIs;
- sending messages;
- other authorized real-world side effects.

Stage C must introduce explicit capability controls, authorization policy,
idempotency/retry semantics, effect journaling, verification, and rollback or
compensation where meaningful. Do not mix these safety questions into the first
Stage A qualification.

## 7. Architectural direction locked by the user

Do **not** implement A015 as only:

`A014 -> A013 -> adapter -> existing run_cognitive_loop()`

with A009 remaining the permanent orchestration center.

Instead design a new top-level subsystem, provisionally called something like:

`flywire_asca.agent_runtime`

or another name approved in the A015 design.

The exact name is not frozen yet.

The new subsystem should own the end-to-end control state and expose a small,
human-facing input contract. Existing qualified components can be invoked behind
well-defined adapters or service boundaries.

A likely conceptual topology is:

`UserRequest`
â†’ Request Interpretation
â†’ Context/Memory Acquisition
â†’ Structural/Relational Routing
â†’ Working Context Assembly
â†’ Strategy/Procedure Resolution
â†’ Execution
â†’ Observation
â†’ Recovery/Re-plan
â†’ Model Assistance when needed
â†’ Terminal Verification
â†’ `AgentResult`

This is a conceptual direction, not yet an approved detailed spec. The A015
design must decide the actual boundaries after inspecting current source.

## 8. Critical design principles for A015

The next design should preserve these principles unless evidence shows a better
alternative.

### 8.1 Natural-language-first public contract

Top-level callers should provide ordinary text, not internal benchmark metadata
or preselected architecture controls.

### 8.2 Target-free runtime

No expected answer IDs, expected relation labels, evaluator truth, benchmark
labels, or post-hoc correctness may enter runtime control.

### 8.3 Selectivity remains evidence-driven

Do not make every subsystem or model call always-on merely because the new
runtime is unified.

A014 strongly suggests that deterministic routing first with selective model
fallback can reduce unnecessary model use.

### 8.4 Bounded autonomy

The runtime needs explicit budgets for:

- model calls;
- retrieval rounds;
- relation traversal;
- procedure/strategy attempts;
- recovery/re-plan rounds;
- context growth;
- eventual tool calls in later stages.

â€œAutonomousâ€ must not mean â€œunbounded loop.â€

### 8.5 Inspectable trace

A successful result must still make it possible to answer:

- what was inferred;
- what memories were used;
- whether relations were traversed;
- what strategy/procedure was selected;
- when/why the model was invoked;
- what recovery occurred;
- why the runtime declared success or failure.

### 8.6 Historical qualification remains historical

Do not mutate A009 or A011-protected source merely to make A015 easier.

If A015 reuses concepts from them, prefer new components/adapters and preserve
the frozen evidence chain.

### 8.7 No premature graph-first architecture

The project name ASCA does not require a persistent graph database or a
graph-first implementation. A012/A013 justify bounded explicit relation
semantics in their qualified scope, not a universal graph substrate.

### 8.8 No hidden direct-model baseline advantage

A015 qualification must compare against a direct-model baseline using the same
task input and a fair comparable completion contract.

## 9. A015 research questions the design should answer

The next architectural design should explicitly answer at least these questions:

1. What is the minimal top-level `AgentRequest` contract?
2. What is a successful `AgentResult`?
3. How does the system infer task intent without benchmark leakage?
4. How are retrieval and A014 structural routing sequenced?
5. How are A013 relation results integrated into the unified working context?
6. How is a root procedure/strategy selected when the user does not provide a
   procedure ID?
7. What happens when no suitable stored procedure exists?
8. When can the model propose a procedure/plan, and how is it validated before
   execution?
9. What observations constitute mismatch/failure?
10. What recovery/re-plan states are allowed?
11. What are the hard loop/cost budgets?
12. When does the model get called and what evidence is it allowed to see?
13. How is final completion verified independently of the model saying
   â€œsuccessâ€?
14. How can Stage A remain side-effect-free while keeping an interface that can
   later support Stage B/C?
15. Which existing A003-A014 components should be reused unchanged, wrapped,
   superseded, or treated only as baselines?
16. How will A015 be compared with direct `qwen3.5:4b`?

## 10. Required A015 qualification philosophy

A015 should not be considered successful merely because the new runtime can run
a demo.

Freeze a task workload **before tuning the runtime to it**.

The workload should include both Thai and English and should contain several
task families, not just relation lookup. Candidate families should include:

- direct factual/context retrieval;
- relation-dependent questions;
- procedural tasks solvable from stored procedures;
- cases requiring recovery after an initial mismatch;
- cases where no procedure is available and selective model assistance is
  appropriate;
- direct/simple cases where heavy machinery should remain off;
- ambiguity/safety controls;
- explicit failure cases where the correct behavior is bounded failure rather
  than fabricated success.

The design should determine exact counts before implementation.

## 11. Baselines and metrics required for A015

At minimum compare:

### Unified ASCA runtime

The new A015 path with all intended Stage A selection/recovery behavior.

### Direct model baseline

Pinned `qwen3.5:4b` receiving the same ordinary task input under a frozen
prompt/completion contract.

Useful ablations may be included if they answer architecture questions, but do
not create unnecessary variants.

Measure at least:

- task completion success;
- final-state correctness / answer correctness;
- false-success count;
- bounded-failure correctness;
- model invocation count;
- prompt tokens;
- generated tokens;
- retrieval query count;
- vector scored count;
- selected/active working-context size;
- relation invocation count;
- relation scanned edges / visited nodes;
- procedure/strategy attempt count;
- recovery/re-plan count;
- observed stage-level and end-to-end duration;
- deterministic/repeatability metrics where applicable;
- provenance/identity/budget/integrity failures.

Do not collapse these into a synthetic scalar â€œefficiency scoreâ€ unless a later
design explicitly justifies one.

The primary architecture decision should use predeclared decision rules.

## 12. Important evidence from earlier work that must shape A015

### A010 caution

A010 proved that â€œselectiveâ€ does not automatically mean â€œless total work.â€

On its frozen primary comparison:

- ASCA procedure successes: 7;
- dense successes: 8;
- ASCA queries: 28;
- dense queries: 27;
- ASCA scored vectors: 1984;
- dense scored vectors: 1440;
- ASCA cumulative selected items: 66;
- dense cumulative selected items: 480;
- ASCA peak selected: 12;
- dense peak selected: 256.

Outcome: `NOT_SUPPORTED`.

Therefore A015 must measure retrieval/recovery overhead explicitly rather than
assuming the unified selective runtime is more efficient.

### A014 positive signal

A014 shows that one specific selective mechanism *can* materially reduce model
use without losing success on its frozen workload.

This is encouraging evidence, not proof that the full unified runtime will win.

A015 exists to test that larger claim.

## 13. Historical outcomes that must remain intact

- A005: `VECTOR_SUFFICIENT`
- A006: `NOT_SUPPORTED`
- A007: `SUPPORTED`
- A008: `SUPPORTED`
- A009: `SUPPORTED`
- A010: `NOT_SUPPORTED`
- A011 frozen v0.x: `ENGINEERING_QUALIFIED`
- A012: `EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED`
- A013: `SIGNAL_GATED_RELATION_JUSTIFIED`
- A014: `HYBRID_STRUCTURAL_ROUTING_JUSTIFIED`

A011 frozen anchors remain:

- profile SHA256:
  `add06f285bf6decc7d492b987d3769dc64db4cb3d0177c8c6586d50ee5f6d46d`;
- protected path count: 67;
- protected mode/path/blob SHA256:
  `8df49f05fe54de43667ab2f8ef5de2caae9376ffedf2cb8f8d26f0e4abcca6b6`.

## 14. Process state and gates for the next session

This next milestone is an **architectural** change.

The user has approved the high-level direction:

- final target: C;
- first proof: Stage A;
- architecture family: Approach 3 / new unified agent runtime.

This approval means the next session does **not** need to ask the user to choose
between the old three approaches again.

However, the detailed A015 architecture has not yet been written or approved.

Follow the architectural design workflow:

1. verify live Git/GitHub/runtime;
2. read this handoff and the required files below;
3. inspect the actual A009/A013/A014/public model/procedure interfaces;
4. refine the A015 architecture and benchmark contract;
5. present the detailed design in sections for user review;
6. once conversational design is approved, write the design spec under
   `docs/superpowers/specs/`;
7. commit the design spec;
8. perform spec self-review;
9. user reviews/approves the written spec;
10. write the implementation plan under `docs/superpowers/plans/`;
11. user reviews the plan and selects execution method;
12. only then activate the A015 task/Issue/branch/worktree according to the plan
    and implement with TDD.

Do not claim that the high-level Approach 3 choice pre-approves a design document
that does not yet exist.

## 15. Files to read first in the next session

Read these before designing A015:

1. `docs/development/reports/ASCA-20261011-full-session-handoff-post-a014-a015-unified-agent-runtime-direction.md`
2. `docs/development/reports/ASCA-20261011-A014-structural-need-inference.md`
3. `docs/development/reports/ASCA-20261011-full-session-handoff-a014-completed.md`
4. `docs/development/tasks/CURRENT.md`
5. `docs/development/tasks/ROADMAP.md`
6. `docs/development/QUALIFICATION-MATRIX.md`
7. `docs/architecture/ASCA-PRE-A011-SNAPSHOT.md`
8. A009 design/report and current `src/flywire_asca/integrated_loop/`
9. A013 report and current `src/flywire_asca/relational_activation/`
10. A014 design/report and current `src/flywire_asca/structural_routing/`
11. current `src/flywire_asca/model/`
12. current `src/flywire_asca/procedural_memory/`

Also inspect current architecture tests before proposing new package dependencies.

## 16. Suggested initial package direction

Not frozen, but the next design should evaluate a new top-level package such as:

`src/flywire_asca/agent_runtime/`

Possible responsibilities to separate internally:

- request/result contracts;
- intent/task analysis;
- context acquisition;
- strategy/procedure resolution;
- execution state machine;
- observation/evaluation;
- recovery/re-plan controller;
- selective model assistance;
- trace/provenance;
- budget accounting.

Avoid building one monolithic controller file.

Stage B/C tool execution should eventually plug into a capability/effect
interface rather than being hardcoded into Stage A.

## 17. Definition of success for the first A015 implementation

The first A015 Stage A implementation should be considered successful only if a
caller can submit ordinary Thai or English task text without manually supplying
internal IDs/policies and the runtime can autonomously reach a verified terminal
result on the frozen workload.

The qualification must then answer, with measured evidence:

> Does the new unified ASCA runtime preserve or improve task completion while
> reducing unnecessary model dependence and keeping retrieval/recovery work
> bounded compared with a direct pinned-model baseline?

A valid negative or mixed result must remain publishable. Do not tune the
benchmark after seeing the result merely to force a positive conclusion.

## 18. Long-term C requirements to keep in the architecture now

Even though Stage A has no side effects, do not design it in a way that makes C
require a rewrite.

Reserve clean seams for future:

- tool/capability registry;
- read vs write capability classification;
- explicit authorization boundary;
- action proposal vs action execution;
- effect journal;
- idempotency keys;
- timeout/cancellation;
- retry policy;
- result observation;
- postcondition verification;
- rollback/compensation when possible;
- human confirmation for classes of high-impact action.

Do not implement all of these in Stage A. The requirement is architectural
extensibility, not premature complexity.

## 19. Ready-to-paste prompt for the new session

Use the following prompt to resume:

---

`@use-local-workspace à¸—à¸³ funggier/FlyWireASCA à¸•à¹ˆà¸­à¸ˆà¸²à¸ Full Handoff à¸¥à¹ˆà¸²à¸ªà¸¸à¸” à¹‚à¸”à¸¢à¸­à¹ˆà¸²à¸™ docs/development/reports/ASCA-20261011-full-session-handoff-post-a014-a015-unified-agent-runtime-direction.md à¸à¹ˆà¸­à¸™à¹€à¸›à¹‡à¸™à¸­à¸±à¸™à¸”à¸±à¸šà¹à¸£à¸ à¸ˆà¸²à¸à¸™à¸±à¹‰à¸™à¸•à¸£à¸§à¸ˆ live Git/GitHub/runtime à¹à¸¥à¸°à¸­à¹ˆà¸²à¸™ A014 final report/handoff, CURRENT.md, ROADMAP.md, QUALIFICATION-MATRIX.md, ASCA-PRE-A011-SNAPSHOT.md à¸£à¸§à¸¡à¸–à¸¶à¸‡ source à¸‚à¸­à¸‡ integrated_loop, relational_activation, structural_routing, model à¹à¸¥à¸° procedural_memory à¹‚à¸”à¸¢à¸¢à¸¶à¸”à¸ªà¸–à¸²à¸™à¸°à¸ªà¸”à¹€à¸›à¹‡à¸™ authoritative source`

`à¹€à¸›à¹‰à¸²à¸«à¸¡à¸²à¸¢à¸–à¸±à¸”à¹„à¸›à¸„à¸·à¸­ A015 End-to-End Unified Agent Runtime à¹‚à¸”à¸¢à¸œà¸¹à¹‰à¹ƒà¸Šà¹‰à¹„à¸”à¹‰à¹€à¸¥à¸·à¸­à¸ Architecture Direction à¹à¸šà¸š Approach 3 à¹à¸¥à¹‰à¸§: à¸ªà¸£à¹‰à¸²à¸‡ unified agent runtime à¹ƒà¸«à¸¡à¹ˆà¹€à¸›à¹‡à¸™ top-level architecture à¹„à¸¡à¹ˆà¹ƒà¸Šà¹ˆà¹à¸„à¹ˆ wrapper à¸„à¸£à¸­à¸š A009 à¹à¸¥à¸°à¹„à¸¡à¹ˆà¹à¸à¹‰ frozen A009/A011 history à¹€à¸žà¸·à¹ˆà¸­à¹ƒà¸«à¹‰à¸žà¸´à¸¡à¸žà¹Œà¸‚à¹‰à¸­à¸„à¸§à¸²à¸¡à¸ à¸²à¸©à¸²à¹„à¸—à¸¢/à¸­à¸±à¸‡à¸à¸¤à¸©à¸›à¸à¸•à¸´à¸­à¸¢à¹ˆà¸²à¸‡à¹€à¸”à¸µà¸¢à¸§à¹à¸¥à¹‰à¸§à¸£à¸°à¸šà¸šà¸ˆà¸±à¸” intent, retrieval, structural/relation routing, working context, strategy/procedure selection, execution, observation, recovery/re-plan, selective model assistance à¹à¸¥à¸° terminal verification à¹€à¸­à¸‡`

`à¹€à¸›à¹‰à¸²à¸«à¸¡à¸²à¸¢à¸›à¸¥à¸²à¸¢à¸—à¸²à¸‡à¸„à¸·à¸­ Stage C à¸—à¸µà¹ˆà¸ªà¸²à¸¡à¸²à¸£à¸–à¹ƒà¸Šà¹‰ real tools/actions à¹„à¸”à¹‰ à¹à¸•à¹ˆ A015 à¸£à¸­à¸šà¹à¸£à¸à¸•à¹‰à¸­à¸‡à¸žà¸´à¸ªà¸¹à¸ˆà¸™à¹Œ Stage A à¹ƒà¸«à¹‰à¹„à¸”à¹‰à¸à¹ˆà¸­à¸™: internal end-to-end autonomous runtime à¹à¸šà¸šà¹„à¸¡à¹ˆà¸¡à¸µ external side effects à¹à¸¥à¹‰à¸§à¹€à¸›à¸£à¸µà¸¢à¸šà¹€à¸—à¸µà¸¢à¸šà¸à¸±à¸š direct pinned qwen3.5:4b à¸­à¸¢à¹ˆà¸²à¸‡à¸¢à¸¸à¸•à¸´à¸˜à¸£à¸£à¸¡à¸”à¹‰à¸§à¸¢ frozen bilingual task workload à¸§à¸±à¸” success/final correctness/false success/model calls/tokens/retrieval work/relation work/procedure attempts/recovery/context size/latency à¹à¸¥à¸° integrity à¹‚à¸”à¸¢à¸•à¹‰à¸­à¸‡à¸ˆà¸³ A010 à¹„à¸§à¹‰à¸§à¹ˆà¸²à¸„à¸§à¸²à¸¡ selective à¹„à¸¡à¹ˆà¹„à¸”à¹‰à¹à¸›à¸¥à¸§à¹ˆà¸²à¸›à¸£à¸°à¸«à¸¢à¸±à¸” retrieval à¹€à¸ªà¸¡à¸­ à¹à¸¥à¸°à¹ƒà¸Šà¹‰ A014 à¹€à¸›à¹‡à¸™à¸«à¸¥à¸±à¸à¸à¸²à¸™à¸§à¹ˆà¸²à¸à¸²à¸£ selective model invocation à¸¡à¸µà¸¨à¸±à¸à¸¢à¸ à¸²à¸ž`

`à¸‡à¸²à¸™à¸™à¸µà¹‰à¹€à¸›à¹‡à¸™ architectural path: à¹„à¸¡à¹ˆà¸•à¹‰à¸­à¸‡à¸¢à¹‰à¸­à¸™à¸à¸¥à¸±à¸šà¸¡à¸²à¸–à¸²à¸¡à¹€à¸¥à¸·à¸­à¸ Approach 1/2/3 à¸­à¸µà¸ à¹à¸•à¹ˆà¹ƒà¸«à¹‰à¸ªà¸³à¸£à¸§à¸ˆ source à¸ªà¸”à¹à¸¥à¹‰à¸§à¸­à¸­à¸à¹à¸šà¸šà¸£à¸²à¸¢à¸¥à¸°à¹€à¸­à¸µà¸¢à¸” A015, benchmark contract, package boundaries, state machine, budgets, completion verification à¹à¸¥à¸° future tool/effect seam à¹ƒà¸«à¹‰à¸„à¸£à¸š à¸ˆà¸²à¸à¸™à¸±à¹‰à¸™à¹€à¸ªà¸™à¸­ detailed design à¹ƒà¸«à¹‰à¸œà¸¡ review à¸à¹ˆà¸­à¸™à¹€à¸‚à¸µà¸¢à¸™ spec; à¹€à¸¡à¸·à¹ˆà¸­ design à¸œà¹ˆà¸²à¸™à¹ƒà¸«à¹‰à¹€à¸‚à¸µà¸¢à¸™/commit spec à¹à¸¥à¹‰à¸§à¸£à¸­ written-spec approval à¸à¹ˆà¸­à¸™à¸—à¸³ implementation plan à¸•à¸²à¸¡ Superpowers gates à¸«à¹‰à¸²à¸¡ activate A015 issue/task à¸«à¸£à¸·à¸­à¹€à¸£à¸´à¹ˆà¸¡ implementation à¸à¹ˆà¸­à¸™à¸–à¸¶à¸‡ gate à¸—à¸µà¹ˆà¸–à¸¹à¸à¸•à¹‰à¸­à¸‡ à¸«à¹‰à¸²à¸¡ reset/clean/rebase/force-push à¸«à¹‰à¸²à¸¡à¹à¸•à¸° FlyWireLLM à¹à¸¥à¸°à¸•à¹‰à¸­à¸‡à¸£à¸±à¸à¸©à¸² A005-A014 historical outcomes à¸à¸±à¸š A011 frozen-source guard à¸—à¸±à¹‰à¸‡à¸«à¸¡à¸”`

---

## 20. Final handoff state

This handoff intentionally does not activate A015.

It records a user-approved **architectural direction** and the rationale needed
for the next session to proceed directly into detailed A015 design without
reconstructing the history or re-asking the already-decided Approach 3 choice.
