# Quickstart: Subtle Row Swap Animation

## Prerequisites
- Python environment set up for this repo
- Node dependencies installed
- Existing bill-pay data available in local DB

## 1) Start CSS watcher (required before styling diagnostics)
- Run: `npm run dev:css`
- Expected result: terminal shows Tailwind/DaisyUI rebuild output on CSS/template changes.

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

## 6) Evidence capture for PR
- Include watcher-running evidence (`npm run dev:css` output)
- Include spec/plan/tasks links
- Include note that no migrations or dependencies were added
