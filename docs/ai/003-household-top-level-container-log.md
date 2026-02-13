# 003 Household Top-Level Container — AI Log

## Prompt References
- speckit.tasks generation and remediation sessions
- speckit.implement execution session

## Key Decisions
- Canonical Tailwind watcher command standardized to `npm run dev:css`
- Household is the active top-level context and finance is mounted at `/household/finance/`
- Session key `current_household_id` drives scoped query behavior

## Implementation Notes
- Added `Household` and `HouseholdMember` models
- Added household FKs to `Account` and `Transaction`
- Added deterministic seed command `seed_households`
- Added household routes (`/household/`, `/household/switch/`, `/household/no-access/`)

## Validation Evidence
- `manage.py makemigrations --settings=core.settings_test --noinput` (no changes after migration creation)
- `manage.py migrate --settings=core.settings_test --noinput` (success)
- `manage.py seed_households --settings=core.settings_test` (success)
- Focused tests:
  - `financial.tests.test_accounts_index`
  - `financial.tests.test_account_transactions_add`
  - household-focused new tests (added in this feature)

## Fail-First Evidence (T051)
- Pre-creation baseline command:
  - `python manage.py test financial.tests.test_household_login_selection financial.tests.test_household_archived_fallback financial.tests.test_household_home financial.tests.test_household_finance_routing financial.tests.test_household_navigation_menus financial.tests.test_household_transactions_scope financial.tests.test_household_object_guards financial.tests.test_household_transaction_invariants financial.tests.test_household_switching_context_reset financial.tests.test_household_seed --settings=core.settings_test`
- Observed result before implementation:
  - `FAILED (errors=10)`
  - `ModuleNotFoundError` for each not-yet-created test module listed above
