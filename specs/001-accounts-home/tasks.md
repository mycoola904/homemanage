---

description: "Task list for Accounts Home + Preview Panel"
---

# Tasks: Accounts Home + Preview Panel

**Input**: plan.md, spec.md, research.md, data-model.md, contracts/accounts.yaml, quickstart.md under `specs/001-accounts-home/`
**Prerequisites**: Python 3.11 + Django 6, django-htmx, django-cotton, Tailwind watcher (`npm run dev:css`), PostgreSQL connection per quickstart

**Tests**: Each user story lists targeted Django tests; ensure they fail before implementing functionality.

**Organization**: Tasks are grouped by user story (US1–US4) to keep increments independently testable.

## Constitution Hooks *(do not remove)*

- Every task cites the relevant spec section (User Story or FR) so reviewers can trace coverage (Principle I).
- Database/migration tasks reference the migration or fixture file and describe deterministic guarantees (Principle II).
- No tasks introduce new dependencies beyond the stack enumerated in plan.md (Principle III).
- Template/CSS/HTMX tasks explicitly call out `npm run dev:css` watcher requirements plus `hx-target`/`hx-swap` documentation (Principle IV).
- AI-generated work must be logged in `docs/ai/001-accounts-home-log.md` as noted in tasks (Principle V).

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify local environment, dependencies, and tooling before touching feature code.

- [x] T001 Install backend requirements via `requirements.txt` and Node dev dependencies via `package.json` to align with quickstart.md before starting the Accounts feature.
- [x] T002 Configure `.env` for PostgreSQL (per quickstart.md) and start `npm run dev:css`, capturing watcher logs so later template tasks satisfy Spec Server-Driven UI constraints.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure needed before any user story work begins.

- [x] T003 Create the `financial` Django app (`python manage.py startapp financial`), add it to `core/settings.py:INSTALLED_APPS`, and scaffold `models.py`, `views.py`, `forms.py`, `urls.py`, `tests/`, `templates/financial/accounts/`, and `fixtures/` as outlined in plan.md.
- [x] T004 Wire `financial.urls` under `/accounts/` in [core/urls.py](core/urls.py) with `login_required` to satisfy spec FR-002 before implementing story routes.
- [x] T005 Define `Account` enums, manager, and model fields in [financial/models.py](financial/models.py) per data-model.md (spec FR-001, US1 requirements) including `Meta.ordering = ("account_type", "name", "created_at")` and FK to `settings.AUTH_USER_MODEL`.
- [x] T006 Create migration [financial/migrations/0001_initial.py](financial/migrations/0001_initial.py) with UUID PKs, decimal precision, and `(user_id, Lower(name))` uniqueness; document deterministic rollback steps per spec Data & Integrity.
- [x] T007 Build deterministic fixture [financial/fixtures/accounts_minimal.json](financial/fixtures/accounts_minimal.json) containing checking, credit_card, and loan examples as described in spec Data & Integrity, ensuring UUIDs are stable for repeatable tests.
- [x] T008 Add scoped queryset helpers (`AccountQuerySet`, `UserAccountQuerysetMixin`) plus USD formatting utility in [financial/models.py](financial/models.py) and `financial/services/formatters.py` to enforce ownership + deterministic display (research.md clarifications).
- [x] T009 Create global django-cotton component directory `templates/components/financial/` with stub files (`accounts_table.html`, `account_row.html`, `account_preview_panel.html`) and note `COTTON_DIR="components"`; confirm `npm run dev:css` is running before touching these templates (plan component rule).
- [x] T010 Add `docs/ai/001-accounts-home-log.md` with instructions for recording AI prompt/response IDs so future tasks can reference it (plan Constitution Check AI Accountability).

**Checkpoint**: Foundation ready—user story implementation can begin in parallel once T001–T010 complete.

---

## Phase 3: User Story 1 – Review Household Accounts (Priority: P1) 🎯 MVP

**Goal**: Render `/accounts/` with deterministic ordering, reusable table component, Add Account CTA, and empty-state messaging (spec US1, FR-003/FR-004/FR-013).

**Independent Test**: With fixtures loaded, visiting `/accounts/` should display all of the current user’s accounts ordered by `account_type`, `name`, `created_at`. Removing fixtures should trigger the empty state + Add Account CTA, all without touching preview/edit flows.

### Tests for User Story 1

