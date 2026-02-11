# PR Checklist — Accounts Home

Use this checklist when preparing the PR for the Accounts Home feature. Update the evidence column with links to logs, screenshots, or test runs.

| Item | Status | Evidence |
|------|--------|----------|
| `/accounts/` index renders deterministic ordering + empty state | ✅ | Verified against fixtures via `python manage.py loaddata financial/fixtures/accounts_minimal.json` and passing index tests in [financial/tests/test_accounts_index.py](financial/tests/test_accounts_index.py). |
| Preview HTMX flow swaps `#account-preview-panel` with concurrency guards | ✅ | Covered by [financial/tests/test_accounts_preview.py](financial/tests/test_accounts_preview.py) and manual review of watcher output recorded on 2026-02-10 (`npm run dev:css`). |
| Edit + validation errors stay inside preview panel | ✅ | Passing tests in [financial/tests/test_accounts_edit.py](financial/tests/test_accounts_edit.py); verified form partial [financial/templates/financial/accounts/_form.html](financial/templates/financial/accounts/_form.html) uses shared panel target. |
| Delete confirmation removes rows and clears preview | ✅ | Covered by [financial/tests/test_accounts_delete.py](financial/tests/test_accounts_delete.py); fragment wiring documented in [financial/views.py](financial/views.py). |
| `GET /accounts/<uuid>/` detail page renders metadata + placeholder | ✅ | Exercised via [financial/tests/test_accounts_detail.py](financial/tests/test_accounts_detail.py) and manual template audit of [financial/templates/financial/accounts/detail.html](financial/templates/financial/accounts/detail.html). |
| Flash messaging + Add Account CTA | ✅ | Confirmed through existing `AccountCreateView` flow and index template review. |
| Tailwind watcher log + regenerated CSS committed | ✅ | `npm run dev:css` log (tailwindcss v4.1.18, DaisyUI 5.5.17) and `npm run build:css` (Done in 401ms on 2026-02-10). |
| Automated test evidence attached | ✅ | `python manage.py test financial.tests --settings=core.settings_sqlite` (13 passing) due to PostgreSQL permission limits. |
