# Coding Standards

## Purpose

These standards define the engineering expectations for the new standalone automation framework.

They are intended to keep the codebase:

- readable
- consistent
- maintainable
- scalable without over-engineering

## A. General Principles

- prefer readability over cleverness
- prefer consistency over flexibility
- build small, reusable components
- avoid duplication when the duplication is real and recurring
- prefer explicit behavior over implicit behavior
- choose simple designs before abstract designs

## B. Project Structure Rules

- UI, API, DB, fixtures, and tests must remain clearly separated
- each layer must own one responsibility area
- no cross-layer leakage is allowed
- shared technical concerns belong in the framework layer
- business workflows should not be hidden in utility modules

Allowed examples:

- tests use page objects, services, repositories, and fixtures
- fixtures use framework, UI, API, DB, and testdata layers

Disallowed examples:

- page objects calling database queries
- tests sending raw HTTP requests
- repositories importing page objects

## C. Naming Conventions

- classes use `PascalCase`
- functions and methods use `snake_case`
- variables use meaningful, explicit names
- test files use `test_*.py`
- test functions use `test_*`
- constants use `UPPER_SNAKE_CASE`

Guidance:

- avoid vague names such as `data`, `obj`, `helper`, `manager` unless the role is truly generic
- avoid abbreviations unless they are standard and widely understood

Good examples:

- `LoginPage`
- `create_transaction_payload`
- `transactions_repository`
- `authenticated_api_client`

Weak examples:

- `TxnMgr`
- `do_stuff`
- `tmp_data`

## D. Page Object Model Rules

- page objects handle UI interactions only
- page objects should model one screen or one reusable UI area
- page objects may include UI-specific validations when necessary
- page objects must not contain business logic
- page objects must not execute raw API calls
- page objects must not query the database
- locators should be centralized and reusable within the page or component

Good example:

```python
class LoginPage(BasePage):
    def login(self, email: str, password: str) -> None:
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.submit_button.click()
```

Bad example:

```python
class LoginPage(BasePage):
    def login_and_verify_db_user(self, email, password, db_client):
        ...
```

## E. API Client Rules

- all HTTP logic must be encapsulated in API clients
- tests must not use raw `requests` directly
- endpoint methods should be reusable and named by behavior
- request execution and response validation should be separated where practical
- services may orchestrate multiple client calls

Good pattern:

- client sends request
- schema validates response shape
- service exposes domain action

## F. DB Layer Rules

- tests must not contain raw SQL
- SQL must live in the DB layer
- repositories should expose meaningful methods, not generic query dumping
- return structured data, not ambiguous tuples where avoidable
- DB validation must support the test, not replace business services

Good example:

- `transactions_repository.get_transaction_by_id(transaction_id)`

Weak example:

- `db.execute("select * from transactions where id = ...")` inside a test

## G. Test Design Rules

- tests must be independent and deterministic
- each test must have clear setup and teardown via fixtures
- avoid shared mutable state
- prefer data-driven tests when the behavior is structurally the same
- tests should read like user or system scenarios
- tests should validate one coherent behavior

Good example:

- `test_user_can_create_transaction`

Weak example:

- one test validating unrelated login, profile, and transaction concerns together

## H. Fixture Rules

- fixtures must be explicit and composable
- avoid hidden dependencies
- teardown must always be reliable
- use function scope by default unless a broader scope is justified
- the fixture that creates a resource owns cleanup for that resource
- fixture names must reveal the prepared state

Good examples:

- `authenticated_page`
- `transactions_service`
- `new_user_payload`

Weak examples:

- `setup_env`
- `prepared_context`
- `default_state`

## I. Assertion Strategy

- assert business behavior, not implementation details
- keep assertions meaningful and descriptive
- prefer one coherent assertion theme per test
- avoid excessive assertions that make failure intent unclear
- compare structured data through typed models or focused helpers when useful

Good:

- assert the transaction appears in the UI and persists in the database

Weak:

- assert every internal field unless the test specifically targets those fields

## J. Error Handling and Logging

- logging must provide useful context for UI, API, and DB layers
- failure output should make debugging straightforward
- errors should include actionable context
- avoid swallowing exceptions silently
- sanitize secrets in logs and reports

Minimum useful context examples:

- UI: page name, action, locator intent
- API: method, endpoint, payload summary, response status
- DB: repository method, key parameters, result summary

## K. Comments And Docstrings

- prefer self-explanatory code first
- do not add docstrings or comments to obvious one-line methods just for coverage
- add a short docstring when a method has hidden behavior, environment assumptions, or non-obvious side effects
- add a short code comment before branching or mutation logic only when the intent would otherwise be hard to infer quickly
- keep docstrings practical and implementation-aware, not academic
- use comments to explain why, not to restate what the next line already says

Good examples:

- a fixture that resets backend state before and after the test
- a settings resolver that falls back through multiple runtime sources
- a mapper that normalizes inconsistent API payload shapes

Weak examples:

- docstrings on every trivial getter
- comments that just restate assignments
- large block comments describing code that should instead be simplified

## L. CI/CD Compatibility

- all tests must be runnable headless
- no local-machine assumptions are allowed
- configuration must come from environment variables or CI inputs
- secrets must not be hardcoded
- tests should be selectable by path, marker, or suite

## M. Performance and Maintainability

- avoid unnecessary abstraction
- avoid deep inheritance chains
- prefer composition where possible
- optimize for clarity before optimization for clever reuse
- only broaden fixture scope when the gain is real and the isolation cost is acceptable

## Review Checklist

Every new module or test should be reviewed against these questions:

- is the responsibility of this module clear
- does it belong in this layer
- is naming explicit and consistent
- is behavior visible rather than hidden
- is teardown owned by the creator
- are assertions focused on behavior
- is the abstraction justified
- is a docstring or short comment needed to explain non-obvious behavior

## Summary

The framework should look senior by being:

- clear
- disciplined
- modular
- practical

Not by being abstract for its own sake.
