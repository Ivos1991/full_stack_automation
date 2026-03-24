from __future__ import annotations

from assertpy import assert_that, soft_assertions
import pytest

from src.framework.reporting.allure_helpers import attach_json


@pytest.mark.api
class TestTransactionCommentService:
    """API coverage for transaction-detail comment creation."""

    def test_transaction_comment_creation_expects_comment_in_api_collection(
        self,
        require_live_rwa_environment,
        comments_service,
        seeded_sent_payment,
        seeded_transaction_comment_payload,
    ):
        """Create a comment on the fixture-created transaction and verify it is returned by the comments API."""
        comments = comments_service.create_comment(
            transaction_id=seeded_sent_payment.id,
            payload=seeded_transaction_comment_payload,
        )
        created_comment = next(
            (item for item in comments if item.content == seeded_transaction_comment_payload.content),
            None,
        )

        attach_json(
            name="transaction-detail-comment-api",
            content={
                "transaction": seeded_sent_payment.__dict__,
                "created_comment": created_comment.__dict__ if created_comment else None,
                "comments_count": len(comments),
            },
        )

        assert_that(created_comment, "Expected created comment in API comments response").is_not_none()

        with soft_assertions():
            assert_that(created_comment.content, "Created comment content should match").is_equal_to(
                seeded_transaction_comment_payload.content
            )
            assert_that(created_comment.transaction_id, "Created comment transaction id should match").is_equal_to(
                seeded_sent_payment.id
            )
            assert_that(created_comment.user_id, "Created comment user should match seeded sender").is_equal_to(
                seeded_sent_payment.sender_id
            )
