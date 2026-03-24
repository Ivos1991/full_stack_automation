from __future__ import annotations

from pathlib import Path

from assertpy import assert_that, soft_assertions
import pytest

from src.framework.reporting.allure_helpers import attach_file, attach_json


@pytest.mark.e2e
class TestTransactionCommentVerticalSlice:
    """End-to-end coverage for transaction-detail comment creation."""

    def test_transaction_comment_vertical_slice_expects_ui_api_and_db_alignment(
        self,
        require_live_rwa_environment,
        settings,
        auth_service,
        comments_service,
        seeded_business_user_credentials,
        seeded_transaction_comment_payload,
        ui_created_transaction_comment_detail_page,
        ui_created_transaction_comment_record,
        ui_created_transaction_comment_transaction,
    ):
        """Create a payment in the UI, add a comment on its detail page, and validate the same comment through API and DB."""
        screenshot_path = ui_created_transaction_comment_detail_page.screenshot(
            str(Path(settings.screenshots_dir) / "transaction-detail-comment-e2e.png")
        )
        attach_file(path=screenshot_path, name="transaction-detail-comment-e2e")

        auth_service.login(seeded_business_user_credentials)
        api_comments = comments_service.get_comments(ui_created_transaction_comment_transaction.id)
        api_comment = next(
            (item for item in api_comments if item.content == seeded_transaction_comment_payload.content),
            None,
        )
        db_comment = ui_created_transaction_comment_record

        attach_json(
            name="transaction-detail-comment-e2e",
            content={
                "transaction": ui_created_transaction_comment_transaction.__dict__,
                "api_comment": api_comment.__dict__ if api_comment else None,
                "db_comment": db_comment.__dict__ if db_comment else None,
            },
        )

        assert_that(api_comment, "Expected created comment in API state after UI creation").is_not_none()
        assert_that(db_comment, "Expected created comment in DB state after UI creation").is_not_none()

        with soft_assertions():
            assert_that(api_comment.content, "API comment content should match UI-created comment").is_equal_to(
                seeded_transaction_comment_payload.content
            )
            assert_that(api_comment.transaction_id, "API comment transaction id should match").is_equal_to(
                ui_created_transaction_comment_transaction.id
            )
            assert_that(api_comment.user_id, "API comment user id should match seeded sender").is_equal_to(
                ui_created_transaction_comment_transaction.sender_id
            )
            assert_that(db_comment.content, "DB comment content should match UI-created comment").is_equal_to(
                seeded_transaction_comment_payload.content
            )
            assert_that(db_comment.transaction_id, "DB comment transaction id should match").is_equal_to(
                ui_created_transaction_comment_transaction.id
            )
            assert_that(db_comment.user_id, "DB comment user id should match seeded sender").is_equal_to(
                ui_created_transaction_comment_transaction.sender_id
            )
