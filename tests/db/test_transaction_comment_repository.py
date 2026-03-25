from __future__ import annotations
import pytest
from assertpy import assert_that, soft_assertions
from src.framework.reporting.evidence_helpers import attach_snapshot

@pytest.mark.db
class TestTransactionCommentRepository:
    """DB coverage for persisted transaction comments."""

    def test_transaction_comment_repository_query_expects_persisted_comment(
        self,
        require_live_rwa_environment,
        connected_comments_repository,
        seeded_sent_payment,
        seeded_created_comment,
    ):
        """Create a comment through fixtures and verify the matching lowdb comment record for that transaction."""
        persisted_comment = connected_comments_repository.get_comment_by_transaction_and_content(
            transaction_id=seeded_sent_payment.id,
            content=seeded_created_comment.content,
        )
        persisted_comments = connected_comments_repository.get_comments_for_transaction(seeded_sent_payment.id)

        attach_snapshot(
            name="transaction-detail-comment-db",
            transaction=seeded_sent_payment,
            persisted_comment=persisted_comment,
            comments_count=len(persisted_comments),
        )

        assert_that(persisted_comment, "Expected persisted comment for transaction detail").is_not_none()

        with soft_assertions():
            assert_that(persisted_comment.id, "Persisted comment id should match created comment").is_equal_to(
                seeded_created_comment.id
            )
            assert_that(persisted_comment.content, "Persisted comment content should match").is_equal_to(
                seeded_created_comment.content
            )
            assert_that(persisted_comment.transaction_id, "Persisted comment transaction id should match").is_equal_to(
                seeded_sent_payment.id
            )
            assert_that(persisted_comment.user_id, "Persisted comment user should match seeded sender").is_equal_to(
                seeded_sent_payment.sender_id
            )
