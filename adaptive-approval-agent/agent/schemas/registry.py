from pydantic import BaseModel, ConfigDict, Field

from agent.schemas.enums import (
    DecisionWeight,
    DefaultVisibility,
    FieldType,
    FormatterName,
    Sensitivity,
    SourceSystem,
)


class FieldDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")
    label: str = Field(..., min_length=1, max_length=80)
    source: SourceSystem
    path: str = Field(..., min_length=1)
    type: FieldType
    formatter: FormatterName
    sensitivity: Sensitivity = "internal"
    default_visibility: dict[str, DefaultVisibility] = Field(default_factory=dict)
    decision_weight: DecisionWeight = "medium"
    computed_attributes: list[str] = Field(default_factory=list)
    description: str | None = Field(default=None, max_length=200)


class PersonaLimits(BaseModel):
    model_config = ConfigDict(extra="forbid")
    max_primary: int = Field(default=6, ge=1, le=12)
    max_expandable: int = Field(default=10, ge=0, le=20)
    preferred_channel: str = "outlook"


class FieldRegistryDoc(BaseModel):
    model_config = ConfigDict(extra="forbid")
    process_type: str
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    fields: dict[str, FieldDefinition]
    personas: dict[str, PersonaLimits]
