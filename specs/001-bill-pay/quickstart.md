# Quickstart: Bill Pay

Date: 2026-02-13

## Prereqs

- Python environment with `requirements.txt` installed
- Node available for Tailwind CLI

## Run locally

1. Apply DB migrations:
   - `python manage.py migrate`
2. Start Tailwind watcher (required before styling/debug checks):
   - `npm run dev:css`
3. Start Django:
   - `python manage.py runserver`

## Manual validation flow (maps to spec)

1. Open Bill Pay
   - Navigate from sidebar to Bill Pay
   - Confirm monthly table appears in main content area

2. Verify row scope and ordering
   - Confirm only `credit_card`, `loan`, and `other` accounts appear
   - Confirm due-day ascending order with null due-days after non-null rows

3. Save one row (valid)
   - Set `actual payment amount` and toggle `paid`
   - Click row Save
   - Confirm row updates without full page reload

4. Save one row (validation)
   - Enter a negative amount
   - Click row Save
   - Confirm row returns inline validation errors with no table-shell replacement

5. Paid independent from amount
   - Leave amount blank or `0.00`, set `paid=true`, Save
   - Confirm save succeeds and persists

6. Historical month edit
   - Switch to a previous month via month selector
   - Mark an unpaid row as paid and Save
   - Reload the same month and confirm persisted value

7. Hard month boundary check
   - Switch between two adjacent months
   - Confirm unpaid rows are not auto-carried into another month unless explicitly saved in that month

## Suggested test command

- `python manage.py test financial.tests.test_bill_pay_index financial.tests.test_bill_pay_save financial.tests.test_bill_pay_months financial.tests.test_bill_pay_validation`
