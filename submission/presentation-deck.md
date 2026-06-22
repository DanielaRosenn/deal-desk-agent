# Deal Desk Agent — Presentation Deck (AgentHack 2026)

> **Track 2: UiPath Maestro BPMN**
> Concept: *"Every sales org has a Deal Desk. Ours is an AI agent."*
>
> Accurate architecture (v1.2.3, June 2026):
> - Approval delivery = Outlook HTML email + AWS HITL portal (NOT Adaptive Card / Action Center)
> - Approval robot = WaitDecision UiPath Robot (NOT Azure Function)
> - Salesforce = live IS connection + AgentHub MCP sidecar (NOT just mock payload)
> - Notification = Slack DM to requester (after outcome)
> - Chain = manager → director → vp_sales → cfo → cro (cro added above $750k)

---

## Slide 1 — Title

**Deal Desk Agent — Your AI Deal Desk Analyst**

UiPath AgentHack 2026 · Track 2: Maestro BPMN
Built with coding agents (Cursor + Claude via UiPath for Coding Agents) · Runs on Automation Cloud
Daniela Rosenstein, Cato Networks

*Notes:* "Every sales org has a Deal Desk — the person who reviews pricing exceptions, chases
managers, documents decisions. We replaced the manual back-and-forth with an AI agent that does
the same job, end to end, governed."

---

## Slide 2 — The problem

**The manual Deal Desk: slow, inconsistent, invisible**

- The Opportunity Owner (AE) submits a discount request → Deal Desk emails managers → waits → collates replies → updates CRM
- No SLA, no consistent routing policy, decisions buried in email threads
- Result: deals stall, thresholds drift, no audit trail

*Notes:* Before: rep emails Deal Desk, Deal Desk emails manager, manager forwards up, someone
replies, rep updates the CRM by hand. Slow, inconsistent, unauditable.

---

## Slide 3 — The idea

**Agent = Deal Desk analyst. Maestro = lifecycle.**

Before: `AE → Deal Desk (human) → Manager → Director → ... → CRM`

After: `Salesforce event → Deal Desk Agent (collect + reason + route) → Approvers (HTML email + HITL portal) → Slack + Outlook summary → Audit`

The agent handles what the human Deal Desk does today. The humans-in-the-loop are the approvers
(Manager → Director → VP Sales → CFO → CRO). The AE gets notified automatically at the end.

*Notes:* Clean seam: agent owns judgment, Maestro owns lifecycle. Each is versioned and testable
independently.

---

## Slide 4 — Step 1: Live data collection

**Real Salesforce data, real org chart**

From **Salesforce** (via AgentHub MCP sidecar — live IS connection):
- `Salesforce DealDesk MCP` server deployed in AgentHub (`Shared/DealDeskApprovalGlobal`)
- Tools: `getSalesforceOpportunity`, `getSalesforceAccount`, `searchSalesforceSoql`
- Fetches live Opportunity fields: `Discount__c`, `Amount`, customer name, opportunity type

From **HiBob** (org chart — mocked for demo):
- Walks `reportsTo` hierarchy from the Opportunity Owner upward
- Resolves named approvers: Maya Stone (Manager) → Daniel Park (Director) → Ari Reynolds (VP Sales) → Lior Cohen (CFO) → Noa Bennett (CRO)
- Chain is built as a data structure, not hardcoded

*Notes:* The Salesforce MCP is a real AgentHub-hosted server. SOQL smoke test ran against the
production IS connection. HiBob is mocked for the demo but the architecture is production-ready.

---

## Slide 5 — Step 2: Business rules + LLM reasoning

**Two layers of intelligence working together**

**Business rules layer** (deterministic, `plan_nodes.py`):
- `risk_score = min(1.0, 0.5 × (discount / 25%) + 0.5 × (value / $500k))`
- `auto_clear`: discount ≤ 5% AND value ≤ $50k — no human touch, log and close
- `needs_approval`: discount > 25% → add Director + VP Sales; value > $500k → add CFO; value > $750k → add CRO
- Invalid payload → `exception` → human review

**LLM reasoning layer** (contextual):
- Drafts `recommendation_rationale` — WHY approve or flag, with deal context and risk framing
- Produces `recommended_decision` that every approver sees in their email card
- The LLM articulates the judgment; the rules define the policy

Output: `RoutingPlan` (disposition · risk_score · rationale · ordered approver chain as data)

*Notes:* The agent is not a rule engine. It uses the LLM to reason about the deal in context,
produce human-readable rationale, and embed that in every approval card.

---

## Slide 6 — Step 3 & 4: Route + Human sign-off

**Right actor at every step — Maestro BPMN orchestrates**

The per-approver loop (sequential multi-instance subprocess):
1. **`render` agent** — generates deal context, risk score, LLM recommendation, formatted for Adaptive Card
2. **WaitDecision UiPath Robot** (RPA v1.3.16) — **three channels simultaneously, no polling:**
   - Creates **Action Center** external task (Deal Desk catalog, Approve/Reject/Request Info)
   - Sends **Outlook Adaptive Card** — real interactive card (originator `61fed71d`), three action buttons, HTML fallback
   - Sends **Slack Block Kit** DM — deal data, agent recommendation, link back to Outlook
   - **Suspends** via `UiPath.Persistence.Activities` until Action Center resolves
3. Approver decides via any channel — Adaptive Card buttons in Outlook OR Action Center portal
4. Robot **resumes**, returns decision directly to BPMN — no separate BPMN polling loop
5. Rejection **short-circuits** remaining chain immediately (BPMN `completionCondition`)

