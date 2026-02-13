# Feature Specification: Household Admin Settings

**Feature Branch**: `001-household-admin-settings`  
**Created**: 2026-02-13  
**Status**: Draft  
**Input**: User description: "Add the ability for an administrator to add Households, create user logins, and manage household members. If an administrator logs in, there is a settings menu item in the sidebar. In settings, the administrator can add households and members."

> Per the Constitution, this spec must be reviewed and approved before any code is written. Capture determinism, dependency, and UI safety decisions here rather than deferring to implementation.

## Clarifications

### Session 2026-02-13

- Q: Should creating a new user login in Settings require assigning at least one household membership at creation time? → A: Yes, require at least one household membership during user creation.
- Q: Should user creation allow assigning multiple household memberships at once, or exactly one household initially? → A: Allow selecting one or more households during account creation.
- Q: Should the system block user account creation when no households exist yet? → A: Yes, block account creation until at least one household exists and guide the administrator to create a household first.

## User Scenarios & Testing *(mandatory)*


### User Story 1 - Access admin Settings (Priority: P1)

As an Administrator, I can see and open a Settings area from the main sidebar so that I can perform household administration tasks from within the application.

**Why this priority**: Without a reliable entry point, administrators cannot discover or complete household management.

**Independent Test**: Can be fully tested by logging in as an Administrator vs a non-Administrator and verifying navigation visibility + access controls.

**Acceptance Scenarios**:

1. **Given** I am logged in as an Administrator, **When** I view the application sidebar, **Then** I see a "Settings" menu item.
2. **Given** I am logged in as an Administrator, **When** I select "Settings", **Then** I land on a Settings screen that includes household and member management areas.
3. **Given** I am logged in as a non-Administrator, **When** I view the application sidebar, **Then** I do not see a "Settings" menu item.
4. **Given** I am logged in as a non-Administrator, **When** I attempt to navigate directly to any Settings URL, **Then** I am denied access.
5. **Given** I am not authenticated, **When** I view navigation, **Then** I see a Login button and do not see module navigation options.
6. **Given** I am authenticated, **When** I view navigation, **Then** the Login button is not shown.

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

### User Story 3 - Create user login accounts (Priority: P3)

As a global Administrator (landlord), I can create user login accounts, set their passwords directly, and assign one or more household memberships so that I can onboard users in this local app.

**Why this priority**: Household membership assignment depends on users existing in the authentication system.

**Independent Test**: Can be fully tested by creating a new user with username/email/password and confirming that user can authenticate.

**Acceptance Scenarios**:

1. **Given** I am an Administrator on the Settings screen, **When** I submit a new user login form with valid username/email/password, **Then** a new user account is created.
2. **Given** I am an Administrator on the Settings screen, **When** I submit a new user without selecting at least one household membership, **Then** validation blocks account creation and prompts me to select at least one household.
3. **Given** I am an Administrator, **When** I submit a valid new user with multiple selected households, **Then** the account is created and memberships are created for all selected households.
4. **Given** I am an Administrator, **When** I submit a duplicate username or duplicate email, **Then** I see validation errors and no duplicate account is created.
5. **Given** I am an Administrator, **When** I submit a password that fails policy validation, **Then** I see a clear password validation error and no account is created.
6. **Given** I am an Administrator, **When** I submit a valid password, **Then** the password is set directly on the new user account.
7. **Given** I am an Administrator and no households exist, **When** I open user creation, **Then** account creation is blocked and I am prompted to create a household first.

---

### User Story 4 - Manage household members (Priority: P4)

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

### Edge Cases

