from __future__ import annotations

from requests import Response

from src.framework.clients.api.base_api_client import BaseAPIClient


class TestDataClient(BaseAPIClient):
    def seed_database(self) -> Response:
        return self.post("/testData/seed")
