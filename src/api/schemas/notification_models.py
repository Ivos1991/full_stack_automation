from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class NotificationRecord:
    id: str
    user_id: str
    transaction_id: str | None
    status: str
    is_read: bool


@dataclass(frozen=True)
class NotificationUpdatePayload:
    is_read: bool

    def to_api_payload(self) -> dict[str, object]:
        return {"isRead": self.is_read}


def infer_notification_status(item: dict[str, object]) -> str:
    """Normalize RWA notification variants into one readable status label for assertions."""
    status = item.get("status")
    if status is not None:
        return str(status)
    if item.get("commentId"):
        return "comment"
    if item.get("likeId"):
        return "like"
    if item.get("transactionType"):
        return str(item["transactionType"])
    return "unknown"


def map_notification_record(item: dict[str, object]) -> NotificationRecord:
    """Map the raw notification shape used by RWA API/lowdb into the shared framework model."""
    transaction = item.get("transaction")
    transaction_id = item.get("transactionId")
    if transaction_id is None and isinstance(transaction, dict):
        transaction_id = transaction.get("id")

    return NotificationRecord(
        id=item["id"],
        user_id=item["userId"],
        transaction_id=transaction_id,
        status=infer_notification_status(item),
        is_read=item["isRead"],
    )
