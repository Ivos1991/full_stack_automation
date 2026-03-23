from __future__ import annotations

from requests import Response

from src.framework.clients.api.base_api_client import BaseAPIClient


class AuthClient(BaseAPIClient):
    def login(self, username: str, password: str, remember: bool | None = None) -> Response:
        payload: dict[str, object] = {"username": username, "password": password}
        if remember is not None:
            payload["remember"] = remember
        return self.post("/login", json=payload)
