# FlyWireASCA Architecture Design Specification

Date: 2026-10-08
Status: DRAFT FOR USER REVIEW
Planned repository: funggier/FlyWireASCA
Planned local workspace: T:\Space\Projects\ProjectsAI\FlyWireASCA
License: MIT
Architecture name: Associative Selective Cognition Architecture (ASCA)

## 1. Purpose

FlyWireASCA is an independent research and engineering project for experimenting with a cognitive architecture that allocates memory, reasoning, learned procedures, and computational effort according to current relevance and uncertainty.

The name "Associative Selective Cognition Architecture" describes the research direction, not a rule that every component must be associative or selective. Components should use the mechanism that is empirically appropriate for the task.

FlyWireASCA is intentionally separate from funggier/FlyWireLLM. FlyWireLLM remains a language-model baseline and training project. FlyWireASCA may later use FlyWireLLM or other models through adapters, but no specific LLM, Transformer, neural architecture, or model provider is a mandatory dependency.

## 2. Core hypothesis

A capable cognitive system need not activate all stored information, all learned procedures, or all available compute for every input.

The first ASCA hypothesis is that a useful system can reduce active computation while preserving or improving task quality by combining:

1. fast familiarity estimation;
2. context-sensitive selective activation;
3. associative recollection when needed;
4. bounded working-memory construction;
5. reusable procedural or skill chunks for familiar actions;
6. prediction and outcome monitoring;
7. uncertainty/surprise-driven expansion of attention, memory, reasoning, or action;
8. evidence-driven learning and memory updates.

This is a hypothesis to test, not a claim of biological equivalence.

## 3. Design principles

### 3.1 Evidence before architecture claims

Every major mechanism must have a baseline, benchmark, measurable acceptance criterion, and reproducible evidence. A component is not retained merely because it appears biologically plausible.

### 3.2 Selectivity is conditional, not ideological

Dense processing is acceptable when it is cheaper, safer, or more accurate. Selective processing is used where it produces measurable value.

### 3.3 Familiarity is not truth

A strong familiarity signal means that a cue or pattern is recognized or strongly associated. It does not prove identity, factual truth, causal correctness, or relevance.

The architecture must distinguish identity relations from weaker associations such as same-name, similarity, co-occurrence, context, or analogy.

### 3.4 Recall is not a single lookup

The architecture must permit iterative recollection. A cue may activate partial information, which activates further associations, until a useful working set is assembled or the retrieval process declares insufficient evidence.

### 3.5 Procedures can be chunked

Frequently repeated successful action sequences may be represented as reusable procedural units. High-level execution should not require re-deriving every low-level step when the environment remains predictable.

### 3.6 Surprise can increase compute

Prediction mismatch, uncertainty, contradiction, unexpected novelty, or failed procedure execution may increase the allowed retrieval radius, reasoning depth, or action caution.

### 3.7 Persistent state is explicit

Working activation, goals, recently used memories, hypotheses, procedures, and uncertainty should be represented explicitly rather than being hidden only inside transient prompt text.

### 3.8 Safety through inhibition and bounded expansion

Spreading activation must be bounded. The architecture must support thresholds, budgets, inhibition, decay, competing hypotheses, and termination criteria to avoid uncontrolled graph expansion or infinite recall loops.

## 4. Initial cognitive loop

The first integrated ASCA loop is:

    Goal / Context
          |
          v
      Perception/Input
          |
          v
      Familiarity
          |
          v
    Selective Activation
       /          \
 familiar        novel/uncertain
    |                |
    v                v
 Procedure       Recall/Reasoning
    |                |
    +--------+-------+
             |
             v
       Working Set
             |
             v
      Decision/Action
             |
             v
    Prediction Monitor
        /         \
      match      surprise
        |           |
     continue   expand/reassess
                    |
                    +----> loop

This diagram defines a research loop, not an implementation mandate. Early prototypes may implement only a subset.

## 5. Initial subsystem boundaries

### 5.1 Familiarity Field

Purpose:
- estimate how familiar an input, entity, pattern, context, procedure, or relation is;
- provide low-cost activation hints before full retrieval.

Must not:
- equate familiarity with identity or truth;
- retrieve the complete memory store by default.

Possible outputs:
- familiarity score;
- familiarity type/vector;
- candidate index regions;
- confidence and provenance.

### 5.2 Associative Memory Fabric

Purpose:
- store memories once while allowing multiple typed retrieval paths;
- support entity, concept, event, temporal, spatial, procedural, similarity, causal, and contextual relations;
- support iterative activation spreading.

A memory can be reachable through multiple indices without duplicating the memory itself.

Relations must be typed. Examples:
- same_person
- same_name
- similar_to
- occurred_at
- occurred_before
- works_at
- caused_by
- used_for
- part_of
- co_occurs_with

Association strength and proposition confidence are separate values.

### 5.3 Working Set Controller

Purpose:
- select the small subset of active memories, hypotheses, goals, procedures, and observations needed for the current step;
- impose explicit budget and eviction/decay policies;
- preserve useful state across turns or action steps.

