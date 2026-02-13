# Tasks: Household Admin Settings

**Input**: Design documents from `/specs/001-household-admin-settings/`
**Prerequisites**: `plan.md` (required), `spec.md` (required), `research.md`, `data-model.md`, `contracts/settings-admin.openapi.yaml`, `quickstart.md`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare project scaffolding and deterministic workflow evidence for this feature.

- [x] T001 Verify CSS watcher workflow and document expected output in `specs/001-household-admin-settings/quickstart.md`
- [x] T002 Create admin settings template directory and base partial stubs in `households/templates/households/settings/`
- [x] T003 [P] Add feature-specific AI accountability note to `specs/001-household-admin-settings/plan.md`
- [x] T004 [P] Add feature test module stubs in `financial/tests/test_admin_settings_access.py`, `financial/tests/test_nav_auth_visibility.py`, `financial/tests/test_admin_households.py`, `financial/tests/test_admin_user_creation.py`, `financial/tests/test_admin_memberships.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core auth/routing/form foundations required before any user story implementation.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T005 Implement global admin policy helper (MVP superuser + extension hook) in `households/services/authorization.py`
- [x] T006 [P] Add reusable admin access mixin/decorator in `households/views.py`
- [x] T007 Add settings URL patterns and route names for contract endpoints in `pages/household_urls.py`
- [x] T008 [P] Add shared settings forms for household create, user create, membership add/remove in `households/forms.py`
- [x] T009 Create settings service layer for household/user/membership operations in `households/services/settings.py`
- [x] T010 [P] Add settings visibility context data for templates in `households/context_processors.py`
- [x] T011 Record schema impact decision (no-change proof or required migration plan) in `specs/001-household-admin-settings/plan.md`

**Checkpoint**: Foundation ready — user story implementation can proceed.

---

## Phase 3: User Story 1 - Access admin Settings (Priority: P1) 🎯 MVP

**Goal**: Authenticated global administrators can access Settings; non-admin/unauthenticated users cannot.

**Independent Test**: Log in as superuser and non-admin user; verify Settings nav visibility and URL access control independently.

### Tests for User Story 1 (write first)

- [x] T012 [P] [US1] Add nav visibility tests for Login/module/Settings behavior in `financial/tests/test_nav_auth_visibility.py`
- [x] T013 [P] [US1] Add access control tests for `/settings/` and related endpoints in `financial/tests/test_admin_settings_access.py`
- [x] T046 [P] [US1] Add unauthenticated module-route redirect tests (including Finance URL) in `financial/tests/test_nav_auth_visibility.py`

### Implementation for User Story 1

- [x] T014 [US1] Implement Settings landing view (full + HTMX partial support) in `households/views.py`
- [x] T015 [US1] Register settings landing route in `pages/household_urls.py`
- [x] T016 [US1] Add Settings nav item visibility logic to sidebar in `templates/components/layout/sidebar.html`
- [x] T017 [US1] Update navbar to hide Finance when unauthenticated in `templates/components/layout/navbar.html`
- [x] T018 [US1] Ensure Login is shown only when unauthenticated via auth menu integration in `templates/components/auth/menu.html`
- [x] T019 [US1] Create settings landing template with stable HTMX containers in `households/templates/households/settings/index.html`
- [x] T047 [US1] Enforce authentication guard on module routes with redirect-to-login behavior in `core/urls.py` and `financial/views.py`

**Checkpoint**: US1 is independently functional and testable.

---

## Phase 4: User Story 2 - Create a household (Priority: P2)

**Goal**: Global administrators can create households from Settings with deterministic validation.

**Independent Test**: Create household via Settings and verify duplicate/missing-name errors without using other story flows.

### Tests for User Story 2 (write first)

- [x] T020 [P] [US2] Add household create success/validation tests in `financial/tests/test_admin_households.py`
- [x] T021 [P] [US2] Add normalized duplicate-name validation tests in `financial/tests/test_admin_households.py`

### Implementation for User Story 2

- [x] T022 [US2] Implement household creation endpoint (`POST /settings/households/`) in `households/views.py`
- [x] T023 [US2] Implement normalized household name validation + create logic in `households/services/settings.py`
- [x] T024 [US2] Wire household create form and panel partials in `households/templates/households/settings/_household_form.html` and `households/templates/households/settings/_household_panel.html`
- [x] T025 [US2] Ensure HTMX target/swap behavior matches contract for households panel in `households/templates/households/settings/index.html`

**Checkpoint**: US2 is independently functional and testable.

---

## Phase 5: User Story 3 - Create user login accounts (Priority: P3)

**Goal**: Global administrators can create login accounts with direct password set and one-or-more household memberships.

**Independent Test**: Create account with valid credentials and multiple households; verify failures for missing memberships, weak password, duplicates, and no-households condition.

### Tests for User Story 3 (write first)

- [x] T026 [P] [US3] Add user-create success path test with multiple memberships in `financial/tests/test_admin_user_creation.py`
- [x] T027 [P] [US3] Add user-create validation tests (duplicate username/email, weak password) in `financial/tests/test_admin_user_creation.py`
- [x] T028 [P] [US3] Add no-households blocking test in `financial/tests/test_admin_user_creation.py`

### Implementation for User Story 3

- [x] T029 [US3] Implement user creation endpoint (`POST /settings/users/`) in `households/views.py`
- [x] T030 [US3] Implement atomic user+membership creation service logic in `households/services/settings.py`
- [x] T031 [US3] Add form-level enforcement for at least one household selection in `households/forms.py`
- [x] T032 [US3] Add no-households guard and guidance message rendering in `households/templates/households/settings/_user_form.html`
- [x] T033 [US3] Add user creation panel partial and success/error rendering in `households/templates/households/settings/_user_panel.html`
- [x] T034 [US3] Ensure password is set via Django auth APIs (not raw assignment) in `households/services/settings.py`

**Checkpoint**: US3 is independently functional and testable.

---

## Phase 6: User Story 4 - Manage household members (Priority: P4)

**Goal**: Global administrators can add/remove memberships safely and idempotently.

**Independent Test**: Add member, prevent duplicate add, remove member, and verify immediate access effect.

### Tests for User Story 4 (write first)

- [x] T035 [P] [US4] Add membership add/remove/duplicate tests in `financial/tests/test_admin_memberships.py`
- [x] T036 [P] [US4] Add membership-not-found/error-state tests in `financial/tests/test_admin_memberships.py`

### Implementation for User Story 4

- [x] T037 [US4] Implement membership add endpoint (`POST /settings/households/{householdId}/memberships/`) in `households/views.py`
- [x] T038 [US4] Implement membership remove endpoint (`POST /settings/households/{householdId}/memberships/{userId}/remove/`) in `households/views.py`
- [x] T039 [US4] Implement idempotent membership add/remove service operations in `households/services/settings.py`
- [x] T040 [US4] Add membership panel and row partials in `households/templates/households/settings/_membership_panel.html` and `households/templates/households/settings/_membership_row.html`
- [x] T041 [US4] Ensure HTMX targets/swaps for membership panel match contract in `households/templates/households/settings/index.html`

**Checkpoint**: US4 is independently functional and testable.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency, determinism proof, and docs update across stories.

- [x] T042 [P] Validate quickstart end-to-end and update any drift in `specs/001-household-admin-settings/quickstart.md`
- [x] T043 [P] Update/confirm API contract consistency with implemented behavior in `specs/001-household-admin-settings/contracts/settings-admin.openapi.yaml`
- [x] T044 Run focused feature tests then full suite and record commands/results in `specs/001-household-admin-settings/plan.md`
- [x] T045 Verify migration/fixture determinism and document rollback evidence in `specs/001-household-admin-settings/plan.md`
- [x] T048 Add explicit fixture idempotency verification task and evidence in `specs/001-household-admin-settings/quickstart.md` and `specs/001-household-admin-settings/plan.md`
- [x] T049 Add deterministic external-input handling checks (timestamps/IDs in tests) in `financial/tests/test_admin_user_creation.py` and `financial/tests/test_admin_memberships.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies; start immediately.
- **Phase 2 (Foundational)**: Depends on Phase 1; blocks all user stories.
- **Phases 3–6 (User Stories)**: Depend on Phase 2 completion.
- **Phase 7 (Polish)**: Depends on completion of desired user stories.

