# Data Model — Household Admin Settings

## Entity: AdministratorAuthorization (policy concept)
- Purpose: Represents whether a logged-in user can access global Settings administration features.
- Backing data (MVP): Django auth user with `is_superuser=True`.
- Future-compatible backing: explicit permission/group check in addition to superuser.
- Validation rules:
  - User must be authenticated.
  - User must satisfy global admin policy.
- State transitions:
  - `not-authorized -> authorized` when user gains superuser/approved permission.
  - `authorized -> not-authorized` when privilege is removed; access revoked immediately.

## Entity: Household
- Purpose: Top-level tenant/home grouping for scoped data access.
- Key fields:
  - `id` (UUID)
  - `name` (string, required)
  - `slug` (string, unique)
  - `is_archived` (boolean)
  - `created_by` (FK to auth user, nullable)
  - `created_at`, `updated_at`
- Validation rules:
  - Name required.
  - Name uniqueness by normalized value (trim + case-insensitive).
- Relationships:
  - One-to-many with `HouseholdMembership`.

## Entity: UserLoginAccount
- Purpose: Auth identity created in Settings for local app login.
- Backing data: Django auth user.
- Key fields (business-relevant):
  - `username` (unique)
  - `email` (unique, case-insensitive normalization per form validation)
  - `password` (set directly at creation)
  - `is_active`
- Validation rules:
  - Username required and unique.
  - Email required and unique.
  - Password must pass configured password validators.
  - Must be assigned to >= 1 household at creation.
- Relationships:
  - One-to-many with `HouseholdMembership`.

## Entity: HouseholdMembership
- Purpose: Association of user login account to one household with optional role/primary semantics.
- Key fields:
  - `id` (UUID)
  - `household` (FK Household)
  - `user` (FK auth user)
  - `role` (owner/admin/member)
  - `is_primary` (bool)
  - `created_at`, `updated_at`
- Validation rules:
  - Unique `(household, user)` pair.
  - `is_primary=True` uniqueness per user.
  - Membership add operation idempotent for duplicate submissions.
- State transitions:
  - `absent -> present` on add.
  - `present -> absent` on remove.
  - Membership changes apply immediately to authorization and household resolution.

## Aggregate/Workflow Rules
- User creation workflow:
  1. Validate admin authorization.
  2. Ensure at least one household exists.
  3. Validate user credentials.
  4. Persist auth user.
  5. Persist one-or-more household memberships atomically.
- Household creation workflow:
  1. Validate admin authorization.
  2. Validate normalized household name uniqueness.
  3. Persist household and return updated list.
- Navigation visibility workflow:
  - Unauthenticated: show Login; hide modules.
  - Authenticated non-admin: hide Settings.
  - Authenticated admin: show Settings.
