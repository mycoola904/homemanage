# Data Model: Account Transactions

Date: 2026-02-11  
Spec: specs/001-account-transactions/spec.md

## Entities

### Account (existing)

- Owned by exactly one authenticated user (`Account.user`).
- Transactions are always accessed through an Account and MUST be scoped by account ownership.

### Transaction (new)

Represents a single account activity entry that can be listed and created from the Account detail page.

#### Fields

- `id`: UUID primary key (or default Django PK if project conventions require; preferred: UUID for consistency with `Account.id`).
- `account`: FK → `financial.Account` (required), `on_delete=CASCADE`.
- `posted_on`: `DateField` (required). Defaults to server-side "today" when rendering the add form.
- `description`: `CharField` (required).
- `direction`: `TextChoices` enum: `debit` | `credit` (required).
- `amount`: `DecimalField(max_digits=10, decimal_places=2)` (required, must be > 0).
- `notes`: `TextField(blank=True)` (optional).
- `created_at`: `DateTimeField(auto_now_add=True)` (required).

#### Validation rules

- `amount` MUST be positive (strictly greater than 0).
- `description` MUST be non-empty after trimming.
- `posted_on` MUST be present.
- `direction` MUST be one of `debit|credit`.

#### Display rules

- Amount display is derived:
  - debit → `-$amount`
  - credit → `+$amount`
- Transactions table columns: Posted On, Description, Amount (signed).

## Ordering

Deterministic ordering for an account’s transactions:

- `posted_on` descending
- `created_at` descending
- `id` descending

## Indexes

Create an index to support account-scoped ordering:

- Composite index on `(account_id, posted_on, created_at, id)`

Note: Direction (ASC/DESC) support varies by DB; the index is for query support, while deterministic ordering is enforced by explicit `order_by`.

## State transitions

- MVP supports CREATE only (no edit/delete).
