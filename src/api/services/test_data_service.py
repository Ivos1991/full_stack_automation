from __future__ import annotations

from assertpy import assert_that

from src.api.clients.test_data_client import TestDataClient


class TestDataService:
    def __init__(self, client: TestDataClient) -> None:
        self.client = client

    def seed_database(self) -> None:
        response = self.client.seed_database()
        assert_that(response.ok, "Expected testData seed HTTP response to be OK").is_true()
