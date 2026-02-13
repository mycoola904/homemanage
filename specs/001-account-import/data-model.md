# Data Model: Household Account Import

## 1) Account (existing entity, updated)
- Purpose: Stores household financial accounts.
- Change in this feature:
  - Add `online_access_url` (nullable/blank URL) for account online portal access.
- Relevant existing fields used by import:
  - `user` (FK, required)
  - `household` (FK, required)
  - `name` (required, uniqueness behavior enforced for this feature at household scope, case-insensitive)
  - `institution`
  - `account_type` (enum: `checking|savings|credit_card|loan|other`)
  - `account_number`
  - `routing_number`
  - `interest_rate`
  - `status` (enum: `active|closed|pending`)
  - `current_balance`
  - `credit_limit_or_principal`
  - `statement_close_date` (`YYYY-MM-DD` input format)
  - `payment_due_day` (1..31 when present)
  - `notes`
  - `online_access_url` (blank or absolute `http/https` URL)

## 2) AccountImportRow (transient validation model, not persisted)
- Purpose: Represents one CSV row during import processing.
- Fields:
  - `row_number` (int, data row index)
  - `name`, `institution`, `account_type`, `account_number`, `routing_number`, `interest_rate`, `status`, `current_balance`, `credit_limit_or_principal`, `statement_close_date`, `payment_due_day`, `online_access_url`, `notes`
- Validation rules:
  - Required header set must exactly exist in CSV.
  - Enum values must be canonical internal values.
  - `statement_close_date` must be ISO `YYYY-MM-DD` when present.
  - `online_access_url` must be blank or valid absolute `http/https` URL.
  - Duplicate account names are invalid when duplicate exists (a) within upload or (b) in active household, case-insensitive.

## 3) ImportResultSummary (transient response model, not persisted)
- Purpose: Return deterministic outcome to UI.
- Fields:
  - `total_rows`
  - `imported_rows`
  - `rejected_rows`
  - `errors` (list of `{row_number, field, message}`)
- State transitions:
  - `received` → `validated` → (`failed` | `committed`)
  - `failed`: any validation error, zero inserts
  - `committed`: all rows valid, transaction commits all inserts

## Relationships & Ownership
- Imported `Account` rows are always assigned to:
  - `household` = currently resolved active household at submission time
  - `user` = authenticated submitting user
- Household context from request overrides any household-like CSV input (ignored by contract).

## Determinism Notes
- Transaction boundary is file-level (all-or-nothing).
- Header order in template CSV is stable and fixed.
- Parsing and validation outcomes are deterministic for the same CSV + household state.
