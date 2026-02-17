# Tasks: Subtle Row Swap Animation

**Input**: Design documents from `/specs/001-row-swap-animation/`
**Prerequisites**: `plan.md` (required), `spec.md` (required), `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Automated tests are included per constitution fail-first requirements and must fail before implementation changes are applied.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare implementation tracking and validation artifacts used by all stories.

- [X] T001 Create AI accountability log scaffold in specs/001-row-swap-animation/ai-log.md
- [X] T002 Capture baseline “no-animation” validation notes in specs/001-row-swap-animation/quickstart.md
- [X] T003 Start and verify Tailwind watcher output (`npm run dev:css`) and log evidence in specs/001-row-swap-animation/quickstart.md
- [X] T004 Confirm endpoint/HTMX contract annotations remain current in specs/001-row-swap-animation/contracts/bill-pay-row-animation.openapi.yaml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared behavior and hooks required before any user story work.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T005 Add shared bill-pay row enter-transition CSS classes in static/src/input.css
- [X] T006 Add bill-pay row HTMX swap event utilities scaffold in static/src/bill_pay_row_keyboard.js
- [X] T007 [P] Add stable transition hook attributes/classes on display rows in financial/templates/financial/bill_pay/_row.html
- [X] T008 [P] Add stable transition hook attributes/classes on edit rows in financial/templates/financial/bill_pay/_row_edit.html

**Checkpoint**: Foundation ready — user story implementation can begin.

---

## Phase 3: User Story 1 - Smooth row transition on mode switch (Priority: P1) 🎯 MVP

**Goal**: Ensure view↔edit bill-pay row swaps show a subtle enter fade/slide transition instead of abrupt pop.

**Independent Test**: Toggle a single bill-pay row through Edit, Save, and Cancel and verify the swapped row always enters with subtle fade/slide motion.

### Implementation for User Story 1

### Tests for User Story 1 (Fail First)

- [X] T009 [P] [US1] Add failing HTMX row swap transition test coverage in financial/tests/test_bill_pay_row_keyboard.py
- [X] T010 [P] [US1] Add failing save/cancel swap regression test coverage in financial/tests/test_bill_pay_save.py

### Implementation for User Story 1

- [X] T011 [US1] Implement `htmx:afterSwap` enter-transition application for bill-pay row swaps in static/src/bill_pay_row_keyboard.js
- [X] T012 [US1] Implement 120–180ms fade/slide enter animation styles in static/src/input.css
- [X] T013 [US1] Preserve view-row `hx-target`/`hx-swap` behavior while exposing animation hooks in financial/templates/financial/bill_pay/_row.html
- [X] T014 [US1] Preserve edit-row save/cancel `hx-target`/`hx-swap` behavior while exposing animation hooks in financial/templates/financial/bill_pay/_row_edit.html
- [X] T015 [US1] Record US1 manual validation evidence for edit/save/cancel swaps in specs/001-row-swap-animation/quickstart.md

**Checkpoint**: User Story 1 is independently functional and demonstrable (MVP).

---

## Phase 4: User Story 2 - Motion remains subtle and non-distracting (Priority: P2)

**Goal**: Keep transitions calm and reliable under repeated interactions without blocking controls.

**Independent Test**: Rapidly toggle a row 20+ times (including validation-error path) and verify transitions stay subtle, controls remain usable, and no stale classes persist.

### Implementation for User Story 2

### Tests for User Story 2 (Fail First)

- [X] T016 [P] [US2] Add failing rapid-toggle/cleanup regression coverage in financial/tests/test_bill_pay_row_keyboard_shortcuts.py
- [X] T017 [P] [US2] Add failing non-bill-pay regression coverage for untouched HTMX flows in financial/tests/test_hx_trigger_preservation.py

### Implementation for User Story 2

- [X] T018 [US2] Tune transition opacity/translate values for non-distracting motion in static/src/input.css
- [X] T019 [US2] Implement transition cleanup and rapid-toggle safety logic in static/src/bill_pay_row_keyboard.js
- [X] T020 [US2] Ensure invalid `422` edit-row responses follow the same transition hook path in financial/views.py
- [X] T021 [US2] Verify optional leaving-animation path remains non-blocking and non-required in static/src/bill_pay_row_keyboard.js
- [X] T022 [US2] Add explicit FR-010 validation step for reduced-motion contexts (animation still present) in specs/001-row-swap-animation/quickstart.md
- [X] T023 [US2] Add explicit FR-011 scope guard validation (no non-bill-pay animation changes) in specs/001-row-swap-animation/quickstart.md
- [X] T024 [US2] Record repeated-toggle and validation-error usability results in specs/001-row-swap-animation/quickstart.md

**Checkpoint**: User Story 2 is independently functional and does not degrade US1 behavior.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency, traceability, and delivery readiness across stories.

- [X] T025 [P] Update implementation evidence and constitution gate notes in specs/001-row-swap-animation/plan.md
- [X] T026 [P] Record final prompt/response references for PR traceability in specs/001-row-swap-animation/ai-log.md
- [X] T027 Run end-to-end quickstart checklist and finalize outcomes in specs/001-row-swap-animation/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies; starts immediately.
- **Phase 2 (Foundational)**: Depends on Phase 1; blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2 completion.
- **Phase 4 (US2)**: Depends on Phase 2 completion; can begin after US1 if single-threaded, or in parallel after shared hooks are stable.
- **Phase 5 (Polish)**: Depends on completion of desired user stories.

### User Story Dependencies

- **US1 (P1)**: No dependency on US2; delivers MVP value alone.
- **US2 (P2)**: Depends on shared foundational hooks; refines and stress-hardens US1 behavior.

### Within Each User Story

- Fail-first tests first, then implementation.
- Shared hooks and CSS foundations next.
- Behavior implementation before validation evidence updates.
- Story-level manual validation before phase checkpoint.

---

## Parallel Opportunities

- **Setup**: T004 can run while T001/T002/T003 are in progress.
- **Foundational**: T007 and T008 can run in parallel after T005/T006.
- **US1**: T009 and T010 run in parallel (both fail-first tests) before T011.
- **US2**: T016 and T017 run in parallel (both fail-first tests) before T018.
- **Polish**: T025 and T026 run in parallel before T027 final pass.

---

## Parallel Example: User Story 1

```bash
# Parallelizable US1 tasks after core event hook is in place:
Task T009: financial/tests/test_bill_pay_row_keyboard.py
Task T010: financial/tests/test_bill_pay_save.py
```

## Parallel Example: User Story 2

```bash
# Parallelizable US2 tasks once cleanup approach is decided:
Task T016: financial/tests/test_bill_pay_row_keyboard_shortcuts.py
Task T017: financial/tests/test_hx_trigger_preservation.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup).
2. Complete Phase 2 (Foundational).
3. Complete Phase 3 (US1).
4. Validate US1 independently and stop for review/demo.

### Incremental Delivery

1. Deliver US1 as the first usable increment.
2. Add US2 refinements for subtlety and interaction resilience.
3. Finish with Polish phase traceability and final checklist.

### Suggested MVP Scope

- **MVP**: Phase 1 + Phase 2 + Phase 3 (User Story 1 only)
