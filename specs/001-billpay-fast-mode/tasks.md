# Tasks: Bill Pay Fast Mode

**Input**: Design documents from `/specs/001-billpay-fast-mode/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

## Constitution Hooks *(do not remove)*

- Every task references the spec ID and scenario it satisfies (Principle I).
- Database tasks MUST cite the migration/fixture file and describe how determinism is enforced (Principle II).
- Tasks that add a dependency must link to the plan’s approved justification; default assumption is “no new dependency” (Principle III).
- UI/tasks touching templates or CSS must include a subtask to confirm the Tailwind watcher is running and to document HTMX targets (Principle IV).
- Tasks generated or implemented with AI must store the prompt/response location noted in the task description (Principle V).

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare workspace and baseline verification for Fast Mode implementation.

- [ ] T001 Verify baseline Bill Pay behavior in `financial/tests/test_bill_pay_save.py` and `financial/tests/test_bill_pay_row_keyboard.py` before Fast Mode changes
- [ ] T002 Confirm watcher workflow for UI tasks by documenting `npm run dev:css` usage in `specs/001-billpay-fast-mode/quickstart.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core Fast Mode plumbing required before user story implementation.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T003 Add Fast Mode request parsing helper (`fast_mode` flag normalization) in `financial/views.py`
- [ ] T004 [P] Add next-unpaid-row selection helper using on-screen row order semantics in `financial/services/bill_pay.py`
- [ ] T005 [P] Add `NextRowInstruction` builder/serializer helper for HTMX trigger payloads in `financial/services/bill_pay.py`
- [ ] T006 Wire shared constants/event names for Fast Mode trigger handling in `financial/views.py` and `static/src/bill_pay_row_keyboard.js`
- [ ] T007 Add/adjust focused foundational tests for helper behavior in `financial/tests/test_bill_pay_save.py`

**Checkpoint**: Foundation ready — user story implementation can begin.

---

## Phase 3: User Story 1 - Save and Continue to Next Unpaid Row (Priority: P1) 🎯 MVP

**Goal**: Enable Fast Mode so saving one unpaid row auto-opens the next unpaid row in edit mode with focus on actual payment amount.

**Independent Test**: Enable Fast Mode, save one valid unpaid row, and verify the saved row returns to view mode while next unpaid row enters edit mode with focus in actual payment amount.

### Tests for User Story 1

- [ ] T008 [P] [US1] Add save-response trigger test for Fast Mode enabled path in `financial/tests/test_bill_pay_save.py`
- [ ] T009 [P] [US1] Add next-row ordering test (top-to-bottom on-screen order) in `financial/tests/test_bill_pay_save.py`
- [ ] T010 [P] [US1] Add keyboard save compatibility test with Fast Mode enabled in `financial/tests/test_bill_pay_row_keyboard.py`

### Implementation for User Story 1

- [ ] T011 [US1] Add Fast Mode toggle UI (default OFF) to bill pay header in `financial/templates/financial/bill_pay/index.html`
- [ ] T012 [US1] Include Fast Mode form field propagation in row edit form submits in `financial/templates/financial/bill_pay/_row_edit.html`
- [ ] T013 [US1] Update row save success path to emit `HX-Trigger` with next-row payload in `financial/views.py`
- [ ] T014 [US1] Add client event handler for `billpay:openNextRow` that opens target edit row in `static/src/bill_pay_row_keyboard.js`
- [ ] T015 [US1] Ensure auto-open focus defaults to `actual_payment_amount` in `static/src/bill_pay_row_keyboard.js`

**Checkpoint**: User Story 1 is fully functional and independently testable.

---

## Phase 4: User Story 2 - Normal Save Behavior When Fast Mode Is Off (Priority: P2)

**Goal**: Preserve existing row-save behavior when Fast Mode is disabled.

**Independent Test**: Leave Fast Mode disabled, save rows using both pointer and keyboard flows, and verify only current row returns to view mode without auto-open.

### Tests for User Story 2

- [ ] T016 [P] [US2] Add test ensuring no trigger payload is returned when Fast Mode is disabled in `financial/tests/test_bill_pay_save.py`
- [ ] T017 [P] [US2] Add default-OFF initial page render test in `financial/tests/test_bill_pay_index.py`
- [ ] T018 [P] [US2] Add validation-error no-auto-advance regression test in `financial/tests/test_bill_pay_validation.py`

### Implementation for User Story 2

- [ ] T019 [US2] Ensure missing/invalid `fast_mode` input is treated as OFF in `financial/views.py`
- [ ] T020 [US2] Keep Fast Mode state page-scoped only (no session/localStorage persistence) in `static/src/bill_pay_row_keyboard.js`
- [ ] T021 [US2] Update bill pay template state wiring for disabled-mode parity in `financial/templates/financial/bill_pay/index.html` and `financial/templates/financial/bill_pay/_row_edit.html`

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - End of List Handling (Priority: P3)

**Goal**: Handle terminal and open-next failure states cleanly without breaking saved-row state.

**Independent Test**: Save final unpaid row with Fast Mode ON and verify no invalid auto-open; simulate next-row open failure and verify an inline status message in the Bill Pay header area with manual continuation.

### Tests for User Story 3

- [ ] T022 [P] [US3] Add no-next-row terminal save test (no auto-open trigger action) in `financial/tests/test_bill_pay_save.py`
- [ ] T023 [P] [US3] Add open-next failure feedback behavior test in `financial/tests/test_bill_pay_row_keyboard.py`

