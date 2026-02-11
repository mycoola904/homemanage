# Quickstart: Account Transactions

Date: 2026-02-11

## Prereqs

- Python environment with `requirements.txt` installed
- Node available for Tailwind CLI

## Run locally

1. Run DB migrations:

   - `python manage.py migrate`

2. Start Tailwind watcher (required for styling changes):

   - `npm run dev:css`

3. Start Django:

   - `python manage.py runserver`

## Manual test flow (matches spec scenarios)

1. Create an account
   - Visit `/accounts/new/`
   - Create a simple account (e.g., Checking)

2. View account detail
   - Open `/accounts/<uuid>/`
   - Confirm Transactions panel renders (empty state with Add button)

3. Add transaction (valid)
   - Click **Add Transaction**
   - Confirm form swaps into the transactions body
   - Save a valid transaction (defaults `posted_on` to today)
   - Confirm table re-renders with the new transaction

4. Add transaction (invalid)
   - Submit with missing/invalid fields
   - Confirm HTTP 422 and inline errors are displayed while the form remains visible

5. Cancel
   - From the form, click **Cancel**
   - Confirm the transactions body swaps back to the table/empty state

6. Missing/unowned
   - Request the transactions fragments for a missing/unowned account
   - Confirm an inline "not found" message in the panel body and no data revealed
