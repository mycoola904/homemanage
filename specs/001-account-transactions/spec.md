# Feature Specification: Transactions (Account Detail + Add Transaction via HTMX)

**Feature Branch**: `[001-account-transactions]`  
**Created**: 2026-02-11  
**Status**: Draft  
**Input**: Add a `Transaction` domain model and a reusable Account Transactions table on the account detail page, including an HTMX Add Transaction form with Save/Cancel.

> Per the Constitution, this spec must be reviewed and approved before any code is written. This feature MUST remain server-rendered and deterministic, use HTMX fragments (HTML-only), add no new runtime dependencies, and follow Django template safety rules.

## Clarifications

### Session 2026-02-11

- Q: Money amount storage (DB precision)? → A: DecimalField(max_digits=10, decimal_places=2)
- Q: Transactions table columns? → A: Posted On, Description, Amount (signed)
- Q: Missing/unowned account fragments HTTP status? → A: 200 with inline “not found” message fragment
- Q: Add Transaction form default `posted_on`? → A: Default to today (server-side)
- Q: Add Transaction form `direction` control? → A: Radio buttons (Debit/Credit)

## Goals

- Users can view a Transactions panel on an Account detail page.
- Users can add a transaction inline via HTMX (no full page reload).
- The Transactions table is a reusable component for “Account Transactions”.
- Transactions data is persisted as a first-class domain model.

## Non-Goals

- Editing or deleting transactions.
- Reconciliation (cleared/pending), running balances, or account balance history.
- Importing transactions from banks/files.
- Categories, budgets, tags, or reporting.
- Pagination, filtering, search, or exporting.
- Multi-currency.

## Key Pages & URLs

### Pages

- `GET /accounts/<uuid>/` — Account detail page (existing). This page will include a “Transactions” panel.

### Endpoints (HTML only)

These endpoints MUST enforce the same auth + ownership rules as accounts: transactions are accessed only through an account owned by the authenticated user.

If the account does not exist or is not owned by the authenticated user, these endpoints MUST return a `200` response containing an inline “not found” message fragment within the Transactions panel body (and MUST NOT reveal any transaction data).

- `GET /accounts/<uuid:account_id>/transactions/`
  - Returns a fragment containing the Transactions panel body (table OR empty state).
  - Used for initial rendering and for “Cancel” to restore the table.

- `GET /accounts/<uuid:account_id>/transactions/new/`
  - Returns a fragment containing the Add Transaction form.

- `POST /accounts/<uuid:account_id>/transactions/new/`
  - On success: creates the transaction and returns the Transactions panel body fragment.
  - On validation failure: returns the Add Transaction form fragment with field errors and status `422`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Transactions on Account (Priority: P1)

As a user, I want to see a Transactions table on an Account detail page so I can review account activity.

**Why this priority**: A visible, reliable Transactions panel is the foundation for all future transaction work.

**Independent Test**: Visit an Account detail page and confirm the panel renders correctly for both empty and non-empty data.

**Acceptance Scenarios**:

1. **Given** an account with no transactions, **When** I view the account detail page, **Then** I see an explicit empty state and an “Add Transaction” button.
2. **Given** an account with transactions, **When** I view the account detail page, **Then** I see a table of transactions rendered in deterministic order.

---

### User Story 2 - Add Transaction Inline (Priority: P1)

As a user, I want to add a transaction without leaving the Account detail page so I can quickly record activity.

**Why this priority**: Creating a transaction is the minimal interactive workflow that makes the panel useful.

**Independent Test**: Click Add → form shows; Save valid → new row appears; Save invalid → errors show; Cancel → table returns.

**Acceptance Scenarios**:

1. **Given** I am on an account detail page, **When** I click “Add Transaction”, **Then** the Transactions body swaps to an Add Transaction form via HTMX without a full page reload.
2. **Given** the Add Transaction form is visible, **When** I click “Cancel”, **Then** the Transactions body swaps back to the table (or empty state).
3. **Given** I submit valid transaction data, **When** I click “Save”, **Then** the transaction is created and the Transactions body swaps back to the table including the new transaction.
4. **Given** I submit invalid transaction data, **When** I click “Save”, **Then** the form re-renders with inline errors and the server response status is `422`.

---

### User Story 3 - Handle Missing/Unauthorized Account (Priority: P2)

As a user, I need the Transactions panel to fail safely if the account is missing or I don’t have access.

**Why this priority**: Prevents confusing broken UI states and avoids leaking data.

**Independent Test**: Request the HTMX transaction endpoints for a non-existent/unowned account and confirm the UI shows a clear inline message.

**Acceptance Scenarios**:

1. **Given** an account ID that does not exist or is not owned by me, **When** I request the Transactions fragments, **Then** I see an inline “not found” message inside the Transactions panel body and no transaction data is revealed.

### Edge Cases

