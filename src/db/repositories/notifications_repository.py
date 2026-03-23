from __future__ import annotations

from src.api.schemas.transaction_models import PaymentNotificationRecord
from src.db.repositories.base_repository import BaseRepository


class NotificationsRepository(BaseRepository):
    def get_unread_payment_notification_by_user_and_transaction(
        self,
        user_id: str,
        transaction_id: str,
    ) -> PaymentNotificationRecord | None:
        state = self.db_client.read_state()

        for item in state.get("notifications", []):
            if (
                item.get("userId") == user_id
                and item.get("transactionId") == transaction_id
                and item.get("status") == "received"
                and item.get("isRead") is False
            ):
                return PaymentNotificationRecord(
                    id=item["id"],
                    user_id=item["userId"],
                    transaction_id=item["transactionId"],
                    status=item["status"],
                    is_read=item["isRead"],
                )

        return None
