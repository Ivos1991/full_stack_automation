from __future__ import annotations
from requests import Response
from src.api.schemas.user_models import GeneratedUserData
from src.framework.clients.api.base_api_client import BaseAPIClient

class UsersClient(BaseAPIClient):
    def get_current_user(self) -> Response:
        return self.get("/checkAuth")

    def create_user(self, user_data: GeneratedUserData) -> Response:
        return self.post("/users", json=user_data.to_api_payload())
