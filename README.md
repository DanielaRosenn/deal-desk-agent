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

## UiPath Components Used

| Component | Role |
|---|---|
| **Maestro BPMN** | Orchestrates the end-to-end approval flow; sequential multi-instance subprocess per approver with `completionCondition` short-circuit |
| **Coded Agents (Python / LangGraph)** | Three agents: `plan` (risk score + LLM rationale + approver chain), `render` (Adaptive Card payload), `process_response` (interprets decisions) |
| **UiPath RPA + Persistence Activities** | WaitDecision Robot sends all three notification channels and suspends via `UiPath.Persistence.Activities` — zero polling |
| **Action Center** | Native external task for in-portal approvals (Deal Desk catalog) |
| **Integration Service** | Outlook 365 (Adaptive Cards), Slack (Block Kit DMs), UiPath Data Fabric (audit records) |
| **AgentHub MCP** | Salesforce read-only sidecar — live opportunity data, ARR, ACV, product mix |
| **Data Fabric** | Writes a structured `ApprovalAudit` record per outcome — queryable system of record |

**Agent Type: Coded Agents** — all three agent entry points (`plan`, `render`, `process_response`) are Python-based LangGraph state machines deployed as Coded Agents on Automation Cloud. No Low-code Agent Builder was used.

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

### Prerequisites

- [UiPath CLI (`uip`)](https://docs.uipath.com/automation-cloud/docs/uipath-cli) installed and authenticated (`uip login`)
- Python 3.11+ with [`uv`](https://docs.astral.sh/uv/) package manager
- A UiPath Automation Cloud tenant with Integration Service connections for **Outlook 365**, **Slack**, and **Data Fabric** already authenticated

### Step 1 — Python agent

```bash
cd adaptive-approval-agent

# Install dependencies
uv sync

# Run unit tests
uv run pytest tests/unit/
```

### Step 2 — Environment secrets

Create a `.env` file at the repo root (see `.env.example` if present):

```
UIPATH_CLIENT_ID=<your-client-id>
UIPATH_CLIENT_SECRET=<your-client-secret>
SLACK_BOT_TOKEN=<xoxb-...>
HITL_CALLBACK_BASE_URL=<your-AWS-CloudFront-or-ngrok-URL>
```

### Step 3 — Deploy to Automation Cloud

```bash
# Publish the solution package
uip solution publish adaptive-approval-agent/DealDeskSolution/out/DealDeskSolution_1.1.15.zip --wait

# Deploy to Shared/DealDeskApprovalGlobal folder
uip solution deploy run \
  --name "DealDeskApproval-Final" \
  --package-name "DealDeskSolution" \
  --package-version "1.1.15" \
  --parent-folder-path "Shared" \
  --folder-name "DealDeskApprovalGlobal"
```

> **Note for judges:** The solution is already live on the hackathon tenant (`hackathon26_218 / DefaultTenant`, folder `Shared/DealDeskApprovalGlobal`) — no local deployment is required to evaluate it.

### Step 4 — Trigger a run

Send a test payload via the Maestro BPMN trigger or run the `plan` agent directly:

```bash
cd adaptive-approval-agent
uv run python -c "
from agent.graphs.plan import run_plan
run_plan({'opportunity_id': 'OPP-TEST-001', 'discount_pct': 32, 'arr': 350000})
"
```

---

## Live evidence

The solution is deployed and tested on **UiPath Automation Cloud** (hackathon tenant `hackathon26_218`,
folder `Shared/DealDeskApprovalGlobal`):

| Component | Version | Status |
|---|---|---|
| WaitDecision Robot | 1.3.16 | deployed |
| DealDeskApproval BPMN | 1.1.9 | deployed |
| DealDeskAgent (plan / render / process_response) | 0.1.17 | deployed |
| Solution package `DealDeskSolution` | 1.1.15 | active |

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
