def build_safe_mode_card(approval_id: str, reason: str) -> dict:
    return {
        "type": "AdaptiveCard",
        "version": "1.5",
        "body": [
            {"type": "TextBlock", "weight": "Bolder", "text": "Approval request"},
            {"type": "TextBlock", "text": f"Approval ID: {approval_id}"},
            {"type": "TextBlock", "isSubtle": True, "text": f"Safe mode: {reason}"},
        ],
        "actions": [
            {"type": "Action.Submit", "title": "Approve", "data": {"decision": "approve"}},
            {"type": "Action.Submit", "title": "Reject", "data": {"decision": "reject"}},
        ],
    }
