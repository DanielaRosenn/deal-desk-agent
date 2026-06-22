import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agent.api import AdaptiveApprovalAgent
from agent.schemas import ApprovalRequest, Approver
from agent.settings import AgentSettings


def main() -> None:
    request = ApprovalRequest(
        approval_id="demo-001",
        process_type="rpc",
        source_system="salesforce",
        source_record_id="006-demo",
        requester_email="requester@example.com",
        raw_payload={"mock": True},
        created_at="2026-05-24T00:00:00Z",
    )
    approver = Approver(
        user_id="u-manager",
        email="manager@example.com",
        persona="manager",
        role="manager",
        display_name="Manager One",
    )
    card = AdaptiveApprovalAgent(AgentSettings()).render(request, approver, [])
    artifacts = REPO_ROOT / "artifacts"
    artifacts.mkdir(exist_ok=True)
    output = artifacts / "smoke_card.json"
    output.write_text(json.dumps(card, indent=2), encoding="utf-8")
    print(str(output))


if __name__ == "__main__":
    main()
