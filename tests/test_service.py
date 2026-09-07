from magic_link_service import public_result


class FakeClient:
    def verify_captcha(self, token):
        return {"ok": True, "data": {"verified": True}}

    def create_user(self, email, name):
        return {"ok": True, "data": {"user_id": "u-42"}}

    def create_session(self, user_id):
        return {"ok": True, "data": {"session_id": "s-42"}}


def test_signin_returns_session_for_verified_donor():
    result = public_result("giver@example.org", "captcha", FakeClient())
    assert result["ok"] is True
    assert result["data"]["user_id"] == "u-42"
    assert result["data"]["session"]["session_id"] == "s-42"
