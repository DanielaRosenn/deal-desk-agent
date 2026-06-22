import json
from datetime import datetime, timezone
from pathlib import Path

from agent.api import AdaptiveApprovalAgent
from agent.schemas import ApprovalRequest, ApproverResponse, RoutingPlan
from agent.settings import AgentSettings

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"


def _request(fixture_name: str) -> ApprovalRequest:
    payload = json.loads((FIXTURES / fixture_name).read_text(encoding="utf-8"))
    return ApprovalRequest.model_validate(payload["request"])


def _agent() -> AdaptiveApprovalAgent:
    return AdaptiveApprovalAgent(AgentSettings())


def test_routing_plan_exposes_disposition_fields():
    fields = RoutingPlan.model_fields
    assert "disposition" in fields
    assert "risk_score" in fields
    assert "recommended_decision" in fields
    assert "recommendation_rationale" in fields


def test_low_discount_low_value_auto_clears():
    plan = _agent().plan(_request("rpc_auto.json"))
    assert plan.disposition == "auto_clear"
    assert plan.recommended_decision == "approve"
    assert plan.recommendation_rationale


def test_mid_discount_needs_single_manager():
    plan = _agent().plan(_request("rpc_8pct.json"))
    assert plan.disposition == "needs_approval"
    assert len(plan.approvers) == 1
    assert plan.approvers[0].role == "manager"
    assert plan.recommended_decision == "approve"
    assert plan.recommendation_rationale


def test_high_discount_escalates_chain():
    plan = _agent().plan(_request("rpc_30pct.json"))
    assert plan.disposition == "needs_approval"
    assert len(plan.approvers) > 1
    assert {"director", "vp_sales"} <= {a.role for a in plan.approvers}


def test_high_value_uses_full_hibob_chain_to_demo_inbox():
    req = ApprovalRequest(
        approval_id="rpc-high-value-001",
        process_type="rpc",
        source_system="salesforce",
        source_record_id="006-high-value",
        requester_email="owner@example.com",
        raw_payload={
            "Opportunity": {
                "Name": "Enterprise Renewal",
                "Discount__c": 0.3,
                "Amount": 900000,
            }
        },
        created_at="2026-05-24T00:00:00Z",
    )
    plan = _agent().plan(req)

    assert [a.role for a in plan.approvers] == [
        "manager",
        "director",
        "vp_sales",
        "cfo",
        "cro",
    ]
    assert {a.email for a in plan.approvers} == {"daniela.rosenstein@catonetworks.com"}


def test_missing_value_is_exception():
    req = ApprovalRequest(
        approval_id="rpc-bad-001",
        process_type="rpc",
        source_system="salesforce",
        source_record_id="006-bad",
        requester_email="owner@example.com",
        raw_payload={"Opportunity": {"Name": "No Numbers"}},
        created_at="2026-05-24T00:00:00Z",
    )
    plan = _agent().plan(req)
    assert plan.disposition == "exception"
    assert plan.recommended_decision == "escalate"


def test_auto_clear_short_circuits_response():
    agent = _agent()
    request = _request("rpc_auto.json")
    plan = agent.plan(request)
    response = ApproverResponse(
        approver_id="user-manager",
        approver_email="approver@example.com",
        decision="approve",
        responded_at=datetime.now(timezone.utc),
        channel="outlook",
    )
    outcome = agent.process_response(
        request=request,
        routing_plan=plan,
        current_approver_index=0,
        response=response,
        history=[],
    )
    assert outcome.next_action == "auto_clear"


def test_process_response_accepts_raw_hitl_statuses():
    agent = _agent()
    request = _request("rpc_8pct.json")
    plan = agent.plan(request)
    response = ApproverResponse(
        approver_id="user-manager",
        approver_email="approver@example.com",
        decision="approved",
        responded_at=datetime.now(timezone.utc),
        channel="outlook",
    )

    outcome = agent.process_response(
        request=request,
        routing_plan=plan,
        current_approver_index=0,
        response=response,
        history=[],
    )

    assert outcome.next_action == "complete_approved"
