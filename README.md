# RWA Automation Framework

Standalone portfolio-ready automation framework for Cypress Real World App with aligned UI, API, and lowdb-backed data-store validation.

## Overview

This project demonstrates a layered pytest framework for validating the same business flow across:

- Playwright UI interactions
- API services built on `requests`
- lowdb-backed repository validation
- Allure reporting evidence

The framework is intentionally modular:

- `src/ui/` models screens and browser interactions only
- `src/api/` encapsulates HTTP clients, services, and response models
- `src/db/` encapsulates data-store access through repositories
- `src/fixtures/` keeps setup and teardown explicit
- `tests/` contains UI, API, DB, and E2E vertical slices

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
poetry run pytest tests/e2e -q
```

## Reporting

Allure artifacts are written to `artifacts/` by default.

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

## Notes

- The framework does not vendor Cypress Real World App.
- The Real World App remains an external local dependency configured through environment variables.
- Some UI execution environments on Windows may require local permission settings that allow Playwright to create browser subprocess pipes.
