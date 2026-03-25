# Reporting and CI

## Objective

The new standalone framework should provide production-like observability without inheriting unnecessary operational complexity.

The reporting and CI design should be:

- simple
- reliable
- easy to troubleshoot
- suitable for local and CI execution

## Allure Reporting Integration

Allure should be the primary reporting layer for test execution results and debugging artifacts.

## Reporting Goals

- provide readable execution summaries
- capture enough evidence to debug failures quickly
- support UI, API, and DB testing in a consistent way

## Allure Integration Rules

- enable Allure for all test types
- attach artifacts from centralized hooks or helpers
- keep attachment naming consistent
- collect evidence automatically on failure
- avoid excessive noise on passing tests unless the artifact is lightweight and useful

## Artifacts to Collect

## Screenshots

Collect:

- failure screenshots for UI tests

Optional:

- explicit screenshots at meaningful checkpoints when debugging complex flows

Guidance:

- capture at page level
- use clear names such as `failure-home-page.png`

## Traces

Collect:

- Playwright trace on UI test failure

Why:

- preserves navigation and interaction history
- supports high-quality root cause analysis

## Videos

Collect:

- Playwright video for UI test failures

Guidance:

- enable at context level
- retain failures by default
- keep successful run retention optional to control storage cost

## Logs

Collect:

- framework logs
- UI action logs when useful
- API request lifecycle logs
- DB validation logs

Rules:

- logs must be readable and structured
- include test name and key identifiers
- avoid noisy debug logging by default

## API Requests and Responses

Collect:

- HTTP method
- endpoint
- request payload
- response status
- relevant response body

Rules:

- sanitize secrets and tokens
- attach failed request/response evidence to Allure
- optionally attach successful calls only for important scenario checkpoints

## DB Validation Evidence

Collect:

- query intent or repository method name
- relevant input parameters
- summarized validation result
- small, meaningful result samples

Rules:

- do not dump large raw result sets unless necessary
- keep evidence focused on the assertion under test

## Recommended Artifact Strategy by Test Type

### UI Tests

- screenshots on failure
- trace on failure
- video on failure
- browser console logs when useful

### API Tests

- request payload
- response metadata
- response body summary

### DB Tests

- repository method used
- validation evidence
- structured result summary

### E2E Tests

- combine UI, API, and DB evidence for the same scenario
- attach only the artifacts needed to explain behavior clearly

## GitHub Actions Pipeline

The CI/CD design should stay intentionally small.

## Workflow Set

### PR Validation Workflow

Purpose:

- protect the main branch with fast, reliable validation

Should include:

- dependency installation
- linting and formatting checks
- unit or framework sanity checks if present
- selected smoke tests
- Allure result artifact upload

Characteristics:

- fast feedback
- headless execution
- minimal external dependency surface

### Scheduled/Nightly Workflow

Purpose:

- run broader regression coverage on a schedule

Should include:

- UI regression subset
- API regression subset
- optional DB validation suite
- artifact upload
- optional Allure history support if desired later

Characteristics:

- slower but more comprehensive
- suitable for discovering drift and integration issues

### Manual Trigger Workflow

Purpose:

- allow targeted execution without changing workflow files

Suggested inputs:

- test type
- marker or path
- browser
- environment name

Characteristics:

- useful for debugging and demo execution
- should remain simple and predictable

## CI Design Rules

- run tests headless in CI
- keep configuration environment-driven
- avoid environment-specific logic inside tests
- upload artifacts even on failure
- keep workflow count low until complexity is justified

## Implemented Workflow Responsibilities

### `pr-validation.yml`

- run on pull requests and pushes to `main`
- call the reusable suite runner
- provision the external Cypress Real World App checkout
- start the app, detect the active backend port, run the full standalone suite
- publish `artifacts/` and RWA startup logs

### `nightly-regression.yml`

- run on a daily schedule and on manual dispatch
- execute the validated standalone suite as the nightly regression signal
- publish the same artifacts and logs for troubleshooting

### `manual-run.yml`

- accept runtime inputs
- run selected tests
- support custom pytest marker expressions without hardcoded workflow markers
- reuse the same environment provisioning path as PR and nightly workflows
- publish the same artifacts as the other workflows

### `run-standalone-suite.yml`

- reusable workflow shared by all public entrypoint workflows
- sets explicit framework environment variables
- checks out Cypress Real World App into an external path inside the runner workspace
- installs Python, Poetry, Node.js, Playwright, and RWA dependencies
- starts RWA, waits for frontend readiness, detects the backend port, and exports `API_BASE_URL`
- supports optional marker-based test selection through a workflow input
- runs pytest with Allure output enabled
- uploads `artifacts/` and `rwa-logs/` even when the run fails

## Reliability Guidance

- use deterministic test selection
- keep secrets in GitHub Actions secrets
- fail fast on infrastructure setup problems
- separate flaky experimental tests from the main validation path
- do not overload the PR pipeline with full regression scope

## Production-Like But Simple

The reference repository demonstrates operational maturity, but the new framework should begin with:

- three workflows, not dozens
- one reporting strategy, not many parallel output paths
- direct artifact publishing, not complex post-processing
- explicit environment configuration, not environment routing logic spread across workflows

## Summary

The new reporting and CI model should give strong evidence and stable execution without reproducing the operational weight of the reference repository.

The target state is:

- Allure as the reporting center
- focused artifact collection
- one reusable suite runner
- one PR workflow
- one nightly workflow
- one manual workflow

This is enough to look senior, practical, and maintainable from the start.
