from __future__ import annotations

from src.api.schemas.comment_models import CommentCreatePayload
from src.api.schemas.transaction_models import TransactionCreatePayload


def build_health_payload(status: str = "ok") -> dict[str, str]:
    return {"status": status}


def build_seeded_send_money_payment_payload(receiver_id: str) -> TransactionCreatePayload:
    return TransactionCreatePayload(
        receiver_id=receiver_id,
        amount=35,
        description="Seeded send money payment",
    )


def build_seeded_transaction_comment_payload() -> CommentCreatePayload:
    return CommentCreatePayload(content="Seeded transaction detail comment")
