# Target Architecture

## Objective

The new framework is a standalone automation solution for Cypress Real World App using:

- Playwright + pytest for UI
- `requests` for API validation
- lowdb-backed repository validation for the real RWA implementation path
- Allure for reporting
- GitHub Actions for CI/CD

The architecture should be modular, layered, explicit, and easy to extend without introducing unnecessary abstraction.

## Design Principles

- separate UI, API, DB, fixtures, and tests clearly
- keep framework code generic and reusable
- prefer composition over inheritance unless the shared behavior is technical and stable
- use function-scoped isolation by default
- keep orchestration visible in tests and flows

## Proposed Folder Structure

```text
standalone-rwa-framework/
  docs/
  pyproject.toml
  pytest.ini
  .env.example
  .gitignore
  .github/
    workflows/
      pr-validation.yml
      nightly.yml
      manual-run.yml
  src/
    framework/
      config/
        settings.py
      logging/
        logger.py
      reporting/
        allure_helpers.py
        artifacts.py
      clients/
        api/
          base_api_client.py
        db/
          postgres_client.py
      models/
        common.py
      assertions/
        custom_assertions.py
      utils/
        paths.py
        time_utils.py
    ui/
      components/
        base_component.py
        nav_bar.py
        modal.py
      pages/
        base_page.py
        login_page.py
        dashboard_page.py
        transactions_page.py
      flows/
        auth_flow.py
        transaction_flow.py
    api/
      clients/
        auth_client.py
        users_client.py
        transactions_client.py
      services/
        auth_service.py
        users_service.py
        transactions_service.py
      schemas/
        auth_models.py
        user_models.py
        transaction_models.py
    db/
      queries/
        users_queries.py
        transactions_queries.py
      repositories/
        base_repository.py
        users_repository.py
        transactions_repository.py
    fixtures/
      hooks.py
      browser_fixtures.py
      auth_fixtures.py
      api_fixtures.py
      db_fixtures.py
      data_fixtures.py
    testdata/
      factories/
        user_factory.py
        transaction_factory.py
      builders/
        payload_builders.py
  tests/
    ui/
      test_login.py
      test_transactions.py
    api/
      test_auth_api.py
      test_users_api.py
    db/
      test_transaction_persistence.py
    e2e/
      test_user_can_create_transaction.py
```

## Layer Definitions

## Framework Layer

Purpose:

- host cross-cutting technical capabilities used by all other layers

Responsibilities:

- settings and environment loading
- logging
- Allure helpers
- generic API and DB clients
- shared models and assertions
- utility helpers
- explicit runtime resolution for external RWA dependency configuration

Rules:

- no application-specific business logic
- no direct test scenarios
- no UI page behavior

## UI Layer

Purpose:

- represent the browser-facing application surface

Sub-layers:

- `components/` for reusable widgets
- `pages/` for screen-level interaction models
- `flows/` for multi-page user journeys

Rules:

- page objects handle locators and UI interactions
- page objects may include UI-specific validations
- business workflows spanning multiple pages belong in flows
- page objects must not call the DB directly
- page objects must not send raw API requests

## API Layer

Purpose:

- provide structured access to application APIs

Sub-layers:

- `clients/` for endpoint-level request execution
- `services/` for domain-oriented operations
- `schemas/` for typed request/response models

Rules:

- tests do not call `requests` directly
- clients encapsulate HTTP details
- services encapsulate domain actions and response handling
- schemas keep API contracts explicit

## DB Layer

Purpose:

- validate backend persistence and data integrity through the current data-store implementation

Sub-layers:

- `queries/` for query ownership where applicable
- `repositories/` for structured data access

Rules:

- tests do not contain raw data-store access
- repositories return meaningful structured data
- DB layer is validation-focused, not an alternative business service layer
- when the real app uses lowdb, repository methods should encapsulate file-backed record access the same way a SQL repository would encapsulate queries

## Fixtures Layer

Purpose:

- provide composable runtime setup and teardown

Responsibilities:

- browser, context, and page lifecycle
- authentication state
- API client/session creation
- DB connection management
- test data setup factories
- pytest hooks for reporting

Rules:

- function scope by default
- each fixture owns cleanup for the resources it creates
- fixture dependencies must be explicit

## Tests Layer

Purpose:

- express behavior clearly by test type

Subdirectories:

- `tests/ui/` for UI behavior
- `tests/api/` for service/API behavior
- `tests/db/` for direct persistence validation
- `tests/e2e/` for cross-layer scenarios

Rules:

- tests should read as user or system scenarios
- test orchestration should remain visible
- e2e tests may combine UI, API, and DB, but lower-level tests should stay focused

## Test Data and Config

### Test Data

Use `src/testdata/` for:

- factories that create domain objects
- builders for request payloads
- reusable test inputs

This keeps synthetic data creation separate from tests and fixtures.

### Config

Use typed settings loaded from environment variables.

Examples:

- base URLs
- credentials
- database connection parameters
- Allure artifact toggles
- CI-specific runtime options

Keep config generic, small, and explicit.

## Documentation Expectations

- non-obvious runtime resolution, fixture orchestration, and payload normalization paths should use short docstrings
- comments should be rare and should clarify hidden intent or side effects
- simple page-object actions and obvious mappers should stay mostly self-documenting

## Layer Boundaries

Allowed dependencies:

- tests -> fixtures, ui, api, db, framework
- fixtures -> ui, api, db, framework, testdata
- ui -> framework
- api -> framework
- db -> framework
- testdata -> framework models if needed

Disallowed dependencies:

- ui -> db
- ui -> raw API transport
- api -> ui
- db -> ui
- framework -> application-specific page/service logic

## Composition vs Inheritance

### Use Inheritance For

- technical shared behavior with stable semantics
- examples:
  - `BasePage`
  - `BaseComponent`
  - `BaseApiClient`
  - `BaseRepository`

### Use Composition For

- business workflows
- page collaboration
- endpoint orchestration
- reusable helper behavior that varies by context

Examples:

- `AuthFlow` composes `LoginPage` and `DashboardPage`
- `TransactionsService` composes `TransactionsClient`
- `TransactionsRepository` composes `PostgresClient`

### Rule of Thumb

- if the relationship is "is a stable technical specialization", inheritance is acceptable
- if the relationship is "uses", "coordinates", or "depends on", use composition

## Anti-Overengineering Guidance

- do not introduce extra layers without a clear ownership reason
- do not add abstract interfaces for single implementations
- do not create deep inheritance chains
- do not split modules prematurely
- keep the first version small and internally consistent

## Summary

The target architecture should be a disciplined, lightweight framework with:

- a small generic core
- strict UI/API/DB separation
- explicit fixture ownership
- readable tests
- enough abstraction to scale, but not enough to obscure behavior
