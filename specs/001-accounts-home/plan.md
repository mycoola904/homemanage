# Implementation Plan: Accounts Home + Preview Panel

**Branch**: `001-accounts-home` | **Date**: 2026-02-09 | **Spec**: [specs/001-accounts-home/spec.md](specs/001-accounts-home/spec.md)
**Input**: Feature specification from `/specs/001-accounts-home/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Deliver a scoped `financial` app that introduces the `Account` model with UUID primary keys and user ownership, renders the `/accounts/` index using django-cotton table/preview components, serves HTMX preview/edit/delete flows with concurrency protection, and exposes a canonical detail page. All behavior follows the acceptance criteria in [specs/001-accounts-home/spec.md](specs/001-accounts-home/spec.md), relies on server-rendered templates, and adds no new dependencies.

## Technical Context

**Language/Version**: Python 3.11 (per constitution) with Django 6.0.2  
**Primary Dependencies**: Django 6.0.2, django-htmx 1.27.0, django-cotton 2.6.1, Tailwind CLI 4.1.18 + DaisyUI 5.5.17 (watcher via `npm run dev:css`), psycopg 3.3.x for PostgreSQL. All already present; no new runtime packages allowed.  
**Storage**: PostgreSQL (prod/staging) with migrations authored in `financial/migrations`.  
**Testing**: Django test runner via `python manage.py test`, emphasizing new `financial.tests` covering `Account` model constraints, views, and HTMX responses.  
**Target Platform**: Server-rendered web experience deployed on Linux containers; supports desktop + mobile browsers with HTMX.  
**Project Type**: Django monolith with modular apps (`core`, `pages`, new `financial`).  
**Performance Goals**: `/accounts/` responds within 2s and HTMX flows return <500ms under expected load, matching Success Criteria in [specs/001-accounts-home/spec.md#L248-L256](specs/001-accounts-home/spec.md#L248-L256).  
**Constraints**: No new dependencies, no JSON endpoints, HTMX swaps limited to declared containers, conditional classes computed server-side, `npm run dev:css` must be running when touching Tailwind/DaisyUI, UUID PK + hard delete only.  
**Scale/Scope**: Single authenticated household user base (no Household model). `/accounts/` renders full dataset (likely dozens of accounts) without pagination per [specs/001-accounts-home/spec.md#L68-L91](specs/001-accounts-home/spec.md#L68-L91).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Spec Traceability**: All work maps to [User Stories 1–4](specs/001-accounts-home/spec.md#L68-L150) plus [Functional Requirements FR-001–FR-013](specs/001-accounts-home/spec.md#L165-L217). Prior to implementation, regression tests would fail for: `AccountsIndexView` ordering, HTMX preview/edit responses, canonical detail rendering, and hard delete flows; these scenarios will be codified in `financial/tests/test_accounts_views.py` and `test_models.py` to enforce acceptance criteria.
- [x] **Deterministic Data Plan**: Introduce `financial` app migration `0001_initial` that creates the `Account` table with UUID PK, FK to `auth.User`, deterministic indexes (`account_type`, `name`, `created_at` ordering, and `(user_id, lower(name))` unique constraint). Reverse migration drops the table. Provide fixture `financial/fixtures/accounts_minimal.json` reflecting spec sample data ([specs/001-accounts-home/spec.md#L218-L235](specs/001-accounts-home/spec.md#L218-L235)). Document rollback procedure (migrate zero + reload fixtures) inside this plan and quickstart.
- [x] **Dependency Discipline**: Reuse existing Django, django-htmx, django-cotton, Tailwind/DaisyUI stacks. No new runtime packages, services, or build tooling introduced; feature stays within Principle III.
- [x] **Template & Watcher Safety**: Confirm `npm run dev:css` (alias for Tailwind/DaisyUI watcher) is running before editing templates/components. Conditional class strings (status badges, empty states) precomputed in view context or single-line `{% with %}` blocks. HTMX swaps remain limited to `#account-preview-panel` (`innerHTML`) and row-specific containers for delete confirmations, matching [specs/001-accounts-home/spec.md#L92-L150](specs/001-accounts-home/spec.md#L92-L150).
- [x] **HTMX Failure Handling**: Preview/edit endpoints return HTML fragments with `200` on success, `422` on validation failure (form re-render), and `404` when an account disappears; delete flows return fragments instructing the client to remove the row and clear preview. `hx-request="queue:last"` + `hx-disabled-elt="this"` guard concurrency (per spec) while the triggering button stays mounted in the table row.
- [x] **AI Accountability**: Prompt/response logs for this feature will be captured at `docs/ai/001-accounts-home-log.md` and referenced in the PR description alongside links to [specs/001-accounts-home/spec.md](specs/001-accounts-home/spec.md) and this plan, satisfying Principle V.

