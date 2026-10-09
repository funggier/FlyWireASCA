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
- [Development tasks](docs/development/tasks/) once A001 creates the task ledger

## Current stage

A009 - Integrated Cognitive Loop is **ACTIVE** on
`research/a009-integrated-cognitive-loop` (GitHub Issue #9).

A009 integrates A003 familiarity, A005 retrieval, A006 working-set selection,
A007 bounded expansion, and A008 procedural execution while preserving each
milestone's evidence boundary. The primary A009 path uses `SINGLE_BEST`,
A007 `SIGNAL_DRIVEN`, and A008 `CHUNKED`, with
`MISMATCH_DRIVEN_RECOVERY` as the primary integrated-loop policy.

Historical outcomes remain unchanged:

- A006 selective-convergence hypothesis: `NOT_SUPPORTED`;
- A007 structural-expansion hypothesis: `SUPPORTED`;
- A008 procedural-memory hypothesis: `SUPPORTED`.

A008's recommended representation remains `CHUNKED`: reusable hierarchical
procedures with explicit step-level checkpoints. A009 keeps A008 zero-auto-retry
and models every higher-level replay as a fresh bounded attempt from an
immutable pre-execution snapshot.

These are control/evidence boundaries; they are not claims of lower hardware
cost, energy use, token use, or faster real-world tool execution.


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