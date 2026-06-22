import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agent.schemas.enums import Decision, Persona, Urgency

_FIELD_ID_RE = r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)*$"


class CardSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    approval_id: str = Field(..., min_length=1, max_length=50)
    approver_persona: Persona
    urgency: Urgency = "standard"
    headline: str = Field(..., min_length=10, max_length=80)
    summary: str = Field(..., min_length=20, max_length=300)
    primary_field_ids: list[str] = Field(..., min_length=1, max_length=8)
    expandable_field_ids: list[str] = Field(default_factory=list, max_length=15)
    decision_options: list[Decision] = Field(..., min_length=2, max_length=4)
    rationale: str = Field(..., max_length=500)
    predicted_decision: Decision | None = None

    @field_validator("primary_field_ids", "expandable_field_ids")
    @classmethod
    def validate_field_id_format(cls, v: list[str]) -> list[str]:
        for fid in v:
            if not re.match(_FIELD_ID_RE, fid):
                raise ValueError(f"Invalid field_id format: {fid!r}")
        return v

    @field_validator("decision_options")
    @classmethod
    def require_approve_and_reject(cls, v: list[str]) -> list[str]:
        if "approve" not in v or "reject" not in v:
            raise ValueError("decision_options must include both 'approve' and 'reject'")
        return v

    @field_validator("expandable_field_ids")
    @classmethod
    def no_overlap_with_primary(cls, v: list[str], info) -> list[str]:
        primary = set(info.data.get("primary_field_ids", []))
        overlap = primary & set(v)
        if overlap:
            raise ValueError(f"Fields cannot be both primary and expandable: {sorted(overlap)}")
        return v
