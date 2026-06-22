from agent.policy.deal_policy import (
    assess_disposition_and_recommendation,
    build_required_roles_and_reasons,
)
from agent.schemas import RoutingPlan

# Human-readable labels per process so the rationale is not renewal-specific.
_DEAL_LABELS = {
    "rpc": "Renewal price commitment",
    "expense": "Expense approval",
    "access_request": "Access request",
    "vendor_onboarding": "Vendor onboarding",
}


def plan_routing_llm_node(state, agent):
    context = state.get("context", {})
    discount_pct = context.get("deal.discount_pct")
    value_usd = context.get("deal.value_usd")
    customer = context.get("deal.customer_name", "the customer")
    process_type = getattr(state.get("request"), "process_type", "rpc")
    deal_label = _DEAL_LABELS.get(process_type, "Pricing change")

    resolver = agent.manager_resolver
    request = state.get("request")
    raw_payload = getattr(request, "raw_payload", {}) if request is not None else {}
    opportunity = raw_payload.get("Opportunity", {}) if isinstance(raw_payload, dict) else {}
    owner = opportunity.get("Owner", {})
    owner_email = str(
        opportunity.get("OwnerEmail")
        or (owner.get("Email") if isinstance(owner, dict) else "")
        or raw_payload.get("owner_email")
        or ""
    ).strip()

    discount_display = f"{discount_pct * 100:.0f}%" if discount_pct is not None else "unknown"
    value_display = f"${value_usd:,.0f}" if value_usd is not None else "unknown"

    required_roles, reasons, discount_esc, auto_disc = build_required_roles_and_reasons(
        context, discount_pct, value_usd, discount_display, value_display
    )

    if hasattr(resolver, "resolve_management_chain"):
        approvers = resolver.resolve_management_chain(required_roles, owner_email=owner_email)
    else:
        approvers = [resolver.resolve_approver_for_role(r) for r in dict.fromkeys(required_roles)]

    disposition, risk_score, recommended_decision, recommendation_rationale = (
        assess_disposition_and_recommendation(
            context, discount_pct, value_usd, discount_display, value_display, discount_esc, auto_disc
        )
    )

    chain_display = " \u2192 ".join(a.role for a in approvers)
    rationale = (
        f"{deal_label} for {customer}: {value_display} at {discount_display} discount. "
        + "; ".join(reasons)
        + f". Disposition: {disposition}. Approval chain: {chain_display}."
    )

    state["draft_plan"] = RoutingPlan(
        approvers=approvers,
        rationale=rationale[:1000],
        disposition=disposition,
        risk_score=risk_score,
        recommended_decision=recommended_decision,
        recommendation_rationale=recommendation_rationale[:1000],
        guardrail_violations_corrected=[],
        soft_guidance_applied=[],
    )
    return state


def validate_plan_node(state, _agent):
    roles = [a.role for a in state["draft_plan"].approvers]
    state["corrections"] = state["routing_rules"].validate(state["context"], roles)
    state["final_plan"] = state["draft_plan"]
    return state


def force_correct_plan_node(state, agent):
    if not state["corrections"]:
        return state
    existing_roles = {a.role for a in state["final_plan"].approvers}
    for msg in state["corrections"]:
        if "Missing required role:" not in msg:
            continue
        role = msg.split(":", 1)[-1].strip()
        if not role or role in existing_roles:
            continue
        try:
            state["final_plan"].approvers.append(agent.manager_resolver.resolve_approver_for_role(role))
            existing_roles.add(role)
        except Exception:
            pass
    state["final_plan"].guardrail_violations_corrected = list(state["corrections"])
    return state
