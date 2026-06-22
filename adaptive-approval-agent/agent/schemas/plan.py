from pydantic import BaseModel, ConfigDict, Field

from agent.schemas.enums import Decision, Disposition
from agent.schemas.request import Approver


class RoutingPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    approvers: list[Approver] = Field(..., min_length=1, max_length=10)
    rationale: str = Field(..., max_length=1000)
    disposition: Disposition = "needs_approval"
    risk_score: float = Field(default=0.0, ge=0.0, le=1.0)
    recommended_decision: Decision = "approve"
    recommendation_rationale: str = Field(default="", max_length=1000)
    guardrail_violations_corrected: list[str] = Field(default_factory=list)
    soft_guidance_applied: list[str] = Field(default_factory=list)
