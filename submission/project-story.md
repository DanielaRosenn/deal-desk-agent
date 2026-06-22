## Inspiration

Every sales organization has a **Deal Desk** — the person or team that reviews pricing exceptions, emails managers up the chain, waits for replies, consolidates decisions, and updates the CRM. It is 100% manual, 100% inbox-driven, and almost always slower than the sales team needs. I wanted to find out whether an AI agent could actually *do that job* — not just summarize a deal, but reason about it, decide who needs to sign off, route the request, and close the loop — with real governance and a real audit trail.

## What it does

Deal Desk Agent is an AI Deal Desk analyst that runs end to end on UiPath Automation Cloud.

- Collects **live Salesforce** deal data and resolves the approver org chart (AE → Manager → Director → VP Sales → CFO → CRO) from HiBob.
- Scores risk with deterministic business rules, then uses an **LLM to draft a contextual recommendation and rationale** — *why*, not just approve/flag.
- **Auto-approves** low-risk deals with zero human touch.
- For everything else, runs a **sequential multi-instance approver loop**, notifying each approver on **three channels at once**: an interactive **Outlook Adaptive Card**, a **Slack Block Kit** DM, and a native **Action Center** task. A decision on any channel resolves the step.
- A rejection short-circuits the rest of the chain; the agent interprets the collected decisions to determine the final outcome.
- Writes a full **Data Fabric audit record** (agent recommendation vs. each human decision, comments, timestamps) and sends the requester a Slack DM + Outlook summary.

## How we built it

The brain is three **coded agents** (Python / LangGraph): `plan` (data + scoring + rationale), `render` (approval payload), and `process_response` (final outcome). **Maestro BPMN 2.0** orchestrates everything — a disposition gateway plus the sequential multi-instance approval loop. A **UiPath RPA robot** (`WaitDecision`) fans out to all three channels and suspends/resumes via UiPath Persistence, so there is no polling loop in the BPMN. Live data comes through an **AgentHub MCP server** wrapping a read-only Salesforce Integration Service connection (`getSalesforceOpportunity`, `getSalesforceAccount`, `searchSalesforceSoql`). The whole thing — agents, BPMN, robot, MCP, bindings — was authored with **Cursor + Claude via UiPath for Coding Agents** and the `uip` CLI.

## Challenges we ran into

- **Multi-channel HITL that stays in sync.** Getting Outlook Adaptive Card, Slack, and Action Center to represent the *same* pending decision — and letting any one of them resolve the wait — took careful coordination between the response token, the HITL service, and the robot.
- **Suspend/resume instead of polling.** Replacing a polling loop with UiPath Persistence so the BPMN truly idles while waiting on a human was a key design shift.
- **Real Adaptive Cards in email.** Action.Http buttons, originator registration, and a rich HTML fallback for clients that don't render cards.
- **Keeping connection IDs and bindings real.** Phantom/placeholder IDs broke Studio Web validation; everything had to reference the actual tenant connection IDs across the BPMN, bindings, and debug overwrites.

## Accomplishments that we're proud of

- A genuinely **agentic** flow: the agent reasons, decides autonomously on low-risk deals, sizes the approver chain from live org data, and interprets the human decisions at the end — it stays in the loop throughout.
- **Four simultaneous live test runs** verified on all three channels (Outlook Adaptive Card, Slack DM, Action Center) on Jun 22, 2026.
- A clean separation of concerns — the right actor for every step: agents reason, the robot communicates, the BPMN governs, Data Fabric remembers.
- The entire solution was built with coding agents on the UiPath platform.

## What we learned

- The strongest agent designs combine **deterministic rules with LLM reasoning** — rules for policy thresholds, the LLM for context and explanation.
- **BPMN multi-instance loops** are a natural fit for variable-length approval chains produced as data, with no hardcoded branches.
- Meeting approvers where they already are (email, Slack, the UiPath portal) matters more than any single "perfect" UI.
- Coding agents (Cursor + Claude) plus the `uip` CLI can take a UiPath solution from idea to a deployed, governed automation surprisingly fast.

## What's next for DealDesk Agent

- Deeper CRM write-back so approved terms flow straight back into Salesforce.
- Configurable, tenant-specific policy thresholds and approval matrices without code changes.
- Learning from historical decisions to refine the agent's recommendations over time.
- Analytics on the Data Fabric audit trail (cycle time, override rates, bottleneck approvers) and expansion beyond renewals to new-business pricing exceptions.
