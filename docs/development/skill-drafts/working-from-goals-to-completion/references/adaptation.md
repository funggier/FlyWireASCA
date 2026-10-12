# Adapt the workflow to the task

Select checks that establish the requested outcome. Use relevant specialized skills for tools and formats; this workflow coordinates them without assuming particular plugins, project names or programming languages.

| Domain | Current authority | Suitable verification |
|---|---|---|
| Research | Primary sources, frozen inputs and experiment records | Claims match sources; comparable denominators; unknown usage stays unknown |
| Documents and presentations | Current brief, revision and supplied facts | Content, figures, render/layout and required delivery format |
| Data and spreadsheets | Dataset identity, definitions and formulas | Independent totals, missing-data treatment, formulas and reconciliation |
| Software | Live Git/GitHub, source, runtime and project instructions | Relevant tests, runtime behavior, exact commit CI and preserved baselines |
| Operations and project planning | Current records, dependencies, owners and authorization | Observable completion, outstanding blockers and readback of changes |

For research, separate correctness, success, false success, bounded failures, latency and costs relevant to the question. Fewer calls to one component alone does not establish lower total cost. Freeze comparisons before performance-driven changes when required by the study; keep old evidence and disclose new versions.

For design work, keep idea approval, design approval, written specification approval, plan approval and execution/integration approval distinct when those gates apply. For a straightforward document correction, use the existing brief and requested checks; avoid adding a software release workflow.

Use this compact handoff for work spanning sessions:

1. **Goal and current authority:** artifact/version, live state checked and applicable constraints.
2. **Completed:** concrete outputs with verification evidence.
3. **Decisions:** selected approach, assumptions, approvals and material trade-offs.
4. **Open:** remaining work, failed/unknown evidence, dependencies and exact pending gate.
5. **Resume:** current step and the next executable action, including what to recheck first.

Keep detailed evidence in the ledger or artifact. In the conversation, lead with the result, its proof and the decision that needs the user's attention.

Example: a warehouse handoff says all shipments arrived; current records show one still pending. Correct the draft to show confirmed receipts separately, preserve the older statement as history, and prepare checks for the status aggregation fix. Keep system repair and final sending approval pending. Continue drafting under existing authorization; request sending approval only for the concrete final version if sending is part of the task.

| Common mistake | Better action |
|---|---|
| Treat an old completion flag as current truth | Inspect the current artifact and record the discrepancy |
| Reopen an already selected approach | Carry the choice forward and investigate only new conflicting evidence |
| Report a command launch or draft as verified completion | Inspect its result and label the remaining work |
| Copy every finding into several summaries | Reference a shared evidence table and keep the handoff focused on resuming |
| Stop after an ordinary task boundary | Start the next authorized task in the agreed plan |
