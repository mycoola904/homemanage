# Feature Specification: Household Account Import

**Feature Branch**: `001-account-import`  
**Created**: 2026-02-13  
**Status**: Draft  
**Input**: User description: "Add an import feature for the financial app. The link to this will be in the finance side bar. Clicking this link will show the upload form in the main content area. The upload form will ask for the path to the import file, upload the file and insert into the database. This import feature will be for the Account model in the financial app. The file can be csv or excel formats. The accounts uploaded should be imported to the household that the user is logged into. At the end of the implementation, deliver the proper template csv file."

> Per the Constitution, this spec must be reviewed and approved before any code is written. Capture determinism, dependency, and UI safety decisions here rather than deferring to implementation.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Import accounts from finance navigation (Priority: P1)

As a household member managing finances, I can open an account import screen from the finance sidebar and upload a file so new accounts are created for my currently selected household.

**Why this priority**: This is the core user value and the requested feature entry point.

**Independent Test**: Can be fully tested by navigating from the finance sidebar to the import form, uploading a valid file, and confirming new accounts appear only in the active household.

**Acceptance Scenarios**:

1. **Given** a logged-in user is viewing finance pages for Household A, **When** they click the Import link in the finance sidebar, **Then** the account import form is shown in the main content area.
2. **Given** a logged-in user in Household A has a valid CSV file, **When** they upload and submit it, **Then** the system creates account records for Household A and shows an import summary.
3. **Given** a logged-in user in Household A has a valid Excel file, **When** they upload and submit it, **Then** the system creates account records for Household A and shows an import summary.

---

### User Story 2 - Receive actionable validation feedback (Priority: P2)

As a household member, I get clear feedback when the upload file is invalid so I can correct it and retry.

**Why this priority**: Import safety and clear errors prevent bad data and reduce repeated failed attempts.

**Independent Test**: Can be tested by submitting unsupported file types, missing required columns, and malformed rows; verify no accounts are created and errors are shown.

**Acceptance Scenarios**:

1. **Given** a user uploads an unsupported format, **When** they submit, **Then** the system rejects the file and shows a format error.
2. **Given** a user uploads a file missing required columns, **When** they submit, **Then** the system rejects the import and lists missing columns.
3. **Given** a user uploads a file with invalid row values, **When** they submit, **Then** the system rejects the import and reports row-level validation issues.

---

### User Story 3 - Use a standard template file (Priority: P3)

As a household member, I can access a template CSV so I can prepare import files in the correct structure.

**Why this priority**: A standard template lowers setup effort and reduces validation failures.

**Independent Test**: Can be tested by obtaining the template CSV and validating that required headers match import expectations.

**Acceptance Scenarios**:

1. **Given** a user opens the account import form, **When** they request the template CSV, **Then** they receive a CSV file with required headers and sample values.

### Edge Cases

- User uploads an empty file (no data rows).
- File contains duplicate account names that already exist in the active household.
- File includes duplicate rows within the same upload batch.
- File includes leading/trailing whitespace in fields.
- User switches households between opening the form and submitting the file.
- File exceeds the permitted upload size or row count limit.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The finance sidebar MUST include an "Import" navigation entry for accounts.
- **FR-002**: Selecting the import entry MUST render the account import form in the page's main content area.
- **FR-003**: The import form MUST allow the user to choose a local file and display the selected file path or filename before submission.
- **FR-004**: The system MUST accept account import files in CSV and Excel formats only.
- **FR-005**: The system MUST validate file type, required columns, and row-level data before persisting any imported account records.
- **FR-006**: The system MUST treat each upload as an atomic operation: if any validation error exists, no accounts from that upload are created.
- **FR-007**: The system MUST create imported accounts only in the household context active for the logged-in user at submission time.
- **FR-008**: The system MUST ignore any household identifier provided in the uploaded file and use the active household context instead.
- **FR-009**: The system MUST prevent creating duplicate account names within the same household and report duplicates in the import feedback.
- **FR-010**: After processing, the system MUST show a result summary including total rows processed, rows imported, and rows rejected with reasons.
- **FR-011**: The import form MUST provide access to a template CSV that contains the exact required headers for account import.
- **FR-012**: The template CSV MUST be included as a tracked project artifact deliverable for this feature.

### Key Entities *(include if feature involves data)*

- **Account Import File**: A user-provided CSV or Excel document containing rows intended to create account records.
- **Account Import Row**: One logical account entry from the file, including required account fields and optional metadata.
- **Import Result Summary**: Outcome data for one upload attempt, including counts and row-level validation messages.
- **Household Context**: The active household selected by the logged-in user that determines ownership of imported records.

### Server-Driven UI & Template Safety *(mandatory for UI work)*

- **UI-001**: The finance import trigger MUST target a stable main-content container so the sidebar link remains in the DOM after content swap.
- **UI-002**: The upload form and result messaging MUST be returned as server-rendered partial content for main-content updates.
- **UI-003**: Dynamic classes and attributes for validation states MUST be computed server-side (view context or single-line template helpers), avoiding multiline template tags and inline conditional attribute logic.
- **UI-004**: Before troubleshooting styling/layout issues for this feature, the Tailwind/DaisyUI watcher command `npm run dev:css` MUST be running and rebuild output verified.

## Deterministic Data & Integrity *(mandatory)*

- **Schema Changes**: No schema change is required; account records are created using existing Account model fields and constraints.
- **Data Fixtures**: Provide a deterministic template CSV with stable header ordering and representative sample rows; repeated use of the same valid import file must produce the same resulting account set when starting from the same database state.
- **External Inputs**: Import behavior must not depend on randomness; parsing and validation outcomes must be deterministic for the same file content and household context.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of successful imports create accounts only in the user's active household, with zero cross-household inserts.
- **SC-002**: At least 95% of valid files with up to 1,000 rows complete import processing in under 10 seconds.
- **SC-003**: At least 90% of first-time users can complete a valid account import using the provided template without assistance.
- **SC-004**: 100% of invalid upload attempts present clear, actionable error feedback that identifies the failed rule and affected rows.

## Assumptions & Open Questions *(mandatory)*

- **Assumptions**:
  - Only authenticated users with access to the current household can use account import.
  - Import creates new accounts only and does not update existing account records.
  - Required account columns in template CSV align with existing Account model requirements.
  - A practical upload limit exists (size and/or row count) and is enforced consistently.
- **Open Questions**:
  - None at this stage; defaults above are sufficient for planning and implementation kickoff.
