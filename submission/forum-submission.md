# UiPath Forum Submission — Deal Desk Agent

> Paste-ready. One team member submits. Fill the `<LINK>` placeholders before posting.

## Project name

**Deal Desk Agent — Your AI Deal Desk Analyst**

## Track

**Track 2: UiPath Maestro BPMN** — with the coding-agent bonus (built entirely with Cursor + Claude via UiPath for Coding Agents).

## Tagline (≤200 chars)

The deal desk that never sleeps. An AI agent reviews every renewal, flags the ones at risk, reasons about why, and routes only the special cases for sign-off — across Outlook, Slack, and Action Center.

## The problem — a story every revenue team knows

It's the end of the quarter. A renewals analyst opens the pipeline and starts going down the list, one opportunity at a time. Most are fine. But buried in there is a $28K renewal with a **45% discount** a rep promised to save the logo, and a $350K deal at **32%** that quietly breaks the discount ceiling. Each one has to be eyeballed, judged against policy, and — if it's a special case — emailed up the chain to a manager, a director, sometimes Finance. Then the waiting starts: replies trickle in over days, decisions get buried in email threads, and the rep keeps pinging "any update?"

That is the **Deal Desk**: the human who manually reviews opportunities, spots the ones that are problematic or at risk, and shepherds the exceptions through approval. It works — but it's slow, it's inconsistent from analyst to analyst, and it leaves no audit trail. It's the most judgment-heavy, least scalable step between a quote and a signature.

## What we built — a real deal desk, end to end

**Deal Desk Agent is that analyst, as an AI agent — running end to end on UiPath Automation Cloud.**

The moment a Salesforce opportunity changes, a **Maestro BPMN** process wakes up. A **coded agent** pulls the live deal, looks at the discount and the value the way an analyst would, and **scores the risk** — then writes a plain-English rationale for *why* this deal is fine, risky, or a hard no. Clean deals inside policy clear on their own, with **zero human touch**. The ones that genuinely need a human — the special cases — are routed to exactly the right approvers, sized from the live org chart, and each approver is reached on **three channels at once**: an interactive **Outlook Adaptive Card**, a **Slack** DM, and a native **Action Center** task. They decide wherever they already are; the same decision resolves the step. A rejection anywhere stops the chain. The agent reads the collected decisions, the rep gets a clean summary, and the entire trail — agent recommendation vs. each human call — is written to **UiPath Data Fabric**.

It is the manual deal desk, automated: **collect, reason, route, sign-off, audit** — without the inbox.

## See the agent reason (real runs)

These aren't mock-ups — they're live runs from Jun 22, where the agent reviewed each opportunity and made the call before any human looked:

- **StartupXYZ — $28K at 45% off →** *Reject.* "Discount is margin-destructive for a deal this size; the savings don't justify the erosion." The agent caught the at-risk deal a tired analyst might wave through.
- **MegaCorp — $350K at 32% off →** *Approve with conditions.* "Exceeds the 25% ceiling — escalate for a multi-year commitment." It reasoned about the *policy threshold*, not just the number.
- **GlobalTech — $120K at 18% off →** *Approve.* Inside policy, low risk, cleared cleanly.
- **Pharma Global — $780K at 22% off →** *Approve.* Large enterprise expansion, already Finance-pre-approved — recognized and fast-tracked with an audit note.

The design principle throughout: **the right actor for every step.** The agent reasons, the robot communicates, the AWS HITL bridge and Action Center handle the human wait, the BPMN governs, and Data Fabric remembers.

## What makes it innovative

- **Coded Agents (Python / LangGraph)** — three agents carry the intelligence: `plan` (risk score + LLM rationale + approver chain), `render` (approval payload), and `process_response` (interprets each human decision). The agent stays in the loop end to end, not just at kickoff.
- **AWS Lambda HITL bridge for the approval loop** — a CloudFront + Lambda API (`/api/v1/approvals`) mints a response token per approver and accepts the decision through a secure token callback, making the wait instant and channel-agnostic.
- **Action Center "wait for task"** — a native UiPath external task; the WaitDecision robot suspends via `UiPath.Persistence.Activities` and resumes on decision, so an approver can act right inside the UiPath portal.
- **Microsoft Adaptive Cards in Outlook** — a real `application/adaptivecard+json` card embedded in email (originator `61fed71d`) with Approve / Reject / Request Info `Action.Http` buttons and an HTML fallback for clients that don't render cards.
- **Slack Block Kit** — the same deal data, recommendation, and rationale mirrored as a DM to both approver and requester, linking back to Outlook.
- **UiPath Data Fabric audit** — every terminal path writes an `ApprovalAudit` record (ordered trail, agent recommendation vs. each human decision, comments, timestamps, outcome). A queryable system of record, not a log line.

## How it works

1. **Trigger + plan** — a Salesforce opportunity change starts the BPMN. The `plan` agent enriches data via the **Salesforce DealDesk MCP** (AgentHub) and resolves the chain: AE → Manager → Director → VP Sales → CFO → CRO.
2. **Decide** — deterministic rules (`risk_score = min(1.0, 0.5·discount/25% + 0.5·value/$500k)`) plus an LLM rationale. `auto_approve` clears low-risk deals; otherwise the approver loop begins.
3. **Approve** — per approver, `render` builds the payload, the **WaitDecision robot** fires all three channels, and the **AWS Lambda HITL bridge** mints the token. Any channel resolves the wait; a rejection short-circuits the rest of the chain.
4. **Close** — `process_response` interprets the decisions, the requester gets a Slack DM + Outlook summary, and **Data Fabric** records the audit trail.

## Proof it runs (live, Jun 22 2026)

The four cases above ran simultaneously on Automation Cloud — Outlook Adaptive Cards, Slack DMs, and Action Center tasks all delivered and verified.

Deployed in `Shared/DealDeskApprovalGlobal`: agent package `adaptive-approval-agent-core` v0.1.17 (3 entry points) · BPMN `DealDeskApproval` v1.1.9 · Robot `WaitDecision` v1.3.16 · Solution `.uipx` v1.2.3 · `Salesforce DealDesk MCP` AgentHub server live · AWS HITL bridge (CloudFront + Lambda) serving the approval API.

## Built with

UiPath Maestro BPMN 2.0 · Coded Agents (Python / LangGraph) · UiPath RPA + UiPath.Persistence · Action Center · Data Fabric · Integration Service (Salesforce + Outlook) · AgentHub MCP · Microsoft Adaptive Cards · Slack Block Kit · AWS Lambda + CloudFront · Cursor + Claude via UiPath for Coding Agents.

## Links & supporting files

| Item | Link |
|---|---|
| Demo video | `<LINK>` |
| Presentation deck (Other resources) | `<OneDrive/Drive/Dropbox link — set to "anyone with link can view">` |
| Code (repo or downloadable .zip) | `<LINK>` |
| Interactive project page | `<hosted URL of submission/explore/index.html>` |
| Judges' bundle (.zip — Additional info upload) | attached: architecture doc, diagrams, test evidence, blueprint |

## Team

Daniela Rosenstein, Cato Networks — submitted by one team member per the rules. Built with coding agents (Cursor + Claude via UiPath for Coding Agents).
