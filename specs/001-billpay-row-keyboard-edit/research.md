# Research: BillPay Row Keyboard Editing

## Decision 1: Reuse existing row endpoint and partial swap architecture
- Decision: Continue using `GET/POST /financial/bill-pay/{account_id}/row/?month=YYYY-MM` (`financial:bill-pay-row`) for edit entry, save, and validation re-render.
- Rationale: Current implementation is already deterministic, row-scoped, and aligned with server-driven UI principles. It supports `outerHTML` swaps for the row container and returns 422 for validation failures.
- Alternatives considered:
  - Add new dedicated keyboard endpoints (`/edit`, `/cancel`, `/save`) per row: rejected as unnecessary surface-area growth.
  - Replace with client-side grid state management: rejected by user constraint and constitution dependency/surface principles.

## Decision 2: Keep persistence model unchanged
- Decision: Do not introduce schema or model changes; keep `MonthlyBillPayment` as-is.
- Rationale: Requested behavior is interaction/focus/keyboard semantics, not data model expansion. Existing uniqueness and upsert behavior already satisfy deterministic save behavior.
- Alternatives considered:
  - Add temporary edit-session model: rejected as over-engineering with no business need.
  - Add new fields for keyboard metadata: rejected; this state belongs in request/response rendering, not persistence.

## Decision 3: Implement keyboard behavior as progressive enhancement on existing row partials
- Decision: Add minimal client behavior (event handling/focus nudges) around existing row templates while preserving server authority for state transitions.
- Rationale: Keyboard order and Enter/Esc are UI interaction concerns; keeping save/cancel outcomes server-driven preserves parity and avoids drift.
- Alternatives considered:
  - Pure server-only without any client event binding: insufficient for reliable key capture and focus choreography.
  - Heavy JS component rewrite: rejected due to architecture and scope constraints.

## Decision 4: Canonical tab order within active edit row
- Decision: Enforce this order when row is in edit mode: Funding Account → Actual Payment → Paid → Save → Cancel.
- Rationale: Explicit acceptance criteria and accessibility predictability.
- Alternatives considered:
  - Browser natural DOM order only: rejected because current row edit markup does not include all required controls in that order.
  - Custom roving tabindex for entire table: rejected as broader-than-needed and riskier.

## Decision 5: Cancel behavior remains row re-render of display state
- Decision: Esc triggers cancel through existing row-display path (same observable result as Cancel action), without persisting unsaved edits.
- Rationale: Matches current save/cancel parity requirement and preserves deterministic behavior.
- Alternatives considered:
  - Client-only revert without server render: rejected because server-rendered row is canonical.
  - Full table refresh on cancel: rejected because current architecture is row-targeted.

## Best-Practice Notes Applied
- Keep HTMX targets stable: always target `#bill-pay-row-<account_id>` for row swaps.
- Return partial roots matching target element (`<tr id="bill-pay-row-...">`).
- Preserve trigger availability after each swap (Edit button in display row, Save/Cancel controls in edit row).
- Keep all dynamic UI state values server-computed; avoid multiline Django template tags/comments.
