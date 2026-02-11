# homemanage Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-02-09

## Active Technologies
- Python 3.11 (per constitution) with Django 6.0.2 + Django 6.0.2, django-htmx 1.27.0, django-cotton 2.6.1, Tailwind CLI 4.1.18 + DaisyUI 5.5.17 (watcher via `npm run dev:css`), psycopg 3.3.x for PostgreSQL. All already present; no new runtime packages allowed. (001-accounts-home)
- PostgreSQL (prod/staging) with migrations authored in `financial/migrations`; local dev can continue using SQLite but migrations must remain PostgreSQL-compatible (expression index for case-insensitive uniqueness). (001-accounts-home)
- Python (project assumes 3.11+ per constitution) + Django 6.0.2, django-htmx 1.27.0, django-cotton 2.6.1 (001-account-transactions)
- SQLite for local/dev/tests (`db.sqlite3` in repo); production DB may vary (out of scope) (001-account-transactions)

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
- 001-account-transactions: Added Python (project assumes 3.11+ per constitution) + Django 6.0.2, django-htmx 1.27.0, django-cotton 2.6.1
- 001-accounts-home: Added Python 3.11 (per constitution) with Django 6.0.2 + Django 6.0.2, django-htmx 1.27.0, django-cotton 2.6.1, Tailwind CLI 4.1.18 + DaisyUI 5.5.17 (watcher via `npm run dev:css`), psycopg 3.3.x for PostgreSQL. All already present; no new runtime packages allowed.

- 001-accounts-home: Added Python 3.11 + Django 5.0 (per starter settings) + Django ORM & templates, HTMX (already wired), django-cotton components, Tailwind + DaisyUI watcher

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