**Two human roles:**
- **Opportunity Owner (AE)** — Slack DM + Outlook summary with full ordered trail at end
- **Approvers** — Adaptive Card in Outlook (one click) or Action Center — their choice

*Notes:* Live test: four simultaneous runs Jun 22. Adaptive Card ✅ Slack ✅ Action Center ✅
All three channels delivering simultaneously. That is the "right actor for every step" story —
human touch where it matters, zero human touch where it doesn't.

---

## Slide 7 — The whole flow

**(Embed `code-graph/deal-desk-flow.gif`)**

Salesforce → `plan` (collect + reason) → BPMN gateway →
per-approver loop: `render` → WaitDecision Robot → Outlook email → HITL portal → BPMN poll →
`process_response` → Slack DM + Outlook summary → Data Fabric audit

*Notes:* Walk the animation. Key moments: Salesforce trigger, LLM rationale in the email card,
approver one-click portal decision, rejection short-circuit, Slack notification, audit record.

---

## Slide 8 — Three paths, one process

**Same BPMN, agent decides the path**

1. **Auto-clear** (≤5% / ≤$50k) — zero human touches, closed in seconds
2. **One approver** (8% / $40k) — one email to Maya Stone → approve → Slack + Outlook to AE
3. **Full chain** (30% / $1.2M) — four sequential approvers, each gets LLM rationale card;
   rejection at any step stops the chain

*Notes:* The multi-tier path is the wow moment: four real named approvers, right order, each
card containing the agent's reasoning. This is what replaces a week of email.

---

## Slide 8b — Live evidence (v1.3.12, Jun 22 2026)

**Four simultaneous test runs. All channels confirmed.**

| Customer | Amount | Discount | Agent recommendation |
|---|---|---|---|
| GlobalTech Solutions | $120k | 18% | Approve — within policy |
| MegaCorp Industries | $350k | 32% | Approve with conditions — escalation |
| StartupXYZ Inc | $28k | 45% | Reject — margin impact too high |
| Pharma Global Ltd | $780k | 22% | Approve — enterprise expansion |

Outlook Adaptive Card ✅ · Slack Block Kit ✅ · Action Center ✅

*Notes:* Real job keys, real Approval IDs, real emails received. The agent correctly
recommended Reject on the 45% deal — the LLM reasoning, not just the rule.

---

## Slide 9 — Built by coding agents (the bonus)

**Natural language → coding agents → governed cloud process**

- Entire solution authored with **Cursor + Claude** via **UiPath for Coding Agents** (`uip` CLI + skills)
- Coding agents generated/edited: LangGraph agent, BPMN, WaitDecision XAML, bindings, Salesforce MCP tools, Data Fabric entity
- Low-code Maestro + pro-code LangGraph agent + RPA robot — all three combined
- This IS the laptop → production bridge UiPath asked for this year

*Notes:* The medium is the message. The agent that manages your Deal Desk was built by coding
agents. Directly earns the coding-agent bonus and embodies the 2026 event theme.

---

## Slide 10 — Governance

**Trustworthy by construction**

- **Human gate**: approvers decide via AWS HITL portal (email link → one-click)
- **SLA**: 30-second poll cycle; future: webhook callback for instant notification
- **Short-circuit**: rejection at any step ends the chain immediately
- **Audit**: Data Fabric `ApprovalAudit` — ordered trail, agent rec vs. each human decision
- **Notification**: Slack DM + Outlook summary to Opportunity Owner
- **Guardrails**: invalid payload → exception; empty chain → manager fallback
- **Deployed**: agent v0.1.17, BPMN v1.1.9, Robot v1.2.4, solution v1.2.3 on Automation Cloud

*Notes:* Every decision is logged and traceable. The audit record is also the training signal
to safely expand auto-clear thresholds over time.

---

## Slide 11 — Business impact

**What changes for the sales team**

| Before | After |
|---|---|
| AE emails Deal Desk | Salesforce event triggers agent |
| Deal Desk reads SF manually | Live Salesforce MCP query, automated |
| Deal Desk emails manager | Agent collects, reasons, routes — automatically |
| Wait days for email replies | Email → portal link → decision in minutes |
| No SLA | 30s polling cycle, escalation on silence |
| Inconsistent policy | risk_score formula applied identically |
| No audit trail | Data Fabric records every agent + human decision |
| ALL deals touch humans | Low-risk (≤5%/≤$50k) clear with zero human touch |

Same pattern → invoice approval, expense reporting, vendor onboarding (Track 2 examples).

---

## Slide 12 — Close

**Every Deal Desk should work like this.**

Collect. Reason. Route. Sign-off. Audit. Automatically.

Agent owns the analysis · Maestro owns the lifecycle · UiPath owns governance
Built with coding agents · Deployed on Automation Cloud

DevPost: `<link>` · Demo video: `<link>` · Code: `<link>`

*Notes:* Invite judges to try the interactive disposition calculator and watch the animated flow.

---

## Judging-fit map (AgentHack 2026 Track 2)

| Criterion | Slides |
|---|---|
| Real industry pain + business value | 2, 11 |
| Agent reasoning (not just rules) | 4, 5 |
| Clean BPMN with right actor per step | 3, 6, 7, 8 |
| Human-in-the-loop (two distinct roles) | 6, 10 |
| Governance + auditability | 10 |
| Runs on Automation Cloud (hard req) | 8b, 10 |
| Coding-agent bonus | 1, 9 |
| Demo quality / live evidence | 7, 8b, video, interactive page |