- Deterministic ordering: if two transactions share the same `posted_on`, ordering remains stable across refreshes.
- Validation failures return `422` and keep the form visible with errors.
- Double-submits are discouraged via disabled elements and request queuing.
- If the add form is open and a stale response arrives, the “latest action wins” (queue-last behavior).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST introduce a `Transaction` entity that belongs to exactly one `Account`.
- **FR-002**: System MUST allow a user to list transactions for an account they own on the account detail page.
- **FR-003**: System MUST allow a user to create a transaction for an account they own using an inline HTMX form.
- **FR-004**: Transactions MUST render in deterministic order: `posted_on` (descending), then `created_at` (descending), then `id` (descending).
- **FR-005**: System MUST return HTML fragments only for Transactions HTMX endpoints (no JSON responses).
- **FR-006**: On successful create, system MUST return the Transactions body fragment containing the updated table/empty state.
- **FR-007**: On validation failure, system MUST return the form fragment with errors and status `422`.
- **FR-008**: The Transactions table MUST be implemented as a reusable “Account Transactions table” component.

### Key Entities *(include if feature involves data)*

#### Transaction (minimal fields)

The minimal model is designed to support a useful table and a correct create flow without committing to reconciliation, categories, or account-type-specific semantics.

| Field | Required | Meaning | Rationale |
| --- | ---: | --- | --- |
| `account` | yes | Owning account | Enables scoping and display on account detail page. |
| `posted_on` | yes | Date of the transaction | User-facing “when”; defaults to server-side “today” for the add form. |
| `description` | yes | Payee/merchant/memo | Primary identifier in a table; supports real-world entries. |
| `direction` | yes | `debit` or `credit` | Avoids ambiguity of negative amounts across account types. |
| `amount` | yes | Positive money value (USD, 2dp) | Stored as `DecimalField(max_digits=10, decimal_places=2)`; sign is derived from `direction`. |
| `notes` | no | Optional free text | Captures extra detail without categories/tags. |
| `created_at` | yes | Creation timestamp | Deterministic tie-breaker and audit trail. |

**Display rules (UI)**:

- Transactions table columns: Posted On, Description, Amount (signed).
- Amount is displayed as `-$amount` for `debit` and `+$amount` for `credit`.
- Amount uses consistent currency formatting with the existing Accounts feature (USD, en-US) until multi-currency is specified.

### Server-Driven UI & Template Safety *(mandatory for UI work)*

- **UI-001 (Swap boundaries)**: The Transactions panel MUST keep a stable outer container and swap only the panel body.
  - Stable container ID: `#account-transactions`
  - Swap target ID: `#account-transactions-body`

- **UI-002 (HTMX endpoints)**: Each HTMX interaction MUST use the following:
  - Add button: `hx-get` → `/accounts/<account_id>/transactions/new/`, `hx-target="#account-transactions-body"`, `hx-swap="innerHTML"`, `hx-request="queue:last"`, `hx-disabled-elt="this"`
  - Cancel: `hx-get` → `/accounts/<account_id>/transactions/`, same target + swap
  - Save: form `hx-post` → `/accounts/<account_id>/transactions/new/`, same target + swap

The Add Transaction form MUST include a `direction` control implemented as radio buttons: Debit / Credit.

- **UI-003 (Trigger remains in DOM)**: The Add Transaction button MUST remain usable after any swap (no `outerHTML` swaps of the panel container).

- **UI-004 (Template safety)**: Templates MUST NOT split `{% ... %}` tags across multiple lines and MUST NOT use multi-line Django template comments.

- **UI-005 (Watcher workflow)**: If styling issues arise during implementation, the first check MUST be that the Tailwind watcher is running (e.g., `npm run dev`) and rebuilding assets.

## Deterministic Data & Integrity *(mandatory)*

- **Schema Changes**:
  - Add one migration that creates the `Transaction` table with an index supporting account-scoped ordering (account + posted date).
  - Rollback: migration rollback must remove the table cleanly.

- **Data Fixtures**:
  - No fixture changes required for MVP. Optional future fixture: a minimal transactions fixture for development/demo.

- **External Inputs**:
  - No third-party calls.
  - Default values (e.g., initial `posted_on`) must not rely on non-deterministic client behavior; the add form defaults `posted_on` server-side to the server's current local date.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can add a transaction from the account detail page in under 60 seconds on first attempt.
- **SC-002**: Validation feedback is visible without leaving the account detail page (no full page reload) for 100% of invalid submissions.
- **SC-003**: Transactions render in the same order across repeated refreshes when data is unchanged.
- **SC-004**: For an account with up to 200 transactions, the Transactions panel remains usable and readable (no UI breakage; table renders without truncating actions).

## Assumptions & Open Questions *(mandatory)*

### Assumptions

- The existing “account ownership by authenticated user” model continues to serve as the scoping mechanism for transactions.
- Transactions are created only (no edit/delete) in this feature.
- `posted_on` is captured as a date (not a timestamp) for MVP.
- Amounts are positive numbers; sign comes from `direction`.
- No new dependencies are introduced.

### Open Questions

- Do we need a “status” (pending/cleared) now, or explicitly defer to a later reconciliation feature?
