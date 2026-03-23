from __future__ import annotations

from pathlib import Path

from assertpy import assert_that, soft_assertions
import pytest

from src.framework.reporting.allure_helpers import attach_file, attach_json


@pytest.mark.e2e
class TestTransactionCommentNotificationReadVerticalSlice:
    """End-to-end coverage for consuming a comment notification and persisting the read-state transition."""

    def test_receiver_can_dismiss_transaction_comment_notification_and_persist_read_state(
        self,
        require_live_rwa_environment,
        settings,
        auth_service,
        notifications_service,
        connected_comments_repository,
        connected_notifications_repository,
        connected_transactions_repository,
        sign_in_page,
        home_page,
        transaction_create_page,
        transaction_detail_page,
        notifications_page,
        seeded_business_user,
        seeded_business_user_credentials,
        seeded_send_money_contact,
        seeded_send_money_contact_credentials,
        seeded_send_money_payment,
        seeded_transaction_comment_payload,
    ):
        """Create the payment and comment in the UI, dismiss the receiver notification in the UI, then verify API and DB read state."""
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
            "UI-created payment should be resolvable before validating notification read-state transition",
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
        assert_that(db_comment, "Expected persisted comment before dismissing the notification").is_not_none()

        auth_service.login(seeded_send_money_contact_credentials)
        unread_before = notifications_service.get_unread_notification_for_transaction(
            persisted_transaction.id,
            status="comment",
        )
        assert_that(
            unread_before,
            "Expected receiver unread comment notification before the UI read-state transition",
        ).is_not_none()

        home_page.sign_out()
        sign_in_page.sign_in(
            username=seeded_send_money_contact_credentials.username,
            password=seeded_send_money_contact_credentials.password,
        )
        home_page.expect_seeded_user_landing_loaded()
        home_page.open_notifications()
        notifications_page.expect_loaded()
        notifications_page.expect_notification_visible(
            notification_id=unread_before.id,
            expected_text=seeded_business_user["firstName"],
        )

        before_screenshot = notifications_page.screenshot(
            str(Path(settings.screenshots_dir) / "transaction-comment-notification-read-before-e2e.png")
        )
        attach_file(path=before_screenshot, name="transaction-comment-notification-read-before-e2e")

        notifications_page.dismiss_notification(unread_before.id)
        notifications_page.expect_notification_absent(unread_before.id)

        after_screenshot = notifications_page.screenshot(
            str(Path(settings.screenshots_dir) / "transaction-comment-notification-read-after-e2e.png")
        )
        attach_file(path=after_screenshot, name="transaction-comment-notification-read-after-e2e")

        auth_service.login(seeded_send_money_contact_credentials)
        unread_after = notifications_service.get_unread_notification_for_transaction(
            persisted_transaction.id,
            status="comment",
        )
        persisted_notification = connected_notifications_repository.get_notification_by_id(unread_before.id)

        attach_json(
            name="transaction-comment-notification-read-e2e",
            content={
                "transaction": persisted_transaction.__dict__,
                "comment": db_comment.__dict__ if db_comment else None,
                "unread_before": unread_before.__dict__ if unread_before else None,
                "unread_after": unread_after.__dict__ if unread_after else None,
                "persisted_notification": persisted_notification.__dict__ if persisted_notification else None,
            },
        )

        assert_that(unread_after, "Expected no unread API notification after UI dismissal").is_none()
        assert_that(
            persisted_notification,
            "Expected the same notification record to remain available in lowdb after dismissal",
        ).is_not_none()

        with soft_assertions():
            assert_that(unread_before.user_id, "Unread API notification should belong to the receiver").is_equal_to(
                seeded_send_money_contact["id"]
            )
            assert_that(
                unread_before.transaction_id,
                "Unread API notification should belong to the commented transaction",
            ).is_equal_to(persisted_transaction.id)
            assert_that(unread_before.status, "Unread API notification should normalize as a comment event").is_equal_to(
                "comment"
            )
            assert_that(
                unread_before.is_read,
                "Unread API notification should be unread before dismissal",
            ).is_false()
            assert_that(
                persisted_notification.id,
                "Persisted notification should be the same record that was dismissed in the UI",
            ).is_equal_to(unread_before.id)
            assert_that(
                persisted_notification.transaction_id,
                "Persisted notification should remain linked to the commented transaction",
            ).is_equal_to(persisted_transaction.id)
            assert_that(
                persisted_notification.status,
                "Persisted notification should continue to normalize as a comment event",
            ).is_equal_to("comment")
            assert_that(
                persisted_notification.is_read,
                "Persisted notification should be marked read after UI dismissal",
            ).is_true()
