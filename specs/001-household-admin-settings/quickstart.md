# Quickstart — Household Admin Settings

## 1) Prerequisites
- Python environment configured and dependencies installed.
- Node dependencies installed for Tailwind/DaisyUI watcher.

## 2) Start CSS watcher (required before UI checks)
- Run: `npm run dev:css`
- Expected: rebuild output appears on class/template changes.

## 3) Apply database migrations
- Run: `python manage.py migrate`
- Expected: migrations apply with no pending model diffs.

## 4) Create/verify global admin user
- Run: `python manage.py createsuperuser` (if needed)
- Expected: superuser can authenticate and is treated as global Administrator (MVP rule).

## 5) Manual acceptance flow
1. Log out and verify nav shows Login and hides modules (including Finance).
2. Log in as superuser and verify Settings nav appears.
3. In Settings, create a household.
4. Create a user login account with valid username/email/password and select one or more households.
5. Verify account creation is blocked if no household selected.
6. Verify duplicate username/email and weak passwords return validation errors.
7. Add and remove household memberships for an existing user.
8. Verify non-admin user cannot access Settings URL directly.

## 6) Test execution (targeted first)
- Run focused tests for:
  - auth-based nav visibility
  - settings access control
  - household creation validation
  - user creation with required memberships
  - membership add/remove idempotency
- Then run broader suite: `python manage.py test`

## 7) Determinism checks
- Re-run migrations on clean DB to confirm reproducibility.
- Verify fixtures/seeding are idempotent if updated.
- Confirm no unintended model/migration diffs.
