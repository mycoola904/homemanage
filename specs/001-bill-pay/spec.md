# Feature Specification: Bill Pay

**Feature Branch**: `[001-bill-pay]`  
**Created**: 2026-02-13  
**Status**: Draft  
**Input**: User description: "Build the Bill Pay feature. Add a Bill Pay sidebar destination that displays a monthly table of liability accounts, sorted by due day, and allows recording payment amount and paid status per account per month."

> Per the Constitution, this spec must be reviewed and approved before any code is written. Capture determinism, dependency, and UI safety decisions here rather than deferring to implementation.

## Clarifications

### Session 2026-02-13

- Q: How should unfinished bill pay items behave when a new month starts? → A: Hard month boundary; new month shows only that month’s bills, and prior unpaid items remain in prior-month history.
- Q: How should bill row edits be persisted? → A: Each row uses an explicit Save action; changes persist only when that row is saved.
- Q: Should Bill Pay support month selection in this feature? → A: Yes; users can select and edit prior months, with no auto-carry-forward between months.
- Q: What validation rule should apply between paid and actual payment amount? → A: Paid is independent from amount; paid may be true with 0.00 or blank amount.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Review Monthly Bills (Priority: P1)

As a household member, I want to open Bill Pay and immediately see all liability accounts due this month so I can plan payments in due-date order.

**Why this priority**: This is the core value of the feature. Without the monthly bill list, users cannot manage payments.

**Independent Test**: Can be fully tested by navigating to Bill Pay and confirming that only liability accounts are shown in ascending due-day order with the required columns.

**Acceptance Scenarios**:

1. **Given** the user is signed in and has liability accounts, **When** the user opens Bill Pay from the sidebar, **Then** the monthly bill pay table is shown in the main content area.
2. **Given** the user has a mix of account types, **When** the table loads, **Then** only credit card, loan, and other liability accounts are included.
3. **Given** multiple liability accounts with different due days, **When** the table loads, **Then** rows are sorted by payment due day from smallest to largest.
4. **Given** the Bill Pay page is opened, **When** the user views the page, **Then** the current month is shown by default and a month selector is available.

---

### User Story 2 - Record Payment Status (Priority: P1)

As a household member, I want to enter the actual payment made and mark whether a bill is paid so monthly payment tracking is accurate.

**Why this priority**: Recording actual payments is the primary action that turns the bill list into a usable workflow.

**Independent Test**: Can be fully tested by editing one row, saving it, and verifying the stored amount and paid status for the selected month are retained after reload.

**Acceptance Scenarios**:

1. **Given** a bill row in the current month table, **When** the user enters an actual payment amount and sets paid to true, **Then** the row saves successfully and reflects the new values.
2. **Given** a bill row has saved payment values for the month, **When** the user revisits Bill Pay in the same month, **Then** the saved amount and paid state are pre-populated.
3. **Given** a bill row is marked paid, **When** the user unchecks paid and saves, **Then** the updated unpaid state is persisted for that same month.
4. **Given** a user edits a row but does not click Save, **When** the user navigates away or reloads, **Then** unsaved edits are not persisted.
5. **Given** a row has paid checked with amount 0.00 or blank, **When** the row is saved, **Then** the save succeeds and persists the paid state.

---

### User Story 3 - Use Account Payment Links (Priority: P2)

As a household member, I want direct access to each account’s online payment URL from Bill Pay so I can quickly complete payments.

**Why this priority**: This improves usability and speed but is secondary to viewing and recording payments.

**Independent Test**: Can be tested independently by opening Bill Pay and verifying each row displays the account’s online access URL value.

**Acceptance Scenarios**:

1. **Given** an account has an online access URL, **When** the Bill Pay table is shown, **Then** the URL is visible on that row.
2. **Given** an account does not have an online access URL, **When** the Bill Pay table is shown, **Then** the URL cell shows a clear empty-state value without breaking layout.

---

### Edge Cases

