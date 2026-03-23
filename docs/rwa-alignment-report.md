# RWA Alignment Report

Date: 2026-03-22

## Scope

This report aligns the current standalone framework with the real Cypress Real World App implementation using:

- local runtime at `http://localhost:3000/`
- backend runtime at `http://localhost:3001/`
- Cypress Real World App source under `cypress-realworld-app/`

The goal was to correct the existing minimal sign-in/auth vertical slice without broadening coverage.

## Confirmed Routes

Frontend routes confirmed from source and runtime:

- unauthenticated sign-in route: `/signin`
- unauthenticated sign-up route: `/signup`
- authenticated landing route after login: `/`
- authenticated transaction feed variants:
  - `/`
  - `/public`
  - `/contacts`
  - `/personal`
- additional authenticated routes present but not used in the current slice:
  - `/user/settings`
  - `/notifications`
  - `/bankaccounts`
  - `/transaction/new`
  - `/transaction/:transactionId`

Observed runtime behavior:

- visiting `http://localhost:3000/` while unauthenticated renders the sign-in page
- successful login redirects to `http://localhost:3000/`

## Confirmed Selectors

Sign-in page selectors confirmed from source and runtime:

- username field wrapper: `[data-test='signin-username']`
- actual username input: `[data-test='signin-username'] input`
- password field wrapper: `[data-test='signin-password']`
- actual password input: `[data-test='signin-password'] input`
- remember-me control: `[data-test='signin-remember-me']`
- submit button: `[data-test='signin-submit']`
- sign-up link: `[data-test='signup']`
- error alert: `[data-test='signin-error']`

Authenticated landing page selectors confirmed from runtime and source:

- side navigation container: `[data-test='sidenav']`
- home navigation link: `[data-test='sidenav-home']`
- username display: `[data-test='sidenav-username']`
- balance display: `[data-test='sidenav-user-balance']`
- top notification count: `[data-test='nav-top-notifications-count']`
- transaction feed container: `[data-test='transaction-list']`
- transaction feed tabs:
  - `[data-test='nav-public-tab']`
  - `[data-test='nav-contacts-tab']`
  - `[data-test='nav-personal-tab']`

## Confirmed API Endpoints

Auth and user endpoints confirmed from backend source and runtime:

- `POST /login`
  - local session auth via Passport local strategy
  - request body uses `username`, `password`, optional `remember`
  - success response shape: `{ "user": { ...user fields... } }`
- `POST /logout`
  - clears `connect.sid`
- `GET /checkAuth`
  - returns `401 {"error":"User is unauthorized"}` when unauthenticated
  - returns `200 {"user": {...}}` when authenticated
- `POST /users`
  - sign-up endpoint
- `GET /users/:userId`
  - authenticated
- `GET /users/profile/:username`
  - public profile subset

Health/readiness findings:

- no dedicated `/health` or `/ready` route is implemented
- backend root `GET /` responds with plain text: `Cypress Realworld App - backend`

Proxying confirmed from frontend source:

- frontend proxies `/login`, `/callback`, `/logout`, `/checkAuth`, and `/graphql` to the backend

## Confirmed Schema And Data Structures For The First Vertical Slice

The real app does not use PostgreSQL for this implementation path. It uses `lowdb` with JSON files under `cypress-realworld-app/data/`.

Primary backing file:

- `cypress-realworld-app/data/database.json`

Seed source:

- `cypress-realworld-app/data/database-seed.json`

Relevant entities for the current auth slice:

- `users`
  - fields confirmed:
    - `id`
    - `uuid`
    - `firstName`
    - `lastName`
    - `username`
    - `password`
    - `email`
    - `phoneNumber`
    - `balance`
    - `avatar`
    - `defaultPrivacyLevel`
    - `createdAt`
    - `modifiedAt`
- `bankaccounts`
  - relevant because onboarding is conditional on whether a user has bank accounts
