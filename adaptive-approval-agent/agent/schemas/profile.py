from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from agent.schemas.enums import Channel, Persona


class ApproverProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    approver_id: str = Field(..., max_length=50)
    email: EmailStr
    persona: Persona
    total_approvals: int = Field(default=0, ge=0)
    total_rejections: int = Field(default=0, ge=0)
    avg_response_seconds: int | None = Field(default=None, ge=0)
    typically_expanded_field_ids: list[str] = Field(default_factory=list, max_length=10)
    typically_skipped_field_ids: list[str] = Field(default_factory=list, max_length=10)
    preferred_channel: Channel = "outlook"
    override_rate: float | None = Field(default=None, ge=0.0, le=1.0)
    info_request_keywords_top: list[str] = Field(default_factory=list, max_length=10)
    last_updated: datetime
    sample_size: int = Field(default=0, ge=0)

    @property
    def is_warm(self) -> bool:
        return self.sample_size >= 5
