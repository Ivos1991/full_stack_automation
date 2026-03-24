from __future__ import annotations
from assertpy import assert_that
from src.api.schemas.auth_models import CurrentUser
from src.api.clients.users_client import UsersClient
from src.api.schemas.user_models import CreatedUser, GeneratedUserData

class UsersService:
    def __init__(self, client: UsersClient) -> None:
        self.client = client

    def get_current_user(self) -> CurrentUser:
        response = self.client.get_current_user()
        assert_that(response.ok, "Expected checkAuth HTTP response to be OK").is_true()
        payload = response.json()
        user_payload = payload.get("user", payload)

        return CurrentUser(
            id=user_payload.get("id"),
            username=user_payload.get("username") or user_payload.get("userName"),
            first_name=user_payload.get("firstName") or user_payload.get("first_name"),
            last_name=user_payload.get("lastName") or user_payload.get("last_name"),
            balance=user_payload.get("balance"),
        )

    def create_user(self, user_data: GeneratedUserData) -> CreatedUser:
        response = self.client.create_user(user_data)
        assert_that(response.status_code, "Expected create user HTTP status code").is_equal_to(201)

        payload = response.json()["user"]
        return CreatedUser(
            id=payload["id"],
            username=payload["username"],
            first_name=payload["firstName"],
            last_name=payload["lastName"],
            email=payload.get("email"),
        )