- [x] T011 [P] [US1] Author ordering + dataset tests in [financial/tests/test_accounts_index.py](financial/tests/test_accounts_index.py) that assert Spec US1 AC1-2 and FR-013 (full collection, deterministic sort).
- [x] T012 [P] [US1] Write empty-state + CTA coverage in the same test module, ensuring Spec US1 AC3-4 and FR-004 behaviors (Add Account button + row actions stubs) fail before implementation.

### Implementation for User Story 1

- [x] T013 [P] [US1] Implement `AccountSummaryRow` dataclass/serializer in [financial/services/accounts.py](financial/services/accounts.py) to shape data for cotton components (spec US1 AC1-2, FR-003).
- [x] T014 [P] [US1] Build cotton templates [templates/components/financial/accounts_table.html](templates/components/financial/accounts_table.html) and `account_row.html` to render headers, action buttons (Preview/Open/Edit/Delete placeholders), and deterministically sorted rows; ensure `npm run dev:css` watcher is running and document `hx-target`, `hx-swap`, and `hx-request` placeholders inside the component (spec US1 + FR-005).
- [x] T015 [US1] Implement `AccountsIndexView` + context serializer in [financial/views.py](financial/views.py) to load user-scoped queryset, pass `AccountSummaryRow` data, and inject empty-state flags (spec US1 AC1-4, FR-002/FR-003).
- [x] T016 [US1] Create [financial/templates/financial/accounts/index.html](financial/templates/financial/accounts/index.html) using the base layout + flash component, include `#account-preview-panel` container initially empty, and confirm Tailwind watcher logs before editing; document hx-target references per plan (spec US1, US2 pre-req, Server-Driven UI rules).
- [x] T017 [US1] Implement `AccountForm` + `AccountCreateView` in [financial/forms.py](financial/forms.py) and [financial/views.py](financial/views.py) with template partial [financial/templates/financial/accounts/_form.html](financial/templates/financial/accounts/_form.html) for full-page create view `/accounts/new/`, redirecting with flash component upon success (spec FR-004, clarifications on default status).
- [x] T018 [US1] Register `/accounts/` and `/accounts/new/` routes plus success messages in [financial/urls.py](financial/urls.py) and ensure nav/menu entries (e.g., [templates/components/layout/sidebar.html](templates/components/layout/sidebar.html)) expose the Accounts link referencing spec FR-002/FR-004.

**Checkpoint**: `/accounts/` renders full datasets and empty states with Add Account flow; preview panel remains blank pending later stories.

---

## Phase 4: User Story 2 – Preview Account Inline (Priority: P2)

**Goal**: HTMX preview endpoint that swaps account metadata into `#account-preview-panel` with concurrency guards (spec US2, FR-005/FR-006).

**Independent Test**: Clicking Preview for any row should issue `GET /accounts/<uuid>/preview/` with the prescribed HTMX attributes, render only the allowed fields, leave the page otherwise unchanged, and handle 404/permission errors with inline messages.

### Tests for User Story 2

- [x] T019 [P] [US2] Add HTMX preview tests in [financial/tests/test_accounts_preview.py](financial/tests/test_accounts_preview.py) covering success payloads, concurrency queue headers, and allowed fields (spec US2 AC1-3, FR-006).
- [x] T020 [P] [US2] Add error-path tests (404 for missing account, permission restrictions, initial empty panel state) in the same module (spec US2 AC4-5, Edge Cases section).

### Implementation for User Story 2

- [x] T021 [P] [US2] Extend `AccountSummaryRow` helpers or add `AccountPreviewDTO` in [financial/services/accounts.py](financial/services/accounts.py) to filter preview fields (current_balance, credit_limit_or_principal, statement_close_date, payment_due_day, status, notes) per spec US2 AC2.
- [x] T022 [US2] Implement `account_preview` HTMX view in [financial/views.py](financial/views.py) that enforces `hx-request="queue:last"`, `hx-disabled-elt="this"`, returns `200` fragments, and emits `404` partials with refresh guidance when appropriate (spec US2 AC1-5, Edge Cases).
- [x] T023 [US2] Build preview partial [financial/templates/financial/accounts/_preview.html](financial/templates/financial/accounts/_preview.html) using the cotton preview component; confirm `npm run dev:css` watcher logs and annotate `hx-target="#account-preview-panel"` + `hx-swap="innerHTML"` within the template comments (spec US2 AC1-5).
- [x] T024 [US2] Update table component buttons in [templates/components/financial/accounts_row.html](templates/components/financial/account_row.html) (or equivalent) to include HTMX attributes (`hx-get`, `hx-target`, `hx-swap`, `hx-request`, `hx-disabled-elt`) pointing to the preview endpoint per spec US2 AC1 and FR-005.

