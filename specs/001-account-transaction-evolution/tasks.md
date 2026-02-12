---

description: "Task list for account and transaction evolution"
---

# Tasks: Account and Transaction Model Evolution

**Input**: Design documents from `/specs/001-account-transaction-evolution/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

## Constitution Hooks *(do not remove)*

- Every task references the spec ID and scenario it satisfies (Principle I).
- Database tasks MUST cite the migration/fixture file and describe how determinism is enforced (Principle II).
- Tasks that add a dependency must link to the plan’s approved justification; default assumption is “no new dependency” (Principle III).
- UI/tasks touching templates or CSS must include a subtask to confirm the Tailwind watcher is running and to document HTMX targets (Principle IV).
- Tasks generated or implemented with AI must store the prompt/response location noted in the task description (Principle V).

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and audit trail setup

- [x] T001 [P] Add AI prompt log entry in docs/ai/001-account-transaction-evolution-log.md referencing spec/plan/tasks (Principle V)
- [x] T002 [P] Verify and update HTMX contract notes in specs/001-account-transaction-evolution/contracts/transactions.yaml for inline category errors (Spec UI-002, HTMX Contract: Inline category add errors)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core schema changes and backfill that all stories depend on

- [x] T003 Update financial/models.py with Account fields (`account_number`, `routing_number`, `interest_rate`), Category model, Transaction `transaction_type`, and case-insensitive category uniqueness (Spec FR-001, FR-007)
- [x] T004 Create migration financial/migrations/0003_account_transaction_evolution.py to add fields, create Category, backfill `transaction_type`, and drop `direction`/`number_last4` with idempotent logic (Spec FR-011, Migration Strategy)
- [x] T005 [P] Add migration backfill tests in financial/tests/test_migrations_backfill.py covering `direction` → `transaction_type` mapping (Spec SC-002)
- [x] T024 [P] Validate SQLite-default test settings in core/settings_test.py and document `manage.py migrate --check` usage for tests (Spec FR-012)

**Checkpoint**: Foundation ready - user story implementation can begin

---

## Phase 3: User Story 1 - Maintain accurate account details (Priority: P1) 🎯 MVP

**Goal**: Edit forms show only fields that apply to the account type

**Independent Test**: Edit a checking and a credit card account and verify routing number/interest rate visibility and validation

### Tests for User Story 1

- [x] T006 [P] [US1] Add conditional field tests in financial/tests/test_account_fields.py for routing/interest validation (Spec US1, FR-002, FR-003)

### Implementation for User Story 1

- [x] T007 [US1] Update AccountForm in financial/forms.py to include `account_number`, `routing_number`, `interest_rate`, and conditional validation (Spec FR-001, FR-004)
- [x] T008 [US1] Update account edit view in financial/views.py to bind instances and pass visibility flags (Spec FR-009, UI-003)
- [x] T009 [US1] Update financial/templates/financial/accounts/_form.html to render conditional fields using view flags; confirm Tailwind watcher in task notes (Spec UI-004)

**Checkpoint**: User Story 1 works independently

---

## Phase 4: User Story 2 - Record a transaction with deterministic amount sign (Priority: P2)

**Goal**: Stored transaction amounts follow the deterministic sign matrix

**Independent Test**: Create transactions across account types and verify stored signs match the matrix

### Tests for User Story 2

- [x] T010 [P] [US2] Add sign matrix tests in financial/tests/test_transaction_sign_matrix.py (Spec US2, SC-001)
- [x] T011 [P] [US2] Add transaction type restriction + positive amount tests in financial/tests/test_transaction_type_restrictions.py (Spec FR-006, FR-006a)

### Implementation for User Story 2

- [x] T012 [US2] Implement Transaction validation/sign logic in financial/models.py for allowed types and signed persistence (Spec FR-005, FR-006)
- [x] T013 [US2] Update TransactionForm in financial/forms.py to use `transaction_type` and positive amount validation (Spec FR-006a)
- [x] T014 [US2] Update account_transactions_new in financial/views.py to save signed amounts and return correct HTMX fragments (Spec UI-002)
- [x] T015 [US2] Update financial/services/transactions.py to format signed amounts from `transaction_type` (Spec SC-001)
- [x] T016 [US2] Update financial/templates/financial/accounts/transactions/_form.html to expose `transaction_type` choices and absolute amount input; confirm Tailwind watcher in task notes (Spec UI-004)
- [x] T025 [P] [US2] Add transaction edit HTMX tests in financial/tests/test_transaction_edit.py (Spec UI-002, FR-005)
- [x] T026 [US2] Add transaction edit endpoint in financial/urls.py and financial/views.py plus template updates in financial/templates/financial/accounts/transactions/_form.html (Spec UI-002)

**Checkpoint**: User Story 2 works independently

---

## Phase 5: User Story 3 - Categorize transactions without leaving the page (Priority: P3)

**Goal**: Inline category creation updates the dropdown without page reload

**Independent Test**: Add a new category inline and select it immediately in the transaction form

### Tests for User Story 3

- [x] T017 [P] [US3] Add category uniqueness tests in financial/tests/test_category_uniqueness.py (Spec FR-007, FR-007a)
- [x] T018 [P] [US3] Add HTMX inline category error tests in financial/tests/test_inline_category_errors.py (Spec FR-008, HTMX Contract: Inline category add errors)

### Implementation for User Story 3

- [x] T019 [US3] Add CategoryForm and category selection wiring in financial/forms.py (Spec FR-008)
- [x] T020 [US3] Add inline category endpoint in financial/urls.py and financial/views.py returning fragments + 400 on errors (Spec UI-002, Inline category add errors)
- [x] T021 [US3] Add templates for inline category form/options in financial/templates/financial/accounts/transactions/_category_form.html and update _form.html; confirm Tailwind watcher in task notes (Spec FR-008)
- [x] T022 [US3] Update financial/templates/financial/accounts/transactions/_body.html to render category label when present (Spec SC-003)

**Checkpoint**: User Story 3 works independently

---

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T023 [P] Update specs/001-account-transaction-evolution/quickstart.md with final verification steps and test command (Spec SC-002)
- [x] T027 [P] Verify HTMX responses preserve triggering elements for account preview/edit/delete, transaction add/edit, and inline category add (Spec FR-010, UI-001, UI-002)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Stories (Phase 3+)**: Depend on Foundational completion
- **Polish (Final Phase)**: Depends on all desired user stories

### User Story Dependencies

- **US1 (P1)**: Starts after Foundational
- **US2 (P2)**: Starts after Foundational
- **US3 (P3)**: Starts after Foundational

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before views
- Views before templates

---

## Parallel Execution Examples

### User Story 1

- T006 (tests) can run in parallel with T005 once foundational is complete

### User Story 2

- T010 and T011 can run in parallel

### User Story 3

- T017 and T018 can run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phases 1–2
2. Complete Phase 3 (US1)
3. Validate US1 independently against the acceptance scenarios

### Incremental Delivery

1. Complete Setup + Foundational
2. Deliver US1 → validate independently
3. Deliver US2 → validate independently
4. Deliver US3 → validate independently

### Parallel Team Strategy

- After Foundational, parallelize US1, US2, and US3 if staffing allows
