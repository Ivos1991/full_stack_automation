from __future__ import annotations

from assertpy import assert_that

from src.api.clients.transactions_client import TransactionsClient
from src.api.schemas.transaction_models import (
    TransactionCreatePayload,
    TransactionFeedItem,
    TransactionFeedPageData,
    TransactionFeedResponse,
    TransactionRecord,
)


class TransactionsService:
    def __init__(self, client: TransactionsClient) -> None:
        self.client = client

    def get_personal_feed(self, page: int = 1, limit: int = 10) -> TransactionFeedResponse:
        response = self.client.get_personal_transactions(page=page, limit=limit)
        assert_that(response.ok, "Expected personal transactions HTTP response to be OK").is_true()
        return self._map_feed_response(response.json())

    def get_public_feed(self, page: int = 1, limit: int = 10) -> TransactionFeedResponse:
        response = self.client.get_public_transactions(page=page, limit=limit)
        assert_that(response.ok, "Expected public transactions HTTP response to be OK").is_true()
        return self._map_feed_response(response.json())

    def get_transaction_by_id(self, transaction_id: str) -> TransactionRecord:
        response = self.client.get_transaction_by_id(transaction_id)
        assert_that(response.ok, "Expected transaction detail HTTP response to be OK").is_true()

        payload = response.json()["transaction"]
        return self._map_transaction_record(payload)

    def create_payment(self, payload: TransactionCreatePayload) -> TransactionRecord:
        response = self.client.create_transaction(payload)
        assert_that(response.ok, "Expected create transaction HTTP response to be OK").is_true()

        created_transaction = response.json()["transaction"]
        return self._map_transaction_record(created_transaction)

    def _map_feed_response(self, payload: dict[str, object]) -> TransactionFeedResponse:
        page_data = payload["pageData"]
        results = [self._map_transaction_item(item) for item in payload["results"]]

        return TransactionFeedResponse(
            page_data=TransactionFeedPageData(
                page=page_data["page"],
                limit=page_data["limit"],
                has_next_pages=page_data["hasNextPages"],
                total_pages=page_data["totalPages"],
            ),
            results=results,
        )

    @staticmethod
    def _map_transaction_record(item: dict[str, object]) -> TransactionRecord:
        return TransactionRecord(
            id=item["id"],
            sender_id=item["senderId"],
            receiver_id=item["receiverId"],
            amount=int(item["amount"]),
            description=item["description"],
            privacy_level=item["privacyLevel"],
            status=item["status"],
            request_status=item.get("requestStatus"),
            sender_name=item.get("senderName"),
            receiver_name=item.get("receiverName"),
        )

    @staticmethod
    def _map_transaction_item(item: dict[str, object]) -> TransactionFeedItem:
        action = "charged" if item.get("requestStatus") == "accepted" else "requested" if item.get("requestStatus") else "paid"
        sign = "+" if item.get("requestStatus") else "-"
        amount = int(item["amount"])
        amount_display = f"{sign}${amount / 100:,.2f}"

        return TransactionFeedItem(
            id=item["id"],
            sender_name=item["senderName"],
            action=action,
            receiver_name=item["receiverName"],
            amount_display=amount_display,
            description=item["description"],
            privacy_level=item["privacyLevel"],
            likes_count=len(item.get("likes", [])),
            comments_count=len(item.get("comments", [])),
        )
