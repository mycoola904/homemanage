# Feature Specification: Household Top-Level Container (MVP)

**Feature Branch**: `001-add-household-container`  
**Created**: 2026-02-12  
**Status**: Draft  
**Input**: User description: "Introduce a multi-household-ready top-level container called Household for HomeManage MVP."

> Per the Constitution, this spec must be reviewed and approved before any code is written. Capture determinism, dependency, and UI safety decisions here rather than deferring to implementation.

## Clarifications

### Session 2026-02-12

- Q: What should happen when an authenticated user has zero household memberships? → A: Redirect to a dedicated "No household access" page with HTTP 403 and no module navigation.
- Q: How should `is_primary` be constrained for users with multiple household memberships? → A: Enforce at most one `is_primary=True` membership per user across all households.
- Q: What should happen if the active `current_household` becomes archived during a session? → A: Replace `current_household` with the next eligible non-archived membership and redirect to `/household/`; if none exists, redirect to no-household-access (403).
- Q: How should transaction edits handle account changes while preserving household integrity? → A: Always derive `transaction.household` from selected `account`, and reject save if selected account is outside `current_household`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Enter household-scoped workspace after login (Priority: P1)

As an authenticated user, I land in a household context so all subsequent data I see is scoped to one active household.

**Why this priority**: Household context is the root guardrail that prevents cross-household leakage.

**Independent Test**: Can be fully tested by creating a user with one household and a user with multiple households, then verifying session selection and redirect behavior.

**Acceptance Scenarios**:

1. **Given** a user belongs to exactly one household, **When** login succeeds, **Then** `current_household` is set in session and user is redirected to `/household/`.
2. **Given** a user belongs to multiple households with one marked primary, **When** login succeeds, **Then** primary household is selected as `current_household` and user is redirected to `/household/`.
3. **Given** a user belongs to multiple households and none is primary, **When** login succeeds, **Then** first available household is selected as `current_household` and user is redirected to `/household/`.
4. **Given** a user has zero household memberships, **When** login succeeds, **Then** user is redirected to a dedicated no-household-access page that responds with HTTP 403 and does not render module navigation.

---

### User Story 2 - Navigate modules from household home (Priority: P1)

As a household member, I can launch modules from a household home route and keep navigation within a stable server-driven layout.

**Why this priority**: The household home route is the entry point for all module navigation in this architecture.

**Independent Test**: Can be fully tested by loading `/household/`, verifying module launcher visibility, and navigating to `/household/finance/`.

**Acceptance Scenarios**:

1. **Given** an authenticated user with `current_household`, **When** user opens `/household/`, **Then** household home renders a module launcher including Finance.
2. **Given** user is on household home, **When** user selects Finance, **Then** browser navigates via normal route navigation to `/household/finance/`.

---

### User Story 3 - Use finance data within active household only (Priority: P1)

As a user, I can view accounts, account details, and transactions for only the active household.

**Why this priority**: Preventing mixed data across households is the core business and safety requirement.

**Independent Test**: Can be fully tested by seeding two households with distinct records and verifying list/detail data isolation and object-level guards.

**Acceptance Scenarios**:

1. **Given** two households with distinct accounts and transactions, **When** user is in Household A and opens finance views, **Then** only Household A financial data is visible.
2. **Given** user attempts to access an account or transaction outside `current_household`, **When** request is processed, **Then** response is 404 (preferred) and no object existence is leaked.
3. **Given** a transaction belongs to an account, **When** transaction is saved or updated, **Then** transaction household equals the account household.

---

### User Story 4 - Switch households mid-session safely (Priority: P2)

As a user with multiple household memberships, I can switch active household and immediately get a clean household-scoped view.

**Why this priority**: Session household switching is required for multi-household usability in MVP.

**Independent Test**: Can be fully tested by switching households via navbar switcher and confirming redirect and data context reset.

**Acceptance Scenarios**:

