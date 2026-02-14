# Implementation Plan: Bill Pay

**Branch**: `[001-bill-pay]` | **Date**: 2026-02-13 | **Spec**: specs/001-bill-pay/spec.md
**Input**: Feature specification from `specs/001-bill-pay/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a Bill Pay view in the `financial` app that lists liability accounts for a selected month (default current month), allows explicit per-row save of `actual_payment_amount` and `paid`, and persists one record per account-month. The implementation remains server-rendered with HTMX row fragments, enforces hard month boundaries (no carry-forward), and allows historical month edits through month selection.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Django 6.0.2, django-htmx 1.27.0, django-cotton 2.6.1 (existing only)  
**Storage**: SQLite (`db.sqlite3`) for local/tests; production DB unchanged and out of feature scope  
**Testing**: Django `TestCase` suite in `financial/tests/` using `core.settings_test` (SQLite)  
**Target Platform**: Server-rendered web application (HTML + HTMX partials)
**Project Type**: Django web application  
**Performance Goals**: Bill Pay page renders under 2s for typical household datasets; row-save roundtrip remains single-row scoped  
**Constraints**: No new runtime dependencies, deterministic month/account uniqueness, HTML-only endpoints, explicit row-save only, no auto-carry-forward  
**Scale/Scope**: Household-scoped liability accounts (`credit_card`, `loan`, `other`) with monthly editing and historical month selection

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Spec Traceability** (Principle I)
  - Spec: `specs/001-bill-pay/spec.md`
  - Scenarios that fail before implementation and will be covered by tests:
    - Sidebar lacks Bill Pay route/view and monthly table.
    - Liability-only filtering and due-day ordering behavior missing.
    - Row-level Save + 422 inline validation behavior missing.
    - Account-month persistence uniqueness and reload behavior missing.
    - Historical month navigation/edit with no carry-forward missing.
- [x] **Deterministic Data Plan** (Principle II)
  - Planned migration: add `MonthlyBillPayment` model (proposed file: `financial/migrations/0004_monthly_bill_payment.py`) with uniqueness on `(account, month)`.
  - Fixture strategy: extend `financial/fixtures/accounts_minimal.json` or add dedicated bill-pay fixture for deterministic account/month scenarios.
  - Rollback: migrate `financial` to prior migration (`0003_account_minimum_amount_due`) to drop new table and constraints.
  - Determinism: normalize month to first day of month and enforce explicit ordering tie-breakers.
- [x] **Dependency Discipline** (Principle III)
  - New dependencies: NONE.
  - Use existing Django, HTMX patterns, and app services.
- [x] **Template & Watcher Safety** (Principle IV)
  - Tailwind/DaisyUI watcher command: `npm run dev:css` (must be confirmed running before styling/debug changes).
  - Conditional classes/states are server-computed in view/service context or single-line template constructs.
  - Stable containers:
    - Table wrapper remains stable in Bill Pay page.
    - Row updates target row container only.
  - Planned HTMX swaps:
    - Row edit/save target: `#bill-pay-row-<account_id>` with `hx-swap="outerHTML"`.
    - Month switch target: `#bill-pay-table-body` with `hx-swap="innerHTML"`.
- [x] **HTMX Failure Handling** (Principle IV)
  - Validation errors return row form fragment with status `422`.
  - Missing/unowned account-month updates return a safe HTML response with status `404` and no data leakage.
  - Trigger preservation: row Save trigger remains inside the replaced row fragment; table-level month controls live outside row swap targets.
- [x] **AI Accountability** (Principle V)
  - Clarification decisions tracked in `specs/001-bill-pay/spec.md`.
  - Session/prompt log target: `docs/ai/004-bill-pay-log.md`.
  - PR will reference spec + plan + tasks and include AI log path.

Document evidence for every checkbox. If any item is unresolved, stop and revise the spec/plan before coding.

## Project Structure

### Documentation (this feature)

```text
specs/001-bill-pay/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)

```text
core/
├── settings.py
├── settings_test.py
└── urls.py

financial/
├── models.py
├── forms.py
├── urls.py
├── views.py
├── services/
│   └── bill_pay.py                # new service helpers for rows/order/serialization
├── templates/financial/
│   └── bill_pay/
│       ├── index.html             # full Bill Pay page
│       ├── _table_body.html       # month-swapped tbody fragment
│       └── _row.html              # row fragment/view-edit states
├── tests/
│   ├── test_bill_pay_index.py
│   ├── test_bill_pay_save.py
│   ├── test_bill_pay_months.py
│   └── test_bill_pay_validation.py
└── migrations/
    └── 0004_monthly_bill_payment.py

templates/components/
└── financial/
    └── bill_pay_table.html        # reusable table shell component (if extracted)
```

**Structure Decision**: Keep all feature logic within the existing Django `financial` app and its established service/template/test layout. Use app-local templates for feature fragments and optional shared component extraction only if reused.

## Constitution Check (Post-Design Re-check)

- [x] Spec traceability remains intact after design artifacts (`research.md`, `data-model.md`, `contracts/`, `quickstart.md`).
- [x] Deterministic data design is explicit: unique account-month key, no carry-forward side effects, reproducible month selection behavior.
- [x] No new dependencies introduced by design decisions.
- [x] HTMX targets/swaps and failure states are documented in contracts and quickstart.
- [x] AI accountability paths are documented and ready for PR attribution.

## Complexity Tracking

No constitution violations requiring justification.
