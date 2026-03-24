from __future__ import annotations
from uuid import uuid4
from datetime import UTC, datetime
from base64 import urlsafe_b64encode
from src.api.schemas.user_models import GeneratedUserData
from src.db.repositories.base_repository import BaseRepository
from src.db.queries.users_queries import USER_BY_USERNAME_QUERY

class UsersRepository(BaseRepository):
    def get_user_by_id(self, user_id: str) -> dict[str, object] | None:
        state = self.db_client.read_state()
        for item in state.get("users", []):
            if item.get("id") == user_id:
                return item
        return None

    def get_user_by_username(self, username: str) -> dict[str, object] | None:
        return self.db_client.fetch_one(USER_BY_USERNAME_QUERY, (username,))

    def create_user(self, user_data: GeneratedUserData) -> dict[str, object]:
        """Create a lowdb user record for isolated repository validation outside the live backend path."""
        created_at = datetime.now(UTC).isoformat()

        def mutate(state: dict[str, list[dict[str, object]]]) -> dict[str, object]:
            user_record = {
                "id": self._build_shortid_like_id(),
                "uuid": str(uuid4()),
                "firstName": user_data.first_name,
                "lastName": user_data.last_name,
                "username": user_data.username,
                "password": user_data.password,
                "email": user_data.email,
                "phoneNumber": user_data.phone_number,
                "balance": user_data.balance,
                "avatar": user_data.avatar,
                "defaultPrivacyLevel": user_data.default_privacy_level,
                "createdAt": created_at,
                "modifiedAt": created_at,
            }
            state["users"].append(user_record)
            return user_record

        return self.db_client.mutate_state(mutate)

    def delete_user_and_related_data(self, user_id: str) -> None:
        """Remove a user and its directly related lowdb records for isolated repository tests only."""
        def mutate(state: dict[str, list[dict[str, object]]]) -> None:
            # Collect related ids first so dependent records can be removed in one deterministic mutation pass.
            bank_account_ids = {
                item["id"]
                for item in state.get("bankaccounts", [])
                if item.get("userId") == user_id
            }
            transaction_ids = {
                item["id"]
                for item in state.get("transactions", [])
                if item.get("senderId") == user_id or item.get("receiverId") == user_id
            }

            state["users"] = [item for item in state.get("users", []) if item.get("id") != user_id]
            state["contacts"] = [
                item
                for item in state.get("contacts", [])
                if item.get("userId") != user_id and item.get("contactUserId") != user_id
            ]
            state["bankaccounts"] = [
                item for item in state.get("bankaccounts", []) if item.get("userId") != user_id
            ]
            state["transactions"] = [
                item
                for item in state.get("transactions", [])
                if item.get("senderId") != user_id and item.get("receiverId") != user_id
            ]
            state["likes"] = [
                item
                for item in state.get("likes", [])
                if item.get("userId") != user_id and item.get("transactionId") not in transaction_ids
            ]
            state["comments"] = [
                item
                for item in state.get("comments", [])
                if item.get("userId") != user_id and item.get("transactionId") not in transaction_ids
            ]
            state["notifications"] = [
                item
                for item in state.get("notifications", [])
                if item.get("userId") != user_id and item.get("transactionId") not in transaction_ids
            ]
            state["banktransfers"] = [
                item
                for item in state.get("banktransfers", [])
                if item.get("userId") != user_id
                and item.get("transactionId") not in transaction_ids
                and item.get("source") not in bank_account_ids
            ]

        self.db_client.mutate_state(mutate)

    @staticmethod
    def _build_shortid_like_id() -> str:
        return urlsafe_b64encode(uuid4().bytes).decode("ascii").rstrip("=")[:10]
