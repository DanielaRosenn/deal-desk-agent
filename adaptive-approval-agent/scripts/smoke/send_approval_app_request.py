import json
import subprocess


def main() -> int:
    exe = r"C:\Users\DanielaRosenstein\AppData\Roaming\npm\uip.cmd"

    approval_body = {
        "processId": "DealDeskApproval",
        "process_id": "DealDeskApproval",
        "externalRef": "manual-test-approval-app-001",
        "title": "Test Approval",
        "approvalType": "sequential",
        "approval_type": "sequential",
        "priority": "normal",
        "notificationChannel": "both",
        "notification_channel": "both",
        "approvalUrlBase": "https://djun97l419cdy.cloudfront.net",
        "metadata": {
            "approval_id": "manual-test-approval-app-001",
            "approver_role": "manager",
            "approver_index": "0",
            "source": "manual-direct-waitdecision",
        },
        "formSchema": [
            {"name": "approval_id", "label": "Approval ID", "type": "text", "required": False},
            {"name": "customer", "label": "Customer", "type": "text", "required": False},
            {"name": "amount", "label": "Amount", "type": "text", "required": False},
            {"name": "discount", "label": "Discount %", "type": "text", "required": False},
            {
                "name": "recommended_decision",
                "label": "Recommended Decision",
                "type": "text",
                "required": False,
            },
            {"name": "rationale", "label": "Rationale", "type": "text", "required": False},
            {"name": "comments", "label": "Comments", "type": "text", "required": False},
        ],
        "formData": {
            "approval_id": "manual-test-approval-app-001",
            "customer": "Beta Renewal",
            "amount": "250000",
            "discount": "30",
            "recommended_decision": "escalate",
            "rationale": "manual approval app routing test",
        },
        "approvers": [
            {
                "email": "daniela.rosenstein@catonetworks.com",
                "name": "Daniela Rosenstein",
                "sequenceOrder": 1,
                "notificationChannel": "both",
                "notification_channel": "both",
            }
        ],
        "orchestrator_folder_id": 3050804,
        "orchestrator_process_key": "DealDeskApproval",
        "approval_step": "manager",
    }

    input_args = {
        "in_ApprovalBodyJson": json.dumps(approval_body, separators=(",", ":")),
        "in_RenderedCardHtml": "DealDesk approval app routing test message",
        "in_HitlApiKey": "hitl_test_api_key_12345",
        "in_HitlApiUrl": "http://HitlAp-HitlA-faNGMOpTUFLe-988756144.us-east-1.elb.amazonaws.com",
        "in_OrchestratorFolderId": 3050804,
    }

    cmd = [
        exe,
        "or",
        "jobs",
        "start",
        "EDEC7BF6-8785-4037-A4E2-2474EE6609E5",
        "--folder-key",
        "5f93aec0-a43b-4281-9fa4-0b695b23effe",
        "--jobs-count",
        "1",
        "--input-arguments",
        json.dumps(input_args, separators=(",", ":")),
        "--wait-for-completion",
        "--timeout",
        "240",
        "--output",
        "json",
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    print("EXIT", proc.returncode)
    if proc.stdout:
        print(proc.stdout)
    if proc.stderr:
        print(proc.stderr)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