- Creating a household name that differs only by casing/whitespace (e.g., "Smith" vs " smith ").
- Creating a user login with duplicate username or email.
- Creating a user login with a password that fails password policy.
- Creating a user login when no households exist yet.
- Unauthenticated user attempts to access module URLs directly (e.g., Finance URL).
- Administrator removes themselves from a household and needs to immediately lose access.
- Concurrent updates: two administrators add/remove members at the same time.
- Large member lists: ensure the Settings view remains usable when a household has many members.
- Authorization drift: user loses Administrator status mid-session.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support a global "Administrator" authorization concept that grants access to household administration features.
- **FR-002**: For MVP, Django superusers MUST be treated as global Administrators for this feature and receive access automatically.
- **FR-003**: The authorization check MUST be implemented so a future explicit permission/group can be added without changing user-facing behavior.
- **FR-004**: System MUST display a "Settings" sidebar navigation item only to Administrators.
- **FR-005**: System MUST deny non-Administrators from accessing Settings screens even if they navigate directly to the URL.
- **FR-006**: System MUST show a Login button in navbar/header navigation only when the user is not authenticated.
- **FR-007**: System MUST hide module navigation options (including Finance) from unauthenticated users.
- **FR-008**: System MUST require authentication for module routes and redirect unauthenticated users to login.
- **FR-009**: System MUST allow an Administrator to create a new household with, at minimum, a human-friendly household name.
- **FR-010**: System MUST prevent creation of duplicate households based on a normalized household name (case/whitespace-insensitive).
- **FR-011**: System MUST provide a Settings view that lists households and allows selecting a household to manage.
- **FR-012**: System MUST allow an Administrator to create new user login accounts from Settings.
- **FR-013**: System MUST require administrators to set the new user’s password directly at account creation time.
- **FR-014**: System MUST enforce username/email uniqueness and password policy validation when creating user accounts.
- **FR-015**: System MUST require at least one household membership to be selected when creating a user account.
- **FR-016**: System MUST allow selecting one or more households during user account creation and create memberships for all selected households.
- **FR-017**: System MUST block user account creation when no households exist and present clear guidance to create a household first.
- **FR-018**: System MUST allow an Administrator to add an existing user as a member of a selected household.
- **FR-019**: System MUST allow an Administrator to remove an existing member from a selected household.
- **FR-020**: System MUST prevent duplicate memberships for the same (household, user) pair.
- **FR-021**: System MUST present clear, user-friendly validation errors for household creation, user creation, and member management failures.
- **FR-022**: System MUST ensure membership changes take effect immediately for authorization decisions (e.g., newly-added members gain access; removed members lose access).

Functional requirements are considered accepted when the corresponding User Story acceptance scenarios pass.

**Out of scope (explicit)**:

- Bulk import/export of households or members.

### Key Entities *(include if feature involves data)*

- **Household**: A top-level grouping that users can belong to; identified by a unique, human-friendly name and a lifecycle state (e.g., active/archived).
- **User**: An authenticated person who can log in.
- **User Login Account**: Authentication identity created by an Administrator with username/email/password that can later be assigned to one or more households.
- **Household Membership**: The association between a Household and a User, including membership status and (optionally) a role within the household.
- **Administrator**: A global landlord-level user who can access Settings and manage households, user logins, and memberships; for MVP this is satisfied by Django superusers.

### Server-Driven UI & Template Safety *(mandatory for UI work)*

- **UI-001**: Document each Settings interaction that updates part of the page (e.g., create household, add member, remove member), including the stable container that is updated and how navigation/controls remain available after updates.
- **UI-002**: Ensure any conditional UI state (visibility, disabled buttons, error states) is computed server-side and rendered deterministically; avoid complex conditional logic inside templates.
- **UI-003**: Confirm the project’s CSS build/watch process is running and producing rebuild output before diagnosing styling/layout issues in Settings.

## Deterministic Data & Integrity *(mandatory)*

- **Schema Changes**: Household and membership data definitions (including uniqueness constraints) are versioned, deterministic, and reversible.
- **Data Fixtures**: Seed data used for tests/demos is idempotent (can be applied multiple times without creating duplicates) and includes at least one Administrator and at least one household with members.
- **External Inputs**: Any timestamps or generated identifiers used in tests are controlled so that test outcomes are deterministic.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An Administrator can create a new household in under 60 seconds (from opening Settings to seeing the new household listed).
- **SC-002**: An Administrator can create a user login account (including password set) in under 90 seconds.
- **SC-002**: An Administrator can create a user login account (including password set and at least one household membership) in under 90 seconds.
- **SC-003**: An Administrator can add an existing user as a household member in under 60 seconds.
- **SC-004**: Non-Administrators are unable to access Settings and are unable to create households, create user accounts, or change memberships (0 successful unauthorized attempts in acceptance testing).
- **SC-005**: Validation errors for duplicate household names, duplicate usernames/emails, weak passwords, and duplicate memberships are displayed clearly and prevent unintended data creation (100% of tested cases).
- **SC-006**: In acceptance testing, unauthenticated users see Login navigation and do not see module navigation (including Finance) in 100% of tested views.
- **SC-007**: In acceptance testing, when no households exist, user creation is blocked and administrators are directed to household creation in 100% of tested cases.

## Assumptions & Open Questions *(mandatory)*

- **Assumptions**:
  - "Administrator" is a global authorization concept that allows managing all households.
  - For MVP, Django superusers are automatically treated as global Administrators.
  - A future permission/group-based administrator path may be introduced without changing the Settings UX.
  - Households have a unique name after normalization (trim + case-insensitive).
  - Administrators create user login accounts directly in Settings, set passwords directly, and assign one or more households at creation time.
  - User account creation requires at least one existing household.
- **Open Questions**:
  - None identified for MVP scope.
