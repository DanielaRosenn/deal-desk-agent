import json
import subprocess


def main() -> int:
    exe = r"C:\Users\DanielaRosenstein\AppData\Roaming\npm\uip.cmd"
    connection_id = "3b54e9a8-9153-4e04-abcb-2eb38bcf1651"

    card = {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.4",
        "body": [
            {"type": "TextBlock", "weight": "Bolder", "text": "DealDesk Approval Required"},
            {
                "type": "FactSet",
                "facts": [
                    {"title": "Customer", "value": "Beta Renewal"},
                    {"title": "Amount", "value": "$250,000"},
                    {"title": "Discount", "value": "30%"},
                ],
            },
            {"type": "TextBlock", "text": "Adaptive-card isolation delivery test"},
        ],
        "actions": [
            {"type": "Action.Submit", "title": "Approve", "data": {"decision": "approve"}},
            {"type": "Action.Submit", "title": "Reject", "data": {"decision": "reject"}},
        ],
    }

    html = (
        "<html><body><h3>DealDesk Adaptive Card Isolation</h3>"
        '<script type="application/adaptivecard+json">'
        + json.dumps(card, separators=(",", ":"))
        + "</script></body></html>"
    )

    body = {
        "message": {
            "toRecipients": "daniela.rosenstein@catonetworks.com",
            "subject": "DealDesk Adaptive Card Isolation",
            "body": {"contentType": "html", "content": html},
        },
        "saveToSentItems": True,
    }

    body_json = json.dumps(body, separators=(",", ":")).replace("<", "\\u003c").replace(">", "\\u003e")

    cmd = [
        exe,
        "is",
        "resources",
        "run",
        "create",
        "uipath-microsoft-outlook365",
        "send-mail",
        "--connection-id",
        connection_id,
        "--body",
        body_json,
        "--output",
        "json",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    print("EXIT", proc.returncode)
    if proc.stdout:
        print(proc.stdout)
    if proc.stderr:
        print(proc.stderr)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
