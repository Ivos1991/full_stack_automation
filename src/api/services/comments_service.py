from __future__ import annotations

from assertpy import assert_that

from src.api.clients.comments_client import CommentsClient
from src.api.schemas.comment_models import CommentCreatePayload, CommentRecord


class CommentsService:
    def __init__(self, client: CommentsClient) -> None:
        self.client = client

    def get_comments(self, transaction_id: str) -> list[CommentRecord]:
        response = self.client.get_comments(transaction_id)
        assert_that(response.ok, "Expected comments HTTP response to be OK").is_true()

        payload = response.json()
        return [self._map_comment_record(item) for item in payload["comments"]]

    def create_comment(self, transaction_id: str, payload: CommentCreatePayload) -> list[CommentRecord]:
        response = self.client.create_comment(transaction_id, payload)
        assert_that(response.ok, "Expected create comment HTTP response to be OK").is_true()
        return self.get_comments(transaction_id)

    @staticmethod
    def _map_comment_record(item: dict[str, object]) -> CommentRecord:
        return CommentRecord(
            id=item["id"],
            content=item["content"],
            user_id=item["userId"],
            transaction_id=item["transactionId"],
        )
