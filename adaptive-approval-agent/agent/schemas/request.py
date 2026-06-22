from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from agent.schemas.enums import Channel, Decision, Persona, ProcessType, SourceSystem


class Approver(BaseModel):
    model_config = ConfigDict(extra="forbid")
    user_id: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    persona: Persona
    role: str = Field(..., min_length=1, max_length=50)
    display_name: str = Field(..., min_length=1, max_length=100)
    geo: str | None = Field(default=None, max_length=10)
    timezone: str | None = Field(default=None, max_length=50)


class ApprovalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    approval_id: str = Field(..., min_length=1, max_length=50)
    process_type: ProcessType
    source_system: SourceSystem
    source_record_id: str = Field(..., min_length=1, max_length=100)
    requester_email: EmailStr
    requester_id: str | None = Field(default=None, max_length=50)
    raw_payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    sla_minutes: int = Field(default=1440, ge=15, le=43200)
    config_version_snapshot: str | None = None


class EngagementSignals(BaseModel):
    model_config = ConfigDict(extra="forbid")
    time_on_card_seconds: int | None = Field(default=None, ge=0, le=86400)
    expanded_section_ids: list[str] = Field(default_factory=list, max_length=20)
    clicks_before_decision: int | None = Field(default=None, ge=0)
    info_request_keywords: list[str] = Field(default_factory=list, max_length=20)


class ApproverResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    approver_id: str
    approver_email: EmailStr
    decision: Decision
    comments: str | None = Field(default=None, max_length=2000)
    responded_at: datetime
    channel: Channel
    engagement_signals: EngagementSignals = Field(default_factory=EngagementSignals)

    @field_validator("decision", mode="before")
    @classmethod
    def normalize_decision(cls, value: object) -> str:
        raw = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
        if raw in {"approve", "approved", "completed", "completed_approved", "accepted"}:
            return "approve"
        if raw in {"reject", "rejected", "deny", "denied", "decline", "declined"}:
            return "reject"
        if raw in {"request_info", "more_info", "needs_info", "information_requested"}:
            return "request_info"
        return "escalate"
