import pytest
from pydantic import ValidationError

from agent.schemas import CardSpec


def test_card_spec_minimal_valid():
    spec = CardSpec(
        approval_id="a1",
        approver_persona="manager",
        headline="Approve renewal for Acme now",
        summary="Standard renewal request with manageable discount and low risk profile.",
        primary_field_ids=["deal.customer_name"],
        decision_options=["approve", "reject"],
        rationale="baseline",
    )
    assert spec.approval_id == "a1"


def test_decision_options_require_approve_reject():
    with pytest.raises(ValidationError):
        CardSpec(
            approval_id="a1",
            approver_persona="manager",
            headline="Approve renewal for Acme now",
            summary="Standard renewal request with manageable discount and low risk profile.",
            primary_field_ids=["deal.customer_name"],
            decision_options=["approve", "escalate"],
            rationale="baseline",
        )
