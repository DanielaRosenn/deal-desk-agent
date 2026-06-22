"""Self-contained HTML 'adaptive card' email body builder.

Produces an inline-styled HTML block that renders as a clean approval card in
Outlook (Outlook ignores external CSS, so all styling is inline). No external
template files are required, so it always works once the agent is packaged.
"""

import json
from html import escape


def _fmt_pct(value) -> str:
    try:
        return f"{float(value) * 100:.0f}%"
    except (TypeError, ValueError):
        return "N/A"


def _fmt_usd(value) -> str:
    try:
        return f"${float(value):,.0f}"
    except (TypeError, ValueError):
        return "N/A"


def _row(label: str, value: str, accent: str = "#0F172A") -> str:
    return (
        '<tr>'
        f'<td style="padding:6px 0;color:#64748B;font-size:13px;width:140px;">{escape(label)}</td>'
        f'<td style="padding:6px 0;color:{accent};font-size:15px;font-weight:600;">{escape(value)}</td>'
        '</tr>'
    )


# Map Adaptive Card action styles to button colors so the HTML link-buttons
# match the Adaptive Card actions.
_BTN_COLORS = {
    "positive": "#059669",
    "destructive": "#DC2626",
    "default": "#475569",
}


def _html_buttons(card: dict | None) -> str:
    """Render clickable Approve/Reject/Request-info buttons as styled <a> links.

    These render in every mail client (unlike Actionable Message cards, which
    require a registered originator). The link targets are the same callback URLs
    the Adaptive Card actions use, so a click hits the approval bridge directly.
    """
    actions = (card or {}).get("actions") or []
    links = []
    for action in actions:
        url = action.get("url") or ""
        title = action.get("title") or "Action"
        color = _BTN_COLORS.get(action.get("style", "default"), _BTN_COLORS["default"])
        if not url:
            continue
        links.append(
            f'<a href="{escape(url, quote=True)}" '
            f'style="display:inline-block;margin:0 8px 8px 0;padding:11px 22px;'
            f'background:{color};color:#FFFFFF;font-size:14px;font-weight:600;'
            f'text-decoration:none;border-radius:8px;">{escape(title)}</a>'
        )
    if not links:
        return ""
    return (
        '<div style="margin:18px 0 4px;">'
        + "".join(links)
        + "</div>"
    )


def build_html_card(request, approver, context: dict, spec=None, card: dict | None = None) -> str:
    customer = context.get("deal.customer_name", "Unknown Customer")
    discount = _fmt_pct(context.get("deal.discount_pct"))
    amount = _fmt_usd(context.get("deal.value_usd"))
    approval_id = getattr(request, "approval_id", "")
    requester = getattr(request, "requester_email", "")
    role = getattr(approver, "display_name", getattr(approver, "role", "Approver"))
    rationale = getattr(spec, "rationale", "") if spec else ""

    high_discount = False
    try:
        high_discount = float(context.get("deal.discount_pct") or 0) > 0.25
    except (TypeError, ValueError):
        high_discount = False
    badge_color = "#DC2626" if high_discount else "#059669"
    badge_text = "Elevated discount - senior approval" if high_discount else "Standard approval"

    rows = (
        _row("Customer", customer)
        + _row("Discount", discount, badge_color)
        + _row("Contract value", amount)
        + _row("Requester", requester)
        + _row("Approval ID", approval_id)
    )
    rationale_block = (
        f'<div style="margin:16px 0 4px;padding:12px 14px;background:#F1F5F9;border-radius:8px;'
        f'color:#334155;font-size:13px;line-height:1.5;"><b>Why you:</b> {escape(rationale)}</div>'
        if rationale
        else ""
    )
    buttons_block = _html_buttons(card)

    fallback = f"""\
<div style="font-family:Segoe UI,Arial,sans-serif;max-width:520px;margin:0 auto;border:1px solid #E2E8F0;border-radius:14px;overflow:hidden;">
  <div style="background:#1E3A8A;padding:18px 22px;">
    <div style="color:#BFDBFE;font-size:12px;letter-spacing:.5px;text-transform:uppercase;">Renewal Price Commitment</div>
    <div style="color:#FFFFFF;font-size:20px;font-weight:700;margin-top:2px;">Approval needed</div>
  </div>
  <div style="padding:20px 22px;">
    <div style="display:inline-block;padding:4px 10px;border-radius:999px;background:{badge_color};color:#FFFFFF;font-size:12px;font-weight:600;">{escape(badge_text)}</div>
    <p style="color:#475569;font-size:14px;margin:14px 0 6px;">Hello {escape(role)}, please review and action this renewal request.</p>
    <table style="width:100%;border-collapse:collapse;">{rows}</table>
    {rationale_block}
    {buttons_block}
    <p style="color:#94A3B8;font-size:12px;margin-top:16px;">Click <b>Approve / Reject / Request info</b> above to record your decision, or open your UiPath Action Center task. Routing is governed by automated discount and contract-value policy.</p>
  </div>
</div>"""

    if not card:
        return fallback

    # Outlook renders the buttons from this script block (the <div> above is the
    # fallback for clients that do not support Actionable Messages).
    script = (
        '<script type="application/adaptivecard+json">\n'
        + json.dumps(card, indent=2)
        + "\n</script>"
    )
    return fallback + "\n" + script
