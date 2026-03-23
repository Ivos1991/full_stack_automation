from __future__ import annotations

from src.api.schemas.notification_models import NotificationRecord
from src.api.schemas.transaction_models import PaymentNotificationRecord
from src.db.repositories.base_repository import BaseRepository


class NotificationsRepository(BaseRepository):
    def get_notifications_for_user(self, user_id: str) -> list[NotificationRecord]:
        state = self.db_client.read_state()
        matching_notifications = [
            item for item in state.get("notifications", []) if item.get("userId") == user_id
        ]
        ordered_notifications = sorted(
            matching_notifications,
            key=lambda item: (item.get("modifiedAt", ""), item.get("createdAt", "")),
        )
        return [self._map_notification_record(item) for item in ordered_notifications]

    def get_unread_notification_by_user_transaction_and_status(
        self,
        *,
        user_id: str,
        transaction_id: str,
        status: str,
    ) -> NotificationRecord | None:
        notifications = self.get_notifications_for_user(user_id)
        matching_notifications = [
            item
            for item in notifications
            if item.transaction_id == transaction_id and item.status == status and item.is_read is False
        ]
        if not matching_notifications:
            return None
        return matching_notifications[-1]

    def get_unread_comment_notification_by_user_and_transaction(
        self,
        user_id: str,
        transaction_id: str,
    ) -> NotificationRecord | None:
        return self.get_unread_notification_by_user_transaction_and_status(
            user_id=user_id,
            transaction_id=transaction_id,
            status="comment",
        )

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

    @staticmethod
    def _map_notification_record(item: dict[str, object]) -> NotificationRecord:
        return NotificationRecord(
            id=item["id"],
            user_id=item["userId"],
            transaction_id=item.get("transactionId"),
            status=item["status"],
            is_read=item["isRead"],
        )
