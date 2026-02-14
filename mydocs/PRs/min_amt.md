**PR Title**
- Add liability-only minimum amount due to accounts and CSV import contract

**Summary**
- Adds `minimum_amount_due` to Account and enforces that it is only valid for liability account types (`credit_card`, `loan`, `other`).
- Hides `minimum_amount_due` from non-liability account forms and returns clear validation errors if submitted for unsupported types.
- Extends CSV import/template contract to include the new column and maps it during import.

**Changed Files**
- Model + validation: models.py
- Migration: 0003_account_minimum_amount_due.py
- Form visibility + validation: forms.py
- CSV importer contract/mapping: account_import.py
- Template CSV: account_import_template.csv
- Tests: test_account_fields.py, test_account_import.py, test_account_import_validation.py, test_account_import_template.py

**Testing**
- Ran targeted suite: `manage.py test financial.tests.test_account_fields financial.tests.test_account_import financial.tests.test_account_import_validation financial.tests.test_account_import_template --settings=core.settings_test`
- Result: 19 tests passed.

**Migration Note**
- Apply migration `financial.0003_account_minimum_amount_due` before using this change in non-test environments.