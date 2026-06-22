"""Self-contained Adaptive Card + dynamic message drafting.

The agent drafts the approval message (subject + body) and the Adaptive Card
dynamically from the deal terms and the approver's tier - no external template
files, so it always works once packaged.
"""

_DISCOUNT_ESCALATION = 0.25
_VALUE_CFO_THRESHOLD = 500000


def _num(value):
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _fmt_pct(value) -> str:
    v = _num(value)
    return f"{v * 100:.0f}%" if v is not None else "N/A"


def _fmt_usd(value) -> str:
    v = _num(value)
    return f"${v:,.0f}" if v is not None else "N/A"


def _deal_facts(request, context: dict) -> dict:
    raw = getattr(request, "raw_payload", {}) or {}
    opp = raw.get("Opportunity", {}) if isinstance(raw, dict) else {}
    discount = context.get("deal.discount_pct", _num(opp.get("Discount__c")))
    amount = context.get("deal.value_usd", _num(opp.get("Amount")))
    customer = context.get("deal.customer_name") or opp.get("Name") or "the customer"
    term = opp.get("TermMonths") or opp.get("Term__c")
    return {
        "customer": customer,
        "discount": _num(discount),
        "amount": _num(amount),
        "term_months": term,
    }


def analyze_terms(request, context: dict) -> str:
    """Human-readable analysis of the renewal terms against policy."""
    f = _deal_facts(request, context)
    parts = [f"{f['customer']} renewal at {_fmt_pct(f['discount'])} discount on {_fmt_usd(f['amount'])}"]
    if f["term_months"]:
        parts.append(f"{f['term_months']}-month term")
    notes = []
    if f["discount"] is not None and f["discount"] > _DISCOUNT_ESCALATION:
        notes.append(
            f"discount exceeds the {_DISCOUNT_ESCALATION * 100:.0f}% policy ceiling \u2014 senior sign-off required"
        )
    else:
        notes.append("discount within standard manager authority")
    if f["amount"] is not None and f["amount"] > _VALUE_CFO_THRESHOLD:
        notes.append(f"value above {_fmt_usd(_VALUE_CFO_THRESHOLD)} \u2014 CFO review required")
    return ". ".join([", ".join(parts), "; ".join(notes)]) + "."


def draft_subject(request, approver, context: dict) -> str:
    f = _deal_facts(request, context)
    urgent = f["discount"] is not None and f["discount"] > _DISCOUNT_ESCALATION
    prefix = "[Action required] " if urgent else ""
    return f"{prefix}Renewal approval - {f['customer']} ({_fmt_pct(f['discount'])} off)"


def build_adaptive_card(
    request,
    approver,
    context: dict,
    rationale: str = "",
    originator: str = "",
    callback_url: str = "",
) -> dict:
    """An Outlook Actionable Message Adaptive Card (1.5) with live Approve / Reject /
    Request Info buttons.

    Outlook email renders buttons only for ``Action.Http`` (``Action.Submit`` is ignored),
    and only when the card carries a registered ``originator``. ``approvalId`` and
    ``decision`` travel in the callback query string, which is what the approval bridge
    reads to resume the case.
    """
    f = _deal_facts(request, context)
    approval_id = getattr(request, "approval_id", "")
    high = f["discount"] is not None and f["discount"] > _DISCOUNT_ESCALATION

    facts = [
        {"title": "Customer", "value": str(f["customer"])},
        {"title": "Discount", "value": _fmt_pct(f["discount"])},
        {"title": "Contract value", "value": _fmt_usd(f["amount"])},
        {"title": "Requester", "value": getattr(request, "requester_email", "")},
        {"title": "Approval ID", "value": approval_id},
    ]
    if f["term_months"]:
        facts.insert(3, {"title": "Term", "value": f"{f['term_months']} months"})

    body = [
        {
            "type": "TextBlock",
            "text": "Renewal Price Commitment - Approval needed",
            "weight": "Bolder",
            "size": "Large",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": ("Elevated discount - senior approval" if high else "Standard approval"),
            "color": ("Attention" if high else "Good"),
            "weight": "Bolder",
            "spacing": "Small",
            "wrap": True,
        },
        {"type": "FactSet", "facts": facts},
    ]
    if rationale or context:
        body.append(
            {
                "type": "TextBlock",
                "text": f"Why you: {rationale or analyze_terms(request, context)}",
                "wrap": True,
                "isSubtle": True,
                "spacing": "Medium",
            }
        )

    def _decision_url(decision: str) -> str:
        sep = "&" if "?" in callback_url else "?"
        return f"{callback_url}{sep}approvalId={approval_id}&decision={decision}"

    def _action(title: str, decision: str, style: str) -> dict:
        return {
            "type": "Action.Http",
            "title": title,
            "style": style,
            "method": "POST",
            "url": _decision_url(decision),
            "body": "",
        }

    return {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.5",
        "originator": originator,
        "hideOriginalBody": True,
        "body": body,
        "actions": [
            _action("Approve", "approve", "positive"),
            _action("Reject", "reject", "destructive"),
            _action("Request info", "request_info", "default"),
        ],
    }
