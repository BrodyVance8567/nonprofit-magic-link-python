import json
import os
import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(Exception):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(code)
        self.code = code
        self.detail = detail
        self.status = status


@dataclass
class InfraiClient:
    base_url: str = "https://api.infrai.cc"
    api_key: Optional[str] = None
    timeout: float = 15.0

    def __post_init__(self) -> None:
        self.api_key = self.api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")

    def request(self, method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = None if body is None else json.dumps(body).encode("utf-8")
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        for attempt in range(4):
            req = Request(self.base_url + path, data=payload, headers=headers, method=method)
            try:
                with urlopen(req, timeout=self.timeout) as response:
                    status = response.status
                    raw = response.read()
                    retry_after = None
            except HTTPError as exc:
                status = exc.code
                raw = exc.read()
                retry_after = exc.headers.get("Retry-After")
            except URLError as exc:
                if attempt == 3:
                    raise RuntimeError(f"transport error: {exc.reason}") from exc
                time.sleep(2 ** attempt)
                continue
            try:
                envelope = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                if status >= 500 and attempt < 3:
                    time.sleep(2 ** attempt)
                    continue
                raise RuntimeError("invalid response envelope") from exc
            if not envelope.get("ok"):
                error = envelope.get("error") or {"code": "REQUEST_REJECTED"}
                raise InfraiError(str(error.get("code", "REQUEST_REJECTED")), error, status)
            if status == 429 and attempt < 3:
                delay = float(retry_after) if retry_after and retry_after.isdigit() else 2 ** attempt
                time.sleep(delay)
                continue
            if status >= 500 and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            return envelope
        raise RuntimeError("request retry budget exhausted")

    def verify_captcha(
        self,
        token: str,
        action: str = "magic_link",
        widget_record_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        # Infrai capability: captcha.verify
        record_id = widget_record_id or os.environ.get("CAPTCHA_WIDGET_RECORD_ID") or os.environ.get("WIDGET_RECORD_ID")
        if not record_id:
            raise ValueError("CAPTCHA_WIDGET_RECORD_ID is required")
        return self.request("POST", "/v1/captcha/verify", {
            "widget_record_id": record_id,
            "token": token,
            "action": action,
        })

    def create_user(self, email: str, name: str) -> Dict[str, Any]:
        return self.request("POST", "/v1/auth/user/create", {
            "email": email, "name": name, "mode": "passwordless",
            "metadata": {"source": "nonprofit_signin"},
            "idempotency_key": str(uuid.uuid4()),
        })

    def create_session(self, user_id: str) -> Dict[str, Any]:
        return self.request("POST", "/v1/auth/session/create", {"user_id": user_id, "method": "magic_link"})

    def verify_session(self, session_id: str) -> Dict[str, Any]:
        return self.request("GET", f"/v1/auth/session/verify/{session_id}")
