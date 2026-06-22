"""Decision/routing graph - real LangGraph StateGraph.

Nodes run deterministic policy first, then an AI node that drafts
bounded rationale text.  A finalize node always emits all output fields
so the UiPath LangGraph runtime captures a complete result.
"""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Mapping
from typing import Any

from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

_APPROVAL_REQUEST_FIELDS = frozenset({
    "approval_id", "approvalId", "process_type", "source_system",
    "source_record_id", "requester_email", "requester_id",
    "raw_payload", "created_at", "sla_minutes", "config_version_snapshot",
})


class PlanState(TypedDict, total=False):
    # Raw input as received from the BPMN / caller
    input_payload: dict

    # UiPath maps JobArguments directly to LangGraph state top-level keys.
    # Declaring these here prevents LangGraph from stripping them as "unknown".
    approval_id: str
    approvalId: str
    process_type: str
    source_system: str
    source_record_id: str
    requester_email: str
    requester_id: str
    raw_payload: dict
    created_at: str
    sla_minutes: int
    config_version_snapshot: str

    # All state fields are plain JSON-serialisable types (required by LangGraph SQLite checkpointer)
    request: dict         # serialised ApprovalRequest
    context: dict         # Salesforce context
    draft_plan: dict      # serialised RoutingPlan (from deterministic policy)
    corrections: list     # guardrail corrections
    final_plan: dict      # serialised RoutingPlan (after correction)
    ai_rec: dict          # AI-drafted text fields

    # Output fields - set by finalize_plan, returned by the runtime
    disposition: str
    approvers: list
    rationale: str
    recommended_decision: str
    recommendation_rationale: str
    risk_score: float
    request: dict                        # noqa: F811 - serialized for BPMN
    guardrail_violations_corrected: list


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

def _is_usable_request(candidate) -> bool:
    if not isinstance(candidate, Mapping):
        return False
    return bool(candidate.get("approval_id") or candidate.get("approvalId"))


def _load_from_bucket(payload: dict) -> dict:
    from uipath.platform import UiPath

    bucket_name = payload.get("bucket") or os.getenv("DEAL_INPUT_BUCKET", "DealDeskInputs")
    folder_path = payload.get("folder") or os.getenv("DEAL_INPUT_FOLDER", "Shared/DealDeskApprovalGlobal")
    blob_path = payload.get("blob_file_path") or os.getenv("DEAL_INPUT_BLOB", "deal-input.json")

    sdk = UiPath()
    with tempfile.TemporaryDirectory() as tmp:
        dest = os.path.join(tmp, os.path.basename(blob_path) or "deal-input.json")
        sdk.buckets.download(
            name=bucket_name,
            blob_file_path=blob_path,
            destination_path=dest,
            folder_path=folder_path,
        )
        with open(dest, encoding="utf-8") as fh:
            data = json.load(fh)

    return data.get("request", data) if isinstance(data, dict) else data


def resolve_request(state: PlanState) -> dict:
    payload = state.get("input_payload") or {}
    # UiPath maps JobArguments to LangGraph state top-level keys.
    # Approval request fields are declared in PlanState so LangGraph keeps them.
    if not _is_usable_request(payload):
        flat = {k: v for k, v in state.items() if k in _APPROVAL_REQUEST_FIELDS and v is not None}
        if _is_usable_request(flat):
            payload = flat
    # UiPath runtime may also wrap the JobArguments under a "JobArguments" key
    if "JobArguments" in payload and not _is_usable_request(payload):
        payload = payload["JobArguments"]
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError:
                payload = {}
    candidate = payload.get("request") if "request" in payload else payload
    if not _is_usable_request(candidate):
        state_request = state.get("request")
        if state_request is not None:
            candidate = state_request
    if hasattr(candidate, "model_dump"):
        candidate = candidate.model_dump(mode="json")
    elif not isinstance(candidate, Mapping) and hasattr(candidate, "to_dict"):
        candidate = candidate.to_dict()
    if isinstance(candidate, str):
        try:
            candidate = json.loads(candidate)
        except json.JSONDecodeError:
            candidate = {}
    if isinstance(candidate, Mapping) and "request" in candidate and not _is_usable_request(candidate):
        nested = candidate.get("request")
        if isinstance(nested, str):
            try:
                nested = json.loads(nested)
            except json.JSONDecodeError:
                nested = {}
        if isinstance(nested, Mapping):
            candidate = nested
    if not _is_usable_request(candidate):
        candidate = _load_from_bucket(payload)

    from agent.schemas import ApprovalRequest

    request = ApprovalRequest.model_validate(candidate)
    return {"request": request.model_dump(mode="json")}


