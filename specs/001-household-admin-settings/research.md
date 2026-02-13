# Phase 0 Research — Household Admin Settings

## Decision 1: Global admin authorization policy abstraction
- Decision: Implement a single server-side authorization policy function (e.g., `is_global_admin(user)`) and use it everywhere Settings access is evaluated (views, context, template visibility), with MVP policy treating Django superusers as global administrators.
- Rationale: Matches spec FR-001..FR-003 while preventing hard-coded role checks scattered across templates/views; keeps future permission/group extension low-risk.
- Alternatives considered:
  - Direct `is_superuser` checks everywhere: fastest, but creates migration debt and inconsistent authorization behavior.
  - Permission-first immediately: clean long-term, but unnecessary upfront setup for current MVP.
  - Group-only immediately: operationally simple, less granular than permission model.

## Decision 2: Membership model remains association-based
- Decision: Keep user identity in Django auth user and represent household assignment via household-membership associations (one user can belong to one or more households).
- Rationale: Aligns with clarified requirement for one-or-more household flags at account creation and existing deterministic constraints around duplicate membership prevention.
- Alternatives considered:
  - Single household field on user: cannot support multi-household membership.
  - Separate custom auth model now: larger migration surface with no MVP benefit.

## Decision 3: User creation requires existing household(s)
- Decision: Block user creation until at least one household exists; require selecting one or more households during user creation.
- Rationale: Enforces clarified rules from spec clarifications and avoids orphaned accounts that cannot access household-scoped features.
- Alternatives considered:
  - Allow household-less account only when none exist: weakens deterministic access behavior.
  - Auto-create default household: introduces implicit side effects not requested by spec.

## Decision 4: HTMX server-driven form interaction pattern
- Decision: Use stable container targets and primarily `hx-swap="innerHTML"` for form/panel updates; return bound form partials with validation errors on failure and list/row partials on success.
- Rationale: Preserves trigger elements, keeps swaps predictable, and satisfies constitution requirements for server-driven UI + deterministic HTMX behavior.
- Alternatives considered:
  - Frequent `outerHTML` swaps on broad containers: higher risk of removing triggering controls.
  - Client-managed state for validation/errors: conflicts with server-driven UI principle.

## Decision 5: Navigation gating behavior
- Decision: Show Login nav action only for unauthenticated users; hide module navigation (including Finance) until authentication; enforce server-side route protection regardless of nav visibility.
- Rationale: Directly implements FR-006..FR-008 and avoids security-through-obscurity.
- Alternatives considered:
  - Hide links only: insufficient without route-level auth checks.
  - Always show Login and modules: contradicts spec behavior.

## Decision 6: Deterministic migration and fixture posture
- Decision: Minimize schema changes by reusing existing household/membership structures where possible; any necessary migration must be reversible and accompanied by deterministic fixture updates.
- Rationale: Satisfies Constitution Principle II and reduces rollout risk.
- Alternatives considered:
  - Broad schema refactor now: unnecessary complexity for MVP.
  - Data backfill without idempotent guardrails: non-deterministic and rollback-hostile.

## Resolved Clarifications
- Require at least one household membership during account creation.
- Allow one or more households to be selected during account creation.
- Block account creation if no households exist, with guidance to create household first.
