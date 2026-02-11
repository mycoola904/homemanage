# Data Model — Account and Transaction Evolution

## Entity: Account
- **Table**: `financial_account`
- **Primary Key**: `id UUID`
- **Ownership**: `user_id` FK → `auth_user.id`

| Field | Type | Constraints & Validation | Notes |
|------|------|--------------------------|-------|
| `id` | UUID | Primary key | immutable |
| `user` | FK → `auth.User` | Required | scope per user |
| `name` | CharField(255) | Required, unique per user (case-insensitive) | unchanged |
| `institution` | CharField(255) | Optional | unchanged |
| `account_type` | Choice | checking, savings, credit_card, loan, other | drives conditional fields |
| `account_number` | CharField | Optional | stored for all types; no backfill |
| `routing_number` | CharField | Optional | only for checking/savings; null otherwise |
| `interest_rate` | Decimal | Optional | only for credit_card/loan/other debt; null otherwise |
| `status` | Choice | active, closed, pending | unchanged |
| `current_balance` | Decimal(12,2) | Required | unchanged |
| `credit_limit_or_principal` | Decimal(12,2) | Optional | unchanged |
| `statement_close_date` | Date | Optional | unchanged |
| `payment_due_day` | PositiveSmallInteger | 1..31 when set | unchanged |
| `notes` | Text | Optional | unchanged |
| `created_at` | DateTime | `auto_now_add=True` | unchanged |
| `updated_at` | DateTime | `auto_now=True` | unchanged |

### Account Validation Rules
1. `routing_number` allowed only for checking/savings; set to null for other types.
2. `interest_rate` allowed only for credit_card/loan/other debt; set to null for checking/savings.
3. `account_number` optional; no backfill from `number_last4`.

## Entity: Category
- **Table**: `financial_category`
- **Primary Key**: `id UUID`
- **Ownership**: `user_id` FK → `auth_user.id`

| Field | Type | Constraints & Validation | Notes |
|------|------|--------------------------|-------|
| `id` | UUID | Primary key | immutable |
| `user` | FK → `auth.User` | Required | scope per user |
| `name` | CharField(255) | Required, unique per user when lowercased | preserve casing |
| `created_at` | DateTime | `auto_now_add=True` | audit |

### Category Validation Rules
1. Uniqueness enforced on `(user, lower(name))`.
2. Preserve original casing on write.

## Entity: Transaction
- **Table**: `financial_transaction`
- **Primary Key**: `id UUID`
- **Ownership**: `account_id` FK → `financial_account.id`

| Field | Type | Constraints & Validation | Notes |
|------|------|--------------------------|-------|
| `id` | UUID | Primary key | immutable |
| `account` | FK → `Account` | Required | cascade on delete |
| `posted_on` | Date | Required | unchanged |
| `description` | CharField(255) | Required | unchanged |
| `transaction_type` | Choice | deposit, expense, transfer, adjustment, payment, charge | restricted by account type |
| `amount` | Decimal(10,2) | Input must be positive; stored with deterministic sign | derived from matrix |
| `category` | FK → `Category` | Optional | nullable |
| `notes` | Text | Optional | unchanged |
| `created_at` | DateTime | `auto_now_add=True` | unchanged |

### Transaction Validation Rules
1. Input amount must be positive and non-zero.
2. Allowed `transaction_type` choices depend on `account_type`.
3. Stored `amount` sign is derived from account type + transaction type matrix.

### State/Transition Notes
- No soft-delete states; deletion removes rows.
- Transfers are outgoing from the selected account; incoming transfers recorded as deposits.