### 5.4 Surprise and Uncertainty Controller

Purpose:
- compare predicted/expected state with observed state;
- detect novelty, contradiction, failed retrieval, failed procedures, or ambiguous interpretation;
- adapt compute/retrieval/action budgets.

Expected behavior:
- familiar predictable state -> narrow/cheap processing;
- partial uncertainty -> broaden cautiously;
- high surprise/risk -> interrupt automatic procedure and invoke deeper recall/reasoning.

### 5.5 Procedural Memory / Skill Chunks

Purpose:
- represent reusable action sequences at multiple abstraction levels;
- allow a familiar sequence to run without reconstructing all low-level reasoning;
- expose links to semantic/causal explanations so the system can answer "why" even when the explanation is not needed during normal execution.

Procedures must remain interruptible by surprise, risk, policy, or explicit goal changes.

### 5.6 Core Reasoner / Model Adapter

Purpose:
- provide a stable interface to one or more reasoning/language models;
- allow FlyWireASCA benchmarks to compare different cores;
- avoid baking ASCA into a single LLM implementation prematurely.

A null/simple deterministic core should be possible for subsystem tests.

### 5.7 Action / Tool Adapter

Purpose:
- execute low-risk actions or tool calls;
- return observations and outcomes to the cognitive loop;
- support exploratory actions whose main value is information gathering.

Initial implementation must not assume physical robotics.

## 6. Memory classes

The architecture may support at least:

- familiarity traces;
- semantic memory;
- episodic memory;
- procedural memory;
- spatial/context memory;
- causal/explanatory links;
- working memory / current activation;
- provenance and source confidence.

These are conceptual classes. The implementation may share storage where appropriate.

## 7. Retrieval states

The first prototype should distinguish states such as:

- UNFAMILIAR
- FAMILIAR
- KNOWN_BUT_NOT_RECALLED
- PARTIAL_RECALL
- RECALLED
- CONFLICTING_RECALL
- INSUFFICIENT_EVIDENCE

These states are not required to be produced by a neural network.

## 8. Progressive activation contract

Retrieval should begin with the cheapest useful scope and expand only when needed.

Typical sequence:

1. exact/salient cue matching;
2. local associative neighborhood;
3. broader concept/context traversal;
4. full local memory search;
5. external knowledge/tool retrieval.

Each expansion must have:
- a trigger;
- a budget;
- a termination condition;
- measurable cost.

## 9. Baseline and evaluation philosophy

FlyWireASCA must keep non-selective baselines.

At minimum compare:
- direct/dense retrieval or processing;
- ASCA selective activation;
- ASCA with surprise-driven expansion disabled;
- ASCA with familiarity disabled where meaningful.

Primary evaluation categories:

- task correctness;
- recall accuracy;
- false familiarity rate;
- identity-confusion rate;
- router/activation miss rate;
- recovery after a miss;
- active memories / total memories;
- active modules / total modules;
- working-set size;
- retrieval expansions;
- model input tokens;
- estimated or measured compute;
- latency;
- memory I/O;
- procedural reuse rate;
- surprise detection;
- post-surprise recovery quality.

A useful efficiency summary may report quality per active computation, but no single scalar metric should replace the underlying measurements.

## 10. First research milestones

Task IDs use the prefix A###.

### A001 - Repository and Research Foundation

Goal:
Create the independent public repository and reproducible engineering foundation.

Deliverables:
- public GitHub repository funggier/FlyWireASCA;
- local workspace T:\Space\Projects\ProjectsAI\FlyWireASCA;
- MIT License;
- Python package skeleton;
- README with project boundary and claims boundary;
- task-ledger system;
- CURRENT.md resume pointer;
- test harness;
- CI;
- contribution/development conventions sufficient for reproducibility.

Acceptance:
- clean local worktree;
- local tests pass;
- CI pass on exact commit;
- local/remote synchronization verified;
- A001 evidence recorded.

### A002 - ASCA Architecture Contract

Goal:
Turn this design into versioned interfaces and invariants without implementing unnecessary cognitive complexity.

Deliverables:
- typed data contracts for cues, memories, relations, activation, working set, uncertainty, procedure, observation, and evidence;
- architecture invariants;
- baseline benchmark definitions;
- no dependence on a specific LLM.

Acceptance:
- interface tests;
- serialization/round-trip tests where relevant;
- architecture audit;
- exact-commit evidence.

### A003 - Familiarity Prototype

Goal:
Measure whether low-cost familiarity signals can narrow candidate memory regions without unacceptable misses.

Acceptance focus:
- familiar/unfamiliar discrimination;
- false familiarity;
- ambiguous same-name cases;
- cost relative to exhaustive baseline.

### A004 - Associative Memory and Recall

Goal:
Implement typed multi-index memory plus bounded progressive recollection.

Acceptance focus:
- one memory reachable through multiple cues;
- no identity collapse from same-name/similarity edges;
- multi-cue convergence;
- bounded graph traversal;
- provenance retained.