def fetch_context(state: PlanState) -> dict:
    from agent.integrations.salesforce import SalesforceClient
    from agent.settings import AgentSettings

    req = state["request"]  # plain dict after resolve_request
    sf = SalesforceClient(AgentSettings())
    context = sf.fetch_context(req.get("source_record_id") or req.get("opportunity_id", ""), req.get("raw_payload", {}))
    return {"context": context}


def load_rules(state: PlanState) -> dict:
    from agent.paths import config_path
    from agent.rendering.computed_attributes import apply_computed_attributes
    from agent.rendering.field_registry import FieldRegistry

    process = (state.get("request") or {}).get("process_type", "rpc")
    try:
        registry = FieldRegistry.from_file(config_path(process, "field-registry.json"))
        context = apply_computed_attributes(registry, state["context"])
    except Exception:
        context = state["context"]
    # routing_rules and card_rules are NOT stored in state (not serializable).
    # validate_and_correct reloads them directly.
    return {"context": context}


def deterministic_policy(state: PlanState) -> dict:
    from agent.integrations.manager_resolver import build_manager_resolver
    from agent.policy.deal_policy import assess_disposition_and_recommendation, build_required_roles_and_reasons
    from agent.schemas import RoutingPlan
    from agent.settings import AgentSettings

    _DEAL_LABELS = {
        "rpc": "Renewal price commitment",
        "expense": "Expense approval",
        "access_request": "Access request",
        "vendor_onboarding": "Vendor onboarding",
    }

    context = state["context"]
    request = state.get("request") or {}  # plain dict
    discount_pct = context.get("deal.discount_pct")
    value_usd = context.get("deal.value_usd")
    customer = context.get("deal.customer_name", "the customer")
    process_type = request.get("process_type", "rpc")
    deal_label = _DEAL_LABELS.get(str(process_type), "Pricing change")

    resolver = build_manager_resolver(AgentSettings())
    raw_payload = request.get("raw_payload", {}) if isinstance(request, dict) else {}
    opportunity = raw_payload.get("Opportunity", {}) if isinstance(raw_payload, dict) else {}
    owner_email = str(
        opportunity.get("OwnerEmail")
        or (opportunity.get("Owner", {}) if isinstance(opportunity.get("Owner"), dict) else {}).get("Email")
        or raw_payload.get("owner_email")
        or ""
    ).strip()

    discount_display = f"{discount_pct * 100:.0f}%" if discount_pct is not None else "unknown"
    value_display = f"${value_usd:,.0f}" if value_usd is not None else "N/A"

    required_roles, reasons, discount_esc, auto_disc = build_required_roles_and_reasons(
        context, discount_pct, value_usd, discount_display, value_display
    )

    if hasattr(resolver, "resolve_management_chain"):
        approvers = resolver.resolve_management_chain(required_roles, owner_email=owner_email)
    else:
        approvers = [resolver.resolve_approver_for_role(role) for role in dict.fromkeys(required_roles)]

    disposition, risk_score, rec_decision, rec_rationale = assess_disposition_and_recommendation(
        context, discount_pct, value_usd, discount_display, value_display, discount_esc, auto_disc
    )

    chain_display = " -> ".join(a.role for a in approvers)
    rationale = (
        f"{deal_label} for {customer}: {value_display} at {discount_display} discount. "
        + "; ".join(reasons)
        + f". Disposition: {disposition}. Chain: {chain_display}."
    )

    draft = RoutingPlan(
        approvers=approvers,
        rationale=rationale[:1000],
        disposition=disposition,
        risk_score=risk_score,
        recommended_decision=rec_decision,
        recommendation_rationale=rec_rationale[:1000],
        guardrail_violations_corrected=[],
        soft_guidance_applied=[],
    )
    return {"draft_plan": draft.model_dump(mode="json")}


