# 004 Bill Pay Log

Date: 2026-02-13

## Artifact Links

- Spec: `specs/001-bill-pay/spec.md`
- Plan: `specs/001-bill-pay/plan.md`
- Tasks: `specs/001-bill-pay/tasks.md`
- Contracts: `specs/001-bill-pay/contracts/bill-pay.yaml`

## Watcher Evidence

- Command run: `npm run dev:css`
- Result: command started in terminal during implementation session.

## HTMX Target/Swap Map

- Bill Pay month switch:
  - Endpoint: `GET /accounts/bill-pay/table-body/?month=YYYY-MM`
  - `hx-target`: `#bill-pay-table-body`
  - `hx-swap`: `innerHTML`
- Bill Pay row edit:
  - Endpoint: `GET /accounts/bill-pay/<account_id>/row/?month=YYYY-MM`
  - `hx-target`: `#bill-pay-row-<account_id>`
  - `hx-swap`: `outerHTML`
- Bill Pay row save:
  - Endpoint: `POST /accounts/bill-pay/<account_id>/row/?month=YYYY-MM`
  - `hx-target`: `#bill-pay-row-<account_id>`
  - `hx-swap`: `outerHTML`
  - Validation failure: `422` response returns editable row

## Pending Evidence Capture

## Test Evidence

- Migration consistency pre-check:
  - `python manage.py makemigrations --check` → `No changes detected`
- Bill Pay tests (SQLite settings):
  - `python manage.py test financial.tests.test_bill_pay_index financial.tests.test_bill_pay_save financial.tests.test_bill_pay_months financial.tests.test_bill_pay_validation --settings=core.settings_test`
  - Result: `Ran 14 tests ... OK`
- Failing-then-passing progression captured:
  - Initial failures addressed:
    - month normalization for string inputs
    - 422 test assertions expecting 200 default
  - Final rerun passed all Bill Pay tests.

## Migration & Fixture Determinism

- Applied migration:
  - `financial.0004_monthly_bill_payment`
- Determinism checks:
  - `python manage.py migrate --check --settings=core.settings_test`
- Fixture updates:
  - `financial/fixtures/accounts_minimal.json` now includes liability accounts and `financial.monthlybillpayment` records keyed by normalized month.

## Quickstart Validation Notes

- Automated validation completed for row save/create/update, month selection, scoping, and validation errors via Django tests.

## Timed Success Criteria Evidence (SC-001, SC-002)

- Date captured: 2026-02-14
- Environment: local Django app via test client (`core.settings_test`, SQLite), 30 samples per scenario.
- Measurement command: one-off script executed with `.venv` Python in repo root.

### SC-001 (open Bill Pay from sidebar under 10s)

- Proxy measurement: authenticated `GET` to `financial:bill-pay-index`.
- Results:
  - p95: `51.71 ms` (`0.052 s`)
  - median: `16.97 ms` (`0.017 s`)
  - max: `90.53 ms` (`0.091 s`)
- Outcome: comfortably within the `< 10s` threshold for all measured samples.

### SC-002 (complete single row update under 30s)

- Proxy measurement: authenticated HTMX `POST` to `financial:bill-pay-row` with amount + paid toggle for selected month.
- Results:
  - p95: `28.96 ms` (`0.029 s`)
  - median: `18.51 ms` (`0.019 s`)
  - max: `32.03 ms` (`0.032 s`)
- Outcome: comfortably within the `< 30s` threshold for all measured samples.

### Notes

- These are system-response proxy timings and indicate significant headroom against SC thresholds.
- Human usability timing (navigation + interaction behavior) should still be confirmed during manual UAT.

## Prompt/Response References

- Speckit workflow prompts used:
  - `speckit.specify.prompt.md`
  - `speckit.clarify.prompt.md`
  - `speckit.plan.prompt.md`
  - `speckit.tasks.prompt.md`
  - `speckit.analyze.prompt.md`
  - `speckit.implement.prompt.md`
