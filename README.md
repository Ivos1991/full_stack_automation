# RWA Automation Framework

Standalone portfolio-ready automation framework for Cypress Real World App with aligned UI, API, and lowdb-backed data-store validation.

## Overview

This project demonstrates a layered pytest framework for validating the same business flow across:

- Playwright UI interactions
- API services built on `requests`
- backend multi-step integration scenarios
- lowdb-backed repository validation
- Allure reporting evidence

The framework is intentionally modular:

- `src/ui/` models screens and browser interactions only
- `src/api/` encapsulates HTTP clients, services, and response models
- `src/db/` encapsulates data-store access through repositories
- `src/framework/` contains cross-cutting technical concerns such as config, runtime clients, logging, and reporting helpers
- `src/fixtures/` keeps setup and teardown explicit
- `tests/` contains UI, API, DB, integration, and E2E layers

## Architecture

The test layers are intentionally distinct:

- `tests/ui/`
  Validates browser-visible behavior through page objects only.
- `tests/api/`
  Validates endpoint-facing service behavior without UI.
- `tests/db/`
  Validates persisted lowdb state through repositories only.
- `tests/integration/`
  Validates multi-step backend business behavior across several API calls plus persisted state.
- `tests/e2e/`
  Validates full vertical slices across UI, API, and DB together.

This keeps the suite readable and prevents the same test intent from being duplicated across layers.

## User Data Strategy

Two test-data paths are supported:

- Dynamic users: created per test for isolated auth and basic flow coverage
- Seeded users: fixed business users from the Real World App seed data for realistic cross-entity scenarios such as send money, transaction detail, and transaction comments

The paths stay separate so business-data tests do not leak assumptions into dynamic-user coverage.

## Setup

### 1. Clone this framework

```bash
git clone <your-framework-repo-url>
cd rwa-automation-framework
```

### 2. Clone Cypress Real World App separately

Clone the app outside this repository, for example:

```bash
git clone https://github.com/cypress-io/cypress-realworld-app.git ../cypress-realworld-app
```

### 3. Configure environment

Copy `.env.example` to `.env` and set:

- `RWA_ROOT_PATH` to your local Real World App checkout
- `BASE_URL` to the frontend URL from `yarn dev`
- `API_BASE_URL` if you want to force the backend URL explicitly
- `RWA_DATA_FILE` only if you want to override the default lowdb path derived from `RWA_ROOT_PATH`

### 4. Start the app

From your Real World App checkout:

```bash
yarn install
yarn dev
```

### 5. Install Python dependencies

Using Poetry:

```bash
poetry install
poetry run playwright install chromium
```

Or with your own virtual environment if preferred.

## Running Tests

Run the full framework suite:

```bash
poetry run pytest -q
```

Run the backend integration layer:

```bash
poetry run pytest tests/integration -q
```

Run a focused vertical slice:

```bash
poetry run pytest tests/e2e/test_seeded_send_money_vertical_slice.py -q
poetry run pytest tests/e2e/test_transaction_detail_vertical_slice.py -q
poetry run pytest tests/e2e/test_transaction_comment_vertical_slice.py -q
```

Run by layer:

```bash
poetry run pytest tests/ui -q
poetry run pytest tests/api -q
poetry run pytest tests/db -q
poetry run pytest tests/integration -q
poetry run pytest tests/e2e -q
```

Run by marker:

```bash
poetry run pytest -m api -q
poetry run pytest -m integration -q
poetry run pytest -m "e2e or ui" -q
```

Current markers:

- `ui`
- `api`
- `db`
- `integration`
- `e2e`

## Reporting

Allure artifacts are written to `artifacts/` by default. The framework keeps reporting concerns in the framework layer instead of pushing them into services or repositories:

- `src/framework/reporting/allure_helpers.py`
  low-level Allure attachment functions
- `src/framework/reporting/evidence_helpers.py`
  reusable test-layer helpers for structured JSON snapshots and UI screenshot-plus-state evidence

Example:

```bash
poetry run pytest tests/e2e/test_transaction_comment_vertical_slice.py --alluredir artifacts/allure-results
allure serve artifacts/allure-results
```

## CI/CD

The public repo ships with three GitHub Actions workflows:

- `pr-validation.yml`
  Runs the full standalone suite on pull requests and pushes to `main`.
- `nightly-regression.yml`
  Runs the same validated suite on a daily schedule.
- `manual-run.yml`
  Lets you run a selected pytest target and optional custom marker expression from the GitHub Actions UI.

The workflows provision Cypress Real World App as an external dependency inside the runner, write explicit framework environment values, start the app, detect the live backend port, run pytest with Allure output, and upload `artifacts/` plus RWA startup logs.

Example manual-run inputs:

- `test_target = tests`
- `marker_expression = api`
- `pytest_args = -q -rs -p no:cacheprovider`

Or for a custom slice:

- `test_target = tests`
- `marker_expression = e2e and not flaky`
- `pytest_args = -q -rs -p no:cacheprovider`

You can also run the new backend integration layer remotely with:

- `test_target = tests/integration`
- `marker_expression = integration`
- `pytest_args = -q -rs -p no:cacheprovider`

## Current Coverage

The repository currently includes validated slices for:

- dynamic-user authentication
- seeded home feed
- seeded send money
- transaction detail
- transaction comments
- comment notification creation
- comment notification read-state transition
- backend multi-step integration coverage for send money and notification read-state

## Notes

- The framework does not vendor Cypress Real World App.
- The Real World App remains an external local dependency configured through environment variables.
- Some UI execution environments on Windows may require local permission settings that allow Playwright to create browser subprocess pipes.
