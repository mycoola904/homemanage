# Research — Accounts Home Feature

## Account Ownership & Scope
Decision: Scope each `Account` directly to `auth.User` via a required FK and filter every query by `request.user`.
Rationale: The current project has no `Household` model and the spec explicitly forbids introducing one, while still requiring per-user segregation of data; FK-level ownership keeps authorization logic simple and enforces Principle I traceability back to [specs/001-accounts-home/spec.md#L18-L51](specs/001-accounts-home/spec.md#L18-L51).
Alternatives considered: Reintroducing or mocking a `Household` abstraction (rejected as scope creep) and storing a nullable FK to future Household records (rejected because it creates ambiguous ownership paths and violates the Prime Directive).

## Case-Insensitive Name Uniqueness
Decision: Enforce `(user_id, Lower('name'))` uniqueness via `UniqueConstraint` plus supporting index.
Rationale: PostgreSQL supports functional indexes, enabling deterministic enforcement without extra dependencies. This satisfies the clarification that account names must be unique per household/user and keeps constraint logic at the database layer for repeatability.
Alternatives considered: Adding the `citext` extension (rejected because it introduces new DB dependencies) or handling uniqueness in form validation only (rejected because it is race-prone and violates Principle II).

## HTMX Concurrency & Targets
Decision: Attach `hx-request="queue:last"`, `hx-disabled-elt="this"`, `hx-target="#account-preview-panel"`, and `hx-swap="innerHTML"` to Preview/Edit triggers, and use row-local containers plus `outerHTML` swaps for delete responses.
Rationale: These attributes satisfy [User Story 2](specs/001-accounts-home/spec.md#L92-L118) requirements, prevent race conditions where stale previews overwrite newer ones, and align with Constitution Principle IV by keeping swaps confined to stable containers.
Alternatives considered: Allowing default HTMX queueing (rejected: can deliver stale responses) or swapping the entire table (rejected: removes triggering element and breaks future interactions).

## django-cotton Component Strategy
Decision: Implement dedicated cotton components for the accounts table and preview panel, each accepting serialized context dictionaries generated in the view.
Rationale: django-cotton is already part of the stack and encourages reusable partials. Packaging the table/preview as cotton components keeps templates single-purpose, satisfies the spec’s reuse mandate, and lets future features (transactions, budgets) reuse the same components.
Alternatives considered: Embedding table markup directly in `index.html` (rejected: duplicates markup and conflicts with cotton usage guidance) or introducing a new component system (rejected: new dependency and unnecessary complexity).

## Currency & Deterministic Formatting
Decision: Format `current_balance` and `credit_limit_or_principal` server-side using a shared helper/filter that outputs USD (en-US) strings before rendering cotton components.
Rationale: Keeping formatting on the server ensures templates remain deterministic, avoids client-side locale drift, and matches the clarification that all households share USD formatting.
Alternatives considered: Introducing a JavaScript formatter (rejected: adds client-side dependency) or relying on browser locale (rejected: inconsistent output and violates deterministic rendering goals).

## Hard Delete Workflow
Decision: Implement POST `/accounts/<uuid>/delete/` as a hard delete that returns HTML instructing HTMX to remove the row and clear the preview when relevant.
Rationale: Spec mandates no soft delete. Hard deletes simplify data state, avoid hidden flags, and keep rollback deterministic (restore via fixture load if necessary).
Alternatives considered: Soft delete flag (rejected: contradicts spec) or deferring delete functionality (rejected: FR-005 requires delete actions now).
