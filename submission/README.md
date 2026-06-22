# AgentHack 2026 Submission — Deal Desk Agent

Submission materials for **UiPath AgentHack 2026**, **Track 2: UiPath Maestro BPMN**, built with
coding agents (Cursor + Claude via UiPath for Coding Agents) for the coding-agent bonus. The UiPath
Community Forum AgentHack space is the official submission channel.

## What this folder contains

| File | Purpose |
| --- | --- |
| `forum-submission.md` | Canonical forum post — narrative, innovation list, links, evidence |
| `project-story.md` | DevPost "Project Story" sections (Inspiration → What's next) |
| `judging-and-architecture.md` | Fit against AgentHack criteria + accurate architecture diagrams |
| `hack-testimonies.md` | Live test evidence (the four verified cases) |
| `demo-script.md` | Demo video script (local-debug cut + full end-to-end cut) |
| `presentation-deck.md` | Deck source + speaker notes, mapped to judging |
| `explore/index.html` | Interactive project page: animated flow + live disposition calculator |
| `deck/Submission-Template-Deal-Desk-Agent.pptx` | Deck on the official AgentHack template |
| `deck/Deal-Desk-Agent-deck.pdf` | PDF export of the deck |
| `deck/make_pdf.py` | Helper to export the deck to PDF |
| `diagrams/*.mmd` + `*.png` | Architecture, agent decision, sequence, three-paths (Mermaid + renders) |
| `diagrams/mmdc.json` | Mermaid render config (theme/palette) |
| `code-graph/deal-desk-flow.gif` | Animated drill-down of the full flow |
| `code-graph/deal-desk-code-graph.png` | Static code graph |
| `code-graph/deal_desk_code_graph.py` | Editable source for the graph/GIF |

> The deck is built/regenerated via the project skill at `.cursor/skills/presentation/`.

## The solution in one paragraph

The **Deal Desk Agent** splits intelligence from lifecycle. Python LangGraph **coded agents**
(`plan` / `render` / `process_response`) review each opportunity change, compute a risk score, set a
disposition (`auto_approve` / `needs_approval` / `exception`), draft an LLM recommendation, and size
the approver chain from the org hierarchy. **Maestro BPMN** orchestrates the rest: a disposition
gateway auto-approves or enters a sequential multi-instance loop where the **WaitDecision robot**
reaches each approver on three channels at once — **Outlook Adaptive Card**, **Slack**, and a native
**Action Center** "wait for task" — backed by an **AWS Lambda HITL bridge**, with a **Data Fabric**
audit record on every terminal path. Salesforce data is live via Integration Service + an AgentHub
MCP sidecar.

## Submission checklist

- [ ] Post on the UiPath Forum AgentHack space, Track 2: Maestro BPMN
- [ ] Paste the description + tagline from `forum-submission.md`
- [ ] Upload the diagram PNGs to the image gallery; add captions
- [ ] Add the demo video link (recorded from `demo-script.md`)
- [ ] Share the deck link (OneDrive/Drive) in "Other resources"
- [ ] Link the code (this repo) in the code field
- [ ] Upload a judges' bundle zip in "Additional info" (regenerate as needed)
- [ ] Call out: runs on Automation Cloud + built with coding agents (bonus)

## Source artifacts referenced

- Agents: `adaptive-approval-agent/agent/` (LangGraph; entry points `plan` / `render` / `process_response`)
- Orchestration: `adaptive-approval-agent/DealDeskSolution/DealDeskApproval/DealDeskApproval.bpmn`
- Packaged solution: `adaptive-approval-agent/DealDeskSolution/DealDeskSolution.uipx`
- Blueprint: `adaptive-approval-agent/docs/SOLUTION_BLUEPRINT.md`
