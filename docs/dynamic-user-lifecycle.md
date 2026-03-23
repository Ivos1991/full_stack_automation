# Dynamic User Lifecycle

Date: 2026-03-22

## Objective

The auth slice now supports dynamic per-test users so login tests do not depend on fixed seeded credentials by default.

The implementation keeps the existing standalone architecture intact:

- test data generation stays in `src/testdata/`
- API setup stays in the API layer
- lowdb persistence helpers stay in the DB layer
- setup and teardown ownership stays in fixtures

## Real RWA Creation Path

For live auth tests, user creation should be done through both layers, with different responsibilities:

- API layer for live user creation
  - reason: `POST /users` is the real application entry point for sign-up/user creation
  - this keeps auth setup aligned with actual app behavior
- DB layer for lowdb persistence support
  - reason: the framework still needs repository-level create/delete support for direct data-layer validation and isolated file-based tests

In practice:

- live auth fixtures create users through `POST /users`
- repository methods exist for lowdb-backed create/delete operations
- live teardown resets through `POST /testData/seed`

## Required User Fields

The backend validator accepts partial user payloads, but the backend `createUser()` implementation uses the following user shape for a complete record:

- `firstName`
- `lastName`
- `username`
- `password`
- `email`
- `phoneNumber`
- `balance`
- `avatar`
- `defaultPrivacyLevel`

The dynamic user factory therefore generates the full record shape instead of relying on partial sign-up payloads.

## Fixture Lifecycle

Function-scoped dynamic auth setup follows this lifecycle:

1. `generated_user_data`
   - builds UUID-based readable user data
   - owned by the test-data factory layer
2. `created_user`
   - resets the backend to the seeded baseline through `POST /testData/seed`
   - creates a new user through the real `POST /users` API
   - verifies the created user exists in lowdb through the repository
   - yields the created user to the test
   - teardown resets the backend again through `POST /testData/seed`
3. `auth_credentials`
   - exposes the created username and generated password explicitly for login flows

This keeps fixture ownership explicit and avoids hidden setup.

## Why Teardown Uses `testData/seed`

The RWA backend uses lowdb inside a running Node process.

That means there are two states to consider during live tests:

- the `database.json` file on disk
- the backend process's in-memory lowdb state

Direct out-of-process file mutation from Python can make those two states diverge.

Risk:

- deleting a user only in the file can leave the running backend with stale in-memory data
- later backend writes can reintroduce deleted test users or overwrite cleanup changes

Because of that, the live fixture teardown does not rely on direct file deletion alone.

Instead it resets through the backend-supported `POST /testData/seed` route, which restores:

- the backend in-memory state
- the lowdb file state

Repository delete methods still exist, but they are intended for:

- isolated lowdb file tests
- direct repository validation outside the running backend process

## Related Data Cleanup Scope

The repository cleanup logic removes user-linked records from:

- `users`
- `contacts`
- `bankaccounts`
- `transactions`
- `likes`
- `comments`
- `notifications`
- `banktransfers`

For live auth fixtures, the backend seed reset is the authoritative cleanup mechanism.

## Dynamic Users vs Seeded Users

Use dynamic users when:

- testing sign-up/login/authentication setup
- validating current-user/session flows
- the scenario does not require existing transaction history, contacts, or bank accounts
- deterministic per-test isolation is more important than rich pre-seeded business data

Use seeded users when:

- testing transaction feeds
- testing flows that depend on existing contacts, bank accounts, notifications, or transaction history
- the scenario needs realistic pre-existing business relationships already present in the RWA seed

## Current Limitation

A newly created dynamic user does not have seeded business data.

For the current auth slice, that is expected and valid:

- first login for a new dynamic user lands in the authenticated onboarding state

Future transaction/feed/business-flow slices should keep using seeded users unless they also create the additional required domain data explicitly.
