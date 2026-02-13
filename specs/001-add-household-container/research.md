# Research — Household Top-Level Container (MVP)

## No-New-Dependency Decision (T001)
Decision: No new runtime or infrastructure dependencies are introduced for this feature.
Rationale: Existing Django + HTMX + Tailwind/DaisyUI stack already supports the full MVP scope and keeps rollout deterministic.

## Session Household Scoping Strategy
Decision: Use session key `current_household_id` as the sole active scope, resolved from authenticated user memberships on login and revalidated on each household-scoped request.
Rationale: This directly satisfies FR-002/FR-003/FR-011 and keeps tenancy deterministic with one active household at a time.
Alternatives considered: Stateless per-request query parameter (rejected: tamper-prone and leaks cross-household selection complexity), storing active household on `User` model (rejected: couples shared user preference across devices/sessions).

## Membership Model Constraints
Decision: Implement `HouseholdMember` with role enum (`owner`, `admin`, `member`), `is_primary`, unique `(household, user)`, and enforce at most one `is_primary=True` per user.
Rationale: Supports multi-household membership while keeping default login selection deterministic and explicit.
Alternatives considered: Primary household field on user profile (rejected: does not scale cleanly with memberships metadata), allowing multiple primaries (rejected by clarification and deterministic principle).

## Transaction Household Invariant Enforcement
Decision: Persist `Transaction.household` by deriving it from `Transaction.account.household` during save/form processing and reject edits selecting accounts outside `current_household`.
Rationale: Guarantees invariant `transaction.household == transaction.account.household`, prevents client-side tampering, and aligns with FR-008/FR-009/FR-009a.
Alternatives considered: Trust posted household hidden field (rejected: security risk), omit `Transaction.household` and join through account only (rejected: requirement explicitly calls for FK on transaction).

## Migration Path A (Reset + Re-seed)
Decision: Adopt early-stage reset/re-seed flow with reusable management command creating two canonical households and isolated finance data in each.
Rationale: Matches spec directive, minimizes complex backfill risk at current project stage, and enables deterministic local/test setup.
Alternatives considered: Incremental backfill-only migration without reset (rejected: higher complexity and less deterministic for current stage), ad-hoc fixture-only setup (rejected: less reusable in developer workflows).

## Route and Namespace Composition
Decision: Introduce `household` namespace for `/household/` launcher and mount finance entry at `/household/finance/` while preserving internal `financial` namespace semantics.
Rationale: Keeps module launcher and module internals distinct, and enables namespace-based sidebar rendering contract.
Alternatives considered: Replace `financial` namespace entirely (rejected: unnecessary churn), keep finance only at root `/accounts/` (rejected: does not satisfy household module architecture).

## HTMX Boundary Contract
Decision: Keep HTMX interactions restricted to finance-local containers (`#account-preview-panel`, `#account-transactions-body`) and use full route navigation for module transitions/switch redirects.
Rationale: Preserves stable trigger elements and avoids cross-module DOM replacement failures.
Alternatives considered: Using HTMX to navigate between `/household/` and `/household/finance/` (rejected: violates module boundary rule), broad `outerHTML` swaps on parent layouts (rejected: brittle and can remove triggers).

## Watcher and Template Safety
Decision: Treat `npm run dev:css` as required watcher command before debugging style regressions and keep Django template tags/comments single-line.
Rationale: Aligns with constitution and local repository constraints (`agents.md`) to avoid false-positive UI debugging.
Alternatives considered: Adjusting classes before watcher confirmation (rejected: non-deterministic feedback loop).

## Dependency Impact
Decision: Add no new runtime or infrastructure dependencies.
Rationale: Existing Django/HTMX/Tailwind stack already supports all required behavior.
Alternatives considered: Client-side state manager for household context (rejected: violates server-driven UI principle).
