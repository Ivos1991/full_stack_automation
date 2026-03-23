from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NotificationRecord:
    id: str
    user_id: str
    transaction_id: str | None
    status: str
    is_read: bool
