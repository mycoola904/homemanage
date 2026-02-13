# Tasks: Household Account Import

**Input**: Design documents from `/specs/001-account-import/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/account-import.openapi.yaml, quickstart.md

**Tests**: Include test tasks per user story to satisfy constitution requirement for failing scenario coverage before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Constitution Hooks *(do not remove)*

- Every task references the spec ID and scenario it satisfies (Principle I).
- Database tasks cite migration/fixture files and deterministic behavior requirements (Principle II).
- No new dependency tasks are included; Python stdlib `csv` only (Principle III).
- UI/template tasks include watcher verification and HTMX target/swap documentation (Principle IV).
- AI-generated implementation tasks include PR prompt/response traceability artifact update (Principle V).

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare files and verification scaffolding for implementation.

- [ ] T001 Verify Tailwind watcher workflow notes in specs/001-account-import/quickstart.md for FR-001/FR-002 UI safety evidence
- [ ] T002 Create import feature test module stubs in financial/tests/test_account_import.py and financial/tests/test_account_import_validation.py for US1/US2 scenario coverage
- [ ] T003 [P] Create template download test module stub in financial/tests/test_account_import_template.py for US3 scenario coverage

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before any user story implementation.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T004 Add `online_access_url` field to Account model in financial/models.py for FR-017 entity update
- [ ] T005 Create migration for `online_access_url` in financial/migrations/NNNN_account_online_access_url.py (next sequential number) with deterministic forward/backward behavior
- [ ] T006 [P] Add import form class shell (file upload + basic field wiring) in financial/forms.py for FR-003/FR-004
- [ ] T007 [P] Create import service module skeleton for CSV parsing pipeline in financial/services/account_import.py for FR-005/FR-006
- [ ] T008 Add import URL route placeholders in financial/urls.py for /financial/import/, /financial/import/panel/, /financial/import/template/

**Checkpoint**: Foundation ready; user story tasks can proceed.

---

## Phase 3: User Story 1 - Import accounts from finance navigation (Priority: P1) 🎯 MVP

**Goal**: User can open import UI from finance sidebar and successfully import valid CSV rows into the active household.

**Independent Test**: From finance sidebar, open import panel, upload valid CSV, submit, and verify created accounts belong only to active household with success summary displayed.

### Tests for User Story 1

- [ ] T009 [P] [US1] Add navigation + panel rendering integration test in financial/tests/test_account_import.py covering FR-001/FR-002
- [ ] T010 [P] [US1] Add successful CSV import integration test in financial/tests/test_account_import.py covering FR-005/FR-006/FR-007/FR-010
- [ ] T011 [P] [US1] Add active-household scoping test in financial/tests/test_account_import.py covering FR-007/FR-008

### Implementation for User Story 1

- [ ] T012 [P] [US1] Add finance sidebar Import link entry in templates/components/layout/sidebar.html targeting financial import UI (FR-001)
- [ ] T013 [P] [US1] Create import page template with stable main container in financial/templates/financial/accounts/import.html using `#financial-main-content` (FR-002/UI-001)
- [ ] T014 [P] [US1] Create import panel partial root section in financial/templates/financial/accounts/_import_panel.html using `#account-import-panel` (UI-002)
- [ ] T015 [US1] Implement GET import page and GET panel views in financial/views.py for /financial/import/ and /financial/import/panel/ (FR-002, contract GET endpoints)
- [ ] T016 [US1] Implement valid CSV parse-to-domain row mapping in financial/services/account_import.py using `csv.DictReader` (FR-004/FR-005)
- [ ] T017 [US1] Implement atomic account creation transaction and success summary builder in financial/services/account_import.py (FR-006/FR-010)
- [ ] T018 [US1] Implement POST import view in financial/views.py with `hx-target="#account-import-panel"` and `hx-swap="innerHTML"` success path (UI-001/UI-002, contract POST 200)
- [ ] T019 [US1] Wire import views to named routes in financial/urls.py and update any finance navigation links as needed (FR-001/FR-002)
- [ ] T039 [P] [US1] Add test in financial/tests/test_account_import.py verifying selected filename is shown before submit (FR-003)
- [ ] T040 [US1] Implement selected filename display behavior in financial/templates/financial/accounts/_import_panel.html and supporting view/form wiring (FR-003)

**Checkpoint**: US1 is independently functional and testable.

---

## Phase 4: User Story 2 - Receive actionable validation feedback (Priority: P2)

**Goal**: Invalid CSV uploads return actionable, row-level errors with zero inserts.

**Independent Test**: Submit invalid files (type/header/row/limit/duplicate/url/date/enum) and verify HTTP 422 panel response with errors and no persisted accounts.

### Tests for User Story 2

- [ ] T020 [P] [US2] Add unsupported file type and missing-header tests in financial/tests/test_account_import_validation.py for FR-004/FR-005
- [ ] T021 [P] [US2] Add row-level validation tests (enum/date/url/day) in financial/tests/test_account_import_validation.py for FR-015/FR-016/FR-017 and model constraints
- [ ] T022 [P] [US2] Add duplicate detection tests (within-file + household existing, case-insensitive) in financial/tests/test_account_import_validation.py for FR-009
- [ ] T023 [P] [US2] Add file size and row limit tests in financial/tests/test_account_import_validation.py for FR-013/FR-014
- [ ] T024 [P] [US2] Add atomic rollback test ensuring zero inserts on any validation error in financial/tests/test_account_import_validation.py for FR-006

