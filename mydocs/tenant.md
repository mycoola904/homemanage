Build a spec to refactor this Django project so `Household` becomes a top-level tenant boundary app (option 1: destructive refactor; OK to delete/recreate DB; regenerate migrations). The end state must keep the current UX/behavior identical (session-scoped active household, switching UI, finance scoping/guards), but move all household concepts out of financial into a new dedicated app.

Context (current repo state):
- `Household` and `HouseholdMember` models live in models.py.
- Household selection/switching/session logic lives in households.py and is used by views.py and views.py.
- Global template context `current_household` and `available_households` is provided by context_processors.py and configured in settings.py.
- Routes: `/household/` (home), `/household/switch/`, `/household/no-access/` in pages; finance is mounted at `/household/finance/` and every finance view scopes by resolved household.
- There is a migration-history-specific test at test_migrations_backfill.py that asserts behaviors across historical migrations (this will need to be removed or rewritten since we are regenerating migrations).

Goal:
- Create a new Django app named `households` (or `tenancy` if that fits better; pick one and use it consistently) that owns:
  - `Household` model
  - `HouseholdMember` model (roles + primary membership constraint)
  - household session selection/switching utilities (currently households.py)
  - context processor (currently context_processors.py)
- Update all references across the codebase to import from the new app.
- Update settings.py:
  - add the new app to `INSTALLED_APPS`
  - change the context processor path to the new app’s context processor
- Update financial models to FK to the new `Household` model:
  - `Account.household` and `Transaction.household`
  - ensure the existing invariants remain: `Transaction.household` derived from its `Account.household`, and cross-household edits are rejected
- Update views.py to use the new app’s household resolver/switch logic and model imports.
- Update tests:
  - change imports from `financial.models import Household, HouseholdMember` to `households.models import Household, HouseholdMember`
  - ensure all existing tests continue to pass with identical behavior
  - remove/replace test_migrations_backfill.py since migration history is being regenerated (do not keep a test that depends on old migration names)
- Migrations strategy (destructive allowed):
  - regenerate migrations cleanly for financial and the new `households` app
  - ok to delete existing migration files and create new initial migrations that reflect the new structure
  - include in the spec explicit commands a developer will run locally to reset DB and apply migrations (e.g., delete sqlite db if used; if Postgres, drop/recreate db; then `makemigrations` and `migrate`)
- Non-goals:
  - no new UX pages, no new features
  - do not change template structure beyond import/path changes; keep current navbar household switcher and finance link working
  - do not add new dependencies

Acceptance criteria:
1) App structure:
   - new `households/` app exists with models.py, apps.py, households.py (or similar), and context_processors.py.
2) Settings:
   - settings.py references the new context processor and includes the app.
3) Behavior:
   - login selects a household deterministically (prefers primary) and stores `current_household_id` in session
   - switching household via POST to `/household/switch/` updates session and redirects home
   - archived household in session falls back to an active membership
   - users with no active memberships are redirected to no-access and see 403 on the no-access page
   - finance views only show accounts/transactions for the active household; cross-household access returns 404; cross-household transaction edit is rejected (same as existing tests)
4) Tests:
   - all tests pass after the refactor, except the migration-history test which must be removed or replaced with a non-migration behavioral test.

Deliverables the spec should produce:
- A step-by-step implementation checklist (file-by-file)
- Any new files to create and existing files to edit/remove
- A testing plan (which commands to run) and what success looks like