**Checkpoint**: Preview interactions operate without leaving the page, and the panel swaps deterministically with concurrency protection.

---

## Phase 5: User Story 4 – Open Canonical Detail Page (Priority: P2)

**Goal**: Provide `/accounts/<uuid>/` detail page with full layout, summary metadata, and "Transactions (Coming Soon)" placeholder (spec US4, FR-007).

**Independent Test**: Navigating via the Open action from the table should render the full-page detail view with account header info and placeholder transactions section; preview/edit functionality remains unaffected.

### Tests for User Story 4

- [x] T025 [P] [US4] Add detail-page tests in [financial/tests/test_accounts_detail.py](financial/tests/test_accounts_detail.py) ensuring `GET /accounts/<uuid>/` returns 200 with required sections and 404 for missing accounts (spec US4 AC1-4, FR-007).

### Implementation for User Story 4

- [x] T026 [US4] Implement `AccountDetailView` in [financial/views.py](financial/views.py) that loads user-scoped account data, reuses summary helpers, and injects placeholder context for future transactions (spec US4 AC1-4).
- [x] T027 [US4] Create detail template [financial/templates/financial/accounts/detail.html](financial/templates/financial/accounts/detail.html) using the base layout, summary metadata UI, and "Transactions (Coming Soon)" block; confirm Tailwind watcher logs during template edits (spec US4 AC2-3).
- [x] T028 [US4] Wire the detail route in [financial/urls.py](financial/urls.py) and update the table Open action within [templates/components/financial/account_row.html](templates/components/financial/account_row.html) to point to it (spec US4 AC1, FR-005).

**Checkpoint**: Users can open the canonical account page without relying on preview/edit flows; placeholder area is ready for future features.

---

## Phase 6: User Story 3 – Edit from Preview Panel (Priority: P3)

**Goal**: Enable inline edit + delete actions via HTMX using the preview panel, returning fragments for success, validation errors, and deletes (spec US3, FR-005/FR-008/FR-009).

**Independent Test**: From the index, clicking Edit should load the form into `#account-preview-panel`; saving valid data refreshes both preview panel and table row; invalid forms return 422 fragments; delete confirmation removes the row and clears preview when applicable.

### Tests for User Story 3

- [x] T029 [P] [US3] Add edit-form HTMX tests in [financial/tests/test_accounts_edit.py](financial/tests/test_accounts_edit.py) covering GET form load, POST success (preview refresh), and POST 422 validation errors (spec US3 AC1-3, FR-008).
- [x] T030 [P] [US3] Add delete confirmation + hard delete tests in [financial/tests/test_accounts_delete.py](financial/tests/test_accounts_delete.py) ensuring row removal + preview clearing fragments (spec FR-005, FR-009, Edge Cases concurrency/404 states).

### Implementation for User Story 3

- [x] T031 [US3] Implement HTMX edit view (`account_edit`) and POST handler in [financial/views.py](financial/views.py) that reuses `AccountForm`, returns preview fragments on success, and responds with status 422 on validation errors (spec US3 AC1-3, FR-008).
- [x] T032 [US3] Create/edit form partial [financial/templates/financial/accounts/_form.html](financial/templates/financial/accounts/_form.html) for HTMX rendering (shared with create view) and ensure Tailwind watcher is running before modifications; document `hx-target="#account-preview-panel"` + `hx-swap="innerHTML"` usage (spec US3 AC1-3).
- [x] T033 [US3] Implement delete confirmation partial [financial/templates/financial/accounts/_delete_confirm.html](financial/templates/financial/accounts/_delete_confirm.html) and corresponding view in [financial/views.py](financial/views.py) with `hx-request="queue:last"` + `hx-disabled-elt="this"` on buttons (spec FR-005, FR-009, Edge Cases concurrency behavior).
- [x] T034 [US3] Implement delete POST view (`account_delete`) that performs hard deletes, returns row-removal instructions (e.g., `hx-target="tr[data-account-id='…']" hx-swap="outerHTML"`), and clears preview when deleting selected account; update table component to include delete triggers (spec FR-005, FR-009, Edge Cases for concurrency/404 handling).

