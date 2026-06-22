from typing import Literal

ApprovalStatus = Literal[
    "pending_plan",
    "pending_approver",
    "approved",
    "rejected",
    "request_info_pending",
    "escalated",
    "failed",
]
Persona = Literal["manager", "director", "vp", "cfo", "legal"]
Urgency = Literal["standard", "expedited", "critical"]
Channel = Literal["outlook", "slack", "teams"]
Decision = Literal["approve", "reject", "request_info", "escalate"]
Disposition = Literal["auto_clear", "needs_approval", "exception"]
ProcessType = Literal["rpc", "expense", "access_request", "vendor_onboarding"]
SourceSystem = Literal["salesforce", "concur", "okta", "sap", "manual", "concur_computed"]
DefaultVisibility = Literal["primary", "expandable", "hidden"]
Sensitivity = Literal["public", "internal", "restricted", "confidential"]
DecisionWeight = Literal["high", "medium", "low"]
FieldType = Literal["string", "number", "boolean", "list", "object", "date", "datetime"]
FormatterName = Literal[
    "string",
    "string_truncate_300",
    "percentage",
    "currency_usd",
    "years",
    "date_relative",
    "date_iso",
    "renewal_list",
    "category_list",
    "violation_list",
    "history_summary",
    "boolean_yes_no",
]
EventType = Literal[
    "created",
    "routing_planned",
    "card_generated",
    "card_sent",
    "card_viewed",
    "section_expanded",
    "decision_received",
    "corrected_by_guardrail",
    "fell_back_to_safe_mode",
    "escalated",
    "sla_breached",
    "completed",
    "failed",
]
NextAction = Literal[
    "auto_clear",
    "next_approver",
    "complete_approved",
    "complete_rejected",
    "request_info_loop",
    "escalate",
]
