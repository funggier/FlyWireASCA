# FlyWireASCA

FlyWireASCA is an independent research and engineering project for
**Associative Selective Cognition Architecture (ASCA)**.

ASCA is a research direction rather than a requirement that every component be
associative or selective. Dense, symbolic, neural, retrieval-based, or hybrid
mechanisms may be used when evidence shows they are the better engineering
choice.

## Project boundary

FlyWireASCA is independent from `funggier/FlyWireLLM`.

- **FlyWireASCA** studies cognitive control, familiarity, recall, working-set
  selection, surprise/uncertainty, procedural memory, and related architecture.
- **FlyWireLLM** remains a separate language-model architecture and training
  project.

FlyWireASCA is model-agnostic. It may use local or remote models through a
model-adapter boundary, but no specific LLM, Transformer, provider, or cloud
service is a mandatory core dependency.

The current model-under-test is local `qwen3.5:4b` through Ollama. FlyWireLLM
remains an independent project and a future adapter candidate rather than an
A004 dependency.

## Development method

Development is **task-driven** and **evidence-driven**.

Every substantial task records its goal, scope, status, acceptance criteria,
current action, next action, and qualification evidence. Work is not considered
complete merely because code exists.

Start with:

- [Architecture design](docs/superpowers/specs/2026-10-08-asca-architecture-design.md)
- [Implementation plans](docs/superpowers/plans/)
- [Development tasks](docs/development/tasks/)

## Current stage

A011 - ASCA v0.x Qualification is **DONE**. The frozen `asca-v0x-a011-v1`
profile is `ENGINEERING_QUALIFIED` with separate preserved research outcomes:

- A006: `NOT_SUPPORTED`
- A007: `SUPPORTED`
- A008: `SUPPORTED`
- A009: `SUPPORTED`
- A010: `NOT_SUPPORTED`

The qualified A009 primary path remains `SINGLE_BEST` + A007 `SIGNAL_DRIVEN` +
A008 `CHUNKED` with `MISMATCH_DRIVEN_RECOVERY`. A010's dense/non-selective
comparison remains a valid `NOT_SUPPORTED` research result and does not rewrite
A009.

A012 - Relational Reasoning / Structure Decision Gate is **ACTIVE** on GitHub
Issue #14 after explicit user authorization. It will compare the real A005 Vector + Metadata
retrieval primitive with bounded explicit typed relation traversal on causal,
temporal, ownership, part-of, used-for, path and identity-sensitive controlled
workloads.

A012 does not assume that a graph is required. Its portable evidence may
conclude `EXPLICIT_RELATION_TRAVERSAL_JUSTIFIED`,
`VECTOR_METADATA_REMAINS_SUFFICIENT`, or `MIXED`.

A011 remains the qualification of its frozen v0.x profile; it does not
automatically qualify A012.

These results are control/retrieval/procedure evidence. They are not claims of
lower FLOPs, lower energy, lower token use, general speed superiority, or safe
real-world side-effect replay.

## Claims boundary

FlyWireASCA does **not** currently claim:

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
