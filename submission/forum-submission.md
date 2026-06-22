# UiPath Forum / DevPost Submission — Deal Desk Agent

> Paste-ready. One team member submits (UiPath Forum AgentHack space is the official channel).
> Fill the `<LINK>` placeholders with your hosted URLs before posting.

---

## Project name

**Deal Desk Agent — Your AI Deal Desk Analyst**

## Track

**Track 2: UiPath Maestro BPMN** · Coding-agent bonus (Cursor + Claude via UiPath for Coding Agents)

## Tagline / elevator pitch (≤200 chars)

Every sales org has a Deal Desk. Ours is an AI agent: live Salesforce data, LLM reasoning, multi-channel approvals (Adaptive Card + Slack + Action Center), AWS HITL loop, Data Fabric audit — all orchestrated by Maestro BPMN.

---

## Short description

Every sales organization has a **Deal Desk** — the team that reviews pricing exceptions, emails managers up the chain, waits for replies, consolidates decisions, and updates the CRM. It is manual, inbox-driven, and slow.

**Deal Desk Agent does that job.** It collects live Salesforce deal data, sizes the approver chain from the org hierarchy, scores risk and drafts an LLM recommendation, then routes only what needs sign-off across **three channels at once** — an interactive **Outlook Adaptive Card**, a **Slack** DM, and a native **Action Center "wait for task."** The approval loop is backed by an **AWS Lambda HITL bridge**, every human decision is interpreted by the agent, and the full trail is written to **UiPath Data Fabric**. **Maestro BPMN** orchestrates the whole lifecycle end to end on Automation Cloud — and the entire solution was authored with **coded agents** (Cursor + Claude via UiPath for Coding Agents).

---

## What makes this innovative

- **Coded Agents (Python / LangGraph)** — three agents do the thinking: `plan` (risk score + LLM rationale + approver chain), `render` (approval payload), `process_response` (interprets each human decision). The agent stays in the loop end to end, not just at the start.
- **UiPath Data Fabric audit** — every terminal path writes an `ApprovalAudit` record: ordered approval trail, agent recommendation vs. each human decision, comments, timestamps, final outcome. A queryable system of record, not a log file.
- **Microsoft Adaptive Cards in Outlook** — a real `application/adaptivecard+json` card embedded in email (originator `61fed71d`), with Approve / Reject / Request Info `Action.Http` buttons and a rich HTML fallback for clients that don't render cards.
- **Slack Block Kit** — the same deal data, recommendation, and rationale mirrored as a DM to the approver and the requester, with a link back to Outlook.
- **AWS Lambda HITL bridge for the approval loop** — a CloudFront + Lambda API (`/api/v1/approvals`) that issues a response token per approver, accepts the decision via a secure token-based callback, and lets the BPMN resolve the wait. This is what makes the approval loop instant and channel-agnostic.
- **Action Center "wait for task"** — a native UiPath external task in the Deal Desk catalog; the WaitDecision robot suspends via `UiPath.Persistence.Activities` and resumes on decision, so an approver can act in the UiPath portal and the same decision closes the step.

The point: **the right actor for every step.** Agents reason, the robot communicates, the AWS bridge + Action Center handle the human wait, the BPMN governs, and Data Fabric remembers.

---

## How it works (end to end)

1. **Trigger + plan** — a Salesforce opportunity change starts the BPMN. The `plan` agent enriches data via the **Salesforce DealDesk MCP** (AgentHub) and resolves the approver chain (AE → Manager → Director → VP Sales → CFO → CRO).
2. **Decide** — deterministic rules (`risk_score = min(1.0, 0.5·discount/25% + 0.5·value/$500k)`) + an LLM rationale. `auto_approve` low-risk deals with zero human touch; otherwise enter the approver loop.
3. **Approve (multi-instance loop)** — per approver, the `render` agent builds the payload; the **WaitDecision robot** fires all three channels (Outlook Adaptive Card, Slack DM, Action Center task) and the **AWS Lambda HITL bridge** mints the response token. A decision on any channel resolves the wait. Rejection short-circuits the rest of the chain.
4. **Interpret + close** — `process_response` interprets the collected decisions; the requester gets a Slack DM + Outlook summary; **Data Fabric** records the full audit trail.

---

## Live test evidence (Jun 22, 2026, v1.3.x)

Four cases ran simultaneously; all Adaptive Cards, Slack DMs, and Action Center tasks verified.

| # | Customer | Amount | Discount | Agent recommendation |
|---|---|---|---|---|
| TEST-001 | GlobalTech Solutions | $120,000 | 18% | Approve — within policy |
| TEST-002 | MegaCorp Industries | $350,000 | 32% | Approve with conditions — escalation triggered |
| TEST-003 | StartupXYZ Inc | $28,000 | 45% | Reject — margin impact too high |
| TEST-004 | Pharma Global Ltd | $780,000 | 22% | Approve — enterprise expansion, Finance pre-approved |

Channels verified: Outlook Adaptive Card · Slack Block Kit DM · Action Center.

---

## Built with

UiPath Maestro BPMN 2.0 · UiPath Coded Agents (Python / LangGraph) · UiPath RPA (WaitDecision robot + UiPath.Persistence) · UiPath Action Center · UiPath Data Fabric · UiPath Integration Service (Salesforce + Outlook) · UiPath AgentHub MCP · Microsoft Adaptive Cards · Slack Block Kit · AWS Lambda + CloudFront (HITL bridge) · Cursor + Claude via UiPath for Coding Agents.

---

## Supporting files & links (fill in before posting)

| Field | What to attach / link |
|---|---|
| **Demo video** | `<LINK to recorded demo>` (script: `submission/demo-script.md`) |
| **Presentation deck** (Other resources) | `<OneDrive/Drive/Dropbox share link>` — set sharing to "anyone with link can view". Source: `submission/deck/` (PPTX/PDF/slide PNGs) |
| **Code** | `<GitHub repo OR cloud-drive .zip of `adaptive-approval-agent/`>` — must be downloadable by reviewers |
| **Interactive project page** | `<hosted URL>` for `submission/explore/index.html` (animated flow + live disposition calculator) |
| **Architecture diagrams** | `submission/diagrams/*.png` + `submission/judging-and-architecture.md` |
| **Animated code graph** | `submission/code-graph/deal-desk-flow.gif` |
| **Live test evidence** | `submission/hack-testimonies.md` |
| **Solution blueprint** | `adaptive-approval-agent/docs/SOLUTION_BLUEPRINT.md` |

---

## Deployed on Automation Cloud (evidence)

- Agent package `adaptive-approval-agent-core` v0.1.17 — 3 entry points (`plan`, `render`, `process_response`) deployed in `Shared/DealDeskApprovalGlobal`.
- BPMN `DealDeskApproval` v1.1.9 · Robot `WaitDecision` v1.3.16 · Solution `.uipx` v1.2.3.
- `Salesforce DealDesk MCP` AgentHub server live with SOQL tools.
- AWS HITL bridge (CloudFront + Lambda) serving the approval API.

---

## Team

Daniela Rosenstein, Cato Networks. Submitted by one team member per the rules.
Built with coding agents (Cursor + Claude via UiPath for Coding Agents).
