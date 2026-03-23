## Verified Notification Read-State Behavior

Date verified: 2026-03-23

This note captures the live Cypress Real World App behavior for consuming a transaction-comment notification.

### Confirmed behavior

- Notification read state exists as `isRead`.
- The unread notification feed is exposed through `GET /notifications`.
- The read-state transition uses `PATCH /notifications/:notificationId` with `{ "isRead": true }`.
- The patch response returns `204 No Content`.
- Once a notification is marked read, it no longer appears in the unread `GET /notifications` response.
- The lowdb `notifications` record remains in place and persists `isRead: true` on the same record id.

### Reliable UI surface

- The app exposes the unread notifications page at `/notifications`.
- Each notification item renders a dismiss control with `data-test="notification-mark-read-<id>"`.
- Clicking the dismiss control triggers the same `PATCH /notifications/:notificationId` transition used by the app state machine.

### Scope used in this framework slice

- The framework continues to use the receiver-side unread comment notification as the source of truth.
- The slice verifies:
  - unread notification exists before transition
  - UI or API triggers the real read-state update
  - unread API feed no longer returns that notification
  - lowdb persists `isRead: true` on the same notification record
