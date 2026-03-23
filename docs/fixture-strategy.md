# Fixture Strategy

## Objective

Fixtures in the new framework must be:

- explicit
- composable
- deterministic
- isolated by default
- responsible for their own teardown

The fixture model should support UI, API, and DB testing without hiding business behavior behind complex setup chains.

## Scope Strategy

## Function Scope

Use function scope by default for anything that can affect test isolation.

Examples:

- browser context
- page
- authenticated user state
- API client with test-specific auth
- DB connection used for test validation
- created test data

Why:

- strongest isolation
- simplest failure analysis
- lowest risk of shared mutable state

## Module Scope

Use module scope only when reuse is safe and clearly beneficial.

Examples:

- static read-only test data
- expensive but immutable setup helpers
- a pre-authenticated API token for read-only API tests if the token is stable and non-mutating

Use only when:

- the resource is immutable or treated as immutable
- cleanup does not depend on per-test behavior
- test independence is not weakened

## Session Scope

Use session scope only for stable infrastructure resources.

Examples:

- settings
- Playwright browser instance
- DB engine or connection pool
- global reporting hooks
- reusable logger initialization

Do not use session scope for:

- mutable business entities
- authenticated browser state that can be modified by tests
- test-created users, accounts, or transactions

## Setup and Teardown Ownership Rules

### Rule 1: Creator Owns Cleanup

- the fixture that creates a resource is responsible for cleaning it up
- do not rely on another fixture to silently clean what it did not create

### Rule 2: Cleanup Must Be Reliable

- teardown must run even after test failure
- prefer `yield` fixtures over manual cleanup patterns

### Rule 3: Cleanup Must Be Targeted

- remove only the resources created for that test
- avoid broad cleanup that can affect unrelated tests

### Rule 4: Setup Prepares, Tests Validate

- fixtures prepare state
- tests assert business behavior
- fixtures should not hide key scenario assertions

## Browser, Context, and Page Fixtures

## Browser Fixture

Scope:

- session

Responsibility:

- create the Playwright browser instance once
- close it at session end

Example:

```python
@pytest.fixture(scope="session")
def browser(playwright, settings):
    browser = playwright.chromium.launch(headless=settings.headless)
    yield browser
    browser.close()
```

## Browser Context Fixture

Scope:

- function

Responsibility:

- create an isolated browser context per test
- enable tracing, video, and artifact collection
- close the context during teardown

Why:

- avoids cookie/state leakage
- keeps failures easier to reproduce

## Page Fixture

Scope:

- function

Responsibility:

- open a new page from the test context
- set common timeouts if needed

Rule:

- page fixtures should not auto-login unless the fixture name explicitly signals it

## Auth and Session Handling

## UI Authentication Fixture

Provide an explicit authenticated-page fixture for tests that need logged-in UI state.

Examples:

- `authenticated_page`
- `authenticated_dashboard_page`

Rules:

- login action should be visible through fixture naming
- use API-backed auth setup when it improves speed and determinism
- avoid hidden login in generic `page` fixtures

## API Authentication Fixture

Provide explicit API auth fixtures such as:

- `api_client`
- `authenticated_api_client`
- `admin_api_client`

Rules:

- auth tokens should be created or injected explicitly
- token scope should match the test need
- avoid global mutable auth state

## Session Reuse Guidance

Reuse authentication only when:

- it is read-only
- it cannot be modified by tests
- the performance benefit is meaningful

Otherwise prefer per-test auth setup.

## API Client Fixtures

API fixtures should expose prepared domain clients or services rather than raw `requests` sessions.

Good examples:

- `auth_client`
- `users_service`
- `transactions_service`

Avoid:

- fixtures that return unconfigured raw HTTP tools
- fixtures that mix API access with DB validation or UI steps

Example:

```python
@pytest.fixture
def transactions_service(authenticated_api_client):
    return TransactionsService(authenticated_api_client)
```

## DB Connection Fixtures

## DB Engine or Pool Fixture

Scope:

- session

Responsibility:

- initialize the PostgreSQL connection factory or pool

## DB Connection Fixture

Scope:

- function

Responsibility:

- provide a connection or client for one test
- close or release it after use

## Repository Fixtures

Expose repository objects for tests that need DB validation.

Examples:

- `users_repository`
- `transactions_repository`

Rules:

- repositories should encapsulate SQL access
- tests should never write raw SQL

## Test Data Factories

Use factory fixtures for test data generation instead of large numbers of nearly identical fixtures.

Examples:

- `user_factory`
- `transaction_factory`
- `payload_builder`

These factories should:

- create valid default data
- allow clear overrides
- return predictable structured objects

Example:

```python
def test_create_transaction(transactions_service, transaction_factory):
    payload = transaction_factory.build(amount=125.00)
```

## Composability Rules

- fixtures should declare everything they need in their signature
- avoid relying on indirect, hidden fixture side effects
- prefer smaller fixtures that can be combined intentionally
- use descriptive names that reveal the prepared state

Good:

- `authenticated_page`
- `new_user_payload`
- `transactions_repository`

Weak:

- `setup_data`
- `env_context`
- `prepared_state`

## Determinism Rules

- each test must be runnable in isolation
- fixture-created data must be unique per test unless explicitly read-only
- avoid dependence on previous test execution
- avoid dependence on execution order
- do not share mutable entity objects across tests

## Hidden Side Effects to Avoid

- automatic login in a generic page fixture
- automatic creation of backend data in unrelated fixtures
- shared mutable users or sessions reused across tests
- teardown performed by a distant fixture the test does not reference
- environment mutations performed silently during setup

## Recommended Default Fixture Set

- `settings`
- `browser`
- `context`
- `page`
- `authenticated_page`
- `api_client`
- `authenticated_api_client`
- `postgres_client`
- `users_repository`
- `transactions_repository`
- `user_factory`
- `transaction_factory`

## Summary

The fixture strategy should optimize for:

- explicitness over convenience
- isolation over premature performance tuning
- lifecycle ownership over shared cleanup
- composition over hidden orchestration

If a test cannot be understood from its fixture list and body, the fixture design is too implicit.
