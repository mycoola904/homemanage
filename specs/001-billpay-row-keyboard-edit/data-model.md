# Data Model: BillPay Row Keyboard Editing

## Scope
No new persisted entities are introduced. This feature reuses existing BillPay persistence and adds interaction semantics to row rendering.

## Existing Persisted Entities

### MonthlyBillPayment (existing)
- Fields:
  - `id: UUID`
  - `account: FK(Account)`
  - `month: Date (normalized to first day of month)`
  - `actual_payment_amount: Decimal(12,2) | null`
  - `paid: bool`
  - `created_at`, `updated_at`
- Constraints:
  - Unique `(account, month)`
- Validation:
  - `actual_payment_amount >= 0`
- State usage in this feature:
  - Read to populate display row and edit row defaults.
  - Updated only through existing row save flow.

### Account (existing, row identity source)
- Fields used here:
  - `id`, `name`, `institution`, `payment_due_day`, `minimum_amount_due`, `online_access_url`, `account_type`
- Constraints used here:
  - BillPay row endpoint rejects non-liability account types.

## Non-Persisted View Model (existing + clarified)

### BillPayRow (service-layer row projection)
- Purpose: Canonical row display/edit metadata for templates.
- Relevant attributes:
  - `account_id`
  - funding account control metadata (focus/entry target only, non-persisted)
  - display values (`name`, `institution`, `payment_due_day_display`, `minimum_amount_due_display`, `actual_payment_amount_display`, `paid_label`)
  - links (`edit_url`, `save_url`)

## Interaction State (non-persisted)

### RowEditSession (request/response-scoped, not DB)
- `active_row_id`: account UUID currently in edit mode
- `focus_field`: one of `funding_account | actual_payment_amount | paid | save | cancel`
- `keyboard_intent`: one of `save | cancel | none`

## Validation Rules
- Month query must parse (`YYYY-MM`) or endpoint returns row-missing/error response.
- Liability account membership required for row operations.
- Funding account control is focusable and participates in tab order but does not create/update a persisted field in this feature.
- Save intent must continue existing form validation semantics.
- Cancel intent must never mutate persisted values.

## State Transitions
1. Display row → Edit row
  - Trigger: click Funding Account control, Actual Payment, Paid, or Edit action.
   - Result: same row target swapped to edit partial with requested focus field.
2. Edit row → Display row (save)
   - Trigger: Enter or Save.
   - Guard: form valid.
   - Result: persisted update through existing upsert path, then display partial.
3. Edit row → Edit row (validation failure)
   - Trigger: Enter or Save with invalid data.
   - Result: 422 edit partial with errors, focus on first invalid field.
4. Edit row → Display row (cancel)
   - Trigger: Esc or Cancel.
   - Result: display partial restored with unchanged persisted values.
