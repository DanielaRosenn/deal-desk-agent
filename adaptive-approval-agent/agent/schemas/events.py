from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from agent.schemas.enums import EventType


class ApprovalEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_id: str
    approval_id: str = Field(..., min_length=1, max_length=50)
    event_type: EventType
    event_timestamp: datetime
    approver_id: str | None = Field(default=None, max_length=50)
    payload: dict[str, Any] = Field(default_factory=dict)
