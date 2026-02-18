# Feature Specification: Bill Pay Fast Mode

**Feature Branch**: `001-billpay-fast-mode`  
**Created**: 2026-02-17  
**Status**: Draft  
**Input**: User description: "Bill Pay Fast Mode (save → auto-open next unpaid row)"

> Per the Constitution, this spec must be reviewed and approved before any code is written. Capture determinism, dependency, and UI safety decisions here rather than deferring to implementation.

## Clarifications

### Session 2026-02-17

- Q: Which ordering should define "next unpaid row" for Fast Mode after a save? → A: Next unpaid row in the current on-screen table order (top-to-bottom).
- Q: When Fast Mode save succeeds but opening the next row fails (network/server error), what should the UX do? → A: Keep the saved row in view state, show a subtle inline error/toast, and require manual open of the next row.
- Q: What should the default Fast Mode toggle state be when the Bill Pay page first loads? → A: Default OFF on every initial page load.
- Q: How long should a user’s Fast Mode toggle choice persist after they change it from the default OFF state? → A: Current page only (resets to OFF on full page reload/new visit).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Save and Continue to Next Unpaid Row (Priority: P1)

As a user processing multiple bill pay rows, I can enable Fast Mode so that after saving one row, the next unpaid row opens directly in edit mode.

**Why this priority**: This is the core value of Fast Mode and directly reduces repetitive clicks and keyboard travel during bulk payment entry.

**Independent Test**: Can be fully tested by enabling Fast Mode, saving one unpaid row, and verifying that the next unpaid row automatically opens in edit mode with focus set to the payment amount field.

**Acceptance Scenarios**:

1. **Given** Fast Mode is enabled and at least two unpaid rows exist, **When** the user saves the current row, **Then** the saved row returns to view state and the next unpaid row opens in edit state.
2. **Given** Fast Mode is enabled, **When** the next unpaid row opens, **Then** input focus lands on the default payment amount field.

---

### User Story 2 - Normal Save Behavior When Fast Mode Is Off (Priority: P2)

As a user who does not want auto-advance behavior, I can leave Fast Mode disabled and keep the current save experience unchanged.

**Why this priority**: Protects existing workflows and prevents disruptive behavior changes for users who prefer manual row selection.

**Independent Test**: Can be tested by saving rows with Fast Mode disabled and verifying no additional row is auto-opened.

**Acceptance Scenarios**:

1. **Given** Fast Mode is disabled, **When** the user saves a row, **Then** only that row updates to view state and no other row changes state.

---

### User Story 3 - End of List Handling (Priority: P3)

As a user finishing a payment run, I receive a clear outcome when no unpaid rows remain after save.

**Why this priority**: Completes the workflow cleanly and avoids uncertainty when auto-advance has no valid next target.

**Independent Test**: Can be tested by saving the final unpaid row while Fast Mode is enabled and verifying no invalid row is opened.

**Acceptance Scenarios**:

1. **Given** Fast Mode is enabled and no unpaid rows remain after save, **When** save completes, **Then** no additional row enters edit mode and the page remains stable.

---

### Edge Cases

- User enables Fast Mode after the page has loaded and immediately saves a row.
- A previously selected “next” row becomes paid or unavailable before it opens.
- The next unpaid row exists but cannot be opened due to a transient request failure; keep saved row in view state, show subtle failure feedback, and require manual open for continuation.
- The current row save returns validation errors while Fast Mode is enabled.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The bill pay screen MUST provide a Fast Mode toggle that users can enable or disable during a session.
- **FR-001a**: On each initial Bill Pay page load, the Fast Mode toggle MUST default to OFF.
- **FR-001b**: The Fast Mode toggle state MUST persist only for the current page lifecycle and MUST reset to OFF after full page reload or a new visit.
- **FR-002**: When Fast Mode is enabled, each successful row save MUST include a server-evaluated next unpaid row candidate.
- **FR-003**: On successful save with Fast Mode enabled, the saved row MUST return to non-edit (view) state before any next-row edit action occurs.
- **FR-004**: If a next unpaid row is available, the system MUST automatically open that row in edit mode.
- **FR-005**: When auto-opening the next row, the system MUST place focus on the primary payment amount input by default.
- **FR-006**: When Fast Mode is disabled, save behavior MUST remain functionally equivalent to the current manual workflow.
- **FR-007**: If no next unpaid row exists, the system MUST complete save without opening another row.
- **FR-008**: If save fails validation, the system MUST keep the current row in edit mode with validation feedback and MUST NOT auto-advance.
- **FR-009**: Auto-advance logic MUST only consider rows in unpaid status within the active bill pay context shown to the user, and MUST select the next row using the current on-screen table order (top-to-bottom).
- **FR-010**: Fast Mode behavior MUST be available through keyboard-driven save actions as well as pointer-driven save actions.
- **FR-011**: If auto-opening the next row fails after a successful save, the system MUST keep the saved row in view state, display subtle failure feedback, and require manual open of the next row.

### Key Entities *(include if feature involves data)*

- **Bill Pay Row**: A payable row with unique row identity, payment status, and editable payment fields.
- **Fast Mode Preference (Page Scope)**: The user’s current on/off choice used during save operations for the current page lifecycle only.
- **Next Row Instruction**: A server-produced instruction associated with a successful save indicating whether a next unpaid row should open and where focus should start.

### Server-Driven UI & Template Safety *(mandatory for UI work)*

- **UI-001**: Row save endpoint response must document its swap behavior so the saved row container remains addressable and subsequent row actions still target stable row elements.
- **UI-002**: Any conditional UI state for Fast Mode controls or row edit/view state must be computed server-side and rendered without multi-line template tags or multi-line template comments.
- **UI-003**: Before diagnosing styling issues related to the new toggle or row states, the Tailwind/DaisyUI watcher command (`npm run dev:css`) must be running and rebuild output must be observed.

## Deterministic Data & Integrity *(mandatory)*

- **Schema Changes**: No database schema change is required for this feature; rollback is achieved by removing feature behavior without migration impact.
- **Data Fixtures**: Existing bill pay fixtures remain valid; no new fixture data is required to enable deterministic behavior checks.
- **External Inputs**: Next-row selection must be based on persisted unpaid status at save time within the current page context; no randomness or third-party dependency is introduced.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a test set with at least 10 unpaid rows, users complete sequential save-and-advance for all rows with zero manual row re-selection when Fast Mode is enabled.
- **SC-002**: At least 95% of successful saves with Fast Mode enabled open the intended next unpaid row on the first attempt in acceptance testing.
- **SC-003**: With Fast Mode disabled by default and when manually disabled, 100% of regression test scenarios for current row save behavior continue to pass.
- **SC-004**: For runs where no unpaid rows remain, users reach a stable completed state (no broken edit target) in 100% of tested sessions.

## Assumptions & Open Questions *(mandatory)*

- **Assumptions**:
  - The current on-screen bill pay table order is deterministic for the active page context.
  - Fast Mode preference is page scoped only and resets on full reload/new visit.
  - The primary focus target for auto-open is the actual payment amount input unless row type prevents it.
- **Open Questions**:
  - None at this time.
