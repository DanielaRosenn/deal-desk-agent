# AgentHack 2026 Submission — Deal Desk Agent

> **DevPost project page** + UiPath Community Forum AgentHack space.
> **Track 2: UiPath Maestro BPMN** · Coding-agent bonus (Cursor + Claude via UiPath for Coding Agents).

---

## Title

**Deal Desk Agent — Your AI Deal Desk Analyst**

## Track

**Track 2: UiPath Maestro BPMN** — end-to-end BPMN 2.0 process orchestrating AI agents, an RPA
robot, live Salesforce data, multi-channel human approvals, Slack, and an audit trail. The right
actor for every step. Governance built in.

Bonus: the entire solution was authored with **Cursor + Claude** via **UiPath for Coding Agents**.

## Elevator pitch (≤200 chars)

Every sales org has a Deal Desk. Ours is an AI agent: live Salesforce data, LLM reasoning, Adaptive
Card approval in Outlook + Action Center. Maestro BPMN orchestrates everything.

---

## The story

Every sales organization has a **Deal Desk** — the person or team that reviews pricing exceptions,
emails managers up the chain, waits for replies, consolidates decisions, and updates the CRM.
It is 100% manual, 100% inbox-driven, and usually 100% slower than the sales team needs.

**The Deal Desk Agent does that job.**

It acts as the AI Deal Desk analyst: collects live Salesforce deal data, resolves the org chart,
applies business-rule scoring, uses an LLM to draft a contextual recommendation, routes only
what needs sign-off — via a three-channel notification (Adaptive Card + Slack + Action Center),
records every human decision, and closes the loop with Slack + Outlook summaries. End to end,
governed, on Automation Cloud.

---

## Live test results (v1.3.12, Jun 22 2026)

Four test cases ran simultaneously. All emails and Slack DMs received:

| # | Customer | Amount | Discount | Agent recommendation |
|---|---|---|---|---|
| TEST-001 | GlobalTech Solutions | $120,000 | 18% | **Approve** — within policy |
| TEST-002 | MegaCorp Industries | $350,000 | 32% | **Approve with conditions** — escalation triggered |
| TEST-003 | StartupXYZ Inc | $28,000 | 45% | **Reject** — margin impact too high |
| TEST-004 | Pharma Global Ltd | $780,000 | 22% | **Approve** — enterprise expansion, Finance pre-approved |

Channels verified: Outlook Adaptive Card ✅ · Slack Block Kit DM ✅ · Action Center ✅

---

## How it works

### Step 1 — Live data collection (Salesforce)

A Salesforce opportunity change triggers the BPMN. The `plan` agent receives the opportunity
payload and can enrich it via the **AgentHub MCP sidecar** (`Salesforce DealDesk MCP`) — a
live read-only UiPath AgentHub MCP server wrapping the production Salesforce IS connection.
Tools: `getSalesforceOpportunity`, `getSalesforceAccount`, `searchSalesforceSoql`.

The agent also resolves the **org chart from HiBob** — walking the `reportsTo` hierarchy from
the Opportunity Owner upward to build the approver chain:
AE → Manager → Director → VP Sales → CFO → CRO.

### Step 2 — Analysis: business rules + LLM reasoning

Two layers run in sequence:

**Business rules** (deterministic, `plan_nodes.py`):
- `risk_score = min(1.0, 0.5 × (discount / 25%) + 0.5 × (value / $500k))`
- `auto_approve` if discount ≤ 5% and value ≤ $50k — no human needed, log and close.
- `needs_approval` otherwise — discount > 25% escalates to Director + VP Sales; value > $500k
  pulls in CFO; value > $750k adds CRO.
- Invalid or missing payload → `exception` → human review.

**LLM reasoning** (contextual):
- Drafts a `recommendation_rationale` in natural language — not just "approve/flag" but *why*,
  with deal context, risk framing, and policy context.
- Produces `recommended_decision` so every approver sees the agent's view alongside the data.

Output: `RoutingPlan` — disposition, risk_score, recommended_decision, rationale, approver chain.

### Step 3 — Maestro BPMN orchestration

The BPMN `Gateway_Disposition` routes:

- `auto_approve` → notify AE via Slack + Outlook, write audit record, done.
- `exception` → route directly to human review with full context.
- `needs_approval` → enter the **sequential multi-instance approver loop**.

**Per-approver loop:**
1. `render` agent generates a rich approval payload — deal summary, risk score, agent
   recommendation and rationale, formatted for Adaptive Card + HTML.
2. **WaitDecision UiPath Robot** (RPA v1.3.16) handles **all three channels simultaneously**:
   - Creates an **Action Center external task** (Deal Desk catalog, Approve/Reject buttons)
   - POSTs to the HITL service to generate the response token
   - Sends an **Outlook email** containing a full **Adaptive Card** (`Action.Http` buttons)
     with a rich HTML fallback for non-supporting clients
   - Sends a **Slack Block Kit** DM (deal data, recommendation, link back to Outlook)
   - **Suspends** via `UiPath.Persistence.Activities` — no polling loop in the BPMN
