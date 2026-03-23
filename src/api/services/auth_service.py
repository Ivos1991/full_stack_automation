from __future__ import annotations

from assertpy import assert_that

from src.api.clients.auth_client import AuthClient
from src.api.schemas.auth_models import AuthCredentials


class AuthService:
    def __init__(self, client: AuthClient) -> None:
        self.client = client

    def login(self, credentials: AuthCredentials) -> dict[str, object]:
        response = self.client.login(
            credentials.username,
            credentials.password,
            remember=credentials.remember,
        )
        assert_that(response.ok, "Expected login HTTP response to be OK").is_true()
        return response.json()
