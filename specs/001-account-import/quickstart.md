# Quickstart: Household Account Import

## 1) Preconditions
- Branch: `001-account-import`
- Python environment activated
- Database migrated
- Tailwind watcher running before CSS debugging:
  - `npm run dev:css`

## 2) Implement schema change
1. Add `online_access_url` to `financial.models.Account` as URL field (blank allowed).
2. Create migration and apply it.
3. Verify migration rollback/forward is clean.

Expected result:
- `Account` supports online access URL storage and validation.

## 3) Add import routes and views
1. Add URL routes:
   - `GET /financial/import/`
   - `GET /financial/import/panel/`
   - `POST /financial/import/`
   - `GET /financial/import/template/`
2. Implement view handlers with active household resolution.
3. Implement CSV parser/validator using stdlib `csv`.
4. Enforce limits: max 5 MB, max 1,000 data rows.
5. Enforce all-or-nothing insert via `transaction.atomic()`.

Expected result:
- Valid CSV imports create accounts for active household only.
- Invalid CSV returns errors with no inserts.

## 4) Build templates and sidebar integration
1. Add import page and panel templates under `financial/templates/financial/accounts/`.
2. Add finance sidebar import link.
3. Ensure stable HTMX containers:
   - navigation target: `#financial-main-content`
   - form target: `#account-import-panel`
   - swap mode: `innerHTML`
4. Keep conditional classes server-computed.

Expected result:
- Clicking Import shows form in main finance content area.
- Form posts and re-renders panel with summary/errors.

## 5) Add template CSV artifact
1. Add tracked template CSV under `financial/fixtures/account_import_template.csv`.
2. Header order must match contract:
   - `name,institution,account_type,account_number,routing_number,interest_rate,status,current_balance,credit_limit_or_principal,statement_close_date,payment_due_day,online_access_url,notes`
3. Wire download endpoint to return this file.

Expected result:
- Template download is deterministic and matches importer expectations.

## 6) Tests
1. Add tests for:
   - successful import
   - unsupported format / missing headers / row validation errors
   - duplicate detection (household case-insensitive)
   - file size and row limits
   - household scoping
   - template download contract
2. Run targeted tests first, then broader financial suite.

Commands:
- `python manage.py test financial.tests.test_account_import --settings=core.settings_test`
- `python manage.py test financial.tests --settings=core.settings_test`

Expected result:
- Tests fail first for unimplemented behavior, then pass after implementation.

## 7) PR evidence checklist
- Link spec/plan/tasks artifacts.
- Include migration summary + deterministic test evidence.
- Include prompt/response references used for AI-assisted changes.