- Liability accounts with no due day appear after accounts with due days while preserving stable ordering among themselves.
- Accounts with a null minimum amount due remain visible and allow recording an actual payment amount.
- Entering a negative payment amount is rejected with a clear validation error.
- Paid may be set to true even when actual payment amount is blank or 0.00.
- Duplicate save submissions for the same account and month update the existing monthly payment record rather than creating duplicate monthly entries.
- On month rollover, unpaid items from a previous month are not auto-carried into the new month list and remain visible only in prior-month history.
- Users can navigate back to prior months and update payment status within that selected month.
- If a liability account becomes non-liability, it no longer appears in Bill Pay for new loads, while prior monthly payment records remain historically available.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a "Bill Pay" navigation item in the sidebar.
- **FR-002**: System MUST display a monthly bill pay table in the main content area when Bill Pay is opened.
- **FR-003**: System MUST include only liability account types (credit card, loan, other) in the monthly bill pay table.
- **FR-004**: System MUST render each row with account name, institution, payment due day, minimum amount due, and online access URL.
- **FR-005**: System MUST sort rows by payment due day in ascending order for the displayed month.
- **FR-006**: System MUST allow users to enter or edit actual payment amount per account for the displayed month.
- **FR-007**: System MUST allow users to set or clear a paid checkbox per account for the displayed month.
- **FR-008**: System MUST persist payment amount and paid status by account and month when a row is saved.
- **FR-009**: System MUST reload previously saved monthly payment values into the table for that account-month combination.
- **FR-010**: System MUST prevent creation of more than one monthly payment record per account and month.
- **FR-011**: System MUST show meaningful validation feedback when payment entry fails and MUST preserve unsaved user input in the row.
- **FR-012**: System MUST enforce household/user scoping so users only view and modify bill pay data for accounts they are permitted to access.
- **FR-013**: System MUST enforce a hard month boundary: the displayed month includes only bills for that month and MUST NOT auto-carry unpaid bills from prior months into the new month table.
- **FR-014**: System MUST persist row changes only on explicit per-row Save and MUST NOT auto-save on blur, toggle, or background timer events.
- **FR-015**: System MUST default Bill Pay to the current month and provide month navigation/selection so users can view and edit prior months.
- **FR-016**: System MUST treat paid status as independent from actual payment amount; paid=true with amount blank or 0.00 is valid, while negative amounts remain invalid.

### Key Entities *(include if feature involves data)*

- **Account**: Existing financial account record used as the source for bill pay rows, including account type, due day, minimum amount due, institution, and online access URL.
- **Monthly Bill Payment**: Per-account, per-month record storing actual payment amount, paid status, and the effective payment date/month context used for bill pay tracking.

### Server-Driven UI & Template Safety *(mandatory for UI work)*

- **UI-001**: Bill Pay page endpoint returns the full monthly table view; row-save endpoint returns a row or table partial targeted to the row container, ensuring the table wrapper remains in the DOM.
- **UI-002**: Row save interactions target only the edited row and use a swap mode that replaces row content without removing the stable table shell; each row includes a dedicated Save trigger.
- **UI-003**: Any dynamic row state (paid indicator, validation state, empty URL display) is computed server-side and rendered through template context or single-line template assignments.
- **UI-004**: Before any styling/layout debugging, verify the CSS watcher command `npm run dev:css` is running and capture rebuild output.

## Deterministic Data & Integrity *(mandatory)*

- **Schema Changes**: Add schema support for monthly bill payment records keyed by account and month, with a deterministic uniqueness rule to enforce one record per account-month. Include forward and reverse migration behavior.
- **Data Fixtures**: Extend or add financial fixtures with at least one credit card, one loan, and one other liability account plus representative monthly bill payment records. Fixture loading must be idempotent and produce the same account-month outcomes each run.
- **External Inputs**: Use explicit month boundaries derived from application time context and normalize persisted month values so tests and repeated executions produce deterministic results.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 95% of users can locate and open Bill Pay from the sidebar in under 10 seconds during usability testing.
- **SC-002**: 95% of users can complete a single bill row update (amount + paid status) in under 30 seconds.
- **SC-003**: 100% of saved row updates are visible after page reload for the same month in acceptance testing.
- **SC-004**: Monthly bill list ordering matches ascending due day for 100% of test datasets containing mixed due-day values.

## Assumptions & Open Questions *(mandatory)*

- **Assumptions**:
  - Bill Pay defaults to the current calendar month on initial load.
  - Bill Pay month rollover does not carry unpaid items into the next month’s list.
  - Account liability classification is determined solely by account type values: credit_card, loan, and other.
  - Actual payment amount is stored in the account’s existing household currency conventions.
  - Users permitted to edit accounts in a household are also permitted to edit bill pay entries for those accounts.
  - Existing account fields (`payment_due_day`, `minimum_amount_due`, `online_access_url`) remain the source of displayed bill metadata.
- **Open Questions**:
  - None currently blocking implementation.
