# Seeded Business Data Slice

Date: 2026-03-22

## Chosen Flow

This first seeded business-data slice uses:

- seeded user: `Heath93`
- authenticated landing route: `/`
- landing feed endpoint: `GET /transactions/public`

This user was chosen because the RWA seed data provides:

- an existing bank account
- notifications
- a populated transaction feed
- enough related records for meaningful UI, API, and data-layer assertions

## Expected Authenticated Landing Behavior

For the seeded business user:

- login redirects to `/`
- the transaction feed is visible
- the sidenav is visible
- the onboarding dialog is not shown

That differs from the dynamic-user auth slice, where first login for a newly created user lands in onboarding.

## Supporting API And Data Entities

Primary API endpoint:

- `GET /transactions/public`

Primary lowdb-backed entities used in this slice:

- `users`
- `contacts`
- `transactions`
- `likes`
- `comments`
- `notifications`
- `bankaccounts`

## Fixture Separation

Dynamic-user path:

- use for auth/setup/isolation flows
- creates users per test

Seeded-user path:

- use for business-data scenarios that depend on existing seed records
- resets the backend to the seeded baseline before and after each test
- uses explicit seeded credentials fixtures

## Scope Of This Slice

This slice intentionally stays narrow:

- UI landing/feed visibility
- API public feed contract
- lowdb-backed feed repository result
- one UI + API + DB vertical slice

It does not yet expand into:

- transaction detail
- feed filters
- creating new transactions
- notifications workflows