### Implementation for User Story 2

- [ ] T025 [US2] Implement strict header and file-type validation in financial/services/account_import.py including CSV-only enforcement (FR-004/FR-005a/FR-005b)
- [ ] T026 [US2] Implement canonical enum/date/url/field normalization and validation errors in financial/services/account_import.py (FR-015/FR-016/FR-017)
- [ ] T027 [US2] Implement duplicate detection against active household and upload batch in financial/services/account_import.py (FR-009)
- [ ] T028 [US2] Implement file size and max-row guards in financial/forms.py and/or financial/services/account_import.py (FR-013/FR-014)
- [ ] T029 [US2] Implement 422 error response rendering with row-level messages in financial/views.py and financial/templates/financial/accounts/_import_panel.html (FR-010, contract POST 422)

**Checkpoint**: US2 is independently functional and testable.

---

## Phase 5: User Story 3 - Use a standard template file (Priority: P3)

**Goal**: User can download deterministic CSV template matching importer contract headers.

**Independent Test**: Request template endpoint and verify downloaded CSV header order exactly matches FR-005a and includes sample values.

### Tests for User Story 3

- [ ] T030 [P] [US3] Add template download endpoint test in financial/tests/test_account_import_template.py for content type and filename (FR-011/contract GET template)
- [ ] T031 [P] [US3] Add template header order/content contract test in financial/tests/test_account_import_template.py for FR-005a/FR-011/FR-012

### Implementation for User Story 3

- [ ] T032 [P] [US3] Add deterministic template CSV artifact in financial/fixtures/account_import_template.csv with required header order and sample row
- [ ] T033 [US3] Implement template download view in financial/views.py serving financial/fixtures/account_import_template.csv (FR-011/FR-012)
- [ ] T034 [US3] Add template download route in financial/urls.py and import-panel link/button in financial/templates/financial/accounts/_import_panel.html

**Checkpoint**: US3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency, traceability, and verification across stories.

- [ ] T035 [P] Verify final schema-change wording and FR-to-contract header parity between specs/001-account-import/spec.md and specs/001-account-import/contracts/account-import.openapi.yaml
- [ ] T036 Document HTMX target/swap decisions in inline template/view context where applicable in financial/views.py and financial/templates/financial/accounts/_import_panel.html (UI-001/UI-002 evidence)
- [ ] T037 [P] Update AI prompt/response traceability notes in specs/001-account-import/quickstart.md and PR checklist section for Principle V evidence
- [ ] T038 Run feature-targeted and financial test suites via core.settings_test and record outcomes in specs/001-account-import/quickstart.md validation notes
- [ ] T041 [P] Add performance validation task for 1,000-row import under 10s and record evidence in quickstart.md (SC-002)
- [ ] T042 [P] Add SC-003 validation protocol task: run and record at least 10 first-time template-based import trials with >=90% successful completion evidence in specs/001-account-import/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: no dependencies.
- **Phase 2 (Foundational)**: depends on Phase 1; blocks all user stories.
- **Phase 3 (US1)**: depends on Phase 2 completion.
- **Phase 4 (US2)**: depends on Phase 2 completion; can begin after US1 foundation routes/templates exist but remains independently testable.
- **Phase 5 (US3)**: depends on Phase 2 completion; independent from US1/US2 logic except shared routing/view infrastructure.
- **Phase 6 (Polish)**: depends on all selected stories being complete.

### User Story Dependency Graph

- **US1 (P1)**: Start first after foundational phase (MVP).
- **US2 (P2)**: Start after foundational; validates and hardens import pipeline, does not require US3.
- **US3 (P3)**: Start after foundational; template delivery independent from validation complexity.

### Within Each User Story

- Tests first and failing before implementation.
- Services/forms before endpoint response wiring.
- Endpoint/view logic before template polish.
- Complete story-level independent test before moving to next priority story.

---

## Parallel Execution Examples

### User Story 1

- Run in parallel: T009, T010, T011 (tests in one file but independent test cases).
- Run in parallel: T012, T013, T014 (sidebar + page + partial templates in separate files).

### User Story 2

- Run in parallel: T020, T021, T022, T023, T024 (validation test case groups).
- Run in parallel: T026 and T028 (rule validators and limit guards can be implemented in separate functions/files).

### User Story 3

- Run in parallel: T030 and T031 (template endpoint/content tests).
- Run in parallel: T032 and T033 (artifact creation and download view implementation).

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 + Phase 2.
2. Complete Phase 3 (US1).
3. Validate US1 independent test criteria.
4. Demo/deploy MVP if desired.

### Incremental Delivery

1. Deliver US1 import navigation + success path.
2. Deliver US2 validation/error hardening with atomic rollback guarantees.
3. Deliver US3 template download and finalize polish tasks.

### Parallel Team Strategy

1. Team completes Phase 1/2 together.
2. Then split by story:
   - Dev A: US1 tasks.
   - Dev B: US2 tasks.
   - Dev C: US3 tasks.
3. Merge at Phase 6 for final verification/documentation.

---

## Notes

- All tasks follow checklist format: `- [ ] T### [P?] [US?] Description with file path`.
- `[P]` markers indicate no dependency on unfinished tasks in other files.
- No new runtime dependencies are introduced for this feature.
- Template and HTMX safety constraints from constitution are embedded in task descriptions.
