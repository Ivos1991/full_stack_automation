from __future__ import annotations

from assertpy import assert_that, soft_assertions
import pytest

from src.framework.reporting.allure_helpers import attach_json


@pytest.mark.e2e
class TestTransactionCommentNotificationVerticalSlice:
    def test_transaction_comment_creates_unread_receiver_notification_across_api_and_db(
        self,
        require_live_rwa_environment,
        auth_service,
        notifications_service,
        connected_comments_repository,
        connected_notifications_repository,
        connected_transactions_repository,
        sign_in_page,
        home_page,
        transaction_create_page,
        transaction_detail_page,
        seeded_business_user,
        seeded_business_user_credentials,
        seeded_send_money_contact,
        seeded_send_money_contact_credentials,
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
            "UI-created payment should be resolvable before validating the comment notification side effect",
        ).is_not_none()

        transaction_detail_page.expect_loaded()
        transaction_detail_page.add_comment(
            transaction_id=persisted_transaction.id,
            content=seeded_transaction_comment_payload.content,
        )
        transaction_detail_page.expect_comment_displayed(seeded_transaction_comment_payload.content)

        db_comment = connected_comments_repository.get_comment_by_transaction_and_content(
            transaction_id=persisted_transaction.id,
            content=seeded_transaction_comment_payload.content,
        )
        assert_that(db_comment, "Expected persisted comment before validating notification side effect").is_not_none()

        auth_service.login(seeded_send_money_contact_credentials)
        api_notification = notifications_service.get_unread_notification_for_transaction(
            persisted_transaction.id,
            status="comment",
        )
        db_notification = connected_notifications_repository.get_unread_comment_notification_by_user_and_transaction(
            user_id=seeded_send_money_contact["id"],
            transaction_id=persisted_transaction.id,
        )

        attach_json(
            name="transaction-comment-notification-e2e",
            content={
                "transaction": persisted_transaction.__dict__,
                "comment": db_comment.__dict__ if db_comment else None,
                "api_notification": api_notification.__dict__ if api_notification else None,
                "db_notification": db_notification.__dict__ if db_notification else None,
            },
        )

        assert_that(
            api_notification,
            "Expected unread comment notification in API state after UI comment creation",
        ).is_not_none()
        assert_that(
            db_notification,
            "Expected unread comment notification in DB state after UI comment creation",
        ).is_not_none()

        with soft_assertions():
            assert_that(api_notification.user_id, "API notification should belong to the receiver").is_equal_to(
                seeded_send_money_contact["id"]
            )
            assert_that(
                api_notification.transaction_id,
                "API notification transaction id should match",
            ).is_equal_to(persisted_transaction.id)
            assert_that(api_notification.status, "API notification should represent a comment event").is_equal_to(
                "comment"
            )
            assert_that(
                api_notification.is_read,
                "API notification should remain unread immediately after creation",
            ).is_false()
            assert_that(db_notification.user_id, "DB notification should belong to the receiver").is_equal_to(
                seeded_send_money_contact["id"]
            )
            assert_that(
                db_notification.transaction_id,
                "DB notification transaction id should match",
            ).is_equal_to(persisted_transaction.id)
            assert_that(db_notification.status, "DB notification should represent a comment event").is_equal_to(
                "comment"
            )
            assert_that(
                db_notification.is_read,
                "DB notification should remain unread immediately after creation",
            ).is_false()