- `transactions`
  - relevant because the authenticated landing page is the transaction feed
- `notifications`
  - relevant because the top navigation renders a notifications badge after login

Known valid default credentials from source/tests/runtime:

- username: `Heath93`
- password: `s3cret`

## Incorrect Assumptions In The Previous Scaffold

- the DB layer assumed a live PostgreSQL backend with SQL queries against a `users` table
- the DB field names assumed snake_case such as `first_name` and `last_name`
- the current-user API mapping assumed top-level fields from `/checkAuth`
- the default vertical-slice username assumed `johndoe`
- the UI page object assumed `[data-test='signin-username']` and `[data-test='signin-password']` were directly fillable inputs
- the authenticated home assertion only checked side navigation and did not align to the real transaction-feed landing page
- the config defaults used `127.0.0.1` instead of the app's actual `localhost` runtime shape verified in source and execution

## Corrections Applied

- changed default framework URLs to `http://localhost:3000` and `http://localhost:3001`
- updated the sign-in page object to fill nested inputs under the sign-in field wrappers
- updated the home page assertion to require the real authenticated transaction feed
- updated auth credentials to support the optional `remember` flag
- corrected `/checkAuth` DTO mapping to read nested `user` payloads
- replaced the vertical-slice DB assumption with a file-backed lowdb client reading `cypress-realworld-app/data/database.json`
- corrected the user repository lookup to match the real `users` entity and `username` field
- corrected default vertical-slice credentials to `Heath93 / s3cret`

## Runtime Verification

Runtime verification was performed with a temporary Playwright inspection script against `http://localhost:3000/`, then the temporary script was removed.

Confirmed at runtime:

- unauthenticated root renders the sign-in screen
- sign-in fields and submit control are present and visible
- sign-in field `data-test` attributes are on wrapper elements, with nested `<input>` controls
- successful sign-in redirects to `/`
- authenticated landing page shows:
  - side navigation
  - home nav item
  - username and balance
  - transaction feed
- onboarding dialog was not shown for the seeded `Heath93` user

## Unresolved Items

- alternate auth provider flows (`Auth0`, `Okta`, `Cognito`, `Google`) were not aligned in the Python framework yet
- the framework does not yet integrate RWA `POST /testData/seed` into fixture lifecycle
- the target architecture documents still mention PostgreSQL as the intended generic DB validation layer, while the real RWA implementation for this app instance is lowdb-backed JSON
- this alignment only covers the current minimal auth/sign-in slice; downstream business flows still need source-driven alignment before expansion

## Exact Source Files Used To Verify Findings

Frontend source:

- `cypress-realworld-app/src/containers/App.tsx`
- `cypress-realworld-app/src/containers/PrivateRoutesContainer.tsx`
- `cypress-realworld-app/src/containers/TransactionsContainer.tsx`
- `cypress-realworld-app/src/components/SignInForm.tsx`
- `cypress-realworld-app/src/components/NavDrawer.tsx`
- `cypress-realworld-app/src/containers/UserOnboardingContainer.tsx`
- `cypress-realworld-app/src/machines/authMachine.ts`
- `cypress-realworld-app/src/setupProxy.js`

Backend source:

- `cypress-realworld-app/backend/app.ts`
- `cypress-realworld-app/backend/auth.ts`
- `cypress-realworld-app/backend/user-routes.ts`
- `cypress-realworld-app/backend/helpers.ts`
- `cypress-realworld-app/backend/testdata-routes.ts`
- `cypress-realworld-app/backend/database.ts`

Model and data files:

- `cypress-realworld-app/src/models/user.ts`
- `cypress-realworld-app/src/models/db-schema.ts`
- `cypress-realworld-app/data/database.json`
- `cypress-realworld-app/data/database-seed.json`

Cypress project files used as additional verification:

- `cypress-realworld-app/cypress/support/commands.ts`
- `cypress-realworld-app/cypress/tests/ui/auth.spec.ts`
