# Feature Specification: Accounts Home + Preview Panel (HTMX) + Account Detail Page (“Open”)

**Feature Branch**: `[001-accounts-home]`
**Created**: 2026-02-06
**Status**: Draft (Amended for determinism + Option C UX)
**Input**: Household financial accounts (checking, savings, credit card, loan).

Per the HomeManage Constitution, this spec must be reviewed and approved before any code is written. All implementation must remain within defined scope and trace back to this document.

---

## Scope Fence (Hard Constraints)

This feature implements **Account metadata only**.

The system MUST NOT introduce:

* Transactions
* Balance history
* Charts or graphs
* Derived aggregates beyond `current_balance`
* Account-type-driven debit/credit semantics
* Reminders or automation
* Background jobs
* Additional domain models beyond `Account`

The Preview panel MUST render only fields defined in the `Account` entity table.

Any adjacent or derivative feature is considered scope drift and requires a new spec.

---

## Goals

* Introduce a first-class `Account` domain model.
* Provide `/accounts/` index page with reusable table component.
* Provide HTMX Preview panel for inline inspection and edits.
* Provide canonical Account detail page (`/accounts/<uuid>/`) intended to host future Transactions.
* Maintain fully server-rendered architecture with HTMX partials and minimal JavaScript.

## Non-Goals

* Transactions or ledger logic
* Budgeting features
* Reporting dashboards
* Multi-currency support
* Financial institution integrations
* Authorization redesign
* Background processing

---

## Clarifications

### Session 2026-02-09

* Q: How should `Account.name` uniqueness behave within a household? → A: Name must be unique per household (case-insensitive).
* Q: Who is allowed to edit or delete accounts within a household? → A: All authenticated household members can edit/delete.
* Q: When `/accounts/` first loads, what should the preview panel display before any selection? → A: Keep the panel empty with no placeholder content.
* Q: How should monetary fields be formatted in the UI for this feature? → A: Format as USD (en-US) currency for all households.
* Q: What should be the default `status` when creating a new Account? → A: Default to `active` for all new accounts.
* Q: How should the `/accounts/` table handle large households with many accounts? → A: No pagination; render all accounts each load.
* Q: How is household scoping enforced without a Household model? → A: Until a formal Household entity ships, scope every `Account` to the authenticated `User`, which functions as the household proxy for ownership and uniqueness.

---

## User Stories & Acceptance Criteria

### User Story 1 — Review Household Accounts (P1)

As a household admin, I need to open `/accounts/` and see every account with key indicators and actions.

**Acceptance Criteria**

1. Accounts are ordered deterministically by:

   * `account_type`
   * then `name`
   * then `created_at`
2. Table renders:

   * name
   * institution
   * account_type
   * status badge
  * current_balance (USD en-US currency formatted)
   * Preview / Open / Edit / Delete actions
3. Empty dataset renders explicit empty-state message + Add Account CTA.
4. List renders every household account without pagination or lazy loading.

---

### User Story 2 — Preview Account Inline (P2)

As a user, I want to Preview an account without leaving `/accounts/`.

**Acceptance Criteria**

1. Clicking Preview triggers:

   * GET `/accounts/<uuid>/preview/`
   * `hx-target="#account-preview-panel"`
   * `hx-swap="innerHTML"`
   * `hx-request="queue:last"`
   * `hx-disabled-elt="this"`
2. Preview panel displays only:

   * current_balance
   * credit_limit_or_principal (if present)
   * statement_close_date
   * payment_due_day
   * status
   * notes
3. Preview replaces prior preview deterministically.
4. Initial load leaves the preview panel empty until a user clicks Preview.
5. No full page reload occurs.

---

### User Story 3 — Edit from Preview Panel (P3)

As a user, I want to edit account metadata inline.

**Acceptance Criteria**

1. Edit triggers GET `/accounts/<uuid>/edit/`.
2. Form renders in `#account-preview-panel`.
3. POST behavior:

   * Valid → persist → return updated preview fragment.
   * Invalid → return form fragment with `422` status and field errors.
4. Table row values refresh via returned HTML fragment (no JSON).

---

### User Story 4 — Open Canonical Detail Page (P2)

As a user, I want to open the Account page for deeper inspection and future Transactions.

**Acceptance Criteria**

1. Open link navigates to `/accounts/<uuid>/`.
2. Page uses full application layout.
3. Displays:

   * Account header
   * Summary metadata
   * Placeholder section titled “Transactions (Coming Soon)”
