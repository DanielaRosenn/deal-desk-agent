# DealDesk Approval Agent

Agent-based Deal Desk solution that evaluates sales opportunities, routes them through a sequential approval chain, and records a final outcome. Discount %, deal value, and deal type determine the approver chain. The approval chain (Outlook HTML emails + AWS HITL service + BPMN polling) handles non-standard deals.

**Primary reference**: [`docs/SOLUTION_BLUEPRINT.md`](docs/SOLUTION_BLUEPRINT.md) — single source of truth for process design, component map, identifiers, deployment, and gap history.

---

## Quick start

```powershell
cd adaptive-approval-agent

# Run unit tests
python -m pytest tests/unit/ -q

# Run high-risk E2E demo
python scripts/demo/run_e2e_demo.py --scenario high
```

## Source layout

| Path | Description |
|---|---|
| `DealDeskSolution/DealDeskApproval/DealDeskApproval.bpmn` | BPMN orchestration (main process) |
| `DealDeskSolution/DealDeskApproval_WaitDecision/WaitDecision.xaml` | RPA robot: POSTs to HITL, sends email, returns token |
| `agent/` | Python coded agent (`plan`, `render`, `process_response` nodes) |
| `agent/config/hibob_org.json` | Mocked management chain (HiBob substitute) |
| `tests/fixtures/` | Demo deal payloads (`rpc_8pct.json`, `rpc_30pct.json`, ...) |
| `scripts/demo/run_e2e_demo.py` | E2E demo runner |
| `docs/SOLUTION_BLUEPRINT.md` | Full solution blueprint (this is the runbook) |

## Demo scope

- Salesforce is the opportunity source. The base flow can run from payload fixtures, and the hack demo also has an AgentHub `Salesforce DealDesk MCP` sidecar in `Shared/DealDeskApprovalGlobal` for live read-only Opportunity/Account context.
- Agent logic (`plan`, `render`, `process_response`) is AI-driven.
- HiBob management chain is mocked from `agent/config/hibob_org.json`.
- HITL backend is the AWS CloudFront bridge (`https://djun97l419cdy.cloudfront.net`).
