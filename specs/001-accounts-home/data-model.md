# Data Model — Accounts Home

## Entity: Account
- **Table**: `financial_account`
- **Primary Key**: `id UUID` (uuid4, database default)
- **Ownership**: `user_id` FK → `auth_user.id`, `on_delete=CASCADE`, unique scope for names via `(user_id, lower(name))`.
- **Ordering**: Default ordering `(account_type, name, created_at)` to satisfy deterministic list rendering.

| Field | Type | Constraints & Validation | Default/Notes |
|-------|------|--------------------------|---------------|
| `id` | UUID | Primary key, generated via `uuid.uuid4`, immutable | n/a |
| `user` | FK → `auth.User` | Required, cascades on delete; queryset always filtered to `request.user` | scopes account set |
| `name` | CharField (255) | Required, trimmed, unique per user when lowercased | displayed in table + preview |
| `institution` | CharField (255) | Optional | shown on index/detail |
| `account_type` | ChoiceField | Enum: checking, savings, credit_card, loan, other | drives sorting + badge styling |
| `number_last4` | CharField (4) | Optional, digits validation if provided | preview/detail only |
| `status` | ChoiceField | Enum: active (default), closed, pending | influences badge classes |
| `current_balance` | Decimal(12,2) | Required, `MinValueValidator(Decimal("-9999999999.99"))` | default `Decimal("0.00")` |
| `credit_limit_or_principal` | Decimal(12,2) | Optional, only for credit_card/loan; allow null/blank | preview shows when set |
| `statement_close_date` | Date | Optional, validated as calendar date | preview only |
| `payment_due_day` | PositiveSmallInteger | Optional, `1 <= value <= 31` enforced in `clean()` | preview only |
| `notes` | TextField | Optional | preview/detail |
| `created_at` | DateTime | `auto_now_add=True`, timezone-aware | used in ordering |
| `updated_at` | DateTime | `auto_now=True` | concurrency indicator |

### Derived/Helper Structures
- **Enums**:
  - `AccountType`: `checking`, `savings`, `credit_card`, `loan`, `other`.
  - `AccountStatus`: `active`, `closed`, `pending`.
- **Serializers/View helpers**: Create `AccountSummaryRow` dataclass to pass to django-cotton table component (fields: `id`, `name`, `institution`, `account_type_label`, `status_badge`, `current_balance_display`).
- **Preview DTO**: Provide dictionary with optional fields filtered to spec-defined preview columns.

### Validation Rules
1. `(user, Lower(name))` uniqueness enforced by `UniqueConstraint`.
2. `payment_due_day` must be between 1 and 31 when supplied; enforced in `clean()` + form validation.
3. `credit_limit_or_principal` only required for credit_card/loan when displayed; forms allow null but ensure formatting in preview.
4. All decimal fields use `Decimal` for deterministic arithmetic.
5. `status` defaults to `active` on create per clarification.

### State Transitions
- `status`: default `active` → may change to `closed` or `pending` via edit form. `closed` accounts remain visible until deleted. No transitions back to `active` are blocked; forms permit all enumerated states.
- Deletion: POST `/accounts/<uuid>/delete/` performs hard delete; no soft delete states exist.

### Relationships & Future Expansion Notes
- `Account` currently stands alone but future `Transaction` and `Budget` models will reference it via FK. Ensure cascade delete semantics remain acceptable.
- No Household model allowed; if introduced later, migrations will update FK while preserving UUID primary key to maintain referential integrity.
