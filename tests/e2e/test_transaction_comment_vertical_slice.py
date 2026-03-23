from __future__ import annotations

from pathlib import Path

from assertpy import assert_that, soft_assertions
import pytest

from src.framework.reporting.allure_helpers import attach_file, attach_json


@pytest.mark.e2e
class TestTransactionCommentVerticalSlice:
    def test_transaction_comment_vertical_slice_for_ui_created_payment(
        self,
        require_live_rwa_environment,
        settings,
        sign_in_page,
        home_page,
        transaction_create_page,
        transaction_detail_page,
        auth_service,
        comments_service,
        connected_comments_repository,
        connected_transactions_repository,
        seeded_business_user,
        seeded_business_user_credentials,
        seeded_send_money_contact,
        seeded_send_money_payment,
        seeded_transaction_comment_payload,
    ):
        recipient_full_name = (
            f"{seeded_send_money_contact['firstName']} {seeded_send_money_contact['lastName']}"
        )

        sign_in_page.go_to()
        sign_in_page.sign_in(
            username=seeded_business_user_credentials.username,
            password=seeded_business_user_credentials.password,
        )
        home_page.expect_seeded_user_landing_loaded()
        home_page.open_new_transaction()

        transaction_create_page.search_contact(seeded_send_money_contact["firstName"])
        transaction_create_page.select_contact_by_full_name(recipient_full_name)
        transaction_create_page.expect_payment_form_loaded(recipient_full_name=recipient_full_name)
        transaction_create_page.enter_amount(seeded_send_money_payment.amount)
        transaction_create_page.enter_description(seeded_send_money_payment.description)
        transaction_create_page.submit_payment()
        transaction_create_page.expect_payment_success_state(
            amount_display=seeded_send_money_payment.amount_display,
            description=seeded_send_money_payment.description,
        )
        transaction_create_page.return_to_transactions()

        home_page.open_personal_feed()
        home_page.open_transaction_with_description(seeded_send_money_payment.description)

        persisted_transaction = connected_transactions_repository.get_latest_payment_by_participants_and_description(
            sender_id=seeded_business_user["id"],
            receiver_id=seeded_send_money_contact["id"],
            description=seeded_send_money_payment.description,
        )
        assert_that(
            persisted_transaction,
            "UI-created payment should be resolvable before adding a transaction-detail comment",
        ).is_not_none()

        transaction_detail_page.expect_loaded()
        transaction_detail_page.add_comment(
            transaction_id=persisted_transaction.id,
            content=seeded_transaction_comment_payload.content,
        )
        transaction_detail_page.expect_comment_displayed(seeded_transaction_comment_payload.content)

        screenshot_path = transaction_detail_page.screenshot(
            str(Path(settings.screenshots_dir) / "transaction-detail-comment-e2e.png")
        )
        attach_file(path=screenshot_path, name="transaction-detail-comment-e2e")

        auth_service.login(seeded_business_user_credentials)
        api_comments = comments_service.get_comments(persisted_transaction.id)
        api_comment = next((item for item in api_comments if item.content == seeded_transaction_comment_payload.content), None)
        db_comment = connected_comments_repository.get_comment_by_transaction_and_content(
            transaction_id=persisted_transaction.id,
            content=seeded_transaction_comment_payload.content,
        )

        attach_json(
            name="transaction-detail-comment-e2e",
            content={
                "transaction": persisted_transaction.__dict__,
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
                persisted_transaction.id
            )
            assert_that(api_comment.user_id, "API comment user id should match seeded sender").is_equal_to(
                persisted_transaction.sender_id
            )
            assert_that(db_comment.content, "DB comment content should match UI-created comment").is_equal_to(
                seeded_transaction_comment_payload.content
            )
            assert_that(db_comment.transaction_id, "DB comment transaction id should match").is_equal_to(
                persisted_transaction.id
            )
            assert_that(db_comment.user_id, "DB comment user id should match seeded sender").is_equal_to(
                persisted_transaction.sender_id
            )