1. **Given** user belongs to two households, **When** user switches household from navbar control, **Then** `current_household` updates in session and user is redirected to `/household/`.
2. **Given** user has switched households, **When** user views finance pages, **Then** no data from previous household remains visible.

### Edge Cases

- User has no household memberships at login; system redirects to a dedicated no-household-access page (HTTP 403) without rendering module navigation or exposing internal details.
- Household switch request references a household the user is not a member of; session household remains unchanged and access is denied.
- Data mutation attempts to mark two memberships for the same user as `is_primary=True`; write is rejected or previous primary is cleared transactionally so only one primary remains.
- Household has multiple members but no owner due to data corruption; write operations that would persist this invalid state are blocked.
- Transaction create/edit attempts to submit mismatched household and account household values; persisted transaction household is derived from account household and mismatch is rejected or corrected before save.
- Transaction edit changes account to one outside `current_household`; save is rejected and transaction remains unchanged.
- Archived household is selected as current household; system automatically reselects the next eligible non-archived household and redirects to `/household/`, or routes to no-household-access (403) when none exists.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a top-level Household container supporting a user belonging to multiple households.
- **FR-002**: System MUST store exactly one `current_household` in session for each authenticated user interaction context.
- **FR-003**: System MUST redirect successful logins to `/household/` after selecting `current_household` by: only household if single, primary household if multiple with primary, otherwise first membership.
- **FR-003a**: System MUST handle authenticated users with zero household memberships by redirecting them to a dedicated no-household-access page that returns HTTP 403 and omits module navigation.
- **FR-004**: System MUST provide household routes `/household/` (household home) and `/household/finance/` (finance module root), while keeping finance app namespaced as `financial`.
- **FR-005**: System MUST include a global navbar containing drawer toggle, app title link to `/household/`, household switcher, module navigation (Finance for MVP), and user menu.
- **FR-006**: System MUST render sidebar menus by namespace using `request.resolver_match.namespace`, showing household menu for `household` namespace and finance menu for `financial` namespace.
- **FR-007**: System MUST add a Household reference to financial records so all account and transaction queries are scoped to `current_household`.
- **FR-008**: System MUST enforce invariant `Transaction.household == Transaction.account.household` for create and update flows.
- **FR-009**: System MUST derive `Transaction.household` at save-time from the selected account and must not trust client-provided household for transaction persistence.
- **FR-009a**: On transaction edit, system MUST allow account changes only when selected account belongs to `current_household`; otherwise save MUST be rejected.
- **FR-010**: System MUST enforce object-level guards that prevent access to records outside `current_household`, returning 404 by default to avoid cross-household existence leaks.
- **FR-011**: System MUST support household switching mid-session; upon switch, update `current_household`, redirect to `/household/`, and ensure subsequent views use new scope.
- **FR-011a**: System MUST enforce at most one `HouseholdMember.is_primary=True` per user across all memberships.
- **FR-011b**: System MUST ensure `current_household` is always non-archived; when archived, system MUST replace it with the next eligible non-archived membership and redirect to `/household/`, or redirect to no-household-access (403) if no eligible membership exists.
- **FR-012**: System MUST use early-stage migration Path A (Reset + Re-seed) for this feature and provide a reusable seed command that creates at least: "Our Household" and "Mother-in-law Household" with distinct accounts and transactions.
- **FR-013**: System MUST keep HTMX swaps confined to module boundaries; module transitions MUST occur via normal route navigation, not cross-module fragment swaps.
- **FR-014**: System MUST bind edit/update ModelForms with `instance=` on both GET and POST for deterministic update behavior.
- **FR-015**: System MUST execute automated tests under SQLite test settings (`core.settings_test`) and require migrations to apply cleanly from a fresh database.
- **FR-016**: System MUST exclude non-goal capabilities in this MVP: budgets, categories changes for household feature scope, calendar, reports, advanced permissions, background jobs, and external services.

