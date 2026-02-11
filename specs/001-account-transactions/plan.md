# Implementation Plan: Account Transactions

**Branch**: `[001-account-transactions]` | **Date**: 2026-02-11 | **Spec**: specs/001-account-transactions/spec.md
**Input**: Feature specification from `specs/001-account-transactions/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add a first-class `Transaction` model scoped to an `Account`, render an Account Transactions panel on the account detail page, and support inline add (Save/Cancel) using HTMX fragments only. All transaction routes enforce auth + ownership identical to accounts, and render deterministically ordered transaction rows.

## Technical Context

**Language/Version**: Python (project assumes 3.11+ per constitution)  
**Primary Dependencies**: Django 6.0.2, django-htmx 1.27.0, django-cotton 2.6.1  
**Storage**: SQLite for local/dev/tests (`db.sqlite3` in repo); production DB may vary (out of scope)  
**Testing**: Django `TestCase` (unittest-style) under `financial/tests/`  
**Target Platform**: Server-rendered web app (HTML-only responses; HTMX fragments)  
**Project Type**: Django web application  
**Performance Goals**: Account detail page + transactions panel remains responsive with up to ~200 transactions (render without UI breakage)  
**Constraints**: No new runtime dependencies; deterministic ordering; HTML-only endpoints; template safety rules (single-line `{% %}` and `{# #}`)  
**Scale/Scope**: Single-user-per-request (auth-scoped); minimal CRUD (list + create only)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Spec Traceability** (Principle I)
  - Spec: specs/001-account-transactions/spec.md
  - Scenarios expected to fail before implementation:
    - Account detail page currently shows "Transactions (Coming Soon)"; will be replaced by real panel.
    - New tests to add for:
      - Empty-state rendering on account detail
      - Deterministic ordering for non-empty list
      - Add flow: GET form, POST valid returns updated table, POST invalid returns 422 with errors, Cancel swaps back
      - Missing/unowned account fragment behavior (inline not found message, status 200)
- [x] **Deterministic Data Plan** (Principle II)
  - Migration: add `Transaction` table via `financial/migrations/0002_transaction.py` (single migration for MVP)
  - Index: account-scoped ordering support (see design below)
  - Fixtures: none required for MVP
  - Rollback: `python manage.py migrate financial 0001` cleanly drops the table
- [x] **Dependency Discipline** (Principle III)
  - New dependencies: NONE (use Django + existing packages only)
- [x] **Template & Watcher Safety** (Principle IV)
  - Tailwind watcher command in this repo: `npm run dev:css`
  - Conditional classes: computed server-side (views/services) or simple template usage; avoid `{% if %}` inside attributes where possible
  - Stable container: `#account-transactions` (outer), swap target: `#account-transactions-body` (inner)
  - Swap strategy: `hx-swap="innerHTML"` targeting `#account-transactions-body`
- [x] **HTMX Failure Handling** (Principle IV)
  - Validation errors: return the form fragment with errors and HTTP 422
  - Missing/unowned: return a body fragment with an inline "not found" message and HTTP 200 (per spec clarification)
  - Returned partial root elements:
    - Transactions body fragment root: `<div data-component="financial.account_transactions_body">...`
    - New transaction form fragment root: `<form data-component="financial.transaction_form">...`
  - Trigger preservation: the "Add Transaction" button lives outside `#account-transactions-body` in the stable panel header
- [x] **AI Accountability** (Principle V)
  - Prompts/decisions recorded in specs/001-account-transactions/spec.md (Clarifications section)
  - Session log file: docs/ai/002-account-transactions-log.md
  - PR description will link to the spec + plan + tasks and mention the log file for prompt provenance

Document evidence for every checkbox. If any item is unresolved, stop and revise the spec/plan before coding.

## Project Structure

### Documentation (this feature)

```text
specs/001-account-transactions/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
```text
core/
├── settings.py
├── urls.py
└── ...

financial/
├── models.py                 # Add Transaction model here
├── forms.py                  # Add TransactionForm here
├── urls.py                   # Add /transactions/ routes under /accounts/<uuid>/
├── views.py                  # Add HTMX fragment views
├── templates/financial/accounts/
│   ├── detail.html            # Replace "Coming Soon" card with real panel container
│   └── transactions/
│       ├── _body.html         # Transactions panel body fragment (table/empty/missing)
│       ├── _form.html         # Add Transaction form fragment
│       └── _missing.html      # Inline "not found" message fragment
└── tests/
  └── test_account_transactions_*.py

templates/components/financial/
└── account_transactions_table.html  # Reusable table component (spec FR-008)
```

**Structure Decision**: Django app-local templates for feature-specific fragments, plus a shared reusable table component under `templates/components/financial/` consistent with existing components.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations expected for this feature.
