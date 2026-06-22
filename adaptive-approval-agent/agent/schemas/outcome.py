from pydantic import BaseModel, ConfigDict, Field

from agent.schemas.enums import NextAction
from agent.schemas.request import Approver


class DecisionOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid")
    next_action: NextAction
    next_approver: Approver | None = None
    completion_summary: str | None = Field(default=None, max_length=500)
    escalation_reason: str | None = Field(default=None, max_length=300)
    info_request_message: str | None = Field(default=None, max_length=1000)
    learning_signals: dict = Field(default_factory=dict)

    def model_post_init(self, __context) -> None:
        if self.next_action == "next_approver" and self.next_approver is None:
            raise ValueError("next_approver required when next_action == 'next_approver'")
        if self.next_action == "escalate" and not self.escalation_reason:
            raise ValueError("escalation_reason required when next_action == 'escalate'")
        if self.next_action == "request_info_loop" and not self.info_request_message:
            raise ValueError("info_request_message required when next_action == 'request_info_loop'")
        if self.next_action in ("complete_approved", "complete_rejected") and not self.completion_summary:
            raise ValueError("completion_summary required for terminal actions")
