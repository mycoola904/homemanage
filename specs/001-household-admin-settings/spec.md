# Feature Specification: Household Admin Settings

**Feature Branch**: `001-household-admin-settings`  
**Created**: 2026-02-13  
**Status**: Draft  
**Input**: User description: "Add the ability for an administrator to add Households and Household members. If an administrator logs in, there is a settings menu item in the sidebar. In settings, the administrator can add households and members."

> Per the Constitution, this spec must be reviewed and approved before any code is written. Capture determinism, dependency, and UI safety decisions here rather than deferring to implementation.

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Access admin Settings (Priority: P1)

As an Administrator, I can see and open a Settings area from the main sidebar so that I can perform household administration tasks from within the application.

**Why this priority**: Without a reliable entry point, administrators cannot discover or complete household management.

**Independent Test**: Can be fully tested by logging in as an Administrator vs a non-Administrator and verifying navigation visibility + access controls.

**Acceptance Scenarios**:

1. **Given** I am logged in as an Administrator, **When** I view the application sidebar, **Then** I see a "Settings" menu item.
2. **Given** I am logged in as an Administrator, **When** I select "Settings", **Then** I land on a Settings screen that includes household and member management areas.
3. **Given** I am logged in as a non-Administrator, **When** I view the application sidebar, **Then** I do not see a "Settings" menu item.
4. **Given** I am logged in as a non-Administrator, **When** I attempt to navigate directly to any Settings URL, **Then** I am denied access.

---

### User Story 2 - Create a household (Priority: P2)

As an Administrator, I can add a new Household so that new households can be onboarded without manual database changes.

**Why this priority**: Creating households is the foundation for assigning members and enabling household-scoped features.

**Independent Test**: Can be fully tested by creating one new household and confirming it appears in the households list.

**Acceptance Scenarios**:

1. **Given** I am an Administrator on the Settings screen, **When** I provide a household name and submit, **Then** a new household is created and shown in the households list.
2. **Given** I am an Administrator, **When** I attempt to create a household with a name that already exists in the system, **Then** I see a clear validation error and no duplicate household is created.
3. **Given** I am an Administrator, **When** I submit the create household form with missing required fields, **Then** I see inline validation errors and the form preserves my input where appropriate.

---

### User Story 3 - Manage household members (Priority: P3)

As an Administrator, I can add and remove members for a selected household so that the right users can access the household.

**Why this priority**: Membership management is required to safely grant or revoke access to household data.

**Independent Test**: Can be fully tested by selecting one household, adding one member, verifying membership appears, then removing the member.

**Acceptance Scenarios**:

1. **Given** I am an Administrator on the Settings screen, **When** I select a household, **Then** I can view the current members of that household.
2. **Given** I am an Administrator viewing a household’s members, **When** I add a member by selecting an existing user identity (e.g., by email/username), **Then** that user becomes a member of the household.
3. **Given** I am an Administrator, **When** I try to add the same user to the same household twice, **Then** the system prevents duplication and shows a clear message.
4. **Given** I am an Administrator, **When** I remove a member from a household, **Then** that user no longer has access to that household.
5. **Given** I am an Administrator, **When** I attempt to add a member that does not exist as a user in the system, **Then** I see a clear error and no membership is created.

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- Creating a household name that differs only by casing/whitespace (e.g., "Smith" vs " smith ").
- Administrator removes themselves from a household and needs to immediately lose access.
- Concurrent updates: two administrators add/remove members at the same time.
- Large member lists: ensure the Settings view remains usable when a household has many members.
- Authorization drift: user loses Administrator status mid-session.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST support an "Administrator" user role (or equivalent permission) that grants access to household administration features.
- **FR-002**: System MUST display a "Settings" sidebar navigation item only to Administrators.
- **FR-003**: System MUST deny non-Administrators from accessing Settings screens even if they navigate directly to the URL.
- **FR-004**: System MUST allow an Administrator to create a new household with, at minimum, a human-friendly household name.
- **FR-005**: System MUST prevent creation of duplicate households based on a normalized household name (case/whitespace-insensitive).
- **FR-006**: System MUST provide a Settings view that lists households and allows selecting a household to manage.
- **FR-007**: System MUST allow an Administrator to add an existing user as a member of a selected household.
- **FR-008**: System MUST allow an Administrator to remove an existing member from a selected household.
- **FR-009**: System MUST prevent duplicate memberships for the same (household, user) pair.
- **FR-010**: System MUST present clear, user-friendly validation errors for household creation and member management failures.
- **FR-011**: System MUST ensure membership changes take effect immediately for authorization decisions (e.g., newly-added members gain access; removed members lose access).

Functional requirements are considered accepted when the corresponding User Story acceptance scenarios pass.

**Out of scope (explicit)**:

- Creating brand-new user accounts from Settings (member management is limited to associating existing users to households).
- Bulk import/export of households or members.

### Key Entities *(include if feature involves data)*

- **Household**: A top-level grouping that users can belong to; identified by a unique, human-friendly name and a lifecycle state (e.g., active/archived).
- **User**: An authenticated person who can log in.
- **Household Membership**: The association between a Household and a User, including membership status and (optionally) a role within the household.
- **Administrator**: A user who has permission to access Settings and manage households/members.

### Server-Driven UI & Template Safety *(mandatory for UI work)*

- **UI-001**: Document each Settings interaction that updates part of the page (e.g., create household, add member, remove member), including the stable container that is updated and how navigation/controls remain available after updates.
- **UI-002**: Ensure any conditional UI state (visibility, disabled buttons, error states) is computed server-side and rendered deterministically; avoid complex conditional logic inside templates.
- **UI-003**: Confirm the project’s CSS build/watch process is running and producing rebuild output before diagnosing styling/layout issues in Settings.

## Deterministic Data & Integrity *(mandatory)*

- **Schema Changes**: Household and membership data definitions (including uniqueness constraints) are versioned, deterministic, and reversible.
- **Data Fixtures**: Seed data used for tests/demos is idempotent (can be applied multiple times without creating duplicates) and includes at least one Administrator and at least one household with members.
- **External Inputs**: Any timestamps or generated identifiers used in tests are controlled so that test outcomes are deterministic.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: An Administrator can create a new household in under 60 seconds (from opening Settings to seeing the new household listed).
- **SC-002**: An Administrator can add an existing user as a household member in under 60 seconds.
- **SC-003**: Non-Administrators are unable to access Settings and are unable to create households or change memberships (0 successful unauthorized attempts in acceptance testing).
- **SC-004**: Validation errors for duplicate household names and duplicate memberships are displayed clearly and prevent unintended data creation (100% of tested cases).

## Assumptions & Open Questions *(mandatory)*

- **Assumptions**:
  - "Administrator" is a global permission that allows managing all households.
  - Households have a unique name after normalization (trim + case-insensitive).
  - "Add member" associates an already-existing user identity to a household; it does not create new user accounts.
- **Open Questions**:
  - None identified for MVP scope.
