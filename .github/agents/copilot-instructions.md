# homemanage Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-02-09

## Active Technologies
- Python 3.11 (per constitution) with Django 6.0.2 + Django 6.0.2, django-htmx 1.27.0, django-cotton 2.6.1, Tailwind CLI 4.1.18 + DaisyUI 5.5.17 (watcher via `npm run dev:css`), psycopg 3.3.x for PostgreSQL. All already present; no new runtime packages allowed. (001-accounts-home)
- PostgreSQL (prod/staging) with migrations authored in `financial/migrations`; local dev can continue using SQLite but migrations must remain PostgreSQL-compatible (expression index for case-insensitive uniqueness). (001-accounts-home)
- Python (project assumes 3.11+ per constitution) + Django 6.0.2, django-htmx 1.27.0, django-cotton 2.6.1 (001-account-transactions)
- SQLite for local/dev/tests (`db.sqlite3` in repo); production DB may vary (out of scope) (001-account-transactions)
- Python 3.11 with Django 6.0.2 + Django 6.0.2, django-htmx 1.27.0, django-cotton 2.6.1, Tailwind CLI 4.1.18 + DaisyUI 5.5.17, psycopg 3.3.x (already present) (001-account-transaction-evolution)
- PostgreSQL for dev/prod, SQLite for tests via `core.settings_test` (001-account-transaction-evolution)
- Python 3.11+, Django 6.0.2 + Django, django-htmx, django-cotton, Tailwind CLI + DaisyUI (existing only; no new dependencies) (001-add-household-container)
- SQLite for tests/local deterministic runs (`core.settings_test`), PostgreSQL-compatible schema semantics for production (001-add-household-container)
- Python 3.11+, Django 6.x templates + HTMX + Django auth, Django ModelForms, HTMX, Tailwind CSS + DaisyUI (existing) (001-household-admin-settings)
- SQLite for local/tests (`core.settings_test`), production engine unchanged (001-household-admin-settings)
- Python 3.11+, Django 6.0.x, HTML templates with HTMX + Django, django-htmx, django-cotton, Python stdlib `csv` (no new runtime package) (001-account-import)
- SQLite (local/tests via `core.settings_test`), production DB compatible via Django ORM (001-account-import)
- Python 3.11+ + Django 6.0.2, django-htmx 1.27.0, django-cotton 2.6.1 (existing only) (001-bill-pay)
- SQLite (`db.sqlite3`) for local/tests; production DB unchanged and out of feature scope (001-bill-pay)

- Python 3.11 + Django 5.0 (per starter settings) + Django ORM & templates, HTMX (already wired), django-cotton components, Tailwind + DaisyUI watcher (001-accounts-home)

## Project Structure

```text
src/
tests/
```

## Commands

cd src; pytest; ruff check .

## Code Style

Python 3.11 + Django 5.0 (per starter settings): Follow standard conventions

## Recent Changes
- 001-bill-pay: Added Python 3.11+ + Django 6.0.2, django-htmx 1.27.0, django-cotton 2.6.1 (existing only)
- 001-account-import: Added Python 3.11+, Django 6.0.x, HTML templates with HTMX + Django, django-htmx, django-cotton, Python stdlib `csv` (no new runtime package)
- 001-household-admin-settings: Added Python 3.11+, Django 6.x templates + HTMX + Django auth, Django ModelForms, HTMX, Tailwind CSS + DaisyUI (existing)


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
