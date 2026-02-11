# Research — Account and Transaction Model Evolution

## Account Number Backfill
Decision: Leave `account_number` null for existing rows and drop `number_last4` after migration.
Rationale: `number_last4` is not a full account number; copying it would create misleading data and violate deterministic correctness. This keeps data honest and reversible.
Alternatives considered: Copy `number_last4` into `account_number` (rejected: incorrect data) and blocking migration until users provide full numbers (rejected: unnecessary friction).

## Category Casing and Uniqueness
Decision: Preserve user-entered casing while enforcing case-insensitive uniqueness per user.
Rationale: Users expect display casing to remain intact while preventing duplicates like "Groceries" and "groceries".
Alternatives considered: Lowercasing all values (rejected: degrades display) and allowing case-only duplicates (rejected: breaks reporting normalization).

## Inline Category Error Handling
Decision: Return the category form fragment with validation errors and a 400 status; keep the transaction form visible.
Rationale: Maintains HTMX stability and provides immediate feedback without removing the trigger element or forcing a full reload.
Alternatives considered: Returning only a toast or 200 without errors (rejected: weak feedback) and redirecting to a separate page (rejected: violates inline flow requirement).

## Transaction Amount Inputs
Decision: Require positive, non-zero input amounts and reject zero/negative values.
Rationale: Ensures deterministic sign logic and avoids ambiguous ledger effects.
Alternatives considered: Allowing zero as a no-op or accepting negative values (rejected: undermines deterministic sign matrix).

## Deterministic Sign Logic Placement
Decision: Enforce sign conversion in model/service logic before persistence, using the account type + transaction type matrix.
Rationale: Centralizes deterministic behavior and keeps persisted data consistent regardless of form source.
Alternatives considered: Applying sign only in views or templates (rejected: risks inconsistent persistence paths).