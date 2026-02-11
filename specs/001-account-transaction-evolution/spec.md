# Feature Specification: Account and Transaction Model Evolution

**Feature Branch**: `001-account-transaction-evolution`  
**Created**: 2026-02-11  
**Status**: Draft  
**Input**: User description: "Account and Transaction model evolution with deterministic transaction type logic, category normalization, and HTMX contract preservation"

> Per the Constitution, this spec must be reviewed and approved before any code is written. Capture determinism, dependency, and UI safety decisions here rather than deferring to implementation.

## Clarifications

### Session 2026-02-11

- Q: How should existing `number_last4` be handled when introducing `account_number`? → A: Leave `account_number` null for existing rows; drop `number_last4`.
- Q: How should category casing and uniqueness be handled? → A: Preserve original casing; enforce uniqueness on lowercased value; reject duplicates.
- Q: How should inline category add validation errors be returned? → A: Return the category form fragment with validation errors and a 400; keep the transaction form visible.
- Q: Should Category include a created timestamp? → A: Add `created_at` as auto timestamp.
- Q: How should zero or negative transaction amounts be handled? → A: Reject zero/negative inputs; require positive absolute amounts.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Maintain accurate account details (Priority: P1)

Account owners update account details and only see fields that apply to the selected account type.

**Why this priority**: This prevents invalid data entry and preserves correct financial details for core account records.

**Independent Test**: Can be fully tested by editing a checking account and a credit card account and verifying visible fields and validations.

**Acceptance Scenarios**:

1. **Given** a checking or savings account, **When** the edit form is loaded, **Then** routing number is visible and interest rate is hidden.
2. **Given** a credit card, loan, or other debt account, **When** the edit form is loaded, **Then** interest rate is visible and routing number is hidden.

---

### User Story 2 - Record a transaction with deterministic amount sign (Priority: P2)

Account owners add transactions and the system stores amounts with a deterministic sign based on account type and transaction type.

**Why this priority**: Predictable ledger math is critical to balances and reporting.

**Independent Test**: Can be fully tested by creating a transaction for each account type and verifying the stored sign matches the deterministic matrix.

**Acceptance Scenarios**:

1. **Given** a checking account, **When** a deposit is submitted, **Then** the stored amount is positive and increases the account balance.
2. **Given** a credit card account, **When** a charge is submitted, **Then** the stored amount is positive and increases the account balance as debt.

---

### User Story 3 - Categorize transactions without leaving the page (Priority: P3)

Account owners choose an existing category or add a new category inline while creating a transaction.

**Why this priority**: Normalized categories improve reporting while keeping data entry fast.

**Independent Test**: Can be fully tested by adding a new category through the transaction form and immediately selecting it without a full page reload.

**Acceptance Scenarios**:

1. **Given** the transaction form is open, **When** a new category is added inline, **Then** the category appears in the dropdown and can be selected immediately.

---

### Edge Cases

- Attempt to submit routing number for a credit card or loan account.
- Attempt to submit interest rate for a checking or savings account.
- Transaction type not allowed for the account type.
- Category name differing only by case for the same user.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST replace `number_last4` with `account_number` and `routing_number` as account attributes.
- **FR-002**: The system MUST store `routing_number` only for checking or savings accounts and persist it as null for other account types.
- **FR-003**: The system MUST store `interest_rate` only for credit card, loan, or other debt accounts and persist it as null for checking or savings.
- **FR-004**: Account validation MUST be deterministic and enforced in model-level validation.
- **FR-005**: The system MUST replace `direction` with `transaction_type` and enforce the deterministic sign matrix for stored amounts.
- **FR-006**: The system MUST restrict transaction type choices based on account type (e.g., checking: deposit, expense, transfer; credit card: payment, charge).
- **FR-006a**: Transaction amount inputs MUST be positive and non-zero; zero or negative values MUST be rejected.
- **FR-007**: The system MUST introduce a Category entity with a user-owned name that is unique per user in a case-insensitive manner.
- **FR-007a**: Category names MUST preserve user-entered casing while enforcing case-insensitive uniqueness.
- **FR-008**: The transaction form MUST allow selecting an existing category or adding a new category inline without a full page reload.
- **FR-009**: All account and transaction form GET and POST requests MUST bind to the correct model instance.
- **FR-010**: HTMX endpoints MUST preserve existing swap targets and not remove the triggering element from the DOM.
- **FR-011**: Migrations MUST include forward steps and data backfill for direction to transaction type, and MUST be idempotent.
- **FR-012**: Test execution MUST default to SQLite and migrations MUST apply cleanly on both fresh and populated databases.
- **FR-013**: No new runtime dependencies MAY be introduced for this feature.

### Key Entities *(include if feature involves data)*

- **Account**: User-owned financial account with account type, account number, routing number (conditional), and interest rate (conditional).
- **Transaction**: Entry linked to an account with transaction type, amount, date, description, optional notes, and category.
- **Category**: User-owned label with a unique (case-insensitive) name and auto `created_at` timestamp.

### Server-Driven UI & Template Safety *(mandatory for UI work)*