### Key Entities *(include if feature involves data)*

- **Household**: Top-level tenant container with name, timestamps, optional immutable slug, archival flag, timezone, currency code, and optional creator reference.
- **HouseholdMember**: Membership link between user and household with role (`owner`/`admin`/`member`) and `is_primary` marker; each household must always retain at least one owner, and each user may have at most one primary membership.
- **Account (updated)**: Financial account belonging to exactly one household.
- **Transaction (updated)**: Financial transaction belonging to one account and one household, with household derived from its account.
- **Session Household Context**: Per-session state storing the active household used for routing, query scoping, and authorization checks.

### Server-Driven UI & Template Safety *(mandatory for UI work)*

- **UI-001**: Household and finance views render authoritative UI state server-side, including selected household, module navigation visibility, and scoped data.
- **UI-002**: Sidebar rendering MUST branch on `request.resolver_match.namespace` with household menu (`Home`, `Finance`, `Members`, `Settings`) and finance menu (`Dashboard`, `Accounts`, optional `Transactions` when present).
- **UI-003**: Any dynamic classes/attributes in templates MUST be precomputed in views/context or single-line template constructs; multiline template tags/comments are prohibited.
- **UI-004**: For each HTMX endpoint touched by this feature, implementation planning MUST document endpoint route, `hx-target`, `hx-swap`, returned partial root element, and replaced container ID.
- **UI-005**: HTMX endpoints MUST preserve their triggering element unless explicitly justified in planning.
- **UI-006**: Before any styling/layout debugging, implementation must confirm Tailwind/DaisyUI watcher is running (`npm run dev`) and capture rebuild output evidence.

## Deterministic Data & Integrity *(mandatory)*

- **Schema Changes**:
  - Introduce `Household` and `HouseholdMember` schema.
  - Add household references to `Account` and `Transaction`.
  - Enforce transaction/account household consistency constraints at model/business-rule level.
  - Validate migration chain from fresh database and preserve deterministic ordering.
- **Migration Strategy (Path A: Reset + Re-seed)**:
  - Apply schema changes, reset local development data, and reseed baseline households.
  - Provide a reusable management command to reseed deterministic sample data for both households.
  - Seed data must be consistent across repeated runs.
- **Data Fixtures/Seed Guarantees**:
  - Seed command always creates two named households and distinct sample financial data per household.
  - Seed ordering and naming are stable to support deterministic tests and demos.
- **External Inputs**:
  - Avoid unseeded randomness in fixtures/seed command.
  - Use deterministic timestamp handling suitable for repeatable test assertions.
  - No external services are introduced for this feature.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of finance list/detail views in MVP display records only from the active household in seeded two-household test scenarios.
- **SC-002**: 100% of direct object access attempts outside active household return guarded responses (404 preferred) without revealing record existence.
- **SC-003**: In manual QA, household switch updates visible data context within one navigation step (redirect to `/household/`) for 100% of tested flows.
- **SC-004**: Fresh database setup plus migrations and seed command complete successfully in one run with no manual data correction.
- **SC-005**: Automated test execution under SQLite (`core.settings_test`) passes for household and finance scope behaviors targeted by this MVP.

## Assumptions & Open Questions *(mandatory)*

- **Assumptions**:
  - Existing authentication remains in use; this feature extends post-login routing and context selection only.
  - 404 is the default guard response for cross-household object access to minimize data leakage.
  - Archived households are excluded from active session selection and household switcher choices.
  - Finance module root may temporarily render dashboard or accounts index as long as routing and scoping contracts hold.
  - `is_primary` represents household preference per user and is used only for default selection when multiple memberships exist.
  - Household slug, archive flag, timezone, currency code, and created_by are included in MVP data model where available, with currency defaulting to `USD`.
  - Constitution principles and deterministic constraints are mandatory and supersede ad-hoc implementation choices.
- **Open Questions**:
  - None blocking this MVP specification.