4. No HTMX partial behavior on this page for this feature.

---

## Edge Cases

* Preview uses `queue:last` to prevent stale responses.
* Concurrent deletion returns 404 preview partial with refresh guidance.
* Validation errors return `422`.
* Permission failure hides Edit/Delete and renders read-only preview.
* HTMX timeout set to 10 seconds globally.

  * On timeout, preview panel displays inline error message.
  * Last known preview state remains visible.

---

## Functional Requirements

* **FR-001**: Create `Account` model scoped to `auth.User` (temporary household proxy) with UUID primary key.
* **FR-002**: `/accounts/` requires authentication and per-user scoping that mirrors household membership until the Household model exists.
* **FR-003**: Reusable table component consumes `AccountSummaryRow`.
* **FR-004**: Add Account navigates to `/accounts/new/` (full page). Successful POST redirects back to `/accounts/` and uses existing flash component.
* **FR-005 — Row Actions (Option C)**: Each row MUST expose:

  * **Preview** (HTMX)
  * **Open** (normal link)
  * **Edit** (HTMX; loads into preview panel)
  * **Delete** (HTMX confirm partial)
* **FR-006**: Preview endpoint returns partial only (no page chrome).
* **FR-007**: Canonical detail page renders full layout.
* **FR-008**: Edit POST returns HTML fragment only (never JSON).
* **FR-009**: Delete is **hard delete**. POST `/accounts/<uuid>/delete/` returns HTML fragment suitable for:

  * Removing table row via `outerHTML`
  * Clearing preview panel if deleted account was active
    No soft-delete behavior.
* **FR-010**: Explicit empty and error states required.
* **FR-011**: Any authenticated user may Edit/Delete accounts they own (standing in for their household); no admin-only restriction.
* **FR-012**: All monetary fields (current_balance, credit_limit_or_principal) display using USD (en-US) currency formatting until multi-currency support is specified.
* **FR-013**: `/accounts/` renders the full account collection on each request—no pagination, infinite scroll, or client-side slicing.

---

## Key Entities

### Account

| Field                     | Type          | Notes                                       |
| ------------------------- | ------------- | ------------------------------------------- |
| user                      | FK            | Required (`auth.User`, household proxy)     |
| name                      | text          | Required                                    |
| institution               | text          | Optional                                    |
| account_type              | enum          | checking, savings, credit_card, loan, other |
| number_last4              | text          | Nullable                                    |
| status                    | enum          | active, closed, pending                     |
| current_balance           | Decimal(12,2) | Default 0.00                                |
| credit_limit_or_principal | Decimal       | Nullable                                    |
| statement_close_date      | Date          | Nullable                                    |
| payment_due_day           | int           | Nullable                                    |
| notes                     | text          | Nullable                                    |
| created_at                | datetime      | auto                                        |
| updated_at                | datetime      | auto                                        |

**Deterministic Ordering**

* `account_type`, then `name`, then `created_at`

---

## Data & Integrity

* Migration creates `accounts_account`.
* Reverse migration drops table.
* Fixture `accounts_minimal.json` includes:

  * 1 checking
  * 1 credit_card
  * 1 loan
* UUID4 primary keys.
* Enforce case-insensitive uniqueness on `(user_id, lower(name))` for `Account` names (until Household FK is introduced).
* New Accounts default to `status = active` unless specified otherwise.
* No soft-delete.
* No background jobs.
* No randomness beyond UUID.

---

## Server-Driven UI & Template Safety

* All state originates server-side.
* No SPA frameworks.
* No JSON response path.
* No new JavaScript bundles.
* HTMX swaps limited to declared targets.
* Conditional CSS classes computed in view or single-line `{% with %}` blocks.
* Tailwind watcher (`npm run dev:css`) must be running before debugging styling.

---

## Success Criteria

* `/accounts/` loads in under 2 seconds.
* Preview → Edit → Save completes without page reload.
* Users distinguish Preview vs Open semantics in usability testing.

---

## AI Accountability & Guardrails

* Any AI-generated schema, template, or architectural logic must cite:

  * The specific spec paragraph implemented.
  * The prompt/response ID used.
* PR description must link:

  * `/speckit.spec`
  * `/speckit.plan`
  * `/speckit.tasks`
* AI may not introduce:

  * Additional domain models
  * Additional dependencies
  * Expanded feature scope
  * Relaxed template constraints

