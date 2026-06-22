import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agent.api import AdaptiveApprovalAgent
from agent.schemas import ApprovalRequest, ApproverResponse
from agent.settings import AgentSettings

FIX = REPO_ROOT / "tests/fixtures"
EXPECTED = {
    "rpc_auto.json": {"disposition": "auto_clear", "chain": ["manager"]},
    "rpc_8pct.json": {"disposition": "needs_approval", "chain": ["manager"]},
    "rpc_30pct.json": {
        "disposition": "needs_approval",
        "chain": ["manager", "director", "vp_sales"],
    },
    "rpc_high_value.json": {
        "disposition": "needs_approval",
        "chain": ["manager", "director", "vp_sales", "cfo"],
    },
}


def run(fixture: str) -> None:
    agent = AdaptiveApprovalAgent(AgentSettings())
    payload = json.loads((FIX / fixture).read_text(encoding="utf-8"))
    request = ApprovalRequest.model_validate(payload["request"])
    p = agent.plan(request)
    chain = [a.role for a in p.approvers]
    expected = EXPECTED[fixture]
    disposition = p.disposition

    assert disposition == expected["disposition"], (
        f"{fixture} disposition mismatch: expected {expected['disposition']}, got {disposition}"
    )
    assert chain == expected["chain"], (
        f"{fixture} chain mismatch: expected {expected['chain']}, got {chain}"
    )

    print(f"=== {fixture} ===")
    print("disposition:", disposition)
    print("chain      :", " -> ".join(chain))
    print("names      :", [a.display_name for a in p.approvers])
    print("emails     :", [a.email for a in p.approvers])
    print("rationale  :", p.rationale)

    if not p.approvers:
        print("next_action: auto_clear (no approver steps)")
        print()
        return

    first = p.approvers[0]
    r = agent.render(request, first, [])
    subject = r["subject"] if isinstance(r, dict) else r.subject
    card = r["card"] if isinstance(r, dict) else r.card
    html = r["html"] if isinstance(r, dict) else r.html
    print("subject    :", subject)
    action_labels = []
    for action in card.get("actions", []):
        decision = (action.get("data") or {}).get("decision", action.get("id", "unknown"))
        action_labels.append(f"{action.get('title', 'untitled')}->{decision}")
    print("card actions:", action_labels)
    print("html length:", len(html))

    response = ApproverResponse.model_validate(
        {
            "approver_id": first.user_id,
            "approver_email": first.email,
            "decision": "approve",
            "responded_at": "2026-06-02T00:00:00Z",
            "channel": "outlook",
        }
    )
    out = agent.process_response(request, p, 0, response, [])
    next_action = out["next_action"] if isinstance(out, dict) else out.next_action
    print("next_action:", next_action)
    print()


if __name__ == "__main__":
    for fixture_name in EXPECTED:
        run(fixture_name)
