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

A009 - Integrated Cognitive Loop has a **qualified closure candidate** with
primary deterministic outcome `SUPPORTED`.

The frozen A009 fixture demonstrates:

- 2 genuine procedure-mismatch recoveries over `NO_PROCEDURE_RECOVERY`;
- 0 regressions;
- primary success coverage equal to `ALWAYS_MAX_SCOPE` (6 / 6 successful cases);
- 19 primary scope evaluations versus 27 for `ALWAYS_MAX_SCOPE`;
- maximum 3 procedure attempts and maximum scope index 2;
- 0 duplicate-execution-ID failures;
- 0 same-name ambiguity failures;
- CHUNKED/FLAT diagnostic equivalence 6 / 6;
- 0 model-control leakage failures;
- deterministic replay.

The primary path remains `SINGLE_BEST` + A007 `SIGNAL_DRIVEN` + A008
`CHUNKED`, with `MISMATCH_DRIVEN_RECOVERY` as the A009 recovery policy.

Historical outcomes remain unchanged:

- A006 selective-convergence hypothesis: `NOT_SUPPORTED`;
- A007 structural-expansion hypothesis: `SUPPORTED`;
- A008 procedural-memory hypothesis: `SUPPORTED`;
- A009 integrated-loop hypothesis: `SUPPORTED`.

Local physical integration is also GREEN with pinned
`qwen3-embedding:0.6b` retrieval and terminal-only `qwen3.5:4b` fallback.

A009 is fully integrated and GitHub Issue #9 is closed as completed.

A010 - Dense/Non-selective Baseline Comparison is now **ACTIVE** under GitHub
Issue #10. It compares the real A009 selective path against a deliberately
non-selective A005+A006 exhaustive baseline while preserving the historical
A009 `SUPPORTED` result.

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