Document evidence for every checkbox. If any item is unresolved, stop and revise the spec/plan before coding.

## Project Structure

### Documentation (this feature)

```text
specs/001-accounts-home/
├── plan.md
├── research.md          # Phase 0 output (/speckit.plan)
├── data-model.md        # Phase 1 output (/speckit.plan)
├── quickstart.md        # Phase 1 output (/speckit.plan)
├── contracts/           # Phase 1 output (/speckit.plan)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

> **Component rule (django-cotton):** Because `COTTON_DIR = "components"`, **all cotton components MUST live in the global component tree** at `templates/components/**`.  
> App templates MAY include or render these components, but MUST NOT define new cotton components under `financial/templates/...`.  
> App-local templates under `financial/templates/financial/accounts/**` are reserved for **pages** and **HTMX partials**.

```text
core/
├── settings.py          # add financial app; keep cotton config (COTTON_DIR="components")
├── urls.py              # include financial.urls
└── ...                  # project code

financial/
├── __init__.py
├── apps.py
├── models.py            # Account model + manager
├── migrations/
│   └── 0001_initial.py
├── urls.py              # accounts routes listed below
├── views.py             # class-based + HTMX views
├── forms.py             # AccountCreateForm/AccountUpdateForm/DeleteConfirmForm
├── templates/financial/accounts/
│   ├── index.html       # page; renders global cotton components + defines HTMX targets
│   ├── detail.html      # page (“Open”)
│   ├── _form.html       # HTMX partial (edit/create form body)
│   ├── _preview.html    # HTMX partial (preview content; uses global components as needed)
│   └── _delete_confirm.html  # HTMX partial (confirm UI; uses global modal component if present)
└── tests/
    ├── test_models.py
    └── test_views.py

pages/
└── ... (existing app; remains untouched except for nav link additions if required)

templates/
├── base.html
└── components/          # **GLOBAL django-cotton components (authoritative)**
    ├── layout/
    │   ├── app.html
    │   ├── sidebar.html
    │   └── navbar.html
    ├── auth/
    ├── ui/              # reuse flash + card + modal (if present)
    └── financial/        # new global components for this feature
        ├── accounts_table.html        # cotton component for accounts table
        ├── account_row.html           # optional: cotton component for a row
        └── account_preview_panel.html # cotton component wrapper (panel shell)

static/
└── css/output.css        # built via npm run dev:css
'''

**Structure Decision**: Single Django project with modular apps. `financial` app encapsulates account data access, HTMX views, and templates while reusing shared components under `templates/`. Routing lives in `financial/urls.py`, included from `core/urls.py`. Tests sit beside the app. Documentation artifacts stay under `specs/001-accounts-home/`.

## Implementation Breakdown

1. **Create `financial` app structure**: Generate app via `python manage.py startapp financial`, add to `INSTALLED_APPS`, wire `financial.urls` under `/accounts/`, and scaffold folders for models, views, forms, templates, tests, fixtures, and django-cotton partials.
2. **Migration strategy for PostgreSQL**: Author `0001_initial` migration producing the `Account` table with UUID primary key (`models.UUIDField(primary_key=True, default=uuid4, editable=False)`), FK to `settings.AUTH_USER_MODEL` with `CASCADE` delete, decimal fields with fixed precision, `status`/`account_type` choices, timestamps, and deterministic indexes (ordering + `UniqueConstraint` on `Lower('name')`). Provide reversible operations and fixture file for deterministic data loads.
3. **Account model definition**: Define `Account` with fields from [specs/001-accounts-home/spec.md#L192-L217](specs/001-accounts-home/spec.md#L192-L217) plus `user = ForeignKey(User, related_name="accounts", on_delete=CASCADE)`. Include `AccountType` and `AccountStatus` enums, `clean()` enforcing `payment_due_day` range (1–31) when set, default `status='active'`, and model `Meta.ordering = ('account_type', 'name', 'created_at')`.
4. **URL patterns**: Implement the following in `financial/urls.py` (all views login-protected): `/accounts/` (list), `/accounts/new/` (create form), `/accounts/<uuid:pk>/preview/`, `/accounts/<uuid:pk>/edit/`, `/accounts/<uuid:pk>/` (detail), `/accounts/<uuid:pk>/delete/confirm/` (HTMX modal/partial), `/accounts/<uuid:pk>/delete/` (POST). Patterns use `app_name = "financial"` for namespacing (e.g., `financial:accounts-index`).
5. **View structure**: Use class-based views for full pages (`AccountsIndexView`, `AccountCreateView`, `AccountDetailView`) and function-based HTMX views for preview/edit/delete to keep response fragments explicit. Each view scopes queries to `request.user` and injects serialized rows for django-cotton components. Reuse shared mixins for `LoginRequiredMixin` + `UserAccountQuerysetMixin` that enforces user ownership.
6. **HTMX endpoint behavior**: Preview + edit GET endpoints return fragments inserted into `#account-preview-panel` with `hx-swap="innerHTML"`. POST edit returns preview fragment (200) or form fragment (422). Delete confirm returns `hx-swap="innerHTML"` into row-local container; delete POST responds with snippet instructing client to remove `tr[data-account-id]` via `hx-target` referencing the row with `hx-swap="outerHTML"`. All HTMX buttons declare `hx-request="queue:last"` and `hx-disabled-elt="this"`. Errors respond with inline alert partial referencing shared flash system.
7. **Template + django-cotton components**: Build reusable cotton components `accounts/table.cotton.html` and `accounts/preview_panel.cotton.html` composed in `templates/financial/accounts/index.html`. Components accept serialized `AccountSummaryRow` objects and `preview_state`. Use existing base layout and flash component under `templates/components/ui/`. No conditional template logic spans multiple lines; class combinations computed ahead of rendering.
8. **Deterministic data considerations**: All queryset ordering defined at the model level and reinforced in views/tests. Fixtures provide stable sample data for manual QA. Decimal fields default to `Decimal("0.00")`. No timezone or locale randomness; currency formatting uses `babel`-style helper inside template filter (existing) or Python `format_currency` equivalent while remaining deterministic.
9. **Constitution compliance checkpoints**: Before touching CSS/templates, ensure Tailwind watcher logs are visible. Every HTMX endpoint documents targets/swap types in docstrings and plan. Migration/fixture steps recorded in `quickstart.md` with rollback instructions. Tests assert no stray queries and enforce template safety per Principle IV.
10. **Scope confirmation**: This plan adds only the `Account` model plus required views/templates/routes for metadata management. No Household abstraction, no transactions/budgets, no JSON endpoints, no new dependencies, and no out-of-scope UI features will be introduced.
11. **Performance validation**: Add a Django test (e.g., `financial/tests/test_accounts_performance.py`) or management command that times the `/accounts/` view under fixture load and asserts render time ≤2 seconds, capturing evidence in the PR to satisfy the Success Criteria. Document how to run this measurement in `quickstart.md` and rerun whenever table/preview templates change.

## Complexity Tracking

No constitution violations identified; table remains empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|

