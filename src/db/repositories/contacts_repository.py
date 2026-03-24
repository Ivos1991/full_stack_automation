from __future__ import annotations
from src.db.repositories.base_repository import BaseRepository

class ContactsRepository(BaseRepository):
    def get_contact_user_ids_for_user(self, user_id: str) -> list[str]:
        state = self.db_client.read_state()
        return [
            item["contactUserId"]
            for item in state.get("contacts", [])
            if item.get("userId") == user_id
        ]

    def has_contact_relationship(self, user_id: str, contact_user_id: str) -> bool:
        state = self.db_client.read_state()
        return any(
            item.get("userId") == user_id and item.get("contactUserId") == contact_user_id
            for item in state.get("contacts", [])
        )
