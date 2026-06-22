from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BPMN = ROOT / "DealDeskSolution" / "DealDeskApproval" / "DealDeskApproval.bpmn"
WAIT_DECISION = (
    ROOT
    / "DealDeskSolution"
    / "DealDeskApproval_WaitDecision"
    / "WaitDecision.xaml"
)


def test_bpmn_parse_create_preserves_rpa_approval_id():
    """RPA job maps HITL approval id to Var_ApprovalId before parse/poll steps."""
    bpmn = BPMN.read_text(encoding="utf-8")
    create_approval = bpmn.split('id="Task_CreateApproval"', 1)[1].split(
        'id="Task_ParseCreateResponse"', 1
    )[0]
    assert "out_HitlApprovalId" in create_approval
    assert "Var_ApprovalId" in create_approval


def test_wait_decision_preserves_hitl_approval_id_after_task_resume():
    xaml = WAIT_DECISION.read_text(encoding="utf-8")
    assert "out_HitlApprovalId" in xaml
    assert "HitlApprovalId" in xaml
    assert "[out_HitlApprovalId]" in xaml or "out_HitlApprovalId" in xaml


def test_bpmn_final_summary_and_audit_use_ordered_approval_results():
    bpmn = BPMN.read_text(encoding="utf-8")
    notify = bpmn.split('id="Task_NotifyRequester"', 1)[1].split(
        'id="Task_SlackNotify"', 1
    )[0]
    slack = bpmn.split('id="Task_SlackNotify"', 1)[1].split(
        'id="Task_RecordDecision"', 1
    )[0]
    audit = bpmn.split('id="Task_RecordDecision"', 1)[1].split(
        'id="End_Done"', 1
    )[0]

    assert "Deal Desk Approval Decision Summary" in notify
    assert "Array.isArray(input.approvalResults)" in slack
    assert '"approvalTrail"' in audit
    assert "JSON.stringify(vars.Var_ApprovalResults)" in audit
