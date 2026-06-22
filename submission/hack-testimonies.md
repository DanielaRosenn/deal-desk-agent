# Deal Desk Agent — Hackathon Demo Testimonies & Live Test Results

## What was built

An end-to-end AI-powered Deal Desk Approval automation on UiPath, combining:

- **LangGraph coded agent** — analyzes renewal requests, scores risk, drafts recommendation and rationale
- **Maestro BPMN** — orchestrates the approval lifecycle (multi-approver, escalation, audit trail)
- **UiPath Action Center** — native HITL task with Approve / Reject buttons (no custom polling)
- **Microsoft Adaptive Cards in Outlook** — fully interactive email card with Approve / Reject / Request Info buttons
- **Slack DM** — mirrors all approval data to the approver via Slack Block Kit

---

## Live Test Run — Jun 22, 2026 (v1.3.12)

All 4 test cases started simultaneously and sent emails + Slack DMs to **daniela.rosenstein@catonetworks.com**.

| # | Approval ID | Customer | Amount | Discount | Recommendation | Context | Job Key |
|---|-------------|----------|--------|----------|----------------|---------|---------|
| 1 | TEST-001 | GlobalTech Solutions | $120,000 | 18% | **Approve** | Standard renewal within policy | `25f74f40-5f0d-4b6e-882a-a59ce03ccc41` |
| 2 | TEST-002 | MegaCorp Industries | $350,000 | 32% | **Approve with conditions** | High-value deal — discount escalation (exceeds 25% ceiling) | `eb665e1f-aa8d-4e79-ab76-661e99f0ed92` |
| 3 | TEST-003 | StartupXYZ Inc | $28,000 | 45% | **Reject** | Excessive discount for deal size — margin impact too high | `71b22bf6-7d3c-47ad-aa8a-ce675fef2e67` |
| 4 | TEST-004 | Pharma Global Ltd | $780,000 | 22% | **Approve** | Large enterprise expansion, Finance pre-approved | `93895a08-8092-4827-becc-20c39206783d` |

### What each test demonstrated

**TEST-001 (GlobalTech):** Happy path. 18% discount is within the standard 25% policy ceiling. Agent auto-recommends approve. Adaptive card sent, Action Center task created.

**TEST-002 (MegaCorp):** Escalation path. 32% exceeds the standard ceiling. Agent recommends approval with conditions (3-year commit). Shows that the agent reasons about policy thresholds, not just rules.

**TEST-003 (StartupXYZ):** Rejection path. 45% on a $28K deal is margin-destructive. Agent recommends reject and explains why. Approver sees the recommendation in the card and can override with comments.

**TEST-004 (Pharma Global):** Pre-cleared enterprise path. Large deal, within policy, already finance-approved. Agent recommends approve and provides audit rationale. Demonstrates the system handles diverse deal types.

---

## Channels Verified Working

| Channel | Status | Notes |
|---------|--------|-------|
| Outlook Adaptive Card | ✅ Received | Interactive Approve / Reject / Request Info buttons. Requires Outlook desktop for full rendering (originator `61fed71d-3b8c-4605-8f35-d95b70ab0803`). |
| Slack DM | ✅ Received | Block Kit message with Customer, Amount, Discount %, Recommendation, Rationale, Approver, Approval ID. Includes link back to Outlook. |
| UiPath Action Center | ✅ Working | Task created in "Deal Desk" catalog. Approve / Reject buttons visible and functional. |

---

## Key differentiators shown in demo

1. **Zero-touch approvals** for deals within policy (disposition = `auto_approve`) — no human involved
2. **Policy-aware routing** — 25% ceiling triggers escalation; > $500K triggers finance sign-off
3. **Full audit trail** — rationale, recommendation, approver name, and decision logged in Orchestrator
4. **Multi-channel notification** — same rich data in Outlook Adaptive Card AND Slack
5. **Action Center native HITL** — workflow pauses and resumes via UiPath persistence, no AWS polling

---

## Approval flow user experience

When an approval is required, the approver (Daniela Rosenstein in this demo) receives:

**In Outlook (Adaptive Card):**
- Header: "Deal Desk Request - Approval Needed"
- FactSet: Customer, Amount, Discount %, Recommendation, Rationale, Approver, Approval ID
- Three action buttons: **Approve** (green), **Reject** (red), **Request Info** (grey)
- Comments field for feedback
- Rich HTML fallback table with full styling for clients that don't support cards

**In Slack:**
- Header block: "Deal Desk Request - Approval Needed"
- Fields section: Customer, Amount, Discount %, Recommendation, Approver, Approval ID
- Rationale section (memo emoji)
- Prompt to open Outlook for interactive response

---

*Generated automatically by the Deal Desk automation pipeline — Jun 22, 2026*
