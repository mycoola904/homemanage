# Tasks: Bill Pay

**Input**: Design documents from `specs/001-bill-pay/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/bill-pay.yaml, quickstart.md

## Constitution Hooks *(do not remove)*

- Every task references the spec ID and scenario it satisfies (Principle I).
- Database tasks MUST cite the migration/fixture file and describe how determinism is enforced (Principle II).
- Tasks that add a dependency must link to the plan’s approved justification; default assumption is “no new dependency” (Principle III).
- UI/tasks touching templates or CSS must include a subtask to confirm the Tailwind watcher is running and to document HTMX targets (Principle IV).
- Tasks generated or implemented with AI must store the prompt/response location noted in the task description (Principle V).

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare implementation evidence and workflow prerequisites.

- [ ] T001 Confirm Tailwind watcher command `npm run dev:css` and record active output in docs/ai/004-bill-pay-log.md
- [ ] T002 Create Bill Pay AI log scaffold with links to spec/plan/contracts in docs/ai/004-bill-pay-log.md
- [ ] T003 Verify and record HTMX target/swap map from contracts in specs/001-bill-pay/contracts/bill-pay.yaml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core persistence and endpoint scaffolding required before user stories.

**⚠️ CRITICAL**: No user story work begins until this phase is complete.

- [ ] T004 Add `MonthlyBillPayment` model, constraints, and month normalization helpers in financial/models.py
- [ ] T005 [P] Create deterministic migration for monthly bill pay schema in financial/migrations/0004_monthly_bill_payment.py
- [ ] T006 [P] Add Bill Pay row/month forms and validation rules in financial/forms.py
- [ ] T007 [P] Implement liability query, ordering, month parsing, and upsert helpers in financial/services/bill_pay.py
- [ ] T008 Add Bill Pay routes (`/accounts/bill-pay/`, `/table-body/`, `/{accountId}/row/`) in financial/urls.py

**Checkpoint**: Foundation complete; user stories can proceed.

---

## Phase 3: User Story 1 - Review Monthly Bills (Priority: P1) 🎯 MVP

**Goal**: User opens Bill Pay from sidebar and sees month-filtered liability rows sorted by due day.

**Independent Test**: Navigate to Bill Pay and confirm liability-only rows, due-day ordering, and month selector defaulting to current month.

### Implementation for User Story 1

- [ ] T009 [US1] Implement Bill Pay index view with selected-month context in financial/views.py
- [ ] T010 [P] [US1] Create Bill Pay page shell with month selector and stable table container in financial/templates/financial/bill_pay/index.html
- [ ] T011 [P] [US1] Create month-swapped table body fragment in financial/templates/financial/bill_pay/_table_body.html
- [ ] T012 [P] [US1] Create read-only Bill Pay row fragment with required display columns in financial/templates/financial/bill_pay/_row.html
- [ ] T013 [US1] Implement table-body fragment endpoint for month switch HTMX swaps in financial/views.py
- [ ] T014 [US1] Add Bill Pay navigation entry in sidebar menu in templates/components/layout/sidebar.html

**Checkpoint**: US1 is fully functional and independently testable.

---

## Phase 4: User Story 2 - Record Payment Status (Priority: P1)

**Goal**: User edits one row and explicitly saves amount/paid for the selected month.

**Independent Test**: Edit and save a row, reload same month, and confirm persisted values; invalid negative amount returns inline row errors.

### Implementation for User Story 2

- [ ] T015 [US2] Implement row-edit fragment GET endpoint for selected account-month in financial/views.py
- [ ] T016 [P] [US2] Create editable row fragment with explicit Save control in financial/templates/financial/bill_pay/_row_edit.html
- [ ] T017 [US2] Implement row-save POST endpoint with create/update semantics in financial/views.py
- [ ] T018 [US2] Apply row validation behavior (`422` on invalid, paid independent from amount, negative blocked) in financial/forms.py
- [ ] T019 [US2] Wire HTMX row targets/swaps to replace only the edited row in financial/templates/financial/bill_pay/_row.html
- [ ] T020 [US2] Persist account-month updates with deterministic upsert path in financial/services/bill_pay.py

**Checkpoint**: US2 is fully functional and independently testable.

---

## Phase 5: User Story 3 - Use Account Payment Links (Priority: P2)

**Goal**: User sees online payment URL in each row with clear empty-state behavior.

**Independent Test**: Open Bill Pay for a month and verify URL rendering for rows with and without online access links.

### Implementation for User Story 3

- [ ] T021 [US3] Render online access URL cell with clickable link behavior in financial/templates/financial/bill_pay/_row.html
- [ ] T022 [US3] Add URL empty-state rendering and label copy for missing links in financial/templates/financial/bill_pay/_row.html
- [ ] T023 [US3] Ensure URL values are prepared consistently for table and row responses in financial/services/bill_pay.py

**Checkpoint**: US3 is fully functional and independently testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final alignment, evidence capture, and readiness checks across stories.

- [ ] T024 [P] Reconcile endpoint docs with final route/response behavior in specs/001-bill-pay/contracts/bill-pay.yaml
- [ ] T025 Validate quickstart scenario execution and record outcomes in docs/ai/004-bill-pay-log.md
- [ ] T026 Record migration determinism evidence (`migrate --check` and rollback notes) in docs/ai/004-bill-pay-log.md
- [ ] T027 Update manual test steps if implementation details changed in specs/001-bill-pay/quickstart.md
- [ ] T028 Record final AI prompt/response references for PR traceability in docs/ai/004-bill-pay-log.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: no dependencies.
- **Phase 2 (Foundational)**: depends on Phase 1 and blocks all user stories.
- **Phase 3 (US1)**: depends on Phase 2.
- **Phase 4 (US2)**: depends on Phase 2 and US1 row/table shell.
- **Phase 5 (US3)**: depends on Phase 2 and US1 row rendering.
- **Phase 6 (Polish)**: depends on completion of all selected user stories.

### User Story Dependencies

- **US1 (P1)**: first deliverable MVP.
- **US2 (P1)**: depends on US1 table/row containers and foundational persistence.
- **US3 (P2)**: depends on US1 row rendering path; otherwise independent from US2.

```mermaid
graph TD
  US1[US1 Review Monthly Bills] --> US2[US2 Record Payment Status]
  US1 --> US3[US3 Use Account Payment Links]
