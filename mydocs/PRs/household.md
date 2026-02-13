I’ll compile a PR-ready summary from the actual modified files so the scope, evidence, and risk notes are accurate and copy-pasteable for your PR description.

Read changed files in the active git repository

**PR Title**
- Household admin settings: add admin-only settings workflows for households, users, and memberships

**Summary**
- Implements full Household Admin Settings feature end-to-end (US1–US4 + polish), including:
  - admin-only Settings access and navigation visibility
  - household creation with normalized duplicate validation
  - user creation with password validation and one-or-more household memberships
  - membership add/remove with idempotent behavior and owner-protection handling
- Completes and checks off all tasks in tasks.md.

**What Changed**
- **Authorization and routing**
  - Centralized global-admin policy in authorization.py
  - Added settings routes in household_urls.py
  - Added login guard fix for household home dispatch in views.py
  - Added settings visibility context in context_processors.py
- **Settings behavior**
  - Implemented settings endpoints and validation handling in views.py
  - Implemented household/user/membership service operations in settings.py
  - Added forms for household/user/membership operations in forms.py
- **UI/HTMX**
  - Added settings page and partials in index.html, _content.html, _household_panel.html, _household_form.html, _user_panel.html, _user_form.html, _membership_panel.html, _membership_row.html
  - Updated nav/sidebar gating in navbar.html and sidebar.html
- **Docs/contracts**
  - Updated contract to match implemented responses in settings-admin.openapi.yaml
  - Added validation/determinism evidence in plan.md and quickstart.md

**Test Evidence**
- Focused feature suite:
  - `python manage.py test financial.tests.test_nav_auth_visibility financial.tests.test_admin_settings_access financial.tests.test_admin_households financial.tests.test_admin_user_creation financial.tests.test_admin_memberships --settings=core.settings_test`
  - Result: 25 passed
- Full suite:
  - `python manage.py test --settings=core.settings_test`
  - Result: 96 passed
- Determinism checks:
  - `python manage.py makemigrations --check --dry-run --settings=core.settings_test` → No changes detected
  - No migration or fixture file diffs for this feature

**Risk/Notes**
- No schema migration changes in this PR; rollback is code-only reversion.
- Existing auth model remains MVP-based on superuser global-admin policy with centralized extension point.