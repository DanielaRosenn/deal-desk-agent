"""Adaptive-card render graph - real LangGraph StateGraph.

AI node drafts card headline/summary text; deterministic nodes
handle field selection, card rules enforcement, and final rendering.
"""

from __future__ import annotations

import os
from typing import Any

from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

class RenderState(TypedDict, total=False):
    # All state fields are plain JSON-serialisable (required by LangGraph SQLite checkpointer)
    request: dict         # serialised ApprovalRequest
    approver: dict        # serialised Approver
    history: list

    # Working state
    context: dict
    approver_profile: dict
    ai_card_draft: dict   # AI-drafted text (headline, summary, urgency, rationale)
    draft_spec: dict      # serialised CardSpec
    enforced_spec: dict   # serialised CardSpec after rules enforcement
    corrections: list
    used_safe_mode: bool
    rendered_card: dict   # intermediate: set by render_card, read by finalize_render

    # Output fields - set by finalize_render
    subject: str
    html: str
    card: dict
    approver_email: str


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

def parse_input(state: RenderState) -> dict:
    """Validate inputs and normalise to plain dicts for state storage."""
    from agent.schemas import ApprovalRequest, Approver

    req = state.get("request") or {}
    apv = state.get("approver") or {}

    # Validate via pydantic, then immediately serialise to dict
    if not isinstance(req, dict):
        req = ApprovalRequest.model_validate(req).model_dump(mode="json")
    else:
        try:
            req = ApprovalRequest.model_validate(req).model_dump(mode="json")
        except Exception:
            pass

    if not isinstance(apv, dict):
        apv = Approver.model_validate(apv).model_dump(mode="json")
    else:
        try:
            apv = Approver.model_validate(apv).model_dump(mode="json")
        except Exception:
            pass

    return {"request": req, "approver": apv, "history": list(state.get("history") or [])}


def fetch_context(state: RenderState) -> dict:
    from agent.integrations.salesforce import SalesforceClient
    from agent.settings import AgentSettings

    req = state.get("request") or {}  # plain dict
    sf = SalesforceClient(AgentSettings())
    context = sf.fetch_context(
        req.get("source_record_id") or req.get("opportunity_id", ""),
        req.get("raw_payload", {}),
    )
    return {"context": context}


def load_rules(state: RenderState) -> dict:
    from agent.paths import config_path
    from agent.rendering.computed_attributes import apply_computed_attributes
    from agent.rendering.field_registry import FieldRegistry

    process = (state.get("request") or {}).get("process_type", "rpc")
    try:
        registry = FieldRegistry.from_file(config_path(process, "field-registry.json"))
        context = apply_computed_attributes(registry, state.get("context", {}))
    except Exception:
        context = state.get("context", {})
    # registry, routing_rules, card_rules are NOT stored in state (not serialisable).
    # Downstream nodes reload them directly.
    return {"context": context}


async def ai_card_spec(state: RenderState) -> dict:
    """Draft card headline, summary, and urgency via UiPath LLM Gateway."""
    context = state.get("context", {})
    request = state.get("request") or {}  # plain dict
    approver = state.get("approver") or {}  # plain dict
    customer = context.get("deal.customer_name", "the customer")
    discount_pct = context.get("deal.discount_pct")
    value_usd = context.get("deal.value_usd")

    discount_display = f"{discount_pct * 100:.0f}%" if discount_pct is not None else "N/A"
    value_display = f"${value_usd:,.0f}" if value_usd is not None else "N/A"

    prompt = (
        f"You are drafting a deal desk approval card for a {approver.get('persona', 'manager')} reviewer.\n\n"
        f"Customer: {customer}\n"
        f"Discount: {discount_display}\n"
        f"Contract Value: {value_display}\n"
        f"Approval ID: {request.get('approval_id', '')}\n\n"
        f"Write a concise, professional card for the approver. Respond in JSON:\n"
        f'{{"headline": "...(max 80 chars)", '
        f'"summary": "...(max 300 chars)", '
        f'"urgency": "low"|"standard"|"high"|"critical", '
        f'"rationale": "...(max 500 chars)"}}'
    )

    try:
        from langchain_core.messages import HumanMessage
        from uipath_langchain.chat.models import UiPathAzureChatOpenAI

        model_name = os.getenv("UIPATH_LLM_MODEL", "gpt-4o-2024-11-20")
        llm = UiPathAzureChatOpenAI(model=model_name, temperature=0.2)

        class _CardDraft(BaseModel):
            headline: str = Field(default="", max_length=80)
            summary: str = Field(default="", max_length=300)
            urgency: str = Field(default="standard")
            rationale: str = Field(default="", max_length=500)

        structured = llm.with_structured_output(_CardDraft)
        result = await structured.ainvoke([HumanMessage(content=prompt)])
        draft = result.model_dump() if hasattr(result, "model_dump") else dict(result)

        # Clamp urgency to allowed values
        if draft.get("urgency") not in {"low", "standard", "high", "critical"}:
            draft["urgency"] = "standard"

        return {"ai_card_draft": draft}

    except Exception:
        return {"ai_card_draft": {}}


