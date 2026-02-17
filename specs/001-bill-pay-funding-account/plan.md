# Implementation Plan: Bill Pay Funding Account Selector

**Branch**: `[001-bill-pay-funding-account]` | **Date**: 2026-02-14 | **Spec**: specs/001-bill-pay-funding-account/spec.md
**Input**: Feature specification from `specs/001-bill-pay-funding-account/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add a funding-account dropdown to Bill Pay row edit mode, populated with active accounts in household scope, and persist the selected funding account together with existing row fields (`actual_payment_amount`, `paid`) on explicit Save. Keep current HTMX row-swap behavior, enforce required funding account selection, preserve saved closed-account selections as display-only in edit mode, and keep transaction ledger writes out of scope.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Django 6.0.2, django-htmx 1.27.0, django-cotton 2.6.1 (existing only)  
**Storage**: Django ORM with SQLite for local/tests (`db.sqlite3`), existing production DB unchanged  
**Testing**: Django `TestCase` suite in `financial/tests/` via `core.settings_test`  
**Target Platform**: Server-rendered web app (HTML + HTMX row fragments)
**Project Type**: Django monolith web application  
**Performance Goals**: Keep row edit/save interactions single-row scoped and responsive (<1s typical local roundtrip)  
**Constraints**: No new runtime dependencies; no transaction creation side effects; deterministic row persistence and account option ordering  
**Scale/Scope**: Household-scoped account dropdowns for Bill Pay row edits across existing monthly bill payment records

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Spec Traceability** (Principle I)
  - Spec: `specs/001-bill-pay-funding-account/spec.md`
  - Failing-before-implementation scenarios:
    - Row edit does not show funding account selector.
    - Selector does not enforce active-only options (excluding pending/closed for new selections).
    - Save does not persist funding account with amount/paid.
    - Closed saved funding account display behavior is missing.
    - Row save may create transactions (must remain out of scope).
  - Test-first enforcement: user-story tasks include explicit fail-first tests before implementation in `specs/001-bill-pay-funding-account/tasks.md`.
- [x] **Deterministic Data Plan** (Principle II)
  - Migration: add funding account foreign key to `MonthlyBillPayment` (new migration in `financial/migrations/`).
  - Rollback: reverse migration to remove funding-account column and constraint while preserving prior bill-pay data model.
  - Fixtures: add/update deterministic fixture records in `financial/fixtures/accounts_minimal.json` for active + closed accounts and an existing payment row.
  - Determinism: normalize month as first-of-month, enforce explicit ordering for account options, exclude pending/closed from new selector choices, and maintain last-write-wins save behavior.
- [x] **Dependency Discipline** (Principle III)
  - New dependencies: NONE.
- [x] **Template & Watcher Safety** (Principle IV)
  - Watcher command: `npm run dev:css` must be running before styling diagnosis.
  - HTMX target/swap remains row-scoped: `hx-target="#bill-pay-row-<account_id>"` + `hx-swap="outerHTML"`.
  - Dynamic selector state and validation classes are server-computed.
- [x] **HTMX Failure Handling** (Principle IV)
  - Validation failures return `_row_edit.html` with row-level errors and non-200 status.
  - Unauthorized/missing account rows return safe missing fragment and status code.
  - Triggering row container remains stable across edit/save swaps.
- [x] **AI Accountability** (Principle V)
  - Clarification log captured in `specs/001-bill-pay-funding-account/spec.md`.
  - AI activity log target: `docs/ai/005-bill-pay-funding-account-log.md`.

Document evidence for every checkbox. If any item is unresolved, stop and revise the spec/plan before coding.

## Project Structure

### Documentation (this feature)

```text
specs/001-bill-pay-funding-account/
├── plan.md
├── spec.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)
```text
financial/
├── models.py
├── forms.py
├── services/
│   └── bill_pay.py
├── views.py
├── urls.py
├── templates/financial/bill_pay/
│   ├── _row_edit.html
│   ├── _row.html
│   ├── _table_body.html
│   └── index.html
├── tests/
│   ├── test_bill_pay_save.py
│   ├── test_bill_pay_validation.py
│   ├── test_bill_pay_index.py
│   └── test_bill_pay_months.py
└── migrations/

docs/ai/
└── 005-bill-pay-funding-account-log.md
```

**Structure Decision**: Keep changes fully inside the existing `financial` Django app, extending its existing bill-pay model/form/service/view/template/test files with one migration and targeted fixture updates.

## Complexity Tracking

No constitution violations requiring justification.
