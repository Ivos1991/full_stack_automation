from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class CommentCreatePayload:
    content: str

    def to_api_payload(self) -> dict[str, object]:
        return {"content": self.content}


@dataclass(frozen=True)
class CommentRecord:
    id: str
    content: str
    user_id: str
    transaction_id: str
