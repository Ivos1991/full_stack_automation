from __future__ import annotations

from assertpy import assert_that

from src.api.clients.notifications_client import NotificationsClient
from src.api.schemas.notification_models import NotificationRecord


class NotificationsService:
    def __init__(self, client: NotificationsClient) -> None:
        self.client = client

    def get_notifications(self, page: int = 1, limit: int = 10) -> list[NotificationRecord]:
        response = self.client.get_notifications(page=page, limit=limit)
        assert_that(response.ok, "Expected notifications HTTP response to be OK").is_true()

        payload = response.json()
        if isinstance(payload, dict):
            raw_notifications = payload.get("results") or payload.get("notifications") or []
        else:
            raw_notifications = payload

        return [self._map_notification_record(item) for item in raw_notifications]

    def get_unread_notification_for_transaction(
        self,
        transaction_id: str,
        *,
        status: str,
    ) -> NotificationRecord | None:
        notifications = self.get_notifications()
        for item in notifications:
            if item.transaction_id == transaction_id and item.status == status and item.is_read is False:
                return item
        return None

    @staticmethod
    def _map_notification_record(item: dict[str, object]) -> NotificationRecord:
        transaction = item.get("transaction")
        transaction_id = item.get("transactionId")
        if transaction_id is None and isinstance(transaction, dict):
            transaction_id = transaction.get("id")

        return NotificationRecord(
            id=item["id"],
            user_id=item["userId"],
            transaction_id=transaction_id,
            status=item["status"],
            is_read=item["isRead"],
        )
