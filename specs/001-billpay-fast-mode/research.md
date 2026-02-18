# Phase 0 Research — Bill Pay Fast Mode

## Decision 1: Keep Fast Mode preference page-scoped and default OFF
- Decision: Fast Mode starts OFF on initial page load and only persists for current page lifecycle.
- Rationale: Matches clarified requirements (FR-001a, FR-001b), preserves current behavior for existing users, avoids introducing client/server preference persistence state.
- Alternatives considered:
  - Session persistence via browser storage (rejected: adds hidden state and new edge cases).
  - Cross-session user preference (rejected: needs storage model/settings and migration scope not required by spec).

## Decision 2: Server computes next row from current rendered order
- Decision: Next unpaid row is selected according to current on-screen table order, filtered to unpaid rows in active month context.
- Rationale: Aligns with clarification and prevents user-visible order surprises; keeps server authoritative for deterministic behavior.
- Alternatives considered:
  - Canonical resort (e.g., due date/name) on save (rejected: could diverge from current screen order).
  - Client-only next-row selection (rejected: duplicates business logic and risks drift).

## Decision 3: Signal auto-open via HTMX trigger payload
- Decision: On successful save with Fast Mode enabled and a next row available, return normal row HTML plus `HX-Trigger` payload containing next-row edit URL/focus metadata.
- Rationale: Preserves current HTMX swap flow and adds minimal coupling between save response and client follow-up request.
- Alternatives considered:
  - Return OOB swap for both current and next rows (rejected: heavier response and more complex template coupling).
  - Force full table-body refresh then reopen row (rejected: larger swap surface and weaker UX continuity).

## Decision 4: Reuse existing edit-entry mechanics in JavaScript
- Decision: Add small handler in existing `static/src/bill_pay_row_keyboard.js` to consume trigger and issue row edit `hx-get` (or click existing edit trigger) for the target row.
- Rationale: Avoids new framework/dependency and keeps keyboard-focus logic in one place.
- Alternatives considered:
  - New standalone JS file for Fast Mode only (rejected: unnecessary split for small behavior extension).
  - Server-driven immediate edit row HTML return for next row (rejected: multi-row response complexity).

## Decision 5: Failure policy for open-next step
- Decision: If next-row open fails after successful save, keep saved row in view state, show subtle feedback, require manual open.
- Rationale: Matches clarification and avoids unintended resubmission or row state rollback.
- Alternatives considered:
  - Auto-retry once (rejected: hidden retry can mask state issues and create inconsistent focus timing).
  - Reopen saved row (rejected: conflicts with successful save completion and adds confusion).

## Decision 6: No schema/data migration changes
- Decision: Implement entirely in view/template/client behavior with existing `MonthlyBillPayment` model and upsert service.
- Rationale: Feature changes UX/control flow only; no new persisted domain data needed.
- Alternatives considered:
  - Persist fast-mode preference in DB (rejected: out of scope and unnecessary complexity).
