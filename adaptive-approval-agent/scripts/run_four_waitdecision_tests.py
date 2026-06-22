"""
Four Deal Desk WaitDecision smoke tests with enriched Salesforce-style Opportunity data.
Run from repo:  uv run python adaptive-approval-agent/scripts/run_four_waitdecision_tests.py
Or:  py adaptive-approval-agent/scripts/run_four_waitdecision_tests.py  (with uip on PATH)
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

FOLDER = "Shared/DealDeskApprovalGlobal"
PROCESS = "0932CB58-FC8A-4287-AB2C-410E85075EBC"
HITL_URL = "https://djun97l419cdy.cloudfront.net"
HITL_KEY = "hitl_test_api_key_12345"
APPROVER_EMAIL = "daniela.rosenstein@catonetworks.com"
FOLDER_ID = 485092


def _opp(**kwargs) -> dict:
    base = {
        "Name": kwargs.get("name", "Customer"),
        "Type": kwargs.get("opp_type", "Renewal"),
        "Amount": kwargs.get("amount", 100000),
        "Discount__c": kwargs.get("discount", 10),
        "Account": {"Name": kwargs.get("account_name", "Account"), "Industry": kwargs.get("industry", "Technology")},
        "Renewal_Term__c": kwargs.get("renewal_term", 12),
        "Churn_Risk__c": kwargs.get("churn_risk", "Low"),
        "Customer_Tier__c": kwargs.get("tier", "Commercial"),
        "Multi_Year_Discount__c": kwargs.get("multi_year", False),
        "Competitor_Involved__c": kwargs.get("competitor", False),
        "Current_ARR__c": kwargs.get("current_arr", 80000),
        "Health_Score__c": kwargs.get("health", 75),
        "Previous_Discount__c": kwargs.get("prev_discount", 8),
    }
    return base


TESTS = [
    {
        "id": "ENRICH-001",
        "title": "Strategic renewal within policy",
        "opp": _opp(
            name="GlobalTech Solutions",
            account_name="GlobalTech Solutions",
            amount=120000,
            discount=18,
            tier="Strategic",
            churn_risk="Low",
            health=88,
            renewal_term=12,
            competitor=False,
            multi_year=False,
            current_arr=95000,
            prev_discount=12,
            industry="Software",
        ),
    },
    {
        "id": "ENRICH-002",
        "title": "Retention: high churn + competitor",
        "opp": _opp(
            name="MegaCorp Industries",
            account_name="MegaCorp Industries",
            amount=350000,
            discount=32,
            tier="Enterprise",
            churn_risk="High",
            health=62,
            renewal_term=24,
            competitor=True,
            multi_year=True,
            current_arr=310000,
            prev_discount=28,
            industry="Manufacturing",
        ),
    },
    {
        "id": "ENRICH-003",
        "title": "SMB aggressive discount / weak health",
        "opp": _opp(
            name="StartupXYZ Inc",
            account_name="StartupXYZ Inc",
            amount=28000,
            discount=45,
            tier="SMB",
            churn_risk="Medium",
            health=41,
            renewal_term=12,
            competitor=False,
            multi_year=False,
            current_arr=22000,
            prev_discount=20,
            industry="Retail",
        ),
    },
    {
        "id": "ENRICH-004",
        "title": "Large enterprise multi-year expansion",
        "opp": _opp(
            name="Pharma Global Ltd",
            account_name="Pharma Global Ltd",
            amount=780000,
            discount=22,
            tier="Enterprise",
            churn_risk="Low",
            health=91,
            renewal_term=36,
            competitor=False,
            multi_year=True,
            current_arr=650000,
            prev_discount=20,
            industry="Healthcare",
        ),
    },
]


def main() -> int:
    results = []
    for t in TESTS:
        oid = t["opp"]
        body = {
            "processId": "DealDeskApproval",
            "externalRef": t["id"],
            "title": f"[Action required] {t['title']}",
            "approvalType": "sequential",
            "priority": "normal",
            "notificationChannel": "both",
            "approvalUrlBase": HITL_URL,
            "metadata": {"approval_id": t["id"], "source": "run_four_waitdecision_tests.py"},
            "formSchema": [
                {"name": "approval_id", "label": "Approval ID", "type": "text", "required": False},
                {"name": "customer", "label": "Customer", "type": "text", "required": False},
                {"name": "amount", "label": "Amount", "type": "text", "required": False},
                {"name": "discount", "label": "Discount %", "type": "text", "required": False},
                {"name": "requester", "label": "Requester", "type": "text", "required": False},
                {"name": "churn_risk", "label": "Churn risk", "type": "text", "required": False},
                {"name": "customer_tier", "label": "Customer tier", "type": "text", "required": False},
                {"name": "health_score", "label": "Health score", "type": "text", "required": False},
                {"name": "renewal_term_months", "label": "Renewal term (months)", "type": "text", "required": False},
                {"name": "competitor_involved", "label": "Competitor involved", "type": "text", "required": False},
                {"name": "recommended_decision", "label": "Recommended Decision", "type": "text", "required": False},
                {"name": "rationale", "label": "Rationale", "type": "text", "required": False},
            ],
            "formData": {
                "approval_id": t["id"],
                "customer": str(oid.get("Name") or ""),
                "amount": str(oid.get("Amount") or ""),
                "discount": str(oid.get("Discount__c") or ""),
                "requester": APPROVER_EMAIL,
                "churn_risk": str(oid.get("Churn_Risk__c") or ""),
                "customer_tier": str(oid.get("Customer_Tier__c") or ""),
                "health_score": str(oid.get("Health_Score__c") or ""),
                "renewal_term_months": str(oid.get("Renewal_Term__c") or ""),
                "competitor_involved": str(oid.get("Competitor_Involved__c")),
                "recommended_decision": "approve",
                "rationale": f"Fixture scenario: {t['title']}",
            },
            "approvers": [
                {
                    "email": APPROVER_EMAIL,
                    "name": "Daniela Rosenstein",
                    "sequenceOrder": 1,
                    "notificationChannel": "both",
                }
            ],
            "orchestrator_folder_id": FOLDER_ID,
            "orchestrator_process_key": "DealDeskApproval",
            "approval_step": "manager",
        }

        args = {
            "in_ApprovalBodyJson": json.dumps(body),
            "in_RenderedCardHtml": "",
            "in_HitlApiKey": HITL_KEY,
            "in_HitlApiUrl": HITL_URL,
            "in_HitlCreateResponseJson": "{}",
            "in_OrchestratorFolderId": FOLDER_ID,
            "in_SlackBotToken": "",
        }

        r = subprocess.run(
            [
                "uip",
                "or",
                "jobs",
                "start",
                "--folder-path",
                FOLDER,
                "--input-arguments",
                json.dumps(args),
                PROCESS,
            ],
            capture_output=True,
            text=True,
            shell=True,
        )
        try:
            out = json.loads(r.stdout)
            job_key = out.get("Data", {}).get("Jobs", [{}])[0].get("Key", "?")
            status = out.get("Result", "?")
        except Exception:
            job_key = "?"
            status = r.stdout[:200]
        results.append({"id": t["id"], "status": status, "job_key": job_key})
        print(f"{t['id']}: {status} -> {job_key}")

    print(json.dumps(results, indent=2))
    return 0 if all(x.get("status") == "Success" for x in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
