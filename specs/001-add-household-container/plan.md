# Implementation Plan: Household Top-Level Container (MVP)

**Branch**: `001-add-household-container` | **Date**: 2026-02-12 | **Spec**: [specs/001-add-household-container/spec.md](specs/001-add-household-container/spec.md)
**Input**: Feature specification from `/specs/001-add-household-container/spec.md`

## Summary

Introduce first-class `Household` and `HouseholdMember` tenancy primitives, mount finance under `/household/finance/`, and enforce strict session-based household scoping (`current_household`) across accounts and transactions. The implementation uses Path A reset/re-seed migration strategy, preserves server-driven templates/HTMX boundaries, and keeps dependencies unchanged.

## Technical Context

**Language/Version**: Python 3.11+, Django 6.0.2  
**Primary Dependencies**: Django, django-htmx, django-cotton, Tailwind CLI + DaisyUI (existing only; no new dependencies)  
**Storage**: SQLite for tests/local deterministic runs (`core.settings_test`), PostgreSQL-compatible schema semantics for production  
**Testing**: Django test runner (`python manage.py test --settings=core.settings_test`) with targeted financial + household tests and migration checks  
**Target Platform**: Server-rendered web app on Linux/Windows dev environments  
**Project Type**: Django monolith with app modules (`core`, `financial`, `pages`)  
**Performance Goals**: Preserve current finance UX responsiveness while adding household scoping; no additional query fanout for account/transaction list/detail beyond household filter  
**Constraints**: Deterministic model-form updates with `instance=`; all financial queries scoped to `current_household`; no cross-household leakage; no module navigation via HTMX swaps; no new runtime services/deps  
**Scale/Scope**: MVP supports multiple households per user, single active household per session, Finance module only under household launcher

