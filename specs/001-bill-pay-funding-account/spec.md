# Feature Specification: Bill Pay Funding Account Selector

**Feature Branch**: `[001-bill-pay-funding-account]`  
**Created**: 2026-02-14  
**Status**: Draft  
**Input**: User description: "Add a drop-down selector to the bill pay row. This should be populated with all Accounts. When a user edits a row, they will now select the account that is funding the payment. The user will then enter the amount paid, mark the row as paid, and then save the edited row."

> Per the Constitution, this spec must be reviewed and approved before any code is written. Capture determinism, dependency, and UI safety decisions here rather than deferring to implementation.

## Clarifications

### Session 2026-02-14

- Q: Which conflict behavior should apply if two users edit and save the same bill-pay row at nearly the same time? → A: Last-write-wins (latest successful save overwrites prior values), no conflict prompt.
- Q: When populating the funding-account dropdown, which account status should be included? → A: Include only active accounts; if a saved closed account exists, show it as selected but not available for new choices.
- Q: Should saving a bill-pay row with funding account also create/update a financial transaction record automatically? → A: No, do not create transactions; only persist bill-pay row fields.
- Q: Are pending-status accounts eligible as funding-account dropdown options? → A: No. Only active accounts are eligible for new selections; pending and closed accounts are excluded from selectable options.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Edit Bill Row With Funding Account (Priority: P1)

As a household member, I want to select the account that funds a bill payment while editing a bill row so payment records clearly show where money came from.

**Why this priority**: This is the new core behavior requested and is required for accurate payment tracking.

**Independent Test**: Can be fully tested by editing one bill row, selecting a funding account, entering an amount, marking paid, and saving; the saved row shows the selected funding account on reload.

**Acceptance Scenarios**:

1. **Given** a user opens Bill Pay and starts editing a row, **When** the row enters edit mode, **Then** a funding account selector is visible in that row.
2. **Given** the user is editing a row, **When** the selector is opened, **Then** all accounts available to that user are listed as selectable options.
3. **Given** the user selects a funding account, enters paid amount, checks paid, and saves, **When** the save completes, **Then** the row persists all edited values including the funding account.
4. **Given** a row already has a saved funding account, **When** the user edits that row again, **Then** the previously saved funding account is pre-selected.

---

### User Story 2 - Prevent Invalid Save States (Priority: P2)

As a household member, I want clear validation when required bill payment edit fields are missing so I can correct the row before saving.

**Why this priority**: Validation prevents ambiguous or incomplete payment records and reduces accidental bad data.

**Independent Test**: Can be tested by attempting to save an edited row without a funding account selection and verifying that save is blocked with row-level feedback while inputs remain editable.

**Acceptance Scenarios**:

1. **Given** a user edits a row and does not select a funding account, **When** the user clicks Save, **Then** the save is rejected and the row shows validation feedback.
2. **Given** a row fails validation, **When** the row re-renders, **Then** entered amount and paid checkbox state remain visible for correction.

---

### User Story 3 - Keep Existing Row Edit Workflow (Priority: P3)

As a household member, I want the existing bill row edit flow to remain familiar so adding funding account selection does not disrupt how I record payments.

**Why this priority**: Maintaining current edit behavior lowers retraining cost and avoids regressions in routine monthly use.

**Independent Test**: Can be tested by editing and saving multiple rows and confirming the same row-level save interaction still works with the added selector.

**Acceptance Scenarios**:

1. **Given** a user edits a row, **When** they complete selection + amount + paid + save, **Then** the row exits edit mode and shows updated saved values.
2. **Given** a user cancels or leaves a row without saving, **When** the page reloads, **Then** unsaved row edits are not persisted.

### Edge Cases