- **UI-001**: Account preview/edit/delete HTMX actions MUST continue to target `#account-preview-panel` with `hx-swap="innerHTML"` and return a root element compatible with a direct innerHTML swap.
- **UI-002**: Transaction add/edit HTMX actions MUST continue to target `#account-transactions-body` with `hx-swap="innerHTML"` and return a root element compatible with a direct innerHTML swap.
- **UI-003**: The account edit form POST MUST return either the updated preview fragment or the form fragment with errors, without replacing the trigger row or button.
- **UI-004**: Conditional field visibility MUST be server-driven and use simple, single-line template constructs or view-provided flags.
- **UI-005**: Before diagnosing styling issues, the Tailwind watcher output MUST be checked (`npm run dev`).

## Deterministic Sign Matrix *(mandatory)*

Ledger behavior: positive amounts increase the account balance. For liability accounts, a higher balance represents more debt.

| Account Type | Allowed Transaction Types | Stored Sign Rules |
| --- | --- | --- |
| Checking | Deposit, Expense, Transfer, Adjustment | Deposit: positive; Expense: negative; Transfer: negative; Adjustment: positive |
| Savings | Deposit, Expense, Transfer, Adjustment | Deposit: positive; Expense: negative; Transfer: negative; Adjustment: positive |
| Credit Card | Payment, Charge, Adjustment | Payment: negative; Charge: positive; Adjustment: negative |
| Loan | Payment, Charge, Adjustment | Payment: negative; Charge: positive; Adjustment: negative |
| Other Debt | Payment, Charge, Adjustment | Payment: negative; Charge: positive; Adjustment: negative |

Rules:

- Users enter an absolute amount; the system applies the sign based on the matrix before persistence.
- If a transaction type is not listed for an account type, the transaction MUST be rejected.
- Transfer is defined as outgoing from the selected account; incoming transfers MUST be recorded as deposits.

## Deterministic Data & Integrity *(mandatory)*

- **Schema Changes**: Add account_number, routing_number, interest_rate, transaction_type, and category; remove number_last4 and direction; add Category entity; add foreign key from transaction to category.
- **Data Fixtures**: No new fixtures required. Existing fixtures must remain valid after migration.
- **External Inputs**: No nondeterministic external inputs are added. Amount sign is derived deterministically from account and transaction type.

## Migration Strategy *(mandatory)*

1. Add new nullable fields for account_number, routing_number, and interest_rate to accounts.
2. Add Category table and nullable category reference on transactions.
3. Add transaction_type field while retaining direction temporarily for backfill.
4. Backfill transaction_type from direction using deterministic mapping rules by account type.
5. Do not backfill account_number from number_last4; existing account_number remains null until user update.
6. Enforce model validation and constraints after backfill completes.
7. Remove direction and number_last4 once data has been migrated.

Backfill mapping rules:

- For checking or savings accounts: direction credit maps to deposit; direction debit maps to expense.
- For credit card, loan, or other debt accounts: direction credit maps to charge; direction debit maps to payment.

Data integrity rules:

- Migrations MUST be idempotent and safe to re-run.
- Backfill MUST not create or delete rows; it only populates new fields deterministically.
- Migration MUST succeed on a fresh SQLite database and on an existing populated database.

## HTMX Contract Documentation *(mandatory)*

- **Account preview panel**: GET preview/edit/delete responses target `#account-preview-panel` with `hx-swap="innerHTML"` and return a single root `<section>` (preview) or `<form>` (edit/delete confirmation) suitable for innerHTML replacement.
- **Account edit form POST**: POST returns the preview fragment on success or the same form fragment with errors on failure, both swapped into `#account-preview-panel` with `hx-swap="innerHTML"`.
- **Account transactions body**: GET add-transaction form and POST submission target `#account-transactions-body` with `hx-swap="innerHTML"` and return a single root `<div>` or `<form>` compatible with innerHTML replacement.
- **Inline category add**: HTMX partial for category creation returns a fragment that updates the category dropdown options and preserves the transaction form state without full page reload.
- **Inline category add errors**: On validation failure, return the category form fragment with errors and a 400 status; the transaction form remains visible.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of deterministic sign matrix tests pass for all account and transaction type combinations.
- **SC-002**: All migrations apply cleanly on a fresh SQLite test database and on a populated database with existing accounts and transactions.
- **SC-003**: Users can create a transaction with a new category without leaving the page in 3 steps or fewer.
- **SC-004**: Validation tests confirm that disallowed fields are rejected and stored as null for 100% of invalid submissions.

## Constitution Compliance *(mandatory)*

- **Spec-First**: This document defines scope, behavior, and contracts before implementation work begins.
- **Deterministic Correctness**: Transaction amount sign logic is fully specified and testable via the sign matrix.
- **Lean Dependencies**: No new runtime dependencies are permitted.
- **HTMX Contracts**: All swap targets, swap types, and response root elements are documented and preserved.
- **SQLite Tests**: Test execution must use SQLite and migrations must succeed on SQLite.

## Non-Goals

- No SPA rewrite.
- No JavaScript state management libraries.
- No background tasks.
- No third-party category tagging services.

## Assumptions & Open Questions *(mandatory)*

- **Assumptions**:
  - Account types include checking, savings, credit card, loan, and other debt accounts.
  - Account owners enter absolute amounts in forms.
- **Open Questions**: None.
