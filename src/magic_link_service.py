from typing import Any, Dict

from infrai_client import InfraiClient, InfraiError


def start_donor_signin(email: str, captcha_token: str, client: InfraiClient) -> Dict[str, Any]:
    """Start a donor sign-in and return the session envelope for the email workflow."""
    client.verify_captcha(captcha_token)
    user = client.create_user(email, "Donor")
    user_id = user["data"]["user_id"]
    session = client.create_session(user_id)
    return {"email": email, "user_id": user_id, "session": session["data"]}


def public_result(email: str, captcha_token: str, client: InfraiClient) -> Dict[str, Any]:
    try:
        return {"ok": True, "data": start_donor_signin(email, captcha_token, client)}
    except InfraiError as exc:
        return {"ok": False, "error": {"code": exc.code, "detail": exc.detail}, "status": exc.status}
