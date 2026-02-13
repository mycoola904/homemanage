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

## 8) Validation notes (Phase 6 evidence)
- **T035 schema/header parity check**:
   - Verified schema-change wording in `specs/001-account-import/spec.md` reflects migration-backed `online_access_url`.
   - Verified FR-005a header list equals contract/template header order.
   - Scripted parity result: `HEADER_PARITY_OK=True`.
- **T038 test evidence**:
   - `python manage.py test financial.tests.test_account_import financial.tests.test_account_import_validation financial.tests.test_account_import_template --settings=core.settings_test`
      - Result: `Ran 14 tests ... OK`
   - `python manage.py test financial.tests --settings=core.settings_test`
      - Result: `Ran 111 tests ... OK`
- **T041 performance evidence (SC-002)**:
   - Scripted 1,000-row import result: `PERF_ROWS=1000; PERF_IMPORTED=1000; PERF_SECONDS=2.241`
   - Threshold check: `2.241s < 10s` ✅
- **T042 SC-003 protocol evidence**:
   - Ran 10 first-time template-based scripted import trials (new user + first upload each trial).
   - Result: `SC3_TRIALS=10; SC3_SUCCESSES=10; SC3_SUCCESS_RATE=100.00%`
   - Threshold check: `100% >= 90%` ✅

## 9) AI traceability notes
- Planning/spec prompts referenced:
   - `.github/prompts/speckit.specify.prompt.md`
   - `.github/prompts/speckit.clarify.prompt.md`
   - `.github/prompts/speckit.plan.prompt.md`
   - `.github/prompts/speckit.tasks.prompt.md`
   - `.github/prompts/speckit.analyze.prompt.md`
   - `.github/prompts/speckit.implement.prompt.md`
- Implementation generated/updated artifacts tied to those prompts:
   - `specs/001-account-import/spec.md`
   - `specs/001-account-import/plan.md`
   - `specs/001-account-import/tasks.md`
   - `specs/001-account-import/research.md`
   - `specs/001-account-import/data-model.md`
   - `specs/001-account-import/contracts/account-import.openapi.yaml`
