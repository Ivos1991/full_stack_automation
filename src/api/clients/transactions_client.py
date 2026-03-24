from __future__ import annotations
from requests import Response
from src.framework.clients.api.base_api_client import BaseAPIClient
from src.api.schemas.transaction_models import TransactionCreatePayload

class TransactionsClient(BaseAPIClient):
    def get_personal_transactions(self, page: int = 1, limit: int = 10) -> Response:
        return self.get("/transactions", params={"page": page, "limit": limit})

    def get_public_transactions(self, page: int = 1, limit: int = 10) -> Response:
        return self.get("/transactions/public", params={"page": page, "limit": limit})

    def get_transaction_by_id(self, transaction_id: str) -> Response:
        return self.get(f"/transactions/{transaction_id}")

    def create_transaction(self, payload: TransactionCreatePayload) -> Response:
        return self.post("/transactions", json=payload.to_api_payload())
