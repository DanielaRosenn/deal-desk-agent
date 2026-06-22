from agent.schemas import DecisionOutcome


def interpret_decision_llm_node(state, _agent):
    routing_plan = state.get("routing_plan")
    if getattr(routing_plan, "disposition", None) == "auto_clear":
        state["next_action"] = "auto_clear"
        return state
    decision = state["response"].decision
    if decision == "approve":
        next_action = (
            "complete_approved"
            if state["current_approver_index"] >= len(state["routing_plan"].approvers) - 1
            else "next_approver"
        )
    elif decision == "reject":
        next_action = "complete_rejected"
    elif decision == "request_info":
        next_action = "request_info_loop"
    else:
        next_action = "escalate"
    state["next_action"] = next_action
    return state


def extract_learning_signals_node(state, _agent):
    state["learning_signals"] = {
        "engagement_signals": state["response"].engagement_signals.model_dump(),
        "decision": state["response"].decision,
    }
    return state


def decide_next_action_node(state, _agent):
    kwargs = {"next_action": state["next_action"], "learning_signals": state["learning_signals"]}
    if state["next_action"] == "auto_clear":
        kwargs["completion_summary"] = "Auto-cleared by policy; no human approval required"
    if state["next_action"] == "next_approver":
        kwargs["next_approver"] = state["routing_plan"].approvers[state["current_approver_index"] + 1]
    if state["next_action"] in ("complete_approved", "complete_rejected"):
        kwargs["completion_summary"] = "Approval flow completed"
    if state["next_action"] == "request_info_loop":
        kwargs["info_request_message"] = "Additional information required"
    if state["next_action"] == "escalate":
        kwargs["escalation_reason"] = "Approver requested escalation"
    state["outcome"] = DecisionOutcome(**kwargs)
    return state
