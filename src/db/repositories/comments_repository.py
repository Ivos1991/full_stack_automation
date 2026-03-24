from __future__ import annotations
from src.api.schemas.comment_models import CommentRecord
from src.db.repositories.base_repository import BaseRepository

class CommentsRepository(BaseRepository):
    def get_comments_for_transaction(self, transaction_id: str) -> list[CommentRecord]:
        state = self.db_client.read_state()
        matching_comments = [
            item
            for item in state.get("comments", [])
            if item.get("transactionId") == transaction_id
        ]
        ordered_comments = sorted(matching_comments, key=lambda item: item["modifiedAt"])
        return [self._map_comment_record(item) for item in ordered_comments]

    def get_comment_by_transaction_and_content(
        self,
        transaction_id: str,
        content: str,
    ) -> CommentRecord | None:
        comments = self.get_comments_for_transaction(transaction_id)
        for comment in comments:
            if comment.content == content:
                return comment
        return None

    @staticmethod
    def _map_comment_record(item: dict[str, object]) -> CommentRecord:
        return CommentRecord(
            id=item["id"],
            content=item["content"],
            user_id=item["userId"],
            transaction_id=item["transactionId"],
        )
