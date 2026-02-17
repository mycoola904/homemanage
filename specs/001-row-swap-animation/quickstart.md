# Quickstart: Subtle Row Swap Animation

## Prerequisites
- Python environment set up for this repo
- Node dependencies installed
- Existing bill-pay data available in local DB

## Baseline capture (pre-implementation)
- Baseline observation date: 2026-02-17
- Current behavior before animation changes: row `outerHTML` swaps appear immediate/abrupt (no enter fade/slide).
- Baseline evidence notes: capture one Edit -> Save cycle before applying implementation changes.

## 1) Start CSS watcher (required before styling diagnostics)
- Run: `npm run dev:css`
- Expected result: terminal shows Tailwind/DaisyUI rebuild output on CSS/template changes.
- Captured startup evidence (2026-02-17):
   - `tailwindcss v4.1.18`
   - `/*! 🌼 daisyUI 5.5.17 */`
   - `Done in 446ms`

## 2) Start Django app
- Run: `python manage.py runserver`
- Expected result: app served locally and `/financial/bill-pay/` loads.

## 3) Manual validation flow
1. Open Bill Pay page for a month with liability rows.
2. Click `Edit` on a row.
   - Expected: row swaps to edit mode with subtle enter fade/slide (~120–180ms).
3. Click `Save` with valid values.
   - Expected: row swaps back to view mode with same subtle enter animation.
4. Click `Edit` again, then `Cancel`.
   - Expected: row returns to view mode with same enter animation.
5. Submit invalid data to trigger `422` response.
   - Expected: edit row remains with errors and still enters smoothly; controls stay usable.
6. Repeat toggles rapidly on one row (20+ times).
   - Expected: no stuck classes, no broken row state, no interaction lock.

## 4) Focused test execution
- Run focused financial tests, then full suite as needed.
- Example focused command: `python manage.py test financial.tests.test_bill_pay_row_keyboard_edit`
- Expected result: existing bill-pay interaction tests pass with no regressions.

### Implementation evidence (2026-02-17)
- Executed command:
   - `C:/Users/micha/Documents/homemanage/.venv/Scripts/python.exe manage.py test --settings=core.settings_test financial.tests.test_bill_pay_row_keyboard financial.tests.test_bill_pay_save financial.tests.test_bill_pay_row_keyboard_shortcuts financial.tests.test_hx_trigger_preservation`
- Result:
   - `Found 18 test(s)`
   - `Ran 18 tests in 12.282s`
   - `OK`

### US1 evidence notes
- Edit-row and save-response partials include `data-billpay-animate-row` and `billpay-row-transition` markers.
- Focus handling remains intact for edit rows via existing `data-initial-focus-field` behavior.

### US2 evidence notes
- Invalid (`422`) edit-row responses preserve transition markers.
- Repeated edit/cancel swap regression checks pass without losing row transition hooks.
- Non-bill-pay HTMX transaction create response verified to exclude bill-pay transition markers.
- Optional leaving animation path remains non-required (enabled only when `data-billpay-enable-leave="true"`).

## 5) Success criteria evidence checklist

### SC-003 measurement record (required)
- Sample size: 20 consecutive view↔edit swaps on one bill-pay row
- Measurement method: browser DevTools Performance/Timing markers or equivalent stopwatch capture
- Record values:
   - Measured transition duration range (ms): `___` to `___`
   - Any swap with duration outside 120–180ms? `Yes/No`
   - Maximum additional wait before next user action (ms): `___`
- Pass criteria:
   - Duration remains within 120–180ms for all sampled swaps
   - Maximum additional wait is <= 100ms

FR-010 implementation validation note:
- Reduced-motion contexts are intentionally not exempt in this feature; transition logic applies uniformly.
- Verification method: confirm bill-pay row swap responses continue to carry animation hooks in automated tests and perform UI spot-check in browser.

### SC-004 reviewer rubric record (required)
- Reviewer count: minimum 3
- Rubric: each reviewer marks transition as `Pass (subtle/non-distracting)` or `Fail`
- Record:
   - Reviewer 1: `Pass/Fail`
   - Reviewer 2: `Pass/Fail`
   - Reviewer 3: `Pass/Fail`
   - Additional reviewers (optional): `Pass/Fail`
- Pass criteria:
   - At least 2 of first 3 reviewers mark `Pass`

FR-011 implementation validation note:
- Scope guard enforced by regression test (`financial.tests.test_hx_trigger_preservation`) asserting non-bill-pay HTMX transaction flow does not include bill-pay animation markers.

## 6) Evidence capture for PR
- Include watcher-running evidence (`npm run dev:css` output)
- Include spec/plan/tasks links
- Include note that no migrations or dependencies were added

## 7) End-to-end checklist outcome (2026-02-17)
- ✅ Watcher startup verified and recorded.
- ✅ Focused bill-pay regression tests executed with SQLite test settings and passing.
- ✅ FR-010/FR-011 evidence notes recorded.
- ⚠️ Browser manual spot-check for visual timing/reviewer rubric remains a human QA step using this checklist.
