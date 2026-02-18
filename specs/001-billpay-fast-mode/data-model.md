# Data Model — Bill Pay Fast Mode

## Entity: BillPayRowView
Represents one rendered bill-pay table row for a liability account in selected month.

Fields:
- `account_id` (UUID, required)
- `month` (`YYYY-MM`, required)
- `paid` (boolean, required)
- `funding_account_id` (UUID, required for valid save)
- `actual_payment_amount` (decimal >= 0, nullable)
- `edit_url` (string URL, required)
- `save_url` (string URL, required)

Validation rules:
- `account_id` must belong to active household.
- Account type must be one of liability types (`credit_card`, `loan`, `other`).
- `funding_account` must be active and within same household.
- `actual_payment_amount` cannot be negative.

State transitions:
- `view -> edit`: HTMX GET row endpoint (`bill_pay_row` GET).
- `edit -> view (save success)`: HTMX POST row endpoint with valid form.
- `edit -> edit (validation error)`: HTMX POST row endpoint with invalid form (`422`).
- `edit -> view (cancel)`: HTMX POST row endpoint with `keyboard_intent=cancel`.

## Entity: FastModePreference (Page Scope)
Non-persistent request/UI state indicating whether save should auto-open next unpaid row.

Fields:
- `enabled` (boolean, required; default `false`)
- `source` (form/hidden input from current page only)

Validation rules:
- Absent/invalid value coerces to `false`.
- Must reset to `false` on full page reload/new visit.

State transitions:
- `off -> on`: user toggles checkbox on page.
- `on -> off`: user untoggles checkbox.
- `any -> off`: full reload/new visit.

## Entity: NextRowInstruction
Server-derived output attached to successful save response when Fast Mode is enabled.

Fields:
- `next_row_id` (UUID string, nullable)
- `next_edit_url` (string URL, nullable)
- `focus_field` (enum; default `actual_payment_amount`)
- `reason` (enum: `next_available`, `no_next`, `open_failed` client-observed)

Validation rules:
- Produced only on successful save.
- `next_row_id` and `next_edit_url` must both be present when `reason=next_available`.
- Must use current on-screen order semantics for candidate selection.

State transitions:
- `none -> next_available`: save success + fast mode on + unpaid row exists.
- `none -> no_next`: save success + fast mode on + no unpaid row exists.
- Client follow-up request may result in `open_failed` UX handling without mutating saved row state.
