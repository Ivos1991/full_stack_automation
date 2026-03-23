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
