"""Response processing graph - deterministic routing only.

Interprets the approver's decision and emits the next action.
No LLM calls: this graph must be fast and predictable.
"""

from __future__ import annotations

from typing import Any

from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

class ResponseState(TypedDict, total=False):
    # Input fields
    request: Any             # ApprovalRequest (dict or instance)
    routing_plan: Any        # RoutingPlan (dict or instance)
    current_approver_index: int
    response: Any            # ApproverResponse (dict or instance)
    history: list

    # Working
    next_action: str
    learning_signals: dict
    outcome: Any             # DecisionOutcome instance

    # Output fields - set by finalize_response
    next_action_out: str
    next_approver: Any       # dict | None
    completion_summary: str | None
    escalation_reason: str | None
    info_request_message: str | None
    learning_signals_out: dict


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

def parse_input(state: ResponseState) -> dict:
    """Validate and coerce raw dicts to typed objects."""
    from datetime import datetime, timezone

    from agent.schemas import ApprovalRequest, ApproverResponse, RoutingPlan

    request = state.get("request")
    routing_plan = state.get("routing_plan")
    response = state.get("response")

    if isinstance(request, dict):
        request = ApprovalRequest.model_validate(request)
    if isinstance(routing_plan, dict):
        routing_plan = RoutingPlan.model_validate(routing_plan)
    if isinstance(response, dict):
        response = ApproverResponse.model_validate(response)
    elif response is None:
        response = ApproverResponse(
            approver_id="unknown",
            approver_email="unknown@example.com",
            decision="approve",
            responded_at=datetime.now(timezone.utc),
            channel="outlook",
        )

    return {
        "request": request,
        "routing_plan": routing_plan,
        "response": response,
        "current_approver_index": int(state.get("current_approver_index", 0)),
        "history": state.get("history", []),
    }


def interpret_decision(state: ResponseState) -> dict:
    """Deterministic decision routing - no AI needed here."""
    routing_plan = state.get("routing_plan")
    if getattr(routing_plan, "disposition", None) == "auto_clear":
        return {"next_action": "auto_clear"}

    decision = state["response"].decision
    idx = state.get("current_approver_index", 0)
    total = len(routing_plan.approvers) if routing_plan else 1

    if decision == "approve":
        next_action = "complete_approved" if idx >= total - 1 else "next_approver"
    elif decision == "reject":
        next_action = "complete_rejected"
    elif decision == "request_info":
        next_action = "request_info_loop"
    else:
        next_action = "escalate"

    return {"next_action": next_action}


def extract_signals(state: ResponseState) -> dict:
    response = state["response"]
    signals = {
        "engagement_signals": response.engagement_signals.model_dump(),
        "decision": str(response.decision),
    }
    return {"learning_signals": signals}


def finalize_response(state: ResponseState) -> dict:
    """Emit all output fields - UiPath runtime captures this last-node delta."""
    from agent.schemas import DecisionOutcome

    next_action = state.get("next_action", "escalate")
    routing_plan = state.get("routing_plan")
    idx = state.get("current_approver_index", 0)
    signals = state.get("learning_signals", {})

    kwargs: dict[str, Any] = {"next_action": next_action, "learning_signals": signals}

    if next_action == "auto_clear":
        kwargs["completion_summary"] = "Auto-cleared by policy; no human approval required."
    elif next_action == "next_approver" and routing_plan:
        next_approver = routing_plan.approvers[idx + 1]
        kwargs["next_approver"] = next_approver
        outcome_obj = DecisionOutcome(**kwargs)
        return {
            "next_action": next_action,      # BPMN backward-compat
            "next_action_out": next_action,
            "next_approver": outcome_obj.next_approver.model_dump(mode="json") if outcome_obj.next_approver else None,
            "completion_summary": outcome_obj.completion_summary,
            "escalation_reason": outcome_obj.escalation_reason,
            "info_request_message": outcome_obj.info_request_message,
            "learning_signals_out": outcome_obj.learning_signals,
        }
    elif next_action in ("complete_approved", "complete_rejected"):
        kwargs["completion_summary"] = "Approval flow completed."
    elif next_action == "request_info_loop":
        kwargs["info_request_message"] = "Additional information required."
    elif next_action == "escalate":
        kwargs["escalation_reason"] = "Approver requested escalation."

    outcome_obj = DecisionOutcome(**kwargs)
    return {
        "next_action": next_action,          # kept for BPMN backward-compat
        "next_action_out": next_action,
        "next_approver": outcome_obj.next_approver.model_dump(mode="json") if outcome_obj.next_approver else None,
        "completion_summary": outcome_obj.completion_summary,
        "escalation_reason": outcome_obj.escalation_reason,
        "info_request_message": outcome_obj.info_request_message,
        "learning_signals_out": outcome_obj.learning_signals,
    }


# ---------------------------------------------------------------------------
# Graph factory
# ---------------------------------------------------------------------------

def build_response_graph():
    graph = StateGraph(ResponseState)

    graph.add_node("parse_input", parse_input)
    graph.add_node("interpret_decision", interpret_decision)
    graph.add_node("extract_signals", extract_signals)
    graph.add_node("finalize_response", finalize_response)

    graph.set_entry_point("parse_input")
    graph.add_edge("parse_input", "interpret_decision")
    graph.add_edge("interpret_decision", "extract_signals")
    graph.add_edge("extract_signals", "finalize_response")
    graph.add_edge("finalize_response", END)

    return graph.compile()
