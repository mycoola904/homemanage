# Quickstart — Household Top-Level Container (MVP)

## 1) Verify environment and watcher
- Run: `python --version`
- Run: `npm run dev:css`
- What to observe: Python is 3.11+ and Tailwind watcher starts without errors, emitting rebuild output when template/CSS files change.

## 2) Apply schema changes from a fresh database (Path A)
- Run: `Remove-Item .\db.sqlite3 -ErrorAction Ignore`
- Run: `python manage.py migrate --settings=core.settings_test`
- What to observe: Migrations apply cleanly on a fresh SQLite database with no missing dependency errors.

## 3) Seed deterministic households and finance data
- Run: `python manage.py seed_households --settings=core.settings_test`
- What to observe: Seed command reports creation (or idempotent presence) of:
  - `Our Household`
  - `Mother-in-law Household`
  and creates distinct accounts/transactions for each household.

## 4) Start app and validate top-level routing
- Run: `python manage.py runserver`
- What to observe:
  - Login redirects to `/household/` for users with memberships.
  - `/household/` shows module launcher.
  - Finance launcher navigates to `/household/finance/` via standard route navigation.

## 5) Validate household switching flow
- Action: Use navbar household switcher to change household.
- What to observe:
  - Session `current_household_id` changes.
  - User is redirected to `/household/`.
  - Previously visible household data is no longer visible.

## 6) Validate guard behavior
- Action: Attempt to access account/transaction IDs from another household directly.
- What to observe: Response is 404 (preferred) with no cross-household object existence leak.

## 7) Validate transaction household invariants
- Action: Create/edit transactions under finance views, including account change attempts.
- What to observe:
  - Saved transaction household always equals selected account household.
  - Edits selecting an account outside current household are rejected.

## 8) Run deterministic test suite under SQLite
- Run: `python manage.py test --settings=core.settings_test`
- What to observe: Household and financial tests pass with SQLite test settings.

## 9) Migration and seed repeatability check
- Run steps 2 and 3 again.
- What to observe: Migration + seed workflow remains repeatable and deterministic.
