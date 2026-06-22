from agent.rendering.adaptive_card import analyze_terms, build_adaptive_card, draft_subject
from agent.rendering.html_card import build_html_card
from agent.schemas import CardSpec


def load_approver_profile_node(state, _agent):
    state["approver_profile"] = None
    return state


def generate_card_spec_llm_node(state, _agent):
    state["draft_spec"] = CardSpec(
        approval_id=state["request"].approval_id,
        approver_persona=state["approver"].persona,
        urgency="standard",
        headline=f"Approval request {state['request'].approval_id}",
        summary="Review the request details and choose an action.",
        primary_field_ids=state["registry"].ids_for_persona(state["approver"].persona, "primary")[:4]
        or ["deal.customer_name"],
        expandable_field_ids=state["registry"].ids_for_persona(state["approver"].persona, "expandable")[:4],
        decision_options=["approve", "reject", "request_info"],
        rationale="Deterministic fallback card spec",
        predicted_decision="approve",
    )
    return state


def enforce_card_rules_node(state, _agent):
    state["enforced_spec"], state["corrections"] = state["card_rules"].enforce(state["draft_spec"])
    return state


def render_node(state, agent):
    request = state["request"]
    approver = state["approver"]
    context = state["context"]
    rationale = analyze_terms(request, context)
    spec = state.get("enforced_spec")
    if spec is not None:
        spec.rationale = rationale[:1000]
    settings = getattr(agent, "settings", None)
    originator = getattr(settings, "outlook_originator_guid", "")
    callback_url = getattr(settings, "callback_url", "")
    card = build_adaptive_card(
        request, approver, context, rationale, originator=originator, callback_url=callback_url
    )
    state["rendered_card"] = {
        "subject": draft_subject(request, approver, context),
        "html": build_html_card(request, approver, context, spec, card=card),
        "card": card,
    }
    state["used_safe_mode"] = False
    return state


def validate_rendered_card_node(state, _agent):
    return state
