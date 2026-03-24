from __future__ import annotations
from requests import Response
from src.api.schemas.comment_models import CommentCreatePayload
from src.framework.clients.api.base_api_client import BaseAPIClient

class CommentsClient(BaseAPIClient):
    def get_comments(self, transaction_id: str) -> Response:
        return self.get(f"/comments/{transaction_id}")

    def create_comment(self, transaction_id: str, payload: CommentCreatePayload) -> Response:
        return self.post(f"/comments/{transaction_id}", json=payload.to_api_payload())
