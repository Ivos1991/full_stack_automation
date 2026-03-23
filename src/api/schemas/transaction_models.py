from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TransactionCreatePayload:
    receiver_id: str
    amount: int
    description: str
    transaction_type: str = "payment"
    privacy_level: str | None = None
    source: str = ""

    @property
    def amount_cents(self) -> int:
        return self.amount * 100

    @property
    def amount_display(self) -> str:
        return f"${self.amount:,.2f}"

    def to_api_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "receiverId": self.receiver_id,
            "amount": self.amount,
            "description": self.description,
            "transactionType": self.transaction_type,
            "source": self.source,
        }
        if self.privacy_level is not None:
            payload["privacyLevel"] = self.privacy_level
        return payload


@dataclass(frozen=True)
class TransactionRecord:
    id: str
    sender_id: str
    receiver_id: str
    amount: int
    description: str
    privacy_level: str
    status: str
    request_status: str | None
    sender_name: str | None = None
    receiver_name: str | None = None

    @property
    def action(self) -> str:
        if self.request_status == "accepted":
            return "charged"
        if self.request_status:
            return "requested"
        return "paid"

    @property
    def amount_display(self) -> str:
        return f"${self.amount / 100:,.2f}"

    @property
    def signed_amount_display(self) -> str:
        sign = "+" if self.request_status else "-"
        return f"{sign}{self.amount_display}"


@dataclass(frozen=True)
class PaymentNotificationRecord:
    id: str
    user_id: str
    transaction_id: str
    status: str
    is_read: bool


@dataclass(frozen=True)
class TransactionFeedItem:
    id: str
    sender_name: str
    action: str
    receiver_name: str
    amount_display: str
    description: str
    privacy_level: str
    likes_count: int
    comments_count: int


@dataclass(frozen=True)
class TransactionFeedPageData:
    page: int
    limit: int
    has_next_pages: bool
    total_pages: int


@dataclass(frozen=True)
class TransactionFeedResponse:
    page_data: TransactionFeedPageData
    results: list[TransactionFeedItem]
