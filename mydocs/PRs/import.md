**PR Title**  
Household account CSV import with strict validation, template download, and atomic writes

**PR Description**  
## Summary
- Adds a new finance import flow to upload account data from CSV into the active household.
- Enforces strict CSV contract validation (exact header order, canonical enums, ISO date, URL format, size and row limits).
- Ensures all-or-nothing persistence so partial imports never occur on validation failures.
- Adds a deterministic downloadable CSV template aligned to importer expectations.
- Extends account schema with optional online access URL support.

## User Impact
- Users can open **Import** from Finance navigation and upload a CSV.
- Successful imports show a summary count.
- Invalid imports return actionable row-level errors with no records saved.

## Technical Changes
- Added `online_access_url` field to Account and migration.
- Added `AccountImportForm` for CSV upload validation (CSV-only + max 5MB).
- Added import service for parsing/validation/import:
  - exact header/order check
  - canonical value checks
  - duplicate detection (batch + active household, case-insensitive)
  - max 1000 row guard
  - atomic save transaction
- Added endpoints:
  - `GET /financial/import/`
  - `GET /financial/import/panel/`
  - `POST /financial/import/`
  - `GET /financial/import/template/`
- Added import page/panel templates and finance sidebar Import link.
- Added fixture template CSV with contract header order and sample row.
- Added/updated feature docs, task completion, and validation evidence.

## Testing
- `python manage.py test financial.tests.test_account_import financial.tests.test_account_import_validation financial.tests.test_account_import_template --settings=core.settings_test`
  - Result: **Ran 14 tests, OK**
- `python manage.py test financial.tests --settings=core.settings_test`
  - Result: **Ran 111 tests, OK**

## Validation Evidence
- 1,000-row import performance run: **2.241s** (target <10s).
- First-time template-based protocol trials: **10/10 successful** (100%).

## Migration / Deployment Notes
- Apply migration adding `online_access_url` before using the import flow in non-test environments.
- No new runtime dependencies introduced (Python stdlib CSV only).

## Checklist
- [x] Feature implemented per spec/plan/tasks
- [x] Tests passing
- [x] Migration included
- [x] Validation/performance evidence recorded
- [x] No new runtime dependencies