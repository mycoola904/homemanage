# Feature Specification: Subtle Row Swap Animation

**Feature Branch**: `001-row-swap-animation`  
**Created**: 2026-02-17  
**Status**: Draft  
**Input**: User description: "Subtle animation when a row flips view ↔ edit"

> Per the Constitution, this spec must be reviewed and approved before any code is written. Capture determinism, dependency, and UI safety decisions here rather than deferring to implementation.

## Clarifications

### Session 2026-02-17

- Q: What should the spec require for users who prefer reduced motion during row swap transitions? → A: Always animate all row swaps (no reduced-motion exception).
- Q: What should the spec require for the “leaving” animation before the HTMX swap? → A: Keep leaving animation optional; only enter animation is required.
- Q: What should be the feature scope for applying this animation behavior? → A: Apply only to bill-pay row view↔edit swaps.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Smooth row transition on mode switch (Priority: P1)

As a household finance user, when I switch a bill-pay row between read-only and edit modes, I want the updated row to appear with a subtle transition so the change feels intentional instead of abrupt.

**Why this priority**: This is the core user-visible value of the feature and directly addresses the current abrupt row replacement behavior.

**Independent Test**: Can be fully tested by toggling a single row between view and edit states and confirming the replacement row visibly enters with subtle motion and fade.

**Acceptance Scenarios**:

1. **Given** a bill-pay row in view mode, **When** the user activates edit mode and the row is swapped, **Then** the inserted row appears with a subtle fade-and-slide enter transition.
2. **Given** a bill-pay row in edit mode, **When** the user saves or cancels and the row is swapped back to view mode, **Then** the inserted row appears with the same subtle enter transition.

---

### User Story 2 - Motion remains subtle and non-distracting (Priority: P2)

As a finance user working through multiple rows, I want motion to be minimal so the interface feels calm and professional while still making row changes easy to track.

**Why this priority**: Preventing distracting motion protects usability in a data-heavy finance workflow.

**Independent Test**: Can be independently tested by rapidly toggling several rows and confirming transitions are short, low-amplitude, and do not obscure row content.

**Acceptance Scenarios**:

1. **Given** repeated row toggles during normal use, **When** each swap occurs, **Then** animations remain brief and subtle rather than attention-grabbing.
2. **Given** a user interacting with controls immediately after a swap, **When** the row animation is running, **Then** controls remain usable without blocked interaction.

### Edge Cases

- A row is toggled multiple times in quick succession before the prior animation completes.
- A swap returns validation errors in edit mode; the error row still transitions in consistently.
- A row swap occurs when the row is near the top or bottom of the viewport and should not cause visible layout jump.
- Animation classes fail to apply for one event; row content must still render correctly with no broken state.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST apply a short enter animation to table rows inserted by the bill-pay view↔edit HTMX row swap flow.
- **FR-002**: Enter animation MUST combine slight opacity and slight vertical position change to communicate insertion without drawing strong attention.
- **FR-003**: Enter animation MUST complete within 120–180 milliseconds.
- **FR-004**: System MUST trigger animation behavior after each successful bill-pay HTMX row swap for both view→edit and edit→view transitions.
- **FR-005**: System MUST clean up temporary animation state after transition completion so repeated toggles animate consistently.
- **FR-006**: User interactions with row controls MUST remain available during and immediately after the animation.
- **FR-007**: Leaving animation before swap is optional and MUST NOT be required for acceptance of this feature.
- **FR-008**: If an optional leaving animation is used, it MUST NOT prevent or delay row replacement beyond normal interaction expectations.
- **FR-009**: If animation behavior cannot run, swapped row content MUST still appear correctly and remain fully functional.
- **FR-010**: Row-swap transitions MUST animate consistently for all users and contexts, including environments where reduced-motion preferences may be set.
- **FR-011**: This feature MUST NOT change animation behavior for non-bill-pay tables or unrelated HTMX swap flows.

### Key Entities *(include if feature involves data)*

- **Interactive Bill-Pay Row**: A single table row that can exist in view mode or edit mode and is replaced through HTMX swapping.
- **Row Transition State**: Temporary visual state for a swapped row (entering and optional leaving) used only to present motion feedback.

### Server-Driven UI & Template Safety *(mandatory for UI work)*

- **UI-001**: HTMX endpoints in scope are the existing row edit/load/save/cancel endpoints used by the bill-pay row flow in `financial`; each response swaps the row element itself (`<tr>`) with `outerHTML`, and the stable table body container remains in the DOM as the anchor for subsequent interactions.
- **UI-002**: Any dynamic classes needed for row state will be derived by server-rendered templates or single-line template constructs; no multiline template tags/comments and no complex inline conditional blocks embedded across HTML attributes.
- **UI-003**: Tailwind watcher command is `npm run dev:css`; styling diagnostics must first confirm watcher rebuild output in terminal and a hard refresh before concluding class-level issues.

## Deterministic Data & Integrity *(mandatory)*

- **Schema Changes**: None required; no model or migration changes are introduced.
- **Data Fixtures**: Existing financial fixtures remain unchanged; no new seeded data required for this visual behavior.
- **External Inputs**: No random or third-party input is required; behavior is deterministic based on HTMX swap event timing and consistent class application.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In at least 95% of manual row mode switches during validation, users observe a visible but subtle transition instead of an abrupt row pop.
- **SC-002**: In interactive testing across at least 20 consecutive row toggles, no toggle loses functionality or leaves a row in a broken visual state.
- **SC-003**: In manual validation across 20 consecutive view↔edit row swaps, measured transition duration remains within 120–180ms and no swap introduces more than 100ms additional wait before the next user action can be performed.
- **SC-004**: In a usability check with at least 3 reviewers, at least 2 reviewers rate the row transition as “subtle/non-distracting” using a binary pass/fail rubric recorded in `quickstart.md`.

## Assumptions & Open Questions *(mandatory)*

- **Assumptions**:
  - The existing bill-pay row swap flow already uses HTMX row-level replacement and does not require endpoint redesign.
  - Browser support baseline includes CSS transitions and standard HTMX lifecycle events.
  - This feature applies only to bill-pay row-level view↔edit swap behavior, not to unrelated table interactions.
- **Open Questions**:
  - None at this time.
