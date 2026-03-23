from __future__ import annotations

from requests import Response

from src.framework.clients.api.base_api_client import BaseAPIClient


class NotificationsClient(BaseAPIClient):
    def get_notifications(self, page: int = 1, limit: int = 10) -> Response:
        return self.get("/notifications", params={"page": page, "limit": limit})
