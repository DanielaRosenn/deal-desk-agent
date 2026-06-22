"""Shared deterministic Deal Desk routing (used by plan_graph and plan_nodes)."""

from __future__ import annotations

# Policy thresholds (Renewal Price Commitment)
_VALUE_CFO_THRESHOLD = 500_000
_VALUE_CRO_THRESHOLD = 750_000
_AUTO_CLEAR_VALUE = 50_000
_DEFAULT_DISCOUNT_ESCALATION = 0.25
_SMB_DISCOUNT_ESCALATION = 0.20
_DEFAULT_AUTO_CLEAR_DISCOUNT = 0.05
_STRATEGIC_AUTO_CLEAR_DISCOUNT = 0.10


def _tier_norm(context: dict) -> str:
    return str(context.get("deal.customer_tier") or "").strip().lower() or "unknown"


def _churn_norm(context: dict) -> str:
    return str(context.get("deal.churn_risk") or "").strip().lower() or "unknown"


def discount_escalation_threshold(context: dict) -> float:
    return _SMB_DISCOUNT_ESCALATION if _tier_norm(context) == "smb" else _DEFAULT_DISCOUNT_ESCALATION


def auto_clear_discount_threshold(context: dict) -> float:
    if _tier_norm(context) in ("strategic", "enterprise"):
        return _STRATEGIC_AUTO_CLEAR_DISCOUNT
    return _DEFAULT_AUTO_CLEAR_DISCOUNT


def build_required_roles_and_reasons(
    context: dict,
    discount_pct: float | None,
    value_usd: float | None,
    discount_display: str,
    value_display: str,
) -> tuple[list[str], list[str], float, float]:
    """Returns (required_roles, reasons, discount_esc, auto_clear_disc)."""
    discount_esc = discount_escalation_threshold(context)
    auto_disc = auto_clear_discount_threshold(context)
    required_roles: list[str] = ["manager"]
    reasons: list[str] = []

    if context.get("deal.competitor_involved"):
        required_roles.append("director")
        reasons.append("competitor involvement requires director sign-off")

    if discount_pct is not None and discount_pct > discount_esc:
        for r in ("director", "vp_sales"):
            if r not in required_roles:
                required_roles.append(r)
        reasons.append(
            f"discount {discount_display} exceeds {_tier_norm(context).upper()} tier "
            f"threshold ({discount_esc * 100:.0f}%), escalating to Director and VP Sales"
        )
    else:
        reasons.append(
            f"discount {discount_display} is within {_tier_norm(context)} tier authority "
            f"(threshold {discount_esc * 100:.0f}%)"
        )

    if value_usd is not None and value_usd > _VALUE_CFO_THRESHOLD:
        if "cfo" not in required_roles:
            required_roles.append("cfo")
        reasons.append(f"contract value {value_display} exceeds ${_VALUE_CFO_THRESHOLD:,.0f}, adding CFO")
    if value_usd is not None and value_usd > _VALUE_CRO_THRESHOLD:
        if "cro" not in required_roles:
            required_roles.append("cro")
        reasons.append(f"contract value {value_display} exceeds ${_VALUE_CRO_THRESHOLD:,.0f}, adding CRO")

    hs = context.get("deal.health_score")
    if hs is not None and float(hs) < 50:
        reasons.append(f"account health score {float(hs):.0f}/100 is below 50 (at-risk renewal)")

    if context.get("deal.multi_year_commit"):
        reasons.append("multi-year commitment reduces renewal risk")

    churn = _churn_norm(context)
    tier = _tier_norm(context)
    if churn == "high" and tier in ("strategic", "enterprise"):
        reasons.append("high churn risk on strategic/enterprise account: retention priority in routing")

    return required_roles, reasons, discount_esc, auto_disc


def assess_disposition_and_recommendation(
    context: dict,
    discount_pct: float | None,
    value_usd: float | None,
    discount_display: str,
    value_display: str,
    discount_esc: float,
    auto_clear_disc: float,
) -> tuple[str, float, str, str]:
    """Returns (disposition, risk_score, recommended_decision, recommendation_rationale)."""
    if discount_pct is None or value_usd is None:
        return (
            "exception",
            1.0,
            "escalate",
            "Opportunity payload is missing discount or contract value; cannot score the deal. "
            "Routing to a human for manual review.",
        )

    risk_score = min(
        1.0,
        0.5 * (discount_pct / discount_esc) + 0.5 * (value_usd / _VALUE_CFO_THRESHOLD),
    )

    churn = _churn_norm(context)
    tier = _tier_norm(context)
    if churn == "high" and tier in ("strategic", "enterprise"):
        risk_score = max(0.0, risk_score - 0.15)
    if context.get("deal.multi_year_commit"):
        risk_score = max(0.0, risk_score - 0.10)

    hs = context.get("deal.health_score")
    hs_f = float(hs) if hs is not None else None

    if discount_pct <= auto_clear_disc and value_usd <= _AUTO_CLEAR_VALUE:
        return (
            "auto_clear",
            risk_score,
            "approve",
            f"Discount {discount_display} and value {value_display} are within standing pricing policy "
            f"(tier auto-clear <= {auto_clear_disc * 100:.0f}% / <= $50k); no human approval required.",
        )

    # SMB + aggressive discount + weak health + no multi-year -> recommend reject
    if (
        tier == "smb"
        and discount_pct >= 0.40
        and not context.get("deal.multi_year_commit")
        and hs_f is not None
        and hs_f < 50
    ):
        return (
            "needs_approval",
            risk_score,
            "reject",
            f"SMB account with {discount_display} discount, health score below 50, and no multi-year "
            "commitment; margin risk is high. Recommend reject or re-scope to standard commercial terms.",
        )

    return (
        "needs_approval",
        risk_score,
        "approve",
        f"Discount {discount_display} on {value_display} is consistent with comparable approved deals; "
        "recommend approve with standard terms, pending sign-off from the routed approvers.",
    )

