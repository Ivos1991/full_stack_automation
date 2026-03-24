from __future__ import annotations
from assertpy import assert_that
from src.api.clients.notifications_client import NotificationsClient
from src.api.schemas.notification_models import (
    NotificationRecord,
    NotificationUpdatePayload,
    map_notification_record,
)

class NotificationsService:
    def __init__(self, client: NotificationsClient) -> None:
        self.client = client

    def get_notifications(self, page: int = 1, limit: int = 10) -> list[NotificationRecord]:
        """Return normalized notifications despite the RWA endpoint using more than one response shape."""
        response = self.client.get_notifications(page=page, limit=limit)
        assert_that(response.ok, "Expected notifications HTTP response to be OK").is_true()

        payload = response.json()
        if isinstance(payload, dict):
            raw_notifications = payload.get("results") or payload.get("notifications") or []
        else:
            raw_notifications = payload

        return [map_notification_record(item) for item in raw_notifications]

    def get_unread_notification_for_transaction(
        self,
        transaction_id: str,
        *,
        status: str,
    ) -> NotificationRecord | None:
        """Filter the normalized notification feed down to the unread record for one transaction side effect."""
        notifications = self.get_notifications()
        for item in notifications:
            if item.transaction_id == transaction_id and item.status == status and item.is_read is False:
                return item
        return None

    def mark_notification_as_read(self, notification_id: str) -> None:
        """Mark one notification as read through the real API transition path."""
        response = self.client.update_notification(
            notification_id=notification_id,
            payload=NotificationUpdatePayload(is_read=True),
        )
        assert_that(
            response.status_code,
            "Expected notification read-state update to return the backend success status",
        ).is_equal_to(204)

