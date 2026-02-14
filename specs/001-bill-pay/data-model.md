# Data Model: Bill Pay

Date: 2026-02-13  
Spec: specs/001-bill-pay/spec.md

## Entities

### Account (existing)

Source of Bill Pay rows. Bill Pay includes only `Account` records in the selected household/month where:

- `account_type` is one of: `credit_card`, `loan`, `other`

Relevant existing fields used by Bill Pay presentation:

- `name`
- `institution`
- `payment_due_day`
- `minimum_amount_due`
- `online_access_url`

### MonthlyBillPayment (new)

Represents one bill-pay entry for one account in one calendar month.

#### Fields

- `id`: UUID primary key
- `account`: FK → `financial.Account` (required, `on_delete=CASCADE`)
- `month`: `DateField` (required; normalized to first day of month)
- `actual_payment_amount`: `DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)`
- `paid`: `BooleanField(default=False)`
- `created_at`: `DateTimeField(auto_now_add=True)`
- `updated_at`: `DateTimeField(auto_now=True)`

#### Uniqueness and indexes

- Unique constraint on `(account, month)` to guarantee one record per account-month.
- Index on `(month, account)` for selected-month retrieval and deterministic table joins.

## Validation rules

- `month` MUST be normalized to the first day of the selected month (e.g., `2026-02-01`).
- `actual_payment_amount` MUST be `>= 0` when present; negative values are invalid.
- `paid` MAY be true when `actual_payment_amount` is blank or `0.00` (per clarification).
- Save operations MUST scope account ownership/household membership before create/update.

## Query and ordering rules

For selected month `$M`:

1. Fetch liability accounts for the active household.
2. Left-join/lookup `MonthlyBillPayment` for each account with `month=$M`.
3. Sort rows deterministically:
   - non-null `payment_due_day` first, ascending
   - null `payment_due_day` last
   - `name` ascending
   - `id` ascending

## State transitions

For each `(account, month)` entry:

- **Missing → Saved**: first explicit row save creates record.
- **Saved → Updated**: explicit row save updates existing record.
- **Month boundary**: no automatic transition from month `M` to `M+1`; new month starts with missing records unless user saves.
