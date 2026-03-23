from __future__ import annotations

from src.api.schemas.transaction_models import (
    TransactionRecord,
    TransactionFeedItem,
    TransactionFeedPageData,
    TransactionFeedResponse,
)
from src.db.repositories.base_repository import BaseRepository


class TransactionsRepository(BaseRepository):
    def get_transaction_by_id(self, transaction_id: str) -> TransactionRecord | None:
        state = self.db_client.read_state()
        users_by_id = {item["id"]: item for item in state.get("users", [])}
        for item in state.get("transactions", []):
            if item.get("id") == transaction_id:
                return self._map_transaction_record(item, users_by_id)
        return None

    def get_latest_payment_by_participants_and_description(
        self,
        sender_id: str,
        receiver_id: str,
        description: str,
    ) -> TransactionRecord | None:
        state = self.db_client.read_state()
        users_by_id = {item["id"]: item for item in state.get("users", [])}
        matching_transactions = [
            item
            for item in state.get("transactions", [])
            if item.get("senderId") == sender_id
            and item.get("receiverId") == receiver_id
            and item.get("description") == description
            and not item.get("requestStatus")
        ]

        if not matching_transactions:
            return None

        latest_transaction = self._order_transactions(matching_transactions)[0]
        return self._map_transaction_record(latest_transaction, users_by_id)

    def get_public_feed_for_user(self, user_id: str, page: int = 1, limit: int = 10) -> TransactionFeedResponse:
        state = self.db_client.read_state()
        users_by_id = {item["id"]: item for item in state["users"]}
        likes_by_transaction_id: dict[str, list[dict[str, object]]] = {}
        comments_by_transaction_id: dict[str, list[dict[str, object]]] = {}

        for like in state["likes"]:
            likes_by_transaction_id.setdefault(like["transactionId"], []).append(like)

        for comment in state["comments"]:
            comments_by_transaction_id.setdefault(comment["transactionId"], []).append(comment)

        contact_user_ids = [
            item["contactUserId"]
            for item in state["contacts"]
            if item.get("userId") == user_id
        ]

        contact_transactions = []
        for contact_user_id in contact_user_ids:
            for transaction in state["transactions"]:
                if transaction.get("receiverId") == contact_user_id or transaction.get("senderId") == contact_user_id:
                    contact_transactions.append(transaction)

        contact_transaction_ids = {item["id"] for item in contact_transactions}
        public_transactions = [
            item
            for item in state["transactions"]
            if item.get("privacyLevel") == "public" and item.get("id") not in contact_transaction_ids
        ]

        ordered_contact_transactions = self._order_transactions(contact_transactions)
        ordered_public_transactions = self._order_transactions(public_transactions)

        if page == 1:
            combined_transactions = ordered_contact_transactions[:5] + ordered_public_transactions
        else:
            combined_transactions = ordered_public_transactions

        total_pages = (len(combined_transactions) + limit - 1) // limit
        offset = (page - 1) * limit
        paginated_transactions = combined_transactions[offset : offset + limit]

        results = [
            self._map_transaction_item(
                transaction=item,
                users_by_id=users_by_id,
                likes=likes_by_transaction_id.get(item["id"], []),
                comments=comments_by_transaction_id.get(item["id"], []),
            )
            for item in paginated_transactions
        ]

        return TransactionFeedResponse(
            page_data=TransactionFeedPageData(
                page=page,
                limit=limit,
                has_next_pages=page < total_pages,
                total_pages=total_pages,
            ),
            results=results,
        )

    @staticmethod
    def _order_transactions(transactions: list[dict[str, object]]) -> list[dict[str, object]]:
        return sorted(transactions, key=lambda item: item["modifiedAt"], reverse=True)

    @staticmethod
    def _map_transaction_record(
        transaction: dict[str, object],
        users_by_id: dict[str, dict[str, object]],
    ) -> TransactionRecord:
        sender = users_by_id[transaction["senderId"]]
        receiver = users_by_id[transaction["receiverId"]]
        return TransactionRecord(
            id=transaction["id"],
            sender_id=transaction["senderId"],
            receiver_id=transaction["receiverId"],
            amount=int(transaction["amount"]),
            description=transaction["description"],
            privacy_level=transaction["privacyLevel"],
            status=transaction["status"],
            request_status=transaction.get("requestStatus"),
            sender_name=f"{sender['firstName']} {sender['lastName']}",
            receiver_name=f"{receiver['firstName']} {receiver['lastName']}",
        )

    @staticmethod
    def _map_transaction_item(
        transaction: dict[str, object],
        users_by_id: dict[str, dict[str, object]],
        likes: list[dict[str, object]],
        comments: list[dict[str, object]],
    ) -> TransactionFeedItem:
        sender = users_by_id[transaction["senderId"]]
        receiver = users_by_id[transaction["receiverId"]]
        request_status = transaction.get("requestStatus")
        action = "charged" if request_status == "accepted" else "requested" if request_status else "paid"
        sign = "+" if request_status else "-"
        amount_display = f"{sign}${int(transaction['amount']) / 100:,.2f}"

        return TransactionFeedItem(
            id=transaction["id"],
            sender_name=f"{sender['firstName']} {sender['lastName']}",
            action=action,
            receiver_name=f"{receiver['firstName']} {receiver['lastName']}",
            amount_display=amount_display,
            description=transaction["description"],
            privacy_level=transaction["privacyLevel"],
            likes_count=len(likes),
            comments_count=len(comments),
        )
