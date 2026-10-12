# Choose and coordinate subagents

Use delegation to improve a concrete result. Consider elapsed time, reasoning independence, context duplication, integration effort and available capacity. Keep the main agent responsible for the overall goal and final verification.

| Situation | Suitable choice |
|---|---|
| Two or more independent investigations or artifact sections with clear boundaries | Delegate in parallel; assign distinct ownership |
| A substantial draft or change needs an independent challenge | Give a fresh reviewer raw sources and acceptance criteria |
| One tightly coupled edit or a small correction | Work inline; delegate only if a separate check adds value |
| Tasks depend on an unfinished result | Finish the dependency, then dispatch |
| Several agents would edit the same state | Use a single writer and read-only reviewers, or isolate workspaces |
| The user selected Native or another execution method | Preserve that method; use supporting delegation within its permitted scope |
| Tools or subagents are unavailable | Continue inline and state material verification limits |

Supply this dispatch contract:

- **Outcome:** the concrete result and acceptance criteria.
- **Inputs:** source artifacts, identity/version and minimum relevant context.
- **Ownership:** files, section or question owned; read-only versus editing scope.
- **Constraints:** approvals, preserved evidence, budgets and forbidden actions.
- **Return:** findings or artifact/diff, verification, uncertainty and blockers.

Choose the least context needed to do the task correctly. For fresh review, provide raw artifacts rather than the parent's diagnosis or desired conclusion. Include prior decisions only when they constrain the work. Choose a model override only when supported by the user's preferences or applicable instructions.

Before integration, inspect the evidence and any changes, resolve disagreements against authoritative sources, and check interfaces between contributions. A subagent's completion message is a claim to verify. Preserve failed or inconclusive findings when relevant.

Example: for a research memo, delegate source verification and an independent challenge to the comparison method while the owner drafts the argument. Reconcile both with the source material before publishing the memo. Use one owner for edits to the same document.

Reassess delegation when coordination costs exceed its benefit. Do not create one agent per trivial step or leave the user coordinating the agents.
