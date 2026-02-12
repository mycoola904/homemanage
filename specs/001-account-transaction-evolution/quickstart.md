# Quickstart — Account and Transaction Evolution

## Prerequisites
1. Install Python deps: `pip install -r requirements.txt`.
2. Install Node deps (first run only): `npm install`.

## Setup Steps
1. **Apply migrations**
   - `python manage.py makemigrations financial`
   - `python manage.py migrate`
   - Observe: new fields and Category table exist; `manage.py showmigrations financial` shows new migrations applied.
2. **Run Tailwind watcher (when editing templates)**
   - `npm run dev:css`
   - Observe: rebuild output appears when template classes change.
3. **Start Django dev server**
   - `python manage.py runserver`
   - Observe: `/accounts/` and account detail pages render with HTMX forms.

## Verification Flow
1. **Account edit validation**: Open account edit form for checking and credit card accounts.
   - Observe: routing number is visible only for checking/savings; interest rate only for credit card/loan/other debt.
2. **Transaction sign matrix**: Add transactions for each account type and verify stored amounts follow the deterministic sign matrix.
3. **Transaction add/edit HTMX**: Add a transaction, then edit it from the table.
   - Observe: `#account-transactions-body` swaps without a full page reload; the Add Transaction button remains visible.
4. **Inline category add**: Create a new category inline while adding a transaction.
   - Observe: dropdown updates without full page reload; duplicates (case-only) are rejected with errors.
5. **Account preview/edit/delete HTMX**: Use Preview, Edit, and Delete from the accounts table.
   - Observe: `#account-preview-panel` swaps without full page reload; delete updates the table and resets the preview panel.

## Testing
- Run suite with SQLite: `python manage.py test financial --settings=core.settings_test`
- Observe: migration backfill tests, sign matrix tests, and HTMX error tests pass.

## Rollback Plan
1. `python manage.py migrate financial zero`
2. Re-apply: `python manage.py migrate`
3. Validate tables and fields were recreated cleanly.