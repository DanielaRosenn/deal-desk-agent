import json
import os
import tempfile


def _as_float(value):
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _as_int(value):
    try:
        return int(float(value)) if value is not None else None
    except (TypeError, ValueError):
        return None


def _as_bool(value) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    s = str(value).strip().lower()
    if s in ("true", "1", "yes", "y", "on"):
        return True
    if s in ("false", "0", "no", "n", "off", ""):
        return False
    return bool(value)


def _norm_str(value, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def _norm_tier(value) -> str:
    s = _norm_str(value).lower()
    if s in ("strategic", "enterprise", "commercial", "smb"):
        return s
    return s or "unknown"


def _norm_churn(value) -> str:
    s = _norm_str(value).lower()
    if s in ("high", "medium", "low"):
        return s
    return s or "unknown"


def _norm_pct_field(value) -> float | None:
    """Discount-like field: 0-1 fraction or 0-100 percent."""
    v = _as_float(value)
    if v is None:
        return None
    if v > 1.0:
        return v / 100.0
    return v


class SalesforceClient:
    """Mock Salesforce reader.

    Deal context is sourced from ``raw_payload.Opportunity`` (or bucket fallback).
    Returns nested ``Opportunity`` plus flat ``deal.*`` keys for routing rules.
    """

    def __init__(self, settings):
        self.settings = settings

    def fetch_context(self, source_record_id: str, raw_payload: dict | None = None) -> dict:
        raw_payload = raw_payload or {}
        opportunity = dict(raw_payload.get("Opportunity") or {})
        if not opportunity and source_record_id:
            opportunity = self._load_opportunity_from_bucket(source_record_id)
        opportunity.setdefault("Id", source_record_id)

        account = opportunity.get("Account")
        if not isinstance(account, dict) or not account.get("Name"):
            opportunity["Account"] = {"Name": opportunity.get("Name", "Unknown Customer")}

        industry = ""
        if isinstance(account, dict):
            industry = _norm_str(account.get("Industry"))

        discount_pct = _as_float(opportunity.get("Discount__c"))
        if discount_pct is not None and discount_pct > 1.0:
            discount_pct = discount_pct / 100.0

        value_usd = _as_float(opportunity.get("Amount"))

        opp_type = _norm_str(opportunity.get("Type"), "Renewal")
        renewal_term = _as_int(opportunity.get("Renewal_Term__c"))
        churn_risk = _norm_churn(opportunity.get("Churn_Risk__c"))
        customer_tier = _norm_tier(opportunity.get("Customer_Tier__c"))
        multi_year = _as_bool(opportunity.get("Multi_Year_Discount__c"))
        competitor = _as_bool(opportunity.get("Competitor_Involved__c"))
        current_arr = _as_float(opportunity.get("Current_ARR__c"))
        health_score = _as_float(opportunity.get("Health_Score__c"))
        prev_disc = _norm_pct_field(opportunity.get("Previous_Discount__c"))

        return {
            "Opportunity": opportunity,
            "deal.customer_name": opportunity["Account"]["Name"],
            "deal.discount_pct": discount_pct,
            "deal.value_usd": value_usd,
            "deal.opportunity_type": opp_type,
            "deal.account_industry": industry,
            "deal.renewal_term_months": renewal_term,
            "deal.churn_risk": churn_risk,
            "deal.customer_tier": customer_tier,
            "deal.multi_year_commit": multi_year,
            "deal.competitor_involved": competitor,
            "deal.current_arr": current_arr,
            "deal.health_score": health_score,
            "deal.previous_discount_pct": prev_disc,
        }

    def _load_opportunity_from_bucket(self, source_record_id: str) -> dict:
        try:
            from uipath.platform import UiPath
        except Exception:
            return {}

        bucket_name = getattr(self.settings, "input_bucket_name", None) or "DealDeskInputs"
        folder_path = getattr(self.settings, "input_bucket_folder", None) or os.getenv(
            "DEAL_INPUT_FOLDER", "Shared/DealDeskApprovalGlobal"
        )
        fallback_blob = getattr(self.settings, "input_blob_path", None) or "deal-input.json"
        candidates = [f"{source_record_id}.json", fallback_blob]

        sdk = UiPath()
        for blob_path in candidates:
            try:
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
            except Exception:
                continue

            if not isinstance(data, dict):
                continue
            if isinstance(data.get("Opportunity"), dict):
                return dict(data["Opportunity"])
            nested = data.get("request")
            if isinstance(nested, dict) and isinstance(nested.get("raw_payload"), dict):
                opp = nested["raw_payload"].get("Opportunity")
                if isinstance(opp, dict):
                    return dict(opp)
        return {}