### User Story Dependencies

- **US1 (P1)**: Starts after foundational phase; no dependency on other stories.
- **US2 (P2)**: Starts after foundational phase; independent from US3/US4.
- **US3 (P3)**: Starts after foundational phase; relies on household availability behavior defined in US2 but remains testable independently via setup fixtures.
- **US4 (P4)**: Starts after foundational phase; depends on existing users/households but remains independently testable with fixtures.

### Within Each User Story

- Tests must be added first and fail before implementation.
- Views/forms/services implemented before template wiring finalization.
- HTMX target/swap verification before story close-out.

---

## Parallel Execution Examples

### User Story 1

- Run in parallel:
  - T012 in `financial/tests/test_nav_auth_visibility.py`
  - T013 in `financial/tests/test_admin_settings_access.py`

### User Story 2

- Run in parallel:
  - T020 and T021 in `financial/tests/test_admin_households.py`

### User Story 3

- Run in parallel:
  - T026, T027, T028 in `financial/tests/test_admin_user_creation.py`

### User Story 4

- Run in parallel:
  - T035 and T036 in `financial/tests/test_admin_memberships.py`

---

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Phases 1–2.
2. Deliver Phase 3 (US1).
3. Validate nav + access controls independently before continuing.

### Incremental Delivery

1. US1: Admin settings access + auth-gated navigation.
2. US2: Household creation.
3. US3: User creation with required one-or-more household memberships.
4. US4: Membership management.
5. Polish with deterministic validation and full regression run.

### Suggested MVP Scope

- **MVP**: Phase 3 (US1) only after foundational work.
- Recommended first value slice: ship admin access control and navigation gating before CRUD workflows.
