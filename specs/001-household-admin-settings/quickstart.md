# Quickstart — Household Admin Settings

## 1) Prerequisites
- Python environment configured and dependencies installed.
- Node dependencies installed for Tailwind/DaisyUI watcher.

## 2) Start CSS watcher (required before UI checks)
- Run: `npm run dev:css`
- Expected: rebuild output appears on class/template changes (for example, logs indicating build/watch started, then a successful rebuild after saving template or CSS changes).
- Verification note: capture at least one initial startup line and one subsequent rebuild line in terminal output before debugging style/layout issues.

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
- Focused command used:
  - `python manage.py test financial.tests.test_nav_auth_visibility financial.tests.test_admin_settings_access financial.tests.test_admin_households financial.tests.test_admin_user_creation financial.tests.test_admin_memberships --settings=core.settings_test`
- Full-suite command used:
  - `python manage.py test --settings=core.settings_test`
- Expected results:
  - Focused suite passes with all spec feature tests green.
  - Full suite passes without regressions.

## 7) Determinism checks
- Run migration drift check:
  - `python manage.py makemigrations --check --dry-run --settings=core.settings_test`
  - Expected: `No changes detected`
- Verify migration file diff scope:
  - `git diff --name-only -- households/migrations financial/migrations`
  - Expected: no output for this feature
- Fixture idempotency verification:
  - `git diff --name-only -- financial/fixtures`
  - Expected: no output unless fixture updates are intentionally introduced
  - If fixture files change in future work, verify idempotency by applying fixture twice on a clean DB and confirming no duplicate/unexpected records.

## 8) Validation snapshot (2026-02-13)
- Focused feature suite: `25` tests passed.
- Full suite: `96` tests passed.
- Migration drift check: `No changes detected`.
- Feature migration/fixture file diffs: none.
