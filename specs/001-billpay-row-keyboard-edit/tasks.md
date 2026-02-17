# Tasks: BillPay Row Keyboard Editing

**Input**: Design documents from `/specs/001-billpay-row-keyboard-edit/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish execution guardrails and traceability for this feature.

- [ ] T001 Confirm CSS watcher workflow and evidence steps in specs/001-billpay-row-keyboard-edit/quickstart.md (Principle IV)
- [ ] T002 Add implementation prompt/response tracking section in specs/001-billpay-row-keyboard-edit/research.md (Principle V)
- [ ] T003 Verify endpoint reuse scope note in specs/001-billpay-row-keyboard-edit/plan.md matches existing financial/views.py architecture

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared row-edit plumbing required before any user story implementation.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T004 Add row keyboard/focus intent parsing helpers in financial/views.py for bill_pay_row request handling
- [ ] T005 [P] Add canonical focus-field constants and validation mapping in financial/services/bill_pay.py
- [ ] T006 [P] Add stable row control identifiers/data attributes in financial/templates/financial/bill_pay/_row_edit.html for keyboard targeting
- [ ] T007 Extend existing BillPay row contract with finalized request/response examples in specs/001-billpay-row-keyboard-edit/contracts/billpay-row-edit.openapi.yaml

**Checkpoint**: Foundation ready — user stories can now be implemented.

---

## Phase 3: User Story 1 - Click-to-Edit on Intended Field (Priority: P1) 🎯 MVP

**Goal**: Clicking an editable BillPay field opens row edit mode and focuses the clicked field.

**Independent Test**: Open BillPay, click Funding Account, Actual Payment, and Paid cells independently; each action swaps only that row to edit mode and places focus on the corresponding control.

### Tests for User Story 1

- [ ] T008 [P] [US1] Add HTMX row-edit click entry tests for focus-field intent in financial/tests/test_bill_pay_row_focus_entry.py (Spec US1, FR-001, FR-002)
- [ ] T009 [US1] Add row edit response assertions for focus metadata and row-targeted partial root in financial/tests/test_bill_pay_row_focus_entry.py (Spec US1, UI-001)

### Implementation for User Story 1

- [ ] T010 [US1] Update display row editable-cell triggers to request existing bill_pay_row endpoint with focus_field query param in financial/templates/financial/bill_pay/_row.html (Spec US1 Scenario 1-3)
- [ ] T011 [US1] Update bill_pay_row GET path to accept/validate focus_field and pass focus context to edit partial in financial/views.py (Spec FR-002)
- [ ] T012 [US1] Render field-specific autofocus/focus target hooks in financial/templates/financial/bill_pay/_row_edit.html (Spec FR-002, UI-002)
- [ ] T013 [US1] Keep row swap contract stable (`hx-target` row id + `outerHTML`) while adding click-entry controls in financial/templates/financial/bill_pay/_row.html and financial/templates/financial/bill_pay/_row_edit.html (Spec UI-001)

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Keyboard-First Row Editing (Priority: P1)

**Goal**: In edit mode, keyboard flow supports required tab sequence and Enter/Esc shortcuts.

**Independent Test**: Enter edit mode on one row and use keyboard only; Tab cycles Funding Account → Actual Payment → Paid → Save → Cancel, Enter saves, and Esc cancels.

### Tests for User Story 2

- [ ] T014 [P] [US2] Add keyboard tab-order and cycle tests for edit-row controls in financial/tests/test_bill_pay_row_keyboard.py (Spec US2 Scenario 1-2, FR-003, FR-004)
- [ ] T015 [P] [US2] Add Enter-save and Esc-cancel keyboard behavior tests in financial/tests/test_bill_pay_row_keyboard_shortcuts.py (Spec US2 Scenario 3-4, FR-005, FR-006)

### Implementation for User Story 2

- [ ] T016 [US2] Add explicit tab-index/control-order wiring for Funding Account, Actual Payment, Paid, Save, Cancel in financial/templates/financial/bill_pay/_row_edit.html (Spec FR-003)
- [ ] T017 [US2] Add row-scoped keyboard handler (Tab cycle, Enter intent, Esc intent) in static/src/bill_pay_row_keyboard.js (Spec FR-004, FR-005, FR-006)
- [ ] T018 [US2] Wire BillPay page to load row keyboard handler for edit rows in financial/templates/financial/bill_pay/index.html (Spec US2)
- [ ] T019 [US2] Handle keyboard_intent=cancel using existing bill_pay_row endpoint to return display row without persisting edits in financial/views.py (Spec FR-006, FR-010)
- [ ] T020 [US2] Keep validation-failure behavior row-scoped (422 edit row re-render + focus to first invalid field) in financial/views.py and financial/templates/financial/bill_pay/_row_edit.html (Spec Edge Case 2, FR-009)

**Checkpoint**: User Story 2 is independently functional and testable.

---

## Phase 5: User Story 3 - Preserve Existing Save/Cancel Outcomes (Priority: P2)

**Goal**: Keyboard-triggered save/cancel outcomes match button-triggered behavior and persistence rules.

**Independent Test**: Perform equivalent edits via button actions and keyboard actions; compare saved data and UI outcomes for parity.

### Tests for User Story 3

- [ ] T021 [P] [US3] Add parity tests comparing Enter-save with Save-button persistence outcomes in financial/tests/test_bill_pay_save.py (Spec US3 Scenario 1, FR-007)
- [ ] T022 [P] [US3] Add parity tests comparing Esc-cancel with Cancel-action non-persistence outcomes in financial/tests/test_bill_pay_validation.py (Spec US3 Scenario 2, FR-007)

### Implementation for User Story 3

- [ ] T023 [US3] Ensure keyboard save path reuses existing upsert/save logic with no duplicate code path in financial/views.py (Spec FR-007)
- [ ] T024 [US3] Ensure keyboard cancel path returns canonical display row partial identical to cancel-action output in financial/views.py and financial/templates/financial/bill_pay/_row.html (Spec FR-007, FR-010)
- [ ] T025 [US3] Confirm single-active-row edit scope is preserved while keyboard actions execute in financial/templates/financial/bill_pay/_row.html and static/src/bill_pay_row_keyboard.js (Spec FR-008)

**Checkpoint**: User Story 3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize documentation, regression confidence, and readiness checks across stories.

- [ ] T026 [P] Update quick verification steps and expected outcomes in specs/001-billpay-row-keyboard-edit/quickstart.md
- [ ] T027 Run focused regression suite for BillPay row behavior in financial/tests/test_bill_pay_index.py, financial/tests/test_bill_pay_save.py, financial/tests/test_bill_pay_validation.py, financial/tests/test_bill_pay_row_focus_entry.py, financial/tests/test_bill_pay_row_keyboard.py, financial/tests/test_bill_pay_row_keyboard_shortcuts.py
- [ ] T028 [P] Record implementation evidence and AI attribution links for PR in specs/001-billpay-row-keyboard-edit/research.md (Principle V)
- [ ] T029 Define SC-004 usability protocol (participant criteria, scripted task, pass/fail capture) in specs/001-billpay-row-keyboard-edit/quickstart.md
- [ ] T030 Execute SC-004 keyboard-only usability check and record completion metric evidence in specs/001-billpay-row-keyboard-edit/research.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: starts immediately.
- **Phase 2 (Foundational)**: depends on Phase 1 and blocks all stories.
- **Phase 3 (US1)**: depends on Phase 2.
- **Phase 4 (US2)**: depends on Phase 2 and can start after US1 structure is available.
- **Phase 5 (US3)**: depends on US2 keyboard action paths and US1 row-entry behavior.
- **Phase 6 (Polish)**: depends on completion of desired user stories.

### User Story Dependencies

- **US1 (P1)**: no dependency on other stories after foundational phase.
- **US2 (P1)**: depends on US1 row edit entry hooks for complete keyboard flow.
- **US3 (P2)**: depends on US2 keyboard paths to verify parity.

### Within Each User Story

- Write tests first and ensure they fail before implementation.
- Template/view wiring before JavaScript integration checks.
- Keyboard intent handling before parity verification.

## Parallel Opportunities

- **Setup**: T002 and T003 can run in parallel after T001.
- **Foundational**: T005 and T006 can run in parallel; T007 can run in parallel after T004 semantics are agreed.
- **US1**: T008 and T009 can run in parallel; T012 and T013 can run in parallel after T011.
- **US2**: T014 and T015 can run in parallel; T017 and T019 can run in parallel after T016.
- **US3**: T021 and T022 can run in parallel; T024 and T025 can run in parallel after T023.
- **Polish**: T028 and T029 can run in parallel; T030 depends on T029.

---

## Parallel Example: User Story 1

- Run together: T008 and T009 (same story, different assertions in same new test module workflow).
- Run together after T011: T012 and T013 (edit partial focus hooks and swap-contract hardening).

## Parallel Example: User Story 2

- Run together: T014 and T015 (tab-order/cycle tests and Enter/Esc tests).
- Run together after T016: T017 and T019 (client keyboard handler + server cancel intent handling).

## Parallel Example: User Story 3

- Run together: T021 and T022 (save parity vs cancel parity test coverage).
- Run together after T023: T024 and T025 (cancel display parity + single-active-row enforcement).

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phases 1-2.
2. Complete Phase 3 (US1).
3. Validate US1 independently with click-to-edit focus tests and manual HTMX row swap checks.

### Incremental Delivery

1. Deliver US1 (click-to-edit focus) as first shippable increment.
2. Add US2 (keyboard tab/Enter/Esc) and validate keyboard-only flow.
3. Add US3 parity hardening and regression coverage.
4. Execute Phase 6 polish, including SC-004 usability protocol and evidence capture.

### Suggested MVP Scope

- **MVP**: Through Phase 3 (US1) only.
- **Full requested scope**: Through Phase 5 (US1 + US2 + US3), then Phase 6 polish.