3. Approver decides via any channel: click Approve/Reject in the **Outlook Adaptive Card**, or
   via **Action Center** in the UiPath portal — either path resolves the robot's wait.
4. Robot resumes, returns `out_Decision` + `out_DecisionComments` directly to the BPMN.
5. A rejection **short-circuits** the remaining chain (BPMN `completionCondition`).
6. `process_response` agent interprets the collected decisions and determines the final outcome.

### Step 4 — Two human roles

**Opportunity Owner (AE — the requester):**
- Receives **Slack DM** + **Outlook summary email** with the full ordered decision trail at end.
- Never has to chase anyone — the agent routes, the robot sends, the BPMN tracks.

**Approvers (the Deal Desk committee):**
- Receive an **Outlook Adaptive Card** — fully interactive, with deal data + agent recommendation.
- Can also see and act in **Action Center** (UiPath portal).
- Also receive a **Slack Block Kit** DM with all data and a link back to Outlook.
- One-action decision from any channel.

### Step 5 — Closure and audit

Every terminal path writes an `ApprovalAudit` entry to **Data Fabric**: ordered approval trail,
agent recommendation vs. each human decision, comments, timestamps, final outcome.
The requester gets the same summary as a **Slack DM** and an **Outlook email**.

---

## What makes this genuinely agentic

- The `plan` agent **reasons**: computes a risk score AND drafts a natural-language rationale —
  that is contextual judgment, not a rule engine.
- It **decides autonomously** on low-risk deals — no human ever touches those.
- It **sizes the approver chain from live org data** — produced as a data structure; BPMN loops
  over it without hardcoded branches.
- The `process_response` agent **interprets** the collected human decisions — the agent remains
  in the loop throughout, not just at the start.

---

## UiPath ecosystem — every component used

| Component | Role |
|---|---|
| **Coded Agents** (Python / LangGraph) | `plan`, `render`, `process_response` — the AI brain |
| **Maestro BPMN 2.0** | End-to-end orchestration, gateway, sequential multi-instance loop |
| **WaitDecision Robot** (UiPath RPA v1.3.16) | All three channels + UiPath Persistence suspend/resume |
| **Action Center** | Native HITL task (Deal Desk catalog) — Approve/Reject in UiPath portal |
| **Outlook Adaptive Card** | Real interactive card (originator `61fed71d`) with Action.Http buttons |
| **Slack Block Kit** | DM to approver + requester with deal data and recommendation |
| **AgentHub MCP Server** | `Salesforce DealDesk MCP` — live read-only Salesforce SOQL |
| **Integration Service** (Salesforce + Outlook) | Live connections |
| **Data Fabric** | `ApprovalAudit` decision log (agent rec vs. human decisions) |
| **UiPath for Coding Agents** | Cursor + Claude + `uip` CLI authored the entire solution |

---

## Evidence of running on Automation Cloud

- Agent package `adaptive-approval-agent-core` v0.1.17 published; 3 entry points deployed.
- BPMN `DealDeskApproval` v1.1.9 running; Robot `WaitDecision` v1.3.16 deployed.
- `Salesforce DealDesk MCP` AgentHub server live with SOQL tools.
- Full solution packaged as `.uipx` v1.2.3 in `Shared/DealDeskApprovalGlobal`.
- Four simultaneous live test runs confirmed: Adaptive Cards received, Slack DMs received,
  Action Center tasks created — all three channels verified Jun 22 2026.

---

## Demo scenarios (for the video)

1. **Auto-approve** — discount ≤ 5%, value ≤ $50k. Zero human touches. Closes in seconds.
2. **One-manager approval** — 8% / $40k. Robot sends Adaptive Card + Slack to Maya Stone.
   She clicks Approve in Outlook. Requester gets Slack DM + Outlook summary.
3. **Full chain** — 30% / $1.2M. Four sequential approvers. Each gets the LLM rationale card
   on all three channels. Rejection at any step short-circuits. Data Fabric audit trail shown.

---

## Supporting materials

- Presentation deck: `submission/deck/Submission-Template-Deal-Desk-Agent.pptx`
- Animated architecture: `submission/code-graph/deal-desk-flow.gif`
- Interactive project page + live disposition calculator: `submission/explore/index.html`
- Live test evidence: `submission/hack-testimonies.md`
- Solution blueprint: `adaptive-approval-agent/docs/SOLUTION_BLUEPRINT.md`

---

Team: Daniela Rosenstein, Cato Networks.
Built with coding agents (Cursor + Claude via UiPath for Coding Agents).
