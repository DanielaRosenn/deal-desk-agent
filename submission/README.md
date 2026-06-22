# AgentHack 2026 Submission - Deal Desk Agent

Submission materials for **UiPath AgentHack 2026**, **Track 2: UiPath Maestro BPMN** (built with
coding agents - Cursor + Claude - for the coding-agent bonus). Submissions are hosted on **DevPost**;
the UiPath Community Forum AgentHack space is used for support. Hack window: May 15 - Jun 29, 2026.

## What this folder contains

| File | Purpose |
| --- | --- |
| `forum-post.md` | DevPost project description + fields (title, track, elevator pitch, ecosystem) |
| `presentation-deck.md` | 12-slide deck source + speaker notes ("laptop to production" concept), mapped to judging |
| `deck/slide-01..12.png` | Rendered, on-brand slides in the AgentHack palette (orange/ink/blue) |
| `demo-script.md` | Demo video script - a safe local-debug cut and a full end-to-end cut |
| `judging-and-architecture.md` | Fit against AgentHack 2026 expectations + architecture diagrams |
| `explore/index.html` | Interactive project page: animated flow + **live disposition calculator** |
| `code-graph/deal-desk-flow.gif` | Animated drill-down of the full flow (dark AgentHack palette) |
| `code-graph/deal-desk-code-graph.png` | Crisp static of the full code graph |
| `code-graph/deal_desk_code_graph.py` | Editable source for the graph/GIF (palette-parameterized) |
| `diagrams/*.png` | Static flowcharts (architecture, agent decision, sequence, three paths) + Mermaid sources |

## The solution in one paragraph

The **Deal Desk Agent** splits intelligence from lifecycle. A Python LangGraph **coded agent**
(`Agent.AdaptiveApproval`) reviews each opportunity change, computes a risk score, sets a
disposition (`auto_clear` / `needs_approval` / `exception`), drafts a recommendation, and sizes
the approver chain from a mock HiBob org chart. A **Maestro BPMN** process orchestrates the
rest: a disposition gateway auto-clears or enters a sequential multi-instance subprocess that
sends one Outlook Adaptive Card per approver, opens an Action Center user task, and re-invokes
the agent to route the decision - with a boundary SLA timer for escalation and a Data Fabric
record on every terminal path.

## Submission checklist (DevPost)

- [ ] Create the project on DevPost and select **Track 2: Maestro BPMN**
- [ ] Paste the short description + elevator pitch from `forum-post.md`
- [ ] Upload the deck (`deck/slide-*.png` or exported PPTX/PDF) and embed `code-graph/deal-desk-flow.gif`
- [ ] Add the demo video link (recorded from `demo-script.md`)
- [ ] Link the interactive page (`explore/index.html`, hosted) for the "explore it" experience
- [ ] Link the code (zip of `adaptive-approval-agent/` or a repo link)
- [ ] Call out: runs on Automation Cloud + built with coding agents (bonus)
- [ ] Confirm team participation settings on DevPost

## Source artifacts referenced

- Agent: `adaptive-approval-agent/agent/` (LangGraph, schemas, nodes; `uipath.json` entry points `plan`/`render`/`process_response`)
- Orchestration: `adaptive-approval-agent/DealDeskSolution/DealDeskApproval/DealDeskApproval.bpmn`
- Packaged solution: `adaptive-approval-agent/DealDeskSolution/DealDeskSolution.uipx` (deployable bundle)
- Bridge: `adaptive-approval-agent/approval-bridge/` (Azure Function -> CompleteAppTask)
- Evidence: `adaptive-approval-agent/out/` (`agent-pytest.txt`, `bpmn-validate.json`, `deploy-verify.md`, `DEMO-READY.md`)
- Spec / plan: `.cursor/plans/2026-06-02-deal-desk-agent-maestro-bpmn/`
