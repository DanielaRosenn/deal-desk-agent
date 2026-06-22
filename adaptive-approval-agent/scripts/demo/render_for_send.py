import json
from pathlib import Path

from agent.api import AdaptiveApprovalAgent
from agent.schemas import ApprovalRequest
from agent.settings import AgentSettings


def main() -> None:
    payload = json.loads(Path("tests/fixtures/rpc_8pct.json").read_text(encoding="utf-8"))
    request = ApprovalRequest.model_validate(payload["request"])

    agent = AdaptiveApprovalAgent(AgentSettings())
    plan = agent.plan(request)
    approver = plan.approvers[0]
    card = agent.render(request, approver, [])

    out = {
        "approver_email": approver.email,
        "approver_name": approver.display_name,
        "disposition": plan.disposition,
        "rationale": plan.rationale,
        "card": card,
    }
    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/send_payload.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({"approver_email": approver.email, "disposition": plan.disposition, "card_type": card.get("type")}, indent=2))


if __name__ == "__main__":
    main()