```

### Within Each User Story

- Implement view/context flow before dependent template wiring.
- Keep row-level behavior isolated to row fragments and service helpers.
- Complete story checkpoint before moving to the next priority when delivering incrementally.

---

## Parallel Opportunities

- Phase 2 parallel tasks: `T005`, `T006`, `T007` (different files).
- US1 parallel tasks: `T010`, `T011`, `T012` (template files).
- US2 parallel tasks: `T016` can run while endpoint scaffolding (`T015`, `T017`) is in progress.
- Polish parallel tasks: `T024` and `T025` can run together.

---

## Parallel Example: User Story 1

```bash
Task: T010 [US1] Create Bill Pay page shell in financial/templates/financial/bill_pay/index.html
Task: T011 [US1] Create table body fragment in financial/templates/financial/bill_pay/_table_body.html
Task: T012 [US1] Create read-only row fragment in financial/templates/financial/bill_pay/_row.html
```

## Parallel Example: User Story 2

```bash
Task: T016 [US2] Create editable row fragment in financial/templates/financial/bill_pay/_row_edit.html
Task: T017 [US2] Implement row-save POST in financial/views.py
```

## Parallel Example: User Story 3

```bash
Task: T021 [US3] Implement URL link rendering in financial/templates/financial/bill_pay/_row.html
Task: T023 [US3] Normalize URL context in financial/services/bill_pay.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete US1 tasks (`T009`-`T014`).
3. Validate US1 independent test criteria.
4. Demo/deploy MVP slice.

### Incremental Delivery

1. Deliver US1 (monthly list + month selector + sidebar entry).
2. Deliver US2 (explicit row save + persistence + validation).
3. Deliver US3 (online access URL rendering behavior).
4. Finish Phase 6 polish and readiness evidence.

### Parallel Team Strategy

1. One developer handles persistence and forms (`T004`-`T007`).
2. One developer handles US1 templates/view shell (`T009`-`T014`).
3. One developer handles US2 row edit/save path (`T015`-`T020`).
4. US3 and polish work proceed after US1 foundations stabilize.
