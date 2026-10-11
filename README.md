# ProjectASCA

ProjectASCA is an independent research and engineering project for
**Associative Selective Cognition Architecture (ASCA)**.

ASCA is a research direction rather than a requirement that every component be
associative or selective. Dense, symbolic, neural, retrieval-based, or hybrid
mechanisms may be used when evidence shows they are the better engineering
choice.

## Project boundary

ProjectASCA is independent from `funggier/FlyWireLLM`.

- **ProjectASCA** studies cognitive control, familiarity, recall, working-set
  selection, surprise/uncertainty, procedural memory, and related architecture.
- **FlyWireLLM** remains a separate language-model architecture and training
  project.

ProjectASCA is model-agnostic. It may use local or remote models through a
model-adapter boundary, but no specific LLM, Transformer, provider, or cloud
service is a mandatory core dependency.

The current model-under-test is local `qwen3.5:4b` through Ollama. FlyWireLLM
remains an independent project and a future adapter candidate rather than an
A004 dependency.

## Repository identity

The current repository is [funggier/ProjectASCA](https://github.com/funggier/ProjectASCA),
renamed from FlyWireASCA on 2026-10-12. The primary checkout is
`T:\Space\Projects\ProjectsAI\ProjectASCA`.

The preserved `v0.1.0` baseline and A001-A014 history remain unchanged.
The existing Python namespace `flywire_asca` and distribution identity
`FlyWireASCA` / `0.1.0.dev0` are retained for frozen-source compatibility.
See [Repository rename record](docs/development/reports/ASCA-20261012-repository-rename-projectasca.md).

A015 is in conversational architecture design for a new unified agent runtime;
its task is not activated. The selected direction is Approach 3, targeting
Stage C while qualifying internal Stage A first.

## Development method

Development is **task-driven** and **evidence-driven**.

Every substantial task records its goal, scope, status, acceptance criteria,
current action, next action, and qualification evidence. Work is not considered
complete merely because code exists.

Start with:

- [Architecture design](docs/superpowers/specs/2026-10-08-asca-architecture-design.md)
- [Implementation plans](docs/superpowers/plans/)
- [Development tasks](docs/development/tasks/)

## Preserved release

`v0.1.0` is the first preserved post-A014 / pre-A015 baseline. It contains the
qualified A001-A014 system and evidence while A015 remains unactivated. See
docs/development/reports/ASCA-20261011-v0.1.0-release.md for the release
record.

## Current stage

A011 - ASCA v0.x Qualification is **DONE**. The frozen `asca-v0x-a011-v1`
profile is `ENGINEERING_QUALIFIED` with separate preserved research outcomes:

- A006: `NOT_SUPPORTED`
- A007: `SUPPORTED`
- A008: `SUPPORTED`
- A009: `SUPPORTED`
- A010: `NOT_SUPPORTED`

A009 - Integrated Cognitive Loop remains `SUPPORTED`. Its qualified primary path
is `SINGLE_BEST` + A007 `SIGNAL_DRIVEN` + A008 `CHUNKED` with
`MISMATCH_DRIVEN_RECOVERY`.

A010 - Dense/Non-selective Baseline Comparison is **DONE** with portable outcome
`NOT_SUPPORTED`: ASCA/dense query counts are 28/27, scored-vector counts are
1984/1440, and cumulative selected counts are 66/480. This result answers a
different comparison question and does not rewrite A009.

A012 - Relational Reasoning / Structure Decision Gate is **DONE**. The frozen
portable experiment compares the real A005 Vector + Metadata retrieval primitive
with bounded explicit typed relation traversal on causal, temporal, ownership,
part-of, used-for, path and identity-sensitive controlled workloads.

A012's frozen portable evidence now concludes
`EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED` for the declared relation-dependent
workload: bounded relation traversal recovers 6 cases that Vector + Metadata
alone does not, with zero regressions and zero identity/provenance/budget/cycle
failures. This is not a claim that a persistent graph database or graph-first
architecture is generally superior.

A013 - Selective Relational Activation / Hybrid Recall Integration Gate is
**DONE**. A013 introduces target-free bounded relation expansion above the A005
vector retrieval and A012 relation semantics, then compares `VECTOR_ONLY`,
`ALWAYS_RELATION`, and `SIGNAL_GATED_RELATION` on a frozen mixed workload.

A013's portable result is `SIGNAL_GATED_RELATION_JUSTIFIED` for that declared
scope. Vector-only succeeds on 10/16 valid cases, while always-relation and
signal-gated both succeed on 16/16. Signal-gated relation preserves all 6
relation-dependent recoveries and all 6 direct-vector controls while reducing
relation invocations from 16 to 10, scanned edges from 16 to 11, and relation
visited nodes from 29 to 18. False/missed activation and all declared
identity/provenance/budget/duplicate-visit failure counts are zero.

The A013 signal is an explicit typed `StructuralNeed`. A014 now supplies a
qualified target-free way to infer that signal from ordinary English/Thai query
text on its frozen bilingual workload.

A014 - Structural Need Inference / Query Intent Routing Gate is **DONE**. Its
physical result is `HYBRID_STRUCTURAL_ROUTING_JUSTIFIED`: rule-only succeeds on
27/32 cases; model-only and hybrid both succeed on 32/32; hybrid has zero
false/missed activations and reduces model invocations from 32 to 9. A014 does
not yet provide a single production-style end-to-end runtime that carries
arbitrary text through A009 cognition and real tool/action execution until task
completion.

A011 remains the qualification of its frozen v0.x profile; it does not
automatically qualify A012, A013, or A014. A012-A014 are separate post-A011
research gates with their own evidence.

These results are control/retrieval/procedure evidence. They are not claims of
lower FLOPs, lower energy, lower token use, general speed superiority, or safe
real-world side-effect replay.

## Claims boundary

ProjectASCA does **not** currently claim:

- equivalence to human cognition;
- biological fidelity;
- consciousness or AGI;
- lower energy use than the human brain;
- superiority over dense LLMs;
- production safety.

Research claims must follow measured, reproducible evidence.

## License

Repository source code is licensed under the MIT License. See [LICENSE](LICENSE).

External datasets, model weights, third-party code, and research artifacts keep
their own licenses and terms; repository MIT licensing does not relicense them.