### A005 - Working Set and Selective Activation

Goal:
Build explicit active-state management and compare selective vs exhaustive activation.

Acceptance focus:
- quality parity or documented tradeoff;
- reduced active memory/compute;
- deterministic budget behavior.

### A006 - Surprise, Uncertainty, and Expansion

Goal:
Use prediction mismatch or uncertainty to increase retrieval/reasoning scope.

Acceptance focus:
- novelty detection;
- recovery after an initially insufficient route;
- bounded expansion;
- no uncontrolled loops.

### A007 - Procedural Memory and Skill Chunking

Goal:
Represent reusable hierarchical procedures and interrupt them when expected outcomes fail.

Acceptance focus:
- successful reuse;
- lower deliberative work on familiar sequences;
- interruption on mismatch;
- explanation/causal link can still be recalled.

### A008 - Integrated Cognitive Loop

Goal:
Integrate familiarity, recall, working set, procedures, surprise, and model/tool adapters into one bounded loop.

### A009 - Baseline Comparison

Goal:
Compare integrated ASCA against deliberately non-selective baselines on controlled workloads.

### A010 - First ASCA Qualification

Goal:
Freeze the first research-qualified architecture revision only if evidence supports it.

A010 is not required to claim biological equivalence, AGI, or superiority to modern LLMs.

## 11. Task-driven development contract

Every substantial task must have:
- Task ID and title;
- Goal;
- Scope / non-scope;
- Status: PLANNED / ACTIVE / BLOCKED / DONE;
- phases;
- acceptance criteria;
- evidence;
- current action;
- next action;
- exact commit SHA when qualified.

Repository task layout:

    docs/development/tasks/
        README.md
        CURRENT.md
        A001-...
        A002-...
        ...

Long sessions additionally create:

    docs/development/reports/
        ASCA-YYYYMMDD-<topic>-handoff.md

A handoff must record:
- authoritative branch and HEAD;
- local/remote synchronization;
- dirty/clean state;
- active processes if any;
- completed evidence;
- unresolved failures;
- current action;
- next exact action;
- do-not-do constraints;
- resume checks.

Git/GitHub/runtime state overrides stale prose when they disagree.

## 12. Evidence-driven completion

A task is not DONE merely because code exists.

Completion requires evidence appropriate to the task, which may include:
- focused tests;
- full regression;
- benchmark output;
- architecture audit;
- git diff --check;
- exact-commit qualification;
- CI for the same commit;
- remote synchronization.

Negative results are valid research outcomes and should be recorded rather than hidden.

## 13. Repository and licensing boundary

Initial repository:
- owner/name: funggier/FlyWireASCA
- visibility: public
- license: MIT

The MIT license applies to repository source code created for FlyWireASCA.

External datasets, model weights, third-party code, or research artifacts retain their own licenses/terms and must not be implicitly relicensed under MIT.

No raw copyrighted or restricted research data should be committed merely because the repository itself uses MIT.

## 14. Relationship to FlyWireLLM

FlyWireLLM:
- language-model architecture/training baseline;
- independently versioned;
- must not be modified automatically by FlyWireASCA.

FlyWireASCA:
- cognitive architecture research;
- may use FlyWireLLM later through an adapter;
- must support other cores so experiments do not conflate ASCA with one model.

Initial ASCA work must not interfere with an active FlyWireLLM training process.

## 15. Claims boundary

Until measured evidence exists, FlyWireASCA must not claim:
- equivalence to human cognition;
- biological fidelity;
- consciousness;
- AGI;
- lower energy use than the human brain;
- general superiority over dense LLMs;
- production safety.

The project may claim only the behavior and efficiency demonstrated by qualified experiments.

## 16. Initial implementation constraints

For the first implementation:
- Python-first;
- deterministic tests where practical;
- no mandatory cloud dependency;
- no mandatory external LLM;
- no database choice frozen until A002/A004 need it;
- no premature neural implementation of familiarity;
- no integration with active FlyWireLLM training;
- no large model training as part of A001/A002.

## 17. Open architectural choices intentionally deferred

The following are not frozen by this design:
- graph database vs embedded/local storage;
- neural vs symbolic/hybrid familiarity estimator;
- exact activation scoring formula;
- decay/recency formula;
- memory consolidation policy;
- MoE/conditional neural compute;
- SSM vs Transformer vs other core model;
- robotics/perception integration;
- long-term self-modification.

These choices require evidence from earlier milestones.

## 18. Success criterion for the first research cycle

The first research cycle succeeds if FlyWireASCA can demonstrate, on controlled benchmarks, that an explicit familiarity/recall/working-set/surprise loop can selectively activate a smaller relevant state while preserving useful task behavior and can recover when the initial selection is insufficient.

If the selective mechanism does not outperform a simpler baseline after accounting for complexity and cost, the architecture must record that result and simplify or change direction rather than preserve the mechanism for naming consistency.
