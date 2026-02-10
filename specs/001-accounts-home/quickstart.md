# Quickstart — Accounts Home Feature

## Prerequisites
1. Install Python deps: `pip install -r requirements.txt`.
2. Install Node deps (already vendored via npm 10+): `npm install` (first run only).
3. Ensure PostgreSQL connection variables are configured in `.env` (DATABASE_URL or separate settings).

## Setup Steps
1. **Apply migrations**
   - `python manage.py makemigrations financial`
   - `python manage.py migrate`
   - Observe: new `financial_account` table exists; `manage.py showmigrations financial` shows `0001_initial` applied.
2. **Load deterministic fixtures**
   - `python manage.py loaddata financial/fixtures/accounts_minimal.json`
   - Observe: 3 accounts (checking, credit_card, loan) owned by your test user.
3. **Run Tailwind watcher**
   - In a separate terminal: `npm run dev:css`
   - Observe: watcher logs rebuilds when templates/classes change.
4. **Start Django dev server**
   - `python manage.py runserver`
   - Log in with an existing user; navigate to `/accounts/`.

## Verification Flow
1. **Index rendering**: `/accounts/` shows deterministic ordering (account_type → name → created_at) and empty-state when fixture removed.
2. **Preview interaction**: Click Preview on each row. Confirm:
   - Request hits `/accounts/<uuid>/preview/` with `hx-request="queue:last"` and swaps `#account-preview-panel`.
   - Values match fixture data and USD formatting.
3. **Edit workflow**: Click Edit → form loads into preview panel. Submit valid edits (expect preview refresh) and invalid data (expect 422 fragment with errors).
4. **Detail page**: Click Open → `/accounts/<uuid>/` renders with base layout + "Transactions (Coming Soon)" placeholder.
5. **Delete workflow**: Trigger Delete → confirm partial returned → POST to delete endpoint removes row and clears preview if it referenced the deleted account.

## Testing
- Run automated suite: `python manage.py test financial`
- Observe: model constraint tests, HTMX view tests, and template rendering tests pass deterministically.
- Run the `/accounts/` performance benchmark (e.g., `python manage.py test financial.tests.test_accounts_performance`) and record the measured render time; fail the test if it exceeds 2 seconds to enforce the Success Criteria.

## Rollback Plan
1. `python manage.py migrate financial zero`
2. Drop fixture data if loaded (`DELETE FROM financial_account;`).
3. Re-run migrations + fixtures as needed; UUID PKs regenerate deterministically via fixtures.