**Checkpoint**: Inline edit and delete flows operate entirely within HTMX, maintaining deterministic swaps and fragment responses.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Repository-wide follow-ups after all stories function independently.

- [x] T035 [P] Document data migrations, fixtures, and rollback steps in [specs/001-accounts-home/quickstart.md](specs/001-accounts-home/quickstart.md) and ensure instructions mention new HTMX endpoints (Principle II + plan quickstart updates).
- [x] T036 [P] Update [docs/ai/001-accounts-home-log.md](docs/ai/001-accounts-home-log.md) with final prompt/response references for each automated task to satisfy Principle V.
- [x] T037 Run `python manage.py test financial` plus HTMX smoke tests described in quickstart, attaching evidence to the PR to prove deterministic correctness (spec Success Criteria, Constitution Principle II).
- [x] T038 Verify Tailwind watcher output and regenerated `static/css/output.css` for any new classes referenced in templates, documenting watcher logs in the PR (plan Template & Watcher Safety requirement).
- [x] T039 Perform manual UX sweep of `/accounts/`, preview/edit/delete HTMX flows, and detail page to ensure row actions, flash messages, and placeholder content align with spec FR-005–FR-009; log findings in PR checklist.
- [x] T040 [P] Profile `/accounts/` render time using `financial/tests/test_accounts_performance.py` (or equivalent benchmark script) to prove the page responds ≤2s under fixture load, recording results in the PR to satisfy the Success Criteria.

---

## Dependencies & Execution Order

1. **Phase 1 → Phase 2**: Setup tasks (T001–T002) unblock foundational work; foundational tasks (T003–T010) must finish before any user story starts.
2. **User Story Order**: Prioritized delivery follows spec priorities—US1 (P1) → US2 (P2) → US4 (P2) → US3 (P3). US2 requires US1’s table scaffolding; US4 depends only on foundational data + US1 navigation; US3 depends on US1 table + preview panel plumbing from US2 for swap targets.
3. **Cross-Story Dependencies**:
   - HTMX button wiring in US1 (T014/T018) must reference endpoints delivered later (US2/US3); implement placeholders with comments until endpoints exist.
   - Shared components/templates created earlier are reused by later stories; avoid breaking contract when extending them.
4. **Polish Phase** begins only after desired user stories pass their independent tests.

---

## Parallel Execution Examples

- **US1 (P1)**: After foundational tasks, T013 (serializer) and T014 (cotton components) can run in parallel before integrating via T015/T016; tests T011/T012 can also run simultaneously once fixtures exist.
- **US2 (P2)**: T021 (preview DTO) and T023 (preview partial) operate on distinct files and can proceed concurrently while T022 wires the view; T019/T020 tests can run in parallel with implementation because they target separate behaviors.
- **US4 (P2)**: T026 (view) and T027 (template) can be developed concurrently, with T025 verifying behaviors once both are ready; T028 simply wires URLs/actions afterward.
- **US3 (P3)**: T031 (edit view) and T033 (delete confirm) target different endpoints and can progress simultaneously after T029/T030 start; T032 template work can overlap as long as Tailwind watcher is active.
- **Polish**: T035–T038 are all documentation/testing tasks in different files and can be split across team members once core functionality ships.

---

## Implementation Strategy

1. **MVP (US1)**: Complete Phases 1–3 to deliver `/accounts/` index with deterministic ordering and Add Account CTA. This slice is demoable and satisfies the initial spec requirement.
2. **Incremental Delivery**:
   - Add US2 to enable inline previews without leaving the page.
   - Layer in US4 detail page for deeper inspection (shares priority with US2 but can ship immediately after).
   - Finish with US3 to unlock inline edits/deletes once previews are stable.
3. **Testing Cadence**: For each story, write failing Django tests first, implement functionality, then rerun `python manage.py test financial` plus manual HTMX checks noted in quickstart.
4. **Watcher Discipline**: Before modifying any template/component task, verify `npm run dev:css` is live and record the log snippet in your work notes to comply with Principle IV.
5. **AI Logging**: After completing AI-assisted tasks, append prompt/response metadata to `docs/ai/001-accounts-home-log.md`, referencing the task IDs in commit messages for traceability.
