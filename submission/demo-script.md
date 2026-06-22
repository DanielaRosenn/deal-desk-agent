# Deal Desk Agent - Demo Video Script

> Target length: 3-4 minutes. Two recording options below: a low-friction local-debug cut
> (always works, no tenant runtime needed) and a full end-to-end cut (sends real Outlook
> cards). Record the local cut first - it is the safe baseline.

## Pre-flight checklist

- [ ] Terminal open at `adaptive-approval-agent/`
- [ ] `uv run pytest -q` passes (13 tests) - have it ready to show
- [ ] Fixtures visible: `tests/fixtures/rpc_8pct.json`, `rpc_30pct.json`, `rpc_auto.json`
- [ ] BPMN open in Studio Web (full cut) OR `DealDeskApproval.bpmn` open in editor (local cut)
- [ ] Outlook inbox visible on screen (full cut only)
- [ ] Screen recorder + mic tested; close noisy notifications

---

## Cut A - Local debug (safe baseline, ~3 min)

### 0:00-0:25 - Hook + problem
*Show:* title slide / the AS-IS diagram.
*Say:* "Discount and renewal-pricing approvals are slow and inconsistent - every change
touches a human, thresholds drift, and there's no audit trail. Meet the Deal Desk Agent: it
decides which deals can clear themselves, drafts the recommendation, and routes the rest to
the right approvers automatically."

### 0:25-0:55 - The architecture in one breath
*Show:* TO-BE architecture diagram.
*Say:* "Two parts. A Python LangGraph coded agent owns the judgment - disposition, risk score,
recommendation, and the approver chain. A Maestro BPMN process owns the lifecycle - Outlook
cards, the human gate, SLA escalation, and the audit log. The agent produces the chain as
data; the process iterates it."

### 0:55-1:35 - Agent intelligence (the core)
*Show:* run the agent on the 8% fixture.
```bash
uv run python -c "from agent.api import plan; import json; print(json.dumps(plan(json.load(open('tests/fixtures/rpc_8pct.json'))), indent=2))"
```
*Say:* "An 8% discount on a $40k renewal. The agent scores it - low risk, 0.2 - sets
disposition `needs_approval`, drafts an 'approve' recommendation with rationale, and sizes the
chain to a single manager. No hardcoding: change the numbers and the chain changes."

### 1:35-2:05 - Auto-clear (the wow)
*Show:* run on `rpc_auto.json` (within policy).
*Say:* "A within-policy change - under 5% and under $50k. The agent returns `auto_clear`. The
process sends zero cards and logs it automatically. That's the deflection: managers never see
the trivial deals."

### 2:05-2:35 - Multi-tier escalation
*Show:* run on `rpc_30pct.json` (30% / $1.2M).
*Say:* "Now a 30% discount on a $1.2M deal. Same agent, no code change - the chain escalates to
manager, director, VP of Sales, and CFO. The BPMN multi-instance subprocess sends one card per
approver, in order."

### 2:35-3:00 - Proof + close
*Show:* `uv run pytest -q` (13 passed), then `out/bpmn-validate.json` (Valid).
*Say:* "13 tests green, the BPMN validated with full diagramming, agent published to the
tenant. Decide, draft, route, audit - autonomously. Thanks for watching."

---

## Cut B - Full end-to-end (sends real Outlook mail, ~4 min)

Use Cut A through 1:35, then replace the rest with a live run.

### Live run in Studio Web
*Show:* trigger the BPMN debug with the 8% fixture.
*Say:* "Let's run it for real." Trigger -> agent evaluates -> one Outlook Adaptive Card lands
in the approver's inbox.

### The human gate
*Show:* the Adaptive Card in Outlook (deal details + the agent's recommendation).
*Say:* "The card surfaces the deal *and* the agent's recommendation, so the human decides
faster. I'll click Approve."

### Resume + close
*Show:* the Action Center task completing and the BPMN instance resuming -> requester notified
-> Data Fabric record written.
*Say:* "The Azure Function bridge completes the Action Center task and resumes the instance.
The requester is notified, and we log the agent's recommendation against the human decision -
that's our audit trail and our feedback loop. Done."

---

## On-screen lower-thirds (optional captions)

- "Coded Agent: disposition + risk score + approver chain"
- "auto_clear -> zero human touch"
- "Maestro BPMN: sequential multi-instance over the chain"
- "Boundary SLA timer -> reminder + escalate"
- "Data Fabric: agent recommendation vs. human decision"

## Recording tips

- Pre-clear terminal scrollback; bump font size for readability.
- Pre-run commands once so caches are warm (avoid first-run latency on camera).
- If the full E2E run is risky live, screen-record it once beforehand and narrate over it.
