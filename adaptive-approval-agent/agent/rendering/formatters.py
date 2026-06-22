from datetime import datetime, timezone
from typing import Any


def fmt_string(v: Any) -> str:
    return str(v) if v is not None else "N/A"


def fmt_string_truncate_300(v: Any) -> str:
    s = str(v) if v is not None else ""
    return s if len(s) <= 300 else s[:297] + "..."


def fmt_percentage(v: Any) -> str:
    if v is None:
        return "N/A"
    n = float(v)
    if abs(n) <= 1.0:
        n = n * 100
    return f"{n:.1f}%"


def fmt_currency_usd(v: Any) -> str:
    if v is None:
        return "N/A"
    n = float(v)
    return f"${n:,.0f}"


def fmt_years(v: Any) -> str:
    if v is None:
        return "N/A"
    n = float(v)
    if n < 1:
        return f"{int(n * 12)} mo"
    return "1 year" if n < 2 else f"{n:.1f} years"


def fmt_date_relative(v: Any) -> str:
    if v is None:
        return "N/A"
    dt = datetime.fromisoformat(v.replace("Z", "+00:00")) if isinstance(v, str) else v
    now = datetime.now(timezone.utc) if getattr(dt, "tzinfo", None) else datetime.utcnow()
    seconds = (now - dt).total_seconds()
    if abs(seconds) < 3600:
        return f"{int(abs(seconds) // 60)}m ago" if seconds >= 0 else f"in {int(abs(seconds) // 60)}m"
    return f"{int(abs(seconds) // 3600)}h ago" if seconds >= 0 else f"in {int(abs(seconds) // 3600)}h"


def fmt_date_iso(v: Any) -> str:
    return str(v)[:10] if v is not None else "N/A"


def fmt_renewal_list(v: Any) -> str:
    return ", ".join(str(x) for x in (v or [])) if isinstance(v, list) else fmt_string(v)


def fmt_category_list(v: Any) -> str:
    return ", ".join(str(x) for x in (v or [])) if isinstance(v, list) else fmt_string(v)


def fmt_violation_list(v: Any) -> str:
    return ", ".join(str(x) for x in (v or [])) if isinstance(v, list) else fmt_string(v)


def fmt_history_summary(v: Any) -> str:
    return fmt_string(v)


def fmt_boolean_yes_no(v: Any) -> str:
    return "Yes" if bool(v) else "No"


FORMATTERS = {
    "string": fmt_string,
    "string_truncate_300": fmt_string_truncate_300,
    "percentage": fmt_percentage,
    "currency_usd": fmt_currency_usd,
    "years": fmt_years,
    "date_relative": fmt_date_relative,
    "date_iso": fmt_date_iso,
    "renewal_list": fmt_renewal_list,
    "category_list": fmt_category_list,
    "violation_list": fmt_violation_list,
    "history_summary": fmt_history_summary,
    "boolean_yes_no": fmt_boolean_yes_no,
}