## Constitution Check (Pre-Design)

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Spec Traceability**: Coverage maps directly to [User Stories 1–4](specs/001-add-household-container/spec.md#L20-L84), [Edge Cases](specs/001-add-household-container/spec.md#L86-L94), and [FR-001..FR-016](specs/001-add-household-container/spec.md#L100-L137). Tests expected to fail pre-implementation include login household selection, household switch behavior, household-scoped account/transaction access guards, and transaction household derivation.
- [x] **Deterministic Data Plan**: New migrations add `Household` and `HouseholdMember`, then add `household` FK to `Account` and `Transaction`. Path A reset/re-seed command creates two canonical households plus deterministic sample data. Rollback for local dev is deterministic: reset DB + rerun migrations + rerun seed command.
- [x] **Dependency Discipline**: No new dependencies, services, background jobs, or client-side frameworks. All work uses existing Django/HTMX/Tailwind stack.
- [x] **Template & Watcher Safety**: Watcher command documented as `npm run dev:css` (project equivalent of `npm run dev`) and must be active before any CSS/template debugging. Conditional classes remain precomputed in views/services or single-line template constructs.
- [x] **HTMX Failure Handling**: All HTMX form endpoints in financial module keep stable targets, return fragment roots matching target containers, and preserve triggering elements unless explicitly justified (none required here).
- [x] **AI Accountability**: Prompt/response log for this plan and implementation will be recorded in `docs/ai/003-household-top-level-container-log.md` and referenced in PR description with spec/plan/tasks links.

## Project Structure

### Documentation (this feature)

```text
specs/001-add-household-container/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── household-finance.yaml
└── tasks.md
```

### Source Code (repository root)

```text
core/
├── settings.py
├── settings_test.py
├── urls.py
└── ...

financial/
├── models.py                # add household FKs and invariants
├── forms.py                 # ensure scoped querysets + deterministic instance updates
├── views.py                 # enforce household-scoped query access
├── urls.py                  # remains financial namespace
├── services/
│   ├── accounts.py
│   └── transactions.py
├── migrations/
│   └── 0005+               # household-related schema changes
├── management/
│   └── commands/
│       └── seed_households.py
├── templates/financial/
│   ├── accounts/
│   └── households/
└── tests/
    ├── test_household_scoping.py
    ├── test_household_switching.py
    └── existing account/transaction tests updated for household scope

pages/
├── urls.py
└── views.py                 # household home/module launcher if housed here

templates/
├── base.html
├── components/
│   ├── layout/
│   │   ├── navbar.html      # add household switcher + module nav
│   │   └── sidebar.html     # namespace-aware menu rendering
│   └── household/
└── pages/
```

**Structure Decision**: Keep Django monolith architecture. Add household domain primitives in `financial` (or shared app-level model placement as implemented), preserve `financial` namespace, and add a new `household` namespace route layer for module launching.

## Phase 0 — Research

Research output is captured in [specs/001-add-household-container/research.md](specs/001-add-household-container/research.md), resolving model constraints, tenancy scoping pattern, migration reset/re-seed approach, and HTMX boundary-safe integration with existing finance endpoints.

## Phase 1 — Design & Contracts

### Data Model Output

See [specs/001-add-household-container/data-model.md](specs/001-add-household-container/data-model.md) for entities, field rules, invariants, and state transitions.

### API/Route Contract Output

See [specs/001-add-household-container/contracts/household-finance.yaml](specs/001-add-household-container/contracts/household-finance.yaml) for server-rendered endpoint contracts.

### Quickstart Output

See [specs/001-add-household-container/quickstart.md](specs/001-add-household-container/quickstart.md) for local setup, reset/re-seed steps, and deterministic verification flow.

### HTMX Endpoint Contract Matrix (Required)

| Endpoint | Method | hx-target | hx-swap | Expected partial root element | Container ID replaced |
|---|---|---|---|---|---|
| `/household/switch/` | POST | N/A (normal form submit + redirect) | N/A | N/A | N/A |
| `/household/finance/<account_id>/preview/` | GET | `#account-preview-panel` | `innerHTML` | `<aside id="account-preview-panel">` or preview root container | `account-preview-panel` |
| `/household/finance/<account_id>/edit/` | GET/POST | `#account-preview-panel` | `innerHTML` | `<form ...>` for edit or `<aside id="account-preview-panel">` for saved preview | `account-preview-panel` |
| `/household/finance/<account_id>/delete/confirm/` | GET | `#account-preview-panel` | `innerHTML` | `<section>`/`<div>` delete-confirm fragment | `account-preview-panel` |
| `/household/finance/<account_id>/delete/` | POST | `#account-preview-panel` + OOB table target | `innerHTML` (+ OOB) | preview reset fragment + OOB accounts table root | `account-preview-panel` (+ table container OOB) |
| `/household/finance/<account_id>/transactions/new/` | GET/POST | `#account-transactions-body` | `innerHTML` | `<section id="account-transactions-body">` transaction form/body fragment | `account-transactions-body` |
| `/household/finance/<account_id>/transactions/<transaction_id>/edit/` | GET/POST | `#account-transactions-body` | `innerHTML` | `<section id="account-transactions-body">` transaction form/body fragment | `account-transactions-body` |
| `/household/finance/<account_id>/transactions/categories/new/` | POST | `#account-transactions-body` | `innerHTML` | `<section id="account-transactions-body">` transaction form/body fragment | `account-transactions-body` |

Notes:
- Module changes (`/household/` → `/household/finance/`) occur via normal route navigation only.
- HTMX responses must not remove their triggering controls unless explicitly planned; this feature keeps triggers intact.

## Phase 2 Planning Preview (for `/speckit.tasks`)

1. Add `Household` + `HouseholdMember` models and constraints.
2. Add household FKs to `Account` and `Transaction` with invariant enforcement.
3. Create migrations and deterministic reset/re-seed command.
4. Add household namespace routes (`/household/`, `/household/finance/`) and login routing behavior.
5. Implement session `current_household` resolver and switch action.
6. Scope financial querysets/views/forms to `current_household`.
7. Update navbar/sidebar for household switch + namespace-aware menus.
8. Update HTMX endpoint behavior/docstrings to preserve container contracts.
9. Add/adjust tests for scoping, guards, switch flow, and migration/seed reliability under SQLite.
10. Add AI attribution log + docs updates.

## Constitution Check (Post-Design Recheck)

- [x] **Spec Traceability**: Design artifacts map to all clarified FRs including zero-household 403 behavior, primary-membership uniqueness, archived household fallback, and transaction edit invariant.
- [x] **Deterministic Data Plan**: Path A reset/re-seed is explicit in quickstart and contracts; migrations from fresh DB plus deterministic seeds are defined.
- [x] **Dependency Discipline**: Post-design still introduces no new dependency.
- [x] **Template & Watcher Safety**: Watcher command captured and HTMX/container boundaries documented.
- [x] **HTMX Failure Handling**: Contract matrix defines targets, swaps, root elements, and container IDs for each HTMX endpoint in feature scope.
- [x] **AI Accountability**: Logging location defined and ready for implementation prompt references.

## Complexity Tracking

No constitution violations identified; table intentionally empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