async def ai_recommendation(state: PlanState) -> dict:
    """Draft rationale and recommendation text via UiPath LLM Gateway."""
    draft = state.get("draft_plan")  # plain dict
    if not draft:
        return {"ai_rec": {}}

    context = state.get("context", {})
    customer = context.get("deal.customer_name", "the customer")
    discount_pct = context.get("deal.discount_pct")
    value_usd = context.get("deal.value_usd")
    chain = " -> ".join(a.get("role", "") for a in (draft.get("approvers") or []))

    discount_display = f"{discount_pct * 100:.0f}%" if discount_pct is not None else "N/A"
    value_display = f"${value_usd:,.0f}" if value_usd is not None else "N/A"
    tier = str(context.get("deal.customer_tier") or "unknown")
    industry = str(context.get("deal.account_industry") or "N/A")
    opp_type = str(context.get("deal.opportunity_type") or "Renewal")
    term_m = context.get("deal.renewal_term_months")
    term_display = f"{int(term_m)} months" if term_m is not None else "N/A"
    churn = str(context.get("deal.churn_risk") or "unknown")
    competitor = bool(context.get("deal.competitor_involved"))
    multi_year = bool(context.get("deal.multi_year_commit"))
    arr = context.get("deal.current_arr")
    arr_display = f"${float(arr):,.0f}" if arr is not None else "N/A"
    health = context.get("deal.health_score")
    health_display = f"{float(health):.0f}/100" if health is not None else "N/A"
    prev = context.get("deal.previous_discount_pct")
    prev_display = f"{float(prev) * 100:.0f}%" if prev is not None else "N/A"

    prompt = (
        f"You are a Deal Desk AI evaluating a {opp_type} opportunity for {customer} ({industry}).\n\n"
        f"Salesforce context:\n"
        f"  Customer tier: {tier}\n"
        f"  Contract value (Amount): {value_display}\n"
        f"  Current ARR: {arr_display}\n"
        f"  Requested discount: {discount_display} (previous renewal: {prev_display})\n"
        f"  Renewal term: {term_display}\n"
        f"  Churn risk: {churn}\n"
        f"  Account health score: {health_display}\n"
        f"  Multi-year commitment offered: {multi_year}\n"
        f"  Competitor involved: {competitor}\n\n"
        f"Disposition: {draft.get('disposition', '')}\n"
        f"Risk score: {float(draft.get('risk_score') or 0):.2f}\n"
        f"Approval chain: {chain}\n\n"
        f"Write a professional business rationale (max 800 chars) and recommendation rationale "
        f"(max 800 chars) explaining the routing decision. Reference churn risk, tier, health, "
        f"competitive dynamics, and deal economics where relevant.\n"
        f"Also state your recommended_decision as one of: approve, reject, escalate.\n\n"
        f"Respond in JSON: {{\"rationale\": \"...\", \"recommendation_rationale\": \"...\", "
        f"\"recommended_decision\": \"approve\"|\"reject\"|\"escalate\"}}"
    )

    try:
        from langchain_core.messages import HumanMessage
        from uipath_langchain.chat.models import UiPathAzureChatOpenAI

        model_name = os.getenv("UIPATH_LLM_MODEL", "gpt-4o-2024-11-20")
        llm = UiPathAzureChatOpenAI(model=model_name, temperature=0.1)

        class _Rec(BaseModel):
            rationale: str = Field(default="", max_length=1000)
            recommendation_rationale: str = Field(default="", max_length=1000)
            recommended_decision: str = Field(default="approve")

        structured = llm.with_structured_output(_Rec)
        result = await structured.ainvoke([HumanMessage(content=prompt)])
        rec = result.model_dump() if hasattr(result, "model_dump") else dict(result)

        # Clamp to valid values
        if rec.get("recommended_decision") not in {"approve", "reject", "escalate"}:
            rec["recommended_decision"] = str(draft.get("recommended_decision", "approve"))

        return {"ai_rec": rec}

    except Exception:
        # Deterministic fallback - never break the pipeline
        return {"ai_rec": {
            "rationale": draft.get("rationale", ""),
            "recommendation_rationale": draft.get("recommendation_rationale", ""),
            "recommended_decision": str(draft.get("recommended_decision", "approve")),
        }}