### Implementation for User Story 3

- [ ] T024 [US3] Add subtle Fast Mode feedback container for open-next failures in `financial/templates/financial/bill_pay/index.html`
- [ ] T025 [US3] Implement open-next failure handling that keeps saved row stable and prompts manual continuation in `static/src/bill_pay_row_keyboard.js`
- [ ] T026 [US3] Ensure save success with no next unpaid row exits cleanly without extra trigger actions in `financial/views.py`

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation, and accountability updates across stories.

- [ ] T027 [P] [REQ:UI-001] Document finalized HTMX trigger contract examples in `specs/001-billpay-fast-mode/contracts/bill-pay-fast-mode.openapi.yaml`
- [ ] T028 [P] [REQ:UI-003] Update execution notes and manual validation steps in `specs/001-billpay-fast-mode/quickstart.md`
- [ ] T029 Run focused regression suite for bill pay fast mode in `financial/tests/test_bill_pay_save.py`, `financial/tests/test_bill_pay_row_keyboard.py`, `financial/tests/test_bill_pay_validation.py`, and `financial/tests/test_bill_pay_index.py`
- [ ] T030 [REQ:Principle-V] Add AI prompt/response traceability note for implementation in `docs/ai/006-bill-pay-fast-mode-log.md`
- [ ] T031 [REQ:UI-002] Verify template safety constraints (single-line `{% %}` and `{# #}` tags/comments, server-computed conditional state) in `financial/templates/financial/bill_pay/index.html` and `financial/templates/financial/bill_pay/_row_edit.html`
- [ ] T032 [REQ:Deterministic-Data] Verify no schema/fixture drift and record deterministic evidence (no new migrations, no fixture changes required) in `specs/001-billpay-fast-mode/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies; starts immediately.
- **Phase 2 (Foundational)**: Depends on Phase 1; blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2; defines MVP.
- **Phase 4 (US2)**: Depends on Phase 2; can run in parallel with US1 after foundation, but recommended after US1 for MVP-first.
- **Phase 5 (US3)**: Depends on Phase 2 and benefits from US1 trigger plumbing.
- **Phase 6 (Polish)**: Depends on completion of selected user stories.

### User Story Dependencies

- **US1 (P1)**: No dependency on other user stories.
- **US2 (P2)**: No strict dependency on US1, but validates non-fast-mode parity against shared code touched by US1.
- **US3 (P3)**: Depends on Fast Mode trigger/open behavior from US1.

### Within Each User Story

- Write tests first and confirm failure before implementation.
- Implement server behavior before client trigger handling when both are needed.
- Validate story completion independently before moving on.

---

## Parallel Opportunities

- **Setup**: T002 can run independently while T001 baseline test checks run.
- **Foundational**: T004 and T005 can run in parallel after T003 starts interface contracts.
- **US1**: T008/T009/T010 parallel; then T011 and T013 can proceed in parallel, followed by T014/T015.
- **US2**: T016/T017/T018 parallel; then T019 and T021 parallel.
- **US3**: T022/T023 parallel; then T024 and T026 parallel before T025 finalize client behavior.
- **Polish**: T027, T028, T031, and T032 parallel before T029/T030 final sign-off.

---

## Parallel Example: User Story 1

```bash
# Parallel test authoring
Task: T008 [US1] in financial/tests/test_bill_pay_save.py
Task: T009 [US1] in financial/tests/test_bill_pay_save.py
Task: T010 [US1] in financial/tests/test_bill_pay_row_keyboard.py

# Parallel implementation on different files
Task: T011 [US1] in financial/templates/financial/bill_pay/index.html
Task: T013 [US1] in financial/views.py
```

---

## Parallel Example: User Story 2

```bash
# Parallel tests
Task: T016 [US2] in financial/tests/test_bill_pay_save.py
Task: T017 [US2] in financial/tests/test_bill_pay_index.py
Task: T018 [US2] in financial/tests/test_bill_pay_validation.py

# Parallel implementation
Task: T019 [US2] in financial/views.py
Task: T021 [US2] in financial/templates/financial/bill_pay/index.html and financial/templates/financial/bill_pay/_row_edit.html
```

---

## Parallel Example: User Story 3

```bash
# Parallel tests
Task: T022 [US3] in financial/tests/test_bill_pay_save.py
Task: T023 [US3] in financial/tests/test_bill_pay_row_keyboard.py

# Parallel implementation
Task: T024 [US3] in financial/templates/financial/bill_pay/index.html
Task: T026 [US3] in financial/views.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate US1 independently with focused tests and manual flow from quickstart.
4. Demo/deploy MVP if ready.

### Incremental Delivery

1. Build foundation once (Phases 1–2).
2. Deliver US1 (Fast Mode core auto-advance).
3. Deliver US2 (disabled/default-off parity).
4. Deliver US3 (terminal/failure handling).
5. Finish Polish phase and full regression.

### Suggested MVP Scope

- **MVP**: Phase 1 + Phase 2 + Phase 3 (through T015).
- **Post-MVP**: US2 parity hardening, US3 terminal/failure UX, then polish/documentation.

---

## Notes

- `[P]` indicates tasks that can run concurrently without file conflicts/dependencies.
- User story labels `[US1]`, `[US2]`, `[US3]` provide strict traceability to spec scenarios.
- No database migration tasks are included because this feature introduces no schema changes.
- All implementation tasks keep existing dependency set (no new packages/services).
