# Quickstart: BillPay Row Keyboard Editing

## 1) Environment and watcher verification
1. Activate project environment and install deps if needed.
2. Start CSS watcher:
   - `npm run dev:css`
3. Observe:
   - Terminal shows continuous Tailwind/DaisyUI rebuild output.
   - This must be running before troubleshooting focus/styling behavior.

## 2) Run targeted tests first
1. Run BillPay-focused tests:
   - `python manage.py test financial.tests.test_bill_pay_index financial.tests.test_bill_pay_months financial.tests.test_bill_pay_row_focus_entry financial.tests.test_bill_pay_row_keyboard financial.tests.test_bill_pay_row_keyboard_shortcuts financial.tests.test_bill_pay_save financial.tests.test_bill_pay_validation --settings=core.settings_test`
2. Observe:
   - Existing + new keyboard/focus behavior remains green.

## 3) Add/execute keyboard interaction tests
1. Add tests for:
   - Click editable field opens edit row and focuses clicked field.
   - Tab order: Funding Account → Actual Payment → Paid → Save → Cancel (and cycles).
   - Enter triggers same save path/outcome as Save button.
   - Esc triggers same cancel path/outcome as Cancel action.
2. Observe:
   - Tests fail before implementation, then pass after implementation.

## 4) Manual HTMX verification
1. Open Bill Pay page and inspect a row swap flow.
2. Trigger edit entry from each editable field.
3. Observe:
   - `hx-target` remains row id (`#bill-pay-row-<account_id>`).
   - `hx-swap` remains `outerHTML` for row transitions.
   - Edit/display controls remain available after every swap.

## 5) Manual keyboard verification
1. Enter edit mode for a row.
2. Press Tab repeatedly.
3. Observe:
   - Focus order matches required sequence and cycles in-row.
4. Press Enter.
5. Observe:
   - Row saves with same visible result as Save button.
6. Press Esc (with unsaved changes).
7. Observe:
   - Row cancels and returns to display state with unchanged persisted data.

## 6) Regression checks
1. Run broader BillPay tests if present:
   - `python manage.py test financial.tests --settings=core.settings_test`
2. Observe:
   - No regressions in month loading, row missing behavior, or validation 422 rendering.

## 7) SC-004 usability protocol
1. Recruit at least 10 desktop-browser participants familiar with keyboard navigation basics.
2. Scripted task for each participant:
   - Open Bill Pay for a given month.
   - Enter row edit from a specified editable field.
   - Modify payment state using only keyboard.
   - Complete with Save or Cancel.
3. Pass criteria per participant:
   - Completed without mouse interaction and with expected row outcome.
4. Aggregate metric:
   - Success rate = participants passed / total participants.
   - SC-004 passes when success rate is at least 90%.
5. Evidence capture:
   - Record participant-by-participant outcomes and final percentage in `specs/001-billpay-row-keyboard-edit/research.md`.
