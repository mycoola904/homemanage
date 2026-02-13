# Implementation Plan: Household Account Import

**Branch**: `001-account-import` | **Date**: 2026-02-13 | **Spec**: [specs/001-account-import/spec.md](specs/001-account-import/spec.md)
**Input**: Feature specification from `/specs/001-account-import/spec.md`

## Summary

Add a finance-sidebar import entry and a server-driven account import flow that accepts CSV uploads, validates a required near-full Account header set (including `online_access_url`), enforces household-scoped deterministic inserts, and exposes a downloadable template CSV. Implementation uses Django forms/views + HTMX partial swaps for form POST responses, an atomic transaction for all-or-nothing imports, and a model migration to add Account online access URL support.

## Technical Context

**Language/Version**: Python 3.11+, Django 6.0.x, HTML templates with HTMX  
**Primary Dependencies**: Django, django-htmx, django-cotton, Python stdlib `csv` (no new runtime package)  
**Storage**: SQLite (local/tests via `core.settings_test`), production DB compatible via Django ORM  
**Testing**: Django test runner (`python manage.py test --settings=core.settings_test`) with app tests under `financial/tests/`  
**Target Platform**: Server-rendered web app (desktop/mobile browser)  
**Project Type**: Django monolith web application  
**Performance Goals**: Process valid CSV files up to 1,000 rows within 10s in local-like environment (SC-002)  
**Constraints**: CSV only, max 5 MB upload, max 1,000 data rows, canonical enum values, ISO dates, deterministic atomic writes, no cross-household inserts  
**Scale/Scope**: Single feature slice in `financial` app (Account import + Account URL field + template CSV + tests)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Spec Traceability**: Source spec is [specs/001-account-import/spec.md](specs/001-account-import/spec.md), covering scenarios for sidebar navigation, successful import, validation errors, and template download; failing-first tests will map to those scenarios in `financial/tests/` before implementation (Principle I).
- [x] **Deterministic Data Plan**: Add one migration for Account online URL field, with reversible schema operation; CSV import uses deterministic parsing and one atomic DB transaction; template CSV is fixed-order and tracked artifact (Principle II).
- [x] **Dependency Discipline**: No new runtime dependency; CSV parsing uses Python stdlib. This satisfies Principle III (expected NONE).
- [x] **Template & Watcher Safety**: `npm run dev:css` command is documented as mandatory before style troubleshooting; dynamic classes remain server-computed; HTMX targets/swap defined below (`#financial-main-content`, `#account-import-panel`, `innerHTML`) (Principle IV).
- [x] **HTMX Failure Handling**: POST returns the same import panel root partial on 422 with error details; successful import returns panel + summary without removing triggering sidebar link/container (Principle IV).
- [x] **AI Accountability**: Prompt/response references will be listed in PR description and linked to this spec/plan path under branch `001-account-import` (Principle V).

## Project Structure

### Documentation (this feature)

```text
specs/001-account-import/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── account-import.openapi.yaml
└── tasks.md
```

### Source Code (repository root)

```text
financial/
├── forms.py
├── models.py
├── urls.py
├── views.py
├── migrations/
│   └── NNNN_account_online_access_url.py (next sequential migration number)
├── templates/financial/accounts/
│   ├── import.html
│   └── _import_panel.html
└── tests/
    ├── test_account_import.py
    ├── test_account_import_validation.py
    └── test_account_import_template.py

templates/components/layout/
└── sidebar.html

financial/fixtures/
└── account_import_template.csv
```

**Structure Decision**: Keep all implementation within existing Django app/template patterns; add import-specific templates under `financial/templates/financial/accounts/`, wire URLs in `financial/urls.py`, and extend existing sidebar component in `templates/components/layout/sidebar.html`.

## Phase 0: Research Plan

Research outputs are captured in [specs/001-account-import/research.md](specs/001-account-import/research.md). Topics:

1. Model field choice for online access URL (`URLField` vs `CharField`).
2. CSV parsing/validation approach for deterministic, atomic imports.
3. HTMX integration pattern for finance content swaps while preserving sidebar trigger.
4. Duplicate detection strategy aligned to household-scoped case-insensitive uniqueness requirement.

## Phase 1: Design & Contracts

Design outputs:

- Data model: [specs/001-account-import/data-model.md](specs/001-account-import/data-model.md)
- API contract: [specs/001-account-import/contracts/account-import.openapi.yaml](specs/001-account-import/contracts/account-import.openapi.yaml)
- Quickstart: [specs/001-account-import/quickstart.md](specs/001-account-import/quickstart.md)

HTMX endpoint design (form endpoints):

- `GET /financial/import/` renders import page with `#financial-main-content` container.
- `GET /financial/import/panel/` returns panel partial root `<section id="account-import-panel">` for sidebar-triggered content swaps.
- `POST /financial/import/` accepts multipart file upload with `hx-target="#account-import-panel"` and `hx-swap="innerHTML"`; 422 returns same panel root with validation errors.
- Triggering sidebar element remains in DOM because only `#financial-main-content` / `#account-import-panel` containers are swapped.

## Phase 2 Preview (for `/speckit.tasks`)

Expected implementation streams:

1. Schema + model updates (`online_access_url` on Account + migration).
2. Import form/service/view/URL and template CSV download endpoint.
3. Sidebar import navigation + HTMX target container wiring.
4. Deterministic validation + atomic transaction behavior.
5. Tests for success, validation failures, limits, household scoping, and template contract.

## Constitution Check (Post-Design Re-evaluation)

- [x] **Spec Traceability**: Design artifacts map every endpoint/entity back to FR-001..FR-017 and user stories.
- [x] **Deterministic Data Plan**: Migration + atomic write strategy + deterministic CSV contract retained.
- [x] **Dependency Discipline**: Still no new runtime dependencies.
- [x] **Template & Watcher Safety**: HTMX containers/swap strategy documented; watcher command captured in quickstart.
- [x] **HTMX Failure Handling**: Error status/partial-root behavior explicitly defined in contract + quickstart.
- [x] **AI Accountability**: Artifact paths are fixed and ready to reference in PR evidence.

## Complexity Tracking

No constitution violations or complexity exemptions are required for this feature.
