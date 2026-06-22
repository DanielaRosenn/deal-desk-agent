from __future__ import annotations

import json
from typing import Any

from uipath.platform import UiPath
from uipath.platform.connections import ActivityMetadata, ActivityParameterLocationInfo

SEND_EMAIL_V2 = ActivityMetadata(
    object_path="/hubs/productivity/send-mail-v2",
    method_name="POST",
    content_type="multipart/form-data",
    parameter_location_info=ActivityParameterLocationInfo(
        query_params=["saveAsDraft"],
        multipart_params=["body"],
    ),
    json_body_section="body",
)


class OutlookClient:
    def __init__(self, settings):
        self.settings = settings
        self.connection_key = getattr(settings, "outlook_connection_key", "outlook-approval")

    def _fallback_html(self, card_json: dict[str, Any]) -> str:
        return (
            "<html><body>"
            '<script type="application/adaptivecard+json">'
            f"{json.dumps(card_json)}"
            "</script>"
            "</body></html>"
        )

    def send_actionable_message(
        self,
        to_email: str,
        subject: str,
        card_json: dict[str, Any],
        html_body: str | None = None,
    ) -> dict[str, Any]:
        sdk = UiPath()
        connection = sdk.connections.retrieve(self.connection_key)
        message_html = html_body or self._fallback_html(card_json)
        payload = {
            "saveAsDraft": False,
            "body": {
                "message": {
                    "toRecipients": to_email,
                    "subject": subject,
                    "importance": "normal",
                    "body": {
                        "contentType": "HTML",
                        "content": message_html,
                    },
                },
                "saveToSentItems": True,
            },
        }
        result = sdk.connections.invoke_activity(
            activity_metadata=SEND_EMAIL_V2,
            connection_id=connection.id,
            activity_input=payload,
        )
        return {
            "status": result.get("status", "sent"),
            "to": to_email,
            "subject": subject,
            "connection_id": connection.id,
            "payload": payload,
        }
