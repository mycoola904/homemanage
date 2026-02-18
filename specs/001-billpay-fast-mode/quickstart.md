# Quickstart — Bill Pay Fast Mode

## Prerequisites
1. Install Python and Node dependencies.
2. Use test settings backed by SQLite (`core.settings_test`).
3. Ensure database is migrated and seed data includes liability + funding accounts.

## Run locally
1. Start CSS watcher before UI styling/debugging:
   - Command: `npm run dev:css`
   - Observe: Tailwind/DaisyUI watcher logs initial build and rebuild messages.
2. Start Django app:
   - Command: `python manage.py runserver`
   - Observe: Bill Pay page loads with month picker and liability rows.

## Exercise Fast Mode behavior
1. Open Bill Pay page with unpaid rows.
   - Observe: Fast Mode toggle is OFF by default.
2. Enable Fast Mode and open a row in edit mode.
   - Observe: Existing row edit UI appears with focus in configured field.
3. Save valid payment data.
   - Observe: Saved row returns to display mode; next unpaid row auto-opens in edit mode with focus on actual payment amount.
4. Disable Fast Mode and save another row.
   - Observe: Only current row returns to display mode; no auto-open occurs.
5. Trigger validation error (e.g., invalid/missing required field) with Fast Mode ON.
   - Observe: Current row remains in edit mode with validation errors; no auto-open occurs.
6. Save final unpaid row with Fast Mode ON.
   - Observe: No additional row opens; page remains stable.

## Test commands
1. Run focused bill pay tests:
   - `python manage.py test financial.tests.test_bill_pay_save financial.tests.test_bill_pay_row_keyboard financial.tests.test_bill_pay_validation`
   - Observe: New/updated Fast Mode scenarios pass.
2. Run broader financial test slice if needed:
   - `python manage.py test financial.tests`
   - Observe: No regressions in non-Fast-Mode bill-pay behavior.

## HTMX contract verification
1. Save row with Fast Mode enabled.
   - Observe: Response swaps target row (`outerHTML`) and includes trigger metadata only when a next row exists.
2. Simulate next-open failure (network/server error).
   - Observe: Saved row remains in view state, an inline status message appears in the Bill Pay header area, and user manually opens next row.

## Deterministic evidence (no schema/fixture drift)
1. Verify no new migrations are introduced for this feature.
   - Command: `python manage.py makemigrations --check --dry-run`
   - Observe: No changes detected.
2. Verify fixture footprint remains unchanged.
   - Command: `git status --short`
   - Observe: No fixture file changes under `financial/fixtures/`.
