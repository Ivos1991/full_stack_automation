from __future__ import annotations

from requests import Response

from src.api.schemas.notification_models import NotificationUpdatePayload
from src.framework.clients.api.base_api_client import BaseAPIClient


class NotificationsClient(BaseAPIClient):
    def get_notifications(self, page: int = 1, limit: int = 10) -> Response:
        return self.get("/notifications", params={"page": page, "limit": limit})

    def update_notification(self, notification_id: str, payload: NotificationUpdatePayload) -> Response:
        return self.patch(f"/notifications/{notification_id}", json=payload.to_api_payload())
