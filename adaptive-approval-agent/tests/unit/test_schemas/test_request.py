from agent.schemas import ApprovalRequest


def test_approval_request_default_sla():
    req = ApprovalRequest(
        approval_id="a1",
        process_type="rpc",
        source_system="salesforce",
        source_record_id="006",
        requester_email="req@example.com",
        created_at="2026-05-24T00:00:00Z",
    )
    assert req.sla_minutes == 1440