def build_card_spec(state: RenderState) -> dict:
    """Assemble the CardSpec, merging AI text with deterministic field selection."""
    from agent.paths import config_path
    from agent.rendering.field_registry import FieldRegistry
    from agent.schemas import CardSpec

    request = state.get("request") or {}  # plain dict
    approver = state.get("approver") or {}  # plain dict
    ai = state.get("ai_card_draft") or {}
    persona = approver.get("persona", "manager")

    primary_ids: list = ["deal.customer_name"]
    expandable_ids: list = []
    try:
        process = request.get("process_type", "rpc")
        registry = FieldRegistry.from_file(config_path(process, "field-registry.json"))
        primary_ids = registry.ids_for_persona(persona, "primary")[:4] or ["deal.customer_name"]
        expandable_ids = registry.ids_for_persona(persona, "expandable")[:4]
    except Exception:
        pass

    approval_id = request.get("approval_id", "")
    headline = ai.get("headline") or f"Approval required: {approval_id}"
    summary = ai.get("summary") or "Review the request details and choose an action."
    _urgency_map = {"low": "standard", "high": "expedited"}
    urgency = _urgency_map.get(ai.get("urgency", ""), ai.get("urgency") or "standard")
    if urgency not in {"standard", "expedited", "critical"}:
        urgency = "standard"
    rationale = ai.get("rationale") or "Standard approval routing"

    spec = CardSpec(
        approval_id=approval_id,
        approver_persona=persona,
        urgency=urgency,
        headline=headline[:80],
        summary=summary[:300],
        primary_field_ids=primary_ids,
        expandable_field_ids=expandable_ids,
        decision_options=["approve", "reject", "request_info"],
        rationale=rationale[:500],
        predicted_decision="approve",
    )
    return {"draft_spec": spec.model_dump(mode="json")}


def enforce_card_rules(state: RenderState) -> dict:
    draft_spec_data = state.get("draft_spec") or {}
    enforced_data = dict(draft_spec_data)
    corrections: list = []
    try:
        from agent.guardrails.card_rules import CardRulesEngine
        from agent.paths import config_path
        from agent.schemas import CardSpec
        process = (state.get("request") or {}).get("process_type", "rpc")
        card_rules = CardRulesEngine.from_file(config_path(process, "card-rules.yaml"))
        spec = CardSpec.model_validate(draft_spec_data)
        enforced, corrections = card_rules.enforce(spec)
        enforced_data = enforced.model_dump(mode="json") if hasattr(enforced, "model_dump") else draft_spec_data
        corrections = list(corrections or [])
    except Exception:
        pass
    return {"enforced_spec": enforced_data, "corrections": corrections}


def render_card(state: RenderState) -> dict:
    from agent.rendering.adaptive_card import analyze_terms, build_adaptive_card, draft_subject
    from agent.rendering.html_card import build_html_card
    from agent.schemas import ApprovalRequest, Approver, CardSpec
    from agent.settings import AgentSettings

    settings = AgentSettings()
    # Reconstruct pydantic models inside the node (not stored in state)
    request_data = state.get("request") or {}
    approver_data = state.get("approver") or {}
    context = state.get("context") or {}

    try:
        request = ApprovalRequest.model_validate(request_data)
    except Exception:
        from types import SimpleNamespace
        request = SimpleNamespace(**request_data)

    try:
        approver = Approver.model_validate(approver_data)
    except Exception:
        from types import SimpleNamespace
        approver = SimpleNamespace(**approver_data)

    spec_data = state.get("enforced_spec") or state.get("draft_spec") or {}
    try:
        spec = CardSpec.model_validate(spec_data)
    except Exception:
        spec = None

    rationale = analyze_terms(request, context)
    if spec is not None:
        spec.rationale = rationale[:1000]

    card = build_adaptive_card(
        request,
        approver,
        context,
        rationale,
        originator=settings.outlook_originator_guid,
        callback_url=settings.callback_url,
    )
    rendered = {
        "subject": draft_subject(request, approver, context),
        "html": build_html_card(request, approver, context, spec, card=card),
        "card": card,
    }
    return {"rendered_card": rendered, "used_safe_mode": False}


def finalize_render(state: RenderState) -> dict:
    """Emit all output fields - UiPath runtime captures this last-node delta."""
    rendered = state.get("rendered_card", {})
    card_value = rendered.get("card", {})
    approver = state.get("approver") or {}  # plain dict
    approver_email = str(approver.get("email", "") or "")
    return {
        "subject": rendered.get("subject", ""),
        "html": rendered.get("html", ""),
        "card": card_value if isinstance(card_value, dict) else {},
        "approver_email": approver_email,   # for BPMN Var_CurrentApproverEmail
    }


# ---------------------------------------------------------------------------
# Graph factory
# ---------------------------------------------------------------------------

def build_render_graph():
    graph = StateGraph(RenderState)

    graph.add_node("parse_input", parse_input)
    graph.add_node("fetch_context", fetch_context)
    graph.add_node("load_rules", load_rules)
    graph.add_node("ai_card_spec", ai_card_spec)
    graph.add_node("build_card_spec", build_card_spec)
    graph.add_node("enforce_card_rules", enforce_card_rules)
    graph.add_node("render_card", render_card)
    graph.add_node("finalize_render", finalize_render)

    graph.set_entry_point("parse_input")
    graph.add_edge("parse_input", "fetch_context")
    graph.add_edge("fetch_context", "load_rules")
    graph.add_edge("load_rules", "ai_card_spec")
    graph.add_edge("ai_card_spec", "build_card_spec")
    graph.add_edge("build_card_spec", "enforce_card_rules")
    graph.add_edge("enforce_card_rules", "render_card")
    graph.add_edge("render_card", "finalize_render")
    graph.add_edge("finalize_render", END)

    return graph.compile()