- No accounts are available for selection; row save is blocked with a clear message.
- If a previously saved funding account is now closed, edit mode displays it as the current selected value but does not allow choosing closed accounts as new options.
- The bill account and funding account are the same account; selection is permitted unless business rules explicitly forbid it.
- Concurrent edits to the same bill row resolve deterministically so the last successful save is what appears.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST add a funding account selector to each bill pay row in edit mode.
- **FR-002**: System MUST populate the funding account selector with only status=active accounts the current user is authorized to access; status=pending and status=closed accounts MUST NOT be selectable as new options.
- **FR-003**: System MUST require funding account selection before an edited row can be saved.
- **FR-004**: System MUST allow a user to enter or modify paid amount, toggle paid status, and save within the same row edit interaction.
- **FR-005**: System MUST persist funding account, paid amount, and paid status together when row save succeeds.
- **FR-006**: System MUST pre-populate edit mode with any previously saved funding account for that row.
- **FR-007**: System MUST return row-level validation feedback when save fails and keep user-entered values visible for correction.
- **FR-008**: System MUST keep unsaved edits non-persistent unless the user explicitly saves the row.
- **FR-009**: System MUST retain existing household/user data access boundaries so users cannot select or save funding accounts outside their allowed scope.
- **FR-010**: System MUST apply last-write-wins for concurrent saves to the same bill-pay row, where the latest successful save becomes the persisted row state without conflict prompts.
- **FR-011**: System MUST display a previously saved closed funding account as the current selected value during edit, while preventing closed accounts from being selected as new choices.
- **FR-012**: System MUST NOT create or modify financial transaction records when saving a bill-pay row in this feature; save operations persist only bill-pay row fields.

### Key Entities *(include if feature involves data)*

- **Bill Pay Row**: A monthly bill payment record a user edits, including paid amount, paid status, and selected funding account.
- **Funding Account**: An existing account chosen as the source of payment for a specific bill pay row.
- **Bill Account**: The liability account for which the payment row is being tracked.

### Server-Driven UI & Template Safety *(mandatory for UI work)*

- **UI-001**: Bill pay row edit endpoint renders edit-row partials with a stable row container target so save responses only swap the row content, not the surrounding table/container.
- **UI-002**: Row save endpoint returns either updated display-row partial (success) or edit-row partial with validation errors (failure), preserving the triggering row element in the DOM.
- **UI-003**: Selector options, selected value, and row state classes/attributes are computed server-side and rendered via template context or single-line template assignments.
- **UI-004**: Tailwind/DaisyUI watcher command `npm run dev:css` is confirmed active and rebuild output captured before investigating any styling issues.

## Deterministic Data & Integrity *(mandatory)*

- **Schema Changes**: Add deterministic storage for the row’s selected funding account reference and ensure migration rollback cleanly removes that reference while preserving pre-existing bill pay data.
- **Data Fixtures**: Update bill pay fixture coverage with at least one liability account, at least two potential funding accounts, and one saved row demonstrating persisted funding selection. Fixture loading remains idempotent.
- **External Inputs**: Use deterministic timestamps/month context in tests and avoid random account ordering so selector options and saved outcomes are consistent across runs.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 95% of users can complete one edited bill row save (select funding account, enter amount, mark paid, save) in under 45 seconds during usability testing.
- **SC-002**: 100% of successful row saves retain the selected funding account after page reload in acceptance testing.
- **SC-003**: 100% of attempted saves without funding account selection are blocked with clear row-level feedback in validation tests.
- **SC-004**: At least 90% of users report the updated row edit flow as clear and understandable, measured by a post-task survey where at least 10 participants each rate clarity on a 1–5 scale and scores of 4 or 5 count as success.

## Assumptions & Open Questions *(mandatory)*

- **Assumptions**:
  - Funding account selection is required for saving a bill pay row edit.
  - Any account type may be selected as a funding account only when its status is active and the user is authorized to access it.
  - Existing bill pay rows without historical funding account values remain editable and require selection on next save.
  - The existing row-level Save action remains the only persistence trigger.
  - Row save in this feature does not trigger transaction ledger creation or updates.
- **Open Questions**:
  - None currently blocking implementation.
