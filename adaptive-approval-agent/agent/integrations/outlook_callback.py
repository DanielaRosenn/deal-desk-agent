import hashlib
import hmac


def validate_outlook_jwt(token: str, **_: str) -> bool:
    return bool(token)


def verify_callback_token(secret: str, approval_id: str, approver_id: str, nonce: str, token: str) -> bool:
    expected = hmac.new(
        secret.encode("utf-8"),
        f"{approval_id}|{approver_id}|{nonce}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, token)
