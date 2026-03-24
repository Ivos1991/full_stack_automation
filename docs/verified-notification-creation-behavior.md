## Verified Notification Creation Behavior

Date verified: 2026-03-23

This note captures the live Cypress Real World App behavior that was verified for the existing transaction-comment notification slice.

### Confirmed behavior

- `POST /comments/:transactionId` creates the comment and also creates notification records as a side effect.
- `GET /notifications` returns unread notifications only.
- A comment notification is unread immediately after creation (`isRead: false`).
- The receiver-side unread comment notification exists for the seeded send-money flow and is returned through the API and persisted in lowdb.
- The API response shape for a comment notification includes `id`, `userId`, `transactionId`, `commentId`, `isRead`, `createdAt`, `modifiedAt`, and `userFullName`.
- The lowdb notification record shape for a comment notification includes `id`, `uuid`, `userId`, `transactionId`, `commentId`, `isRead`, `createdAt`, and `modifiedAt`.

### Corrected assumptions

- Raw comment notifications do not include `status: "comment"`. The framework normalizes comment notifications as `status="comment"` by inferring the type from `commentId`.
- The live backend creates comment notifications for both transaction participants in the two-party flow, not only for the receiver. The current framework slice remains valid because it intentionally verifies the receiver-side unread notification.

### Source alignment

- Backend creation path: `backend/comment-routes.ts` -> `createComments()` in `backend/database.ts`
- Backend notification feed: `backend/notification-routes.ts` -> `getUnreadNotificationsByUserId()`
- Frontend UI wording: `src/components/NotificationListItem.tsx`
- Upstream scenario coverage: `cypress/tests/ui/notifications.spec.ts`