def validate_and_correct(state: PlanState) -> dict:
    draft_data = state.get("draft_plan") or {}
    context = state.get("context", {})
    approver_roles = [a.get("role", "") for a in (draft_data.get("approvers") or [])]

    corrections: list = []
    try:
        from agent.guardrails.routing_rules import RoutingRulesEngine
        from agent.paths import config_path
        process = (state.get("request") or {}).get("process_type", "rpc")
        routing_rules = RoutingRulesEngine.from_file(config_path(process, "routing-rules.yaml"))
        corrections = list(routing_rules.validate(context, approver_roles) or [])
    except Exception:
        pass  # no rules file - skip guardrails

    import copy

    final_data = copy.deepcopy(draft_data)
    if corrections:
        existing_roles = {a.get("role", "") for a in (final_data.get("approvers") or [])}
        try:
            from agent.integrations.manager_resolver import build_manager_resolver
            from agent.settings import AgentSettings

            resolver = build_manager_resolver(AgentSettings())
            for msg in corrections:
                if "Missing required role:" not in msg:
                    continue
                role = msg.split(":", 1)[-1].strip()
                if not role or role in existing_roles:
                    continue
                try:
                    vp = resolver.resolve_approver_for_role(role)
                    final_data.setdefault("approvers", []).append(
                        vp.model_dump(mode="json") if hasattr(vp, "model_dump") else vars(vp)
                    )
                    existing_roles.add(role)
                except Exception:
                    pass
        except Exception:
            pass
        final_data["guardrail_violations_corrected"] = corrections

    return {"corrections": corrections, "final_plan": final_data}


def finalize_plan(state: PlanState) -> dict:
    """Emit all output fields - UiPath runtime captures this last-node delta."""
    plan = state.get("final_plan") or {}  # plain dict
    ai = state.get("ai_rec") or {}
    request = state.get("request") or {}  # plain dict

    def _str(v):
        return str(v) if v is not None else ""

    approvers = plan.get("approvers") or []
    # Normalise each approver to a plain dict (may already be dicts)
    norm_approvers = [
        (a.model_dump(mode="json") if hasattr(a, "model_dump") else (dict(a) if not isinstance(a, dict) else a))
        for a in approvers
    ]

    return {
        "disposition": _str(plan.get("disposition", "needs_approval")),
        "approvers": norm_approvers,
        "rationale": (ai.get("rationale") or plan.get("rationale", ""))[:1000],
        "recommended_decision": ai.get("recommended_decision") or _str(plan.get("recommended_decision", "approve")),
        "recommendation_rationale": (
            ai.get("recommendation_rationale") or plan.get("recommendation_rationale", "")
        )[:1000],
        "risk_score": float(plan.get("risk_score") or 0.0),
        "request": request,  # already a dict
        "guardrail_violations_corrected": list(plan.get("guardrail_violations_corrected") or []),
    }


# ---------------------------------------------------------------------------
# Graph factory
# ---------------------------------------------------------------------------

def build_plan_graph():
    graph = StateGraph(PlanState)

    graph.add_node("resolve_request", resolve_request)
    graph.add_node("fetch_context", fetch_context)
    graph.add_node("load_rules", load_rules)
    graph.add_node("deterministic_policy", deterministic_policy)
    graph.add_node("ai_recommendation", ai_recommendation)
    graph.add_node("validate_and_correct", validate_and_correct)
    graph.add_node("finalize_plan", finalize_plan)

    graph.set_entry_point("resolve_request")
    graph.add_edge("resolve_request", "fetch_context")
    graph.add_edge("fetch_context", "load_rules")
    graph.add_edge("load_rules", "deterministic_policy")
    graph.add_edge("deterministic_policy", "ai_recommendation")
    graph.add_edge("ai_recommendation", "validate_and_correct")
    graph.add_edge("validate_and_correct", "finalize_plan")
    graph.add_edge("finalize_plan", END)

    return graph.compile()
