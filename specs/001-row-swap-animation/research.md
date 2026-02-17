# Research: Subtle Row Swap Animation

## Decision 1: Trigger enter animation on `htmx:afterSwap` for bill-pay row swaps
- **Decision**: Use HTMX lifecycle hooks to add an enter-state class to newly swapped `<tr id="bill-pay-row-...">` after `outerHTML` swap completes.
- **Rationale**: The swapped node does not exist pre-swap, so `afterSwap` reliably targets the inserted row and avoids timing races.
- **Alternatives considered**:
  - Add class server-side in rendered partials: rejected because it cannot reliably distinguish initial page render from HTMX swap insertion.
  - Use mutation observers: rejected as unnecessary complexity for known HTMX event flow.

## Decision 2: Keep leaving animation optional and not required
- **Decision**: Require only enter animation; leaving animation remains optional and must never block swap timing.
- **Rationale**: Aligns with clarification answer and reduces risk of delayed row replacement in keyboard-heavy finance workflows.
- **Alternatives considered**:
  - Always animate leaving row: rejected due to added complexity and potential perceived latency.
  - Ban leaving animation entirely: rejected to keep future non-blocking enhancement path open.

## Decision 3: Maintain animation for all users, including reduced-motion contexts
- **Decision**: Do not add reduced-motion exception for this feature iteration.
- **Rationale**: Explicitly required by clarification decision A and reflected in FR-010.
- **Alternatives considered**:
  - Disable motion under reduced-motion preference: rejected by clarified requirement.
  - Fade-only under reduced-motion: rejected by clarified requirement.

## Decision 4: No schema, fixture, or dependency changes
- **Decision**: Implement entirely in existing templates/static script/CSS build outputs.
- **Rationale**: Feature is visual behavior only; database and domain model remain unchanged.
- **Alternatives considered**:
  - Persist per-user animation setting: rejected as out of scope and adds schema/dependency surface.

## Decision 5: Preserve existing HTMX endpoint contracts
- **Decision**: Keep `bill_pay_row` GET/POST routes, `hx-target="#bill-pay-row-..."`, and `hx-swap="outerHTML"` unchanged.
- **Rationale**: Existing tests and deterministic flow rely on these contracts; feature should be additive only.
- **Alternatives considered**:
  - Switch to container-level `innerHTML` swap: rejected because it broadens impact and risks focus/trigger regressions.
