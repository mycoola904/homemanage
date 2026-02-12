# Data Model — Household Top-Level Container (MVP)

## Entity: Household
- **Purpose**: Top-level tenant container for module scoping.
- **Table**: `financial_household` (or equivalent app table naming based on model placement).

| Field | Type | Rules |
|---|---|---|
| `id` | UUID / BigAuto (project convention) | Primary key |
| `name` | CharField | Required, non-empty |
| `slug` | SlugField | Optional in UI, auto-generated, immutable, unique |
| `is_archived` | BooleanField | Default `False`; archived households are not selectable as active session household |
| `timezone` | CharField | Optional; defaults to project timezone if blank |
| `currency_code` | CharField | Default `USD` |
| `created_by` | FK `auth.User` | Nullable for backfills/system seeds |
| `created_at` | DateTime | Auto timestamp |
| `updated_at` | DateTime | Auto timestamp |

Validation rules:
1. `slug` uniqueness is global.
2. `currency_code` defaults to `USD` for deterministic formatting.
3. Archived households are excluded from switcher options and active selection.

State transitions:
- `active -> archived` allowed for deactivation.
- `archived -> active` allowed by admin/owner workflow.

## Entity: HouseholdMember
- **Purpose**: Membership and role mapping between users and households.
- **Table**: `financial_householdmember`.

| Field | Type | Rules |
|---|---|---|
| `id` | UUID / BigAuto | Primary key |
| `household` | FK `Household` | Required |
| `user` | FK `auth.User` | Required |
| `role` | CharField | Enum: `owner`, `admin`, `member`; default `member` |
| `is_primary` | BooleanField | Default `False`; at most one primary membership per user |
| `created_at` | DateTime | Auto timestamp |
| `updated_at` | DateTime | Auto timestamp |

Validation rules:
1. Unique membership per `(household, user)`.
2. At most one `is_primary=True` row per `user`.
3. Each household must retain at least one `owner` membership.

State transitions:
- Role may change (`member/admin/owner`) with owner-preservation guard.
- Membership deletion blocked if it would remove final owner.

## Entity Update: Account
- **Existing table**: `financial_account`.
- **New field**: `household` FK to `Household` (required after migration sequence).

Rules:
1. Account queries in views/services filter by `household_id=current_household_id`.
2. Object fetch guards return 404 when account household != current session household.

## Entity Update: Transaction
- **Existing table**: `financial_transaction`.
- **New field**: `household` FK to `Household` (required after migration sequence).

Rules:
1. `transaction.household` is derived from `transaction.account.household` at save-time.
2. Transaction edit may change account only if selected account is in `current_household`.
3. Invariant enforced: `transaction.household_id == transaction.account.household_id`.

## Session Context: Current Household
- **Key**: `current_household_id` stored in session.
- **Selection on login**:
  1. single membership -> that household
  2. multi-membership with one primary -> primary household
  3. otherwise -> first deterministic membership ordering
  4. zero memberships -> no-household page (403)

- **Runtime guard**:
  - If session household archived/invalid, fallback to next eligible non-archived membership.
  - If none eligible, redirect to no-household-access (403).

## Referential Integrity Summary
1. `Account.household` references existing household.
2. `Transaction.account` references existing account.
3. `Transaction.household` references existing household and must match `Transaction.account.household`.
4. Household-scoped object endpoints never expose objects from other households.
