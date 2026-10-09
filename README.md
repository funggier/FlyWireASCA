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

A008 - Procedural Memory / Skill Chunking is active.

The primary architecture is `CHUNKED`: reusable hierarchical procedures with
explicit step-level expected-outcome checkpoints. `FLAT` is the correctness
baseline and `BLIND_CHUNKED` is a negative control for coarser failure
localization.

A008 uses a deterministic simulator only. It does not execute real tools/APIs,
use Qwen3.5:4b or Ollama, traverse a semantic graph, or automatically retry
failed actions. FlyWireLLM remains paused and independent.


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