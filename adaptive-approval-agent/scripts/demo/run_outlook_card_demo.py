import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agent.api import AdaptiveApprovalAgent
from agent.schemas import ApprovalRequest
from agent.settings import AgentSettings

SCENARIOS = {
    "auto": "tests/fixtures/rpc_auto.json",
    "low": "tests/fixtures/rpc_8pct.json",
    "high": "tests/fixtures/rpc_30pct.json",
    "cfo": "tests/fixtures/rpc_high_value.json",
}

UIP_EXE = os.getenv("UIPATH_CLI_EXE", r"C:\Users\DanielaRosenstein\AppData\Roaming\npm\uip.cmd")
OUTLOOK_CONNECTION_ID = os.getenv("DEALDESK_OUTLOOK_CONNECTION_ID", "3b54e9a8-9153-4e04-abcb-2eb38bcf1651")
DEFAULT_RECIPIENT = "daniela.rosenstein@catonetworks.com"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Outlook adaptive-card demo without BPMN/Slack.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--scenario", choices=sorted(SCENARIOS.keys()))
    group.add_argument("--fixture")
    parser.add_argument("--to", default=DEFAULT_RECIPIENT)
    parser.add_argument("--subject-prefix", default="DealDesk Outlook Adaptive Demo")
    return parser.parse_args()


def resolve_fixture_path(args: argparse.Namespace) -> Path:
    if args.scenario:
        return REPO_ROOT / SCENARIOS[args.scenario]
    return (REPO_ROOT / args.fixture).resolve()


def load_request(fixture_path: Path) -> ApprovalRequest:
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    return ApprovalRequest.model_validate(payload["request"])


def build_card_html(request: ApprovalRequest) -> tuple[str, dict[str, Any]]:
    agent = AdaptiveApprovalAgent(AgentSettings())
    plan = agent.plan(request)
    approver = plan.approvers[0]
    opp = request.raw_payload.get("Opportunity", {})
    card = {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.4",
        "body": [
            {"type": "TextBlock", "size": "Medium", "weight": "Bolder", "text": "DealDesk Approval Required"},
            {
                "type": "FactSet",
                "facts": [
                    {"title": "Customer", "value": str(opp.get("Name", "N/A"))},
                    {"title": "Amount", "value": str(opp.get("Amount", "N/A"))},
                    {"title": "Discount", "value": str(opp.get("Discount__c", "N/A"))},
                    {"title": "Disposition", "value": plan.disposition},
                    {"title": "Approver", "value": approver.display_name},
                ],
            },
            {"type": "TextBlock", "text": plan.rationale[:500], "wrap": True},
        ],
        "actions": [
            {"type": "Action.Submit", "title": "Approve", "data": {"decision": "approve", "approval_id": request.approval_id}},
            {"type": "Action.Submit", "title": "Reject", "data": {"decision": "reject", "approval_id": request.approval_id}},
        ],
    }
    html = (
        "<html><body><h3>DealDesk Approval</h3>"
        '<script type="application/adaptivecard+json">'
        + json.dumps(card, separators=(",", ":"))
        + "</script></body></html>"
    )
    return html, {
        "disposition": plan.disposition,
        "approver_email": approver.email,
        "approver_name": approver.display_name,
    }


def send_outlook_card(to_address: str, subject: str, html: str) -> dict[str, Any]:
    body = {
        "message": {
            "toRecipients": to_address,
            "subject": subject,
            "body": {"contentType": "html", "content": html},
        },
        "saveToSentItems": True,
    }
    body_json = json.dumps(body, separators=(",", ":")).replace("<", "\\u003c").replace(">", "\\u003e")
    cmd = [
        UIP_EXE,
        "is",
        "resources",
        "run",
        "create",
        "uipath-microsoft-outlook365",
        "send-mail",
        "--connection-id",
        OUTLOOK_CONNECTION_ID,
        "--body",
        body_json,
        "--output",
        "json",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(
            f"Outlook send failed ({proc.returncode})\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    start = proc.stdout.find("{")
    if start < 0:
        raise RuntimeError(f"No JSON response from uip CLI. STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    return json.loads(proc.stdout[start:])


def main() -> None:
    args = parse_args()
    fixture_path = resolve_fixture_path(args)
    request = load_request(fixture_path)
    html, meta = build_card_html(request)
    subject = f"{args.subject_prefix} - {request.approval_id}"
    send_result = send_outlook_card(args.to, subject, html)
    print(
        json.dumps(
            {
                "fixture": str(fixture_path),
                "to": args.to,
                "subject": subject,
                "meta": meta,
                "send_result": send_result.get("Data", send_result),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
