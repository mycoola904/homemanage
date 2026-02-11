# Research: Account Transactions

Date: 2026-02-11  
Spec: specs/001-account-transactions/spec.md

This document consolidates design decisions required to implement Transactions deterministically using server-rendered HTML + HTMX fragments, with no new runtime dependencies.

## Decisions

### Money representation

- Decision: Store `Transaction.amount` as `DecimalField(max_digits=10, decimal_places=2)`.
- Rationale: Matches existing `Account.current_balance` storage (decimal, 2dp) and supports USD-only MVP without floating point error.
- Alternatives considered:
  - Integer cents: simplifies some math but adds conversion/formatting overhead everywhere.
  - More precision (4dp): unnecessary for USD-only MVP.

### Direction + signed display

- Decision: Persist `direction` as `debit|credit` and store `amount` as a positive value; display as `-$amount` for debit and `+$amount` for credit.
- Rationale: Avoids negative-value ambiguity across account types and keeps validation simple.
- Alternatives considered:
  - Signed amount input: reduces one field but increases validation ambiguity and UI complexity.

### Transactions table columns

- Decision: Table columns are `Posted On`, `Description`, `Amount` (signed).
- Rationale: Compact, scannable, and sufficient for MVP without committing to additional semantics.
- Alternatives considered:
  - Include `Direction` column: redundant with signed amount.
  - Include `Notes`: encourages over-dense tables and is not required for MVP.

### Default `posted_on`

- Decision: Default `posted_on` to "today" server-side when rendering the add form.
- Rationale: Improves speed-to-entry (SC-001) without depending on client-side behavior.
- Alternatives considered:
  - No default: higher friction.

### Missing/unowned account fragment behavior

- Decision: For Transactions HTMX endpoints, return HTTP 200 with an inline "not found" message fragment (no data) if the account does not exist or is unowned.
- Rationale: Keeps HTMX swaps predictable without requiring client-side error handlers.
- Alternatives considered:
  - 404 fragments (used elsewhere in Accounts): valid, but would require consistent handling expectations across these endpoints.

### HTMX boundaries and swap strategy

- Decision: Keep a stable outer container `#account-transactions` on the account detail page; swap only `#account-transactions-body` with `hx-swap="innerHTML"`.
- Rationale: Meets UI safety rules and keeps the Add button stable and reusable after swaps.
- Alternatives considered:
  - `outerHTML` swaps: risks removing stable trigger/container elements.

### Deterministic ordering

- Decision: Order by `posted_on DESC`, then `created_at DESC`, then `id DESC`.
- Rationale: Explicit tie-breakers ensure stable ordering across refreshes.

### Schema + indexing

- Decision: Single migration to create `Transaction` table with an index supporting account-scoped ordering.
- Rationale: Keeps schema change small and reversible.
- Index plan: `(account_id, posted_on, created_at, id)` (direction depends on DB; ordering remains deterministic regardless).

### "Status" field (pending/cleared)

- Decision: Explicitly defer; do not include a status field in MVP.
- Rationale: Non-goal per spec; avoids committing to reconciliation semantics.

## Implementation Notes (repo-specific)

- Tailwind watcher in this repo is `npm run dev:css` (not `npm run dev`).
- Existing patterns:
  - HTMX fragment endpoints use `login_required` + `require_http_methods`.
  - Validation failures use HTTP 422.
  - Reusable UI chunks live under `templates/components/...` (django-cotton components).
