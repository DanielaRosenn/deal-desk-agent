# Deal Desk Agent — UiPath AgentHack 2026

> *The AI analyst that replaced the Deal Desk inbox.*

[![UiPath AgentHack 2026](https://img.shields.io/badge/UiPath-AgentHack%202026-6A1FDB?style=flat-square)](https://community.uipath.com/events/details/uipath-hackathons-presents-agenthack/)
[![Track](https://img.shields.io/badge/Track%202-Maestro%20BPMN%20%2B%20Coded%20Agents-blue?style=flat-square)](https://community.uipath.com/events/details/uipath-hackathons-presents-agenthack/)

---

## What it does

Sales deals over a discount threshold require a sign-off chain — manager, director, VP, sometimes CFO.
Traditionally that means email threads, calendar chasing, and days of stalled pipeline.

The Deal Desk Agent does the whole job autonomously:

1. **Queries live Salesforce data** via AgentHub MCP sidecar (opportunity, ARR, ACV, product mix).
2. **Resolves the approver chain** from HiBob org chart (reportsTo hierarchy, up to CRO tier).
3. **Risk-scores the deal** and generates an LLM recommendation with rationale.
4. **Delivers approval requests on three channels simultaneously** — no polling, no inbox tax:
   - **Outlook Adaptive Card** (real interactive card, `Action.Http` buttons — Approve / Reject / Request Info)
   - **UiPath Action Center** external task (Deal Desk catalog, same three actions)
   - **Slack Block Kit DM** to each approver (deal data, agent recommendation, link back to Outlook)
5. **Suspends via `UiPath.Persistence.Activities`** — the BPMN never polls. When an approver clicks in Outlook or Action Center, the Robot resumes instantly.
6. A **rejection short-circuits the chain** immediately (BPMN `completionCondition`).
7. **Slack + Outlook summary** sent to the Opportunity Owner. **Data Fabric audit record** written.

---

## Architecture

```
Salesforce (live MCP)
        │
        ▼
   plan agent  ──►  disposition + approver chain + LLM rationale
        │
        ▼
  Maestro BPMN ──► sequential multi-instance subprocess (per approver)
        │                    │
        ▼                    ▼
   render agent         WaitDecision Robot v1.3.16 (RPA + Persistence)
   (Adaptive Card            ├── Action Center external task
    payload)                 ├── Outlook Adaptive Card (originator 61fed71d)
                             └── Slack Block Kit DM
                                      │
                                  approver decides ─► Robot resumes
                                                            │
                                                    process_response agent
                                                            │
                                                    Slack + Outlook to AE
                                                    Data Fabric audit record
```

**Stack:** Python LangGraph (coded agents) · Maestro BPMN · UiPath RPA (WaitDecision Robot) ·
UiPath Persistence Activities · Integration Service (Outlook 365, Slack, Data Fabric) ·
AgentHub MCP (Salesforce read-only)

---

## Repository layout

```
adaptive-approval-agent/
  agent/                   # Python LangGraph coded agent (plan, render, process_response)
    graphs/                # LangGraph state machines
    nodes/                 # Individual graph nodes
    rendering/             # Adaptive Card + HTML email rendering
    policy/                # Risk scoring + routing rules
    integrations/          # Salesforce, Outlook, Slack, Data Fabric clients
  DealDeskSolution/
    DealDeskApproval/      # Maestro BPMN process + entry-points
    DealDeskApproval_WaitDecision/  # WaitDecision.xaml (RPA robot)
  docs/SOLUTION_BLUEPRINT.md       # Canonical architecture reference

submission/
  forum-post.md            # DevPost / community forum submission text
  presentation-deck.md     # Slide-by-slide content + speaker notes
  judging-and-architecture.md  # Self-assessment + Mermaid diagrams
  hack-testimonies.md      # Live test results (June 2026)
  code-graph/
    deal-desk-flow.gif     # Animated code graph (92 frames)
    deal-desk-code-graph.png
  deck/
    Submission-Template-Deal-Desk-Agent.pptx  # Final editable presentation
  explore/
    index.html             # Interactive disposition calculator
```

---

## Setup

```bash
# 1. Copy secrets template
cp .env.example .env
# fill in UIPATH_CLIENT_ID, UIPATH_CLIENT_SECRET, SLACK_BOT_TOKEN, HITL_API_KEY

# 2. Install Python dependencies (requires uv)
cd adaptive-approval-agent
uv sync

# 3. Run unit tests
uv run pytest tests/unit/

# 4. Deploy to Automation Cloud (solution already live on catonetworks/Test)
uip solution deploy adaptive-approval-agent/DealDeskSolution/DealDeskSolution_1.2.3.deploy.config.json
```

---

## Live evidence

The solution is deployed and tested on **UiPath Automation Cloud** (`catonetworks / Test` tenant,
folder `Shared/DealDeskApprovalGlobal`):

| Component | Version | Status |
|---|---|---|
| WaitDecision Robot | 1.3.16 | deployed, latest |
| DealDeskApproval BPMN | 1.1.12 | deployed, latest |
| DealDeskAgent (plan/render/process_response) | latest | deployed |

See `submission/hack-testimonies.md` for full end-to-end test results including confirmed
Adaptive Card delivery, Action Center task creation, and Slack DM receipts.

---

## Submission materials

| File | Purpose |
|---|---|
| `submission/forum-post.md` | DevPost / community post |
| `submission/presentation-deck.md` | Slide script |
| `submission/judging-and-architecture.md` | Judging criteria self-assessment |
| `submission/deck/Submission-Template-Deal-Desk-Agent.pptx` | Final presentation |
| `submission/code-graph/deal-desk-flow.gif` | Animated architecture walkthrough |
| `submission/explore/index.html` | Interactive disposition calculator |
