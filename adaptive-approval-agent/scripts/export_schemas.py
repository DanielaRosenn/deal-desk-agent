import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pydantic import BaseModel, ConfigDict, Field

from agent.schemas import ApprovalEvent, ApprovalRequest, Approver, ApproverResponse, DecisionOutcome, RoutingPlan


class RenderInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request: ApprovalRequest
    approver: Approver
    history: list[ApprovalEvent] = Field(default_factory=list)


class RenderOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    card: dict = Field(description="Adaptive Card JSON")
    html: str = Field(description="Inline-styled HTML approval card for the email body")


class ProcessResponseInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request: ApprovalRequest
    routing_plan: RoutingPlan
    current_approver_index: int = Field(default=0, ge=0)
    response: ApproverResponse
    history: list[ApprovalEvent] = Field(default_factory=list)


class LoadRequestInput(BaseModel):
    model_config = ConfigDict(extra="allow")
    bucket: str | None = Field(default=None, description="Override storage bucket name")
    folder: str | None = Field(default=None, description="Override Orchestrator folder path")
    blob_file_path: str | None = Field(default=None, description="Override blob path inside the bucket")


class LoadRequestOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request: ApprovalRequest


class PlanOutput(RoutingPlan):
    """RoutingPlan plus the resolved request echoed back for Var_Request hydration."""

    request: ApprovalRequest


def main() -> None:
    out = Path("agent/schemas_export")
    out.mkdir(parents=True, exist_ok=True)
    (out / "plan_input.json").write_text(json.dumps(ApprovalRequest.model_json_schema(), indent=2), encoding="utf-8")
    (out / "plan_output.json").write_text(json.dumps(PlanOutput.model_json_schema(), indent=2), encoding="utf-8")
    (out / "render_input.json").write_text(json.dumps(RenderInput.model_json_schema(), indent=2), encoding="utf-8")
    (out / "render_output.json").write_text(json.dumps(RenderOutput.model_json_schema(), indent=2), encoding="utf-8")
    (out / "process_response_input.json").write_text(
        json.dumps(ProcessResponseInput.model_json_schema(), indent=2), encoding="utf-8"
    )
    (out / "process_response_output.json").write_text(
        json.dumps(DecisionOutcome.model_json_schema(), indent=2), encoding="utf-8"
    )
    (out / "load_request_input.json").write_text(
        json.dumps(LoadRequestInput.model_json_schema(), indent=2), encoding="utf-8"
    )
    (out / "load_request_output.json").write_text(
        json.dumps(LoadRequestOutput.model_json_schema(), indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
