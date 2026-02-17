# Feature Specification: BillPay Row Keyboard Editing

**Feature Branch**: `[001-billpay-row-keyboard-edit]`  
**Created**: 2026-02-17  
**Status**: Draft  
**Input**: User description: "Write a spec for a change in the BillPay feature so that the user can click on one of the editable fields and the row goes into edit mode and focus goes to the clicked field. And make the process keyboard-friendly row editing with tab order + enter/esc. Ensure that it is proper tab order of Funding Account, Actual Payment, Paid, Save button, Cancel button. Acceptance criteria - Tab cycles through the fields in a sensible order. - Enter saves - Esc cancels"

> Per the Constitution, this spec must be reviewed and approved before any code is written. Capture determinism, dependency, and UI safety decisions here rather than deferring to implementation.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Click-to-Edit on Intended Field (Priority: P1)

As a BillPay user, I want to click any editable cell in a row and immediately enter edit mode on that row with focus on the exact field I clicked so I can start editing without extra clicks.

**Why this priority**: Entering edit mode from the clicked field is the core behavior change and the fastest path to reducing editing friction.

**Independent Test**: Can be tested by opening BillPay, clicking each editable field type in turn, and confirming the row enters edit mode with focus on the clicked field.

**Acceptance Scenarios**:

1. **Given** a BillPay row is in read-only view, **When** the user clicks Funding Account, **Then** that row enters edit mode and focus is placed in Funding Account.
2. **Given** a BillPay row is in read-only view, **When** the user clicks Actual Payment, **Then** that row enters edit mode and focus is placed in Actual Payment.
3. **Given** a BillPay row is in read-only view, **When** the user clicks Paid, **Then** that row enters edit mode and focus is placed on the Paid control.

---

### User Story 2 - Keyboard-First Row Editing (Priority: P1)

As a keyboard user, I want a predictable tab sequence and keyboard shortcuts while editing a row so I can complete edits without using a mouse.

**Why this priority**: Keyboard accessibility is a required behavior and directly tied to acceptance criteria.

**Independent Test**: Can be tested by entering edit mode in one row and using only keyboard input to navigate, save, and cancel.

**Acceptance Scenarios**:

1. **Given** a row is in edit mode, **When** the user presses Tab repeatedly, **Then** focus advances in this order: Funding Account → Actual Payment → Paid → Save button → Cancel button.
2. **Given** focus is on Cancel button in an edited row, **When** the user presses Tab, **Then** focus cycles back to Funding Account in the same row.
3. **Given** a row has pending edits, **When** the user presses Enter while the row is in edit mode, **Then** the row attempts to save the current edits.
4. **Given** a row has pending edits, **When** the user presses Esc while the row is in edit mode, **Then** edits are discarded and the row returns to read-only mode.

---

### User Story 3 - Preserve Existing Save/Cancel Outcomes (Priority: P2)

As a BillPay user, I want keyboard-triggered save/cancel to behave the same as button-triggered save/cancel so outcomes remain consistent.

**Why this priority**: Consistency prevents confusion and regression risk, but depends on primary edit entry and keyboard flow.

**Independent Test**: Can be tested by performing the same row edit twice (once via buttons and once via keyboard shortcuts) and comparing outcomes.

**Acceptance Scenarios**:

1. **Given** valid row edits are present, **When** the user saves with Enter, **Then** persisted values match the result of clicking Save.
2. **Given** unsaved row edits are present, **When** the user cancels with Esc, **Then** row values match the result of clicking Cancel.

### Edge Cases

- If the clicked field is temporarily non-editable, row edit mode still opens and focus moves to the first editable control in the required tab order.
- If a save validation error occurs after Enter, the row remains in edit mode and focus moves to the first field requiring correction.
- Keyboard shortcuts apply only to the active editing row and do not trigger actions in other rows.
- If no values changed, Enter still exits edit mode through the standard save path without creating duplicate updates.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow entry into edit mode by clicking any editable BillPay row field.
- **FR-002**: System MUST place focus on the specific field that triggered row edit mode.
- **FR-003**: System MUST support keyboard tab navigation within an editing row in this exact order: Funding Account control, Actual Payment input, Paid checkbox, Save button, Cancel button.
- **FR-004**: System MUST cycle Tab focus within the active editing row so keyboard users can continue editing without leaving the row unintentionally.
- **FR-005**: System MUST treat Enter as Save for the active editing row.
- **FR-006**: System MUST treat Esc as Cancel for the active editing row.
- **FR-007**: System MUST ensure keyboard-triggered actions (Enter save, Esc cancel) use the same underlying save/cancel outcomes as button-triggered actions, including persisted data and returned row state.
- **FR-008**: System MUST keep row-level editing scoped to one active row at a time.
- **FR-009**: System MUST preserve existing validation behavior during keyboard-triggered save attempts.
- **FR-010**: System MUST return the row to non-edit mode after successful save or cancel.

### Key Entities *(include if feature involves data)*

- **BillPay Row**: A single account-month payment row with read and edit states and row-scoped actions.
- **Editable Inputs**: Row inputs that can be changed in edit mode: Actual Payment and Paid.
- **Funding Account Control**: A focusable row control used for edit-entry and keyboard order; it does not introduce a new persisted field in this feature.
- **Row Action Controls**: Save and Cancel controls tied to a specific row edit session.

### Server-Driven UI & Template Safety *(mandatory for UI work)*

- **UI-001**: BillPay row update interactions MUST target a stable row container so the active row remains addressable after swaps.
- **UI-002**: Row partial responses MUST preserve the triggerable controls needed to re-enter edit mode from any editable field.
- **UI-003**: Any edit-mode state flags and field-order metadata MUST be computed server-side and rendered without multiline template tags or multiline Django template comments.
- **UI-004**: Before investigating styling anomalies related to focus/edit states, confirm `npm run dev:css` is running and rebuild output is visible.

## Deterministic Data & Integrity *(mandatory)*

- **Schema Changes**: No schema change is expected for this interaction-only enhancement.
- **Data Fixtures**: Existing BillPay fixtures remain valid; add or update deterministic fixture rows only if needed to test keyboard navigation and row state transitions consistently.
- **External Inputs**: Keyboard events and focus behavior tests must use deterministic initial row state and controlled test data so outcomes are repeatable.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In acceptance testing, 100% of editable-field clicks enter edit mode on the same row and focus the clicked field.
- **SC-002**: In acceptance testing, Tab navigation follows the required control order for 100% of tested rows.
- **SC-003**: In acceptance testing, Enter saves and Esc cancels with outcome parity to button clicks in 100% of tested scenarios.
- **SC-004**: In a scripted keyboard-only usability check with at least 10 participants on desktop browsers, at least 90% complete a row edit (enter edit mode, modify value, save or cancel) without using a mouse.

## Assumptions & Open Questions *(mandatory)*

- **Assumptions**:
  - This change applies only to BillPay row editing interactions and does not expand editable data scope.
  - Existing Save and Cancel business rules remain authoritative; keyboard shortcuts invoke those same outcomes.
  - Required tab order is strictly: Funding Account, Actual Payment, Paid, Save, Cancel.
  - Focus trapping is row-scoped only while a row is actively in edit mode.
- **Open Questions**:
  - None currently blocking implementation.
