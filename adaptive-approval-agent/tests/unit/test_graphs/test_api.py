from agent.api import AdaptiveApprovalAgent
from agent.schemas import ApprovalRequest
from agent.settings import AgentSettings


def test_plan_returns_routing_plan():
    agent = AdaptiveApprovalAgent(AgentSettings())
    req = ApprovalRequest(
        approval_id="a1",
        process_type="rpc",
        source_system="salesforce",
        source_record_id="006",
        requester_email="req@example.com",
        created_at="2026-05-24T00:00:00Z",
    )
    plan = agent.plan(req)
    assert plan.approvers
