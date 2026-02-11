
# Implementation Plan: Account and Transaction Model Evolution

**Branch**: `001-account-transaction-evolution` | **Date**: 2026-02-11 | **Spec**: [specs/001-account-transaction-evolution/spec.md](specs/001-account-transaction-evolution/spec.md)
**Input**: Feature specification from `/specs/001-account-transaction-evolution/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Evolve `Account` and `Transaction` models to enforce deterministic transaction sign logic, conditional account fields, and normalized categories while preserving HTMX contracts and SQLite testability. This plan implements [User Stories 1–3](specs/001-account-transaction-evolution/spec.md#L17-L76), the deterministic sign matrix, and migration requirements without adding dependencies.

## Technical Context

**Language/Version**: Python 3.11 with Django 6.0.2  
**Primary Dependencies**: Django 6.0.2, django-htmx 1.27.0, django-cotton 2.6.1, Tailwind CLI 4.1.18 + DaisyUI 5.5.17, psycopg 3.3.x (already present)  
**Storage**: PostgreSQL for dev/prod, SQLite for tests via `core.settings_test`  
**Testing**: Django test runner (`python manage.py test`) with `financial.tests` additions  
**Target Platform**: Server-rendered web app with HTMX fragments  
**Project Type**: Django monolith with modular apps (`core`, `financial`, `pages`)  
**Performance Goals**: Not explicitly defined; keep HTMX responses small and deterministic  
**Constraints**: No new runtime dependencies; HTMX swaps only in declared containers; single-line template tags; SQLite tests required  
**Scale/Scope**: Single-user household usage; transactions list sized for deterministic table rendering

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Spec Traceability**: All work maps to [Functional Requirements FR-001–FR-013](specs/001-account-transaction-evolution/spec.md#L92-L134) and the sign matrix. Tests that will fail before implementation: account conditional-field validation, transaction sign matrix enforcement, transaction type restrictions per account type, category case-insensitive uniqueness, and HTMX inline category error handling.
- [x] **Deterministic Data Plan**: Migrations add `account_number`, `routing_number`, `interest_rate`, `transaction_type`, and `category` (nullable), backfill `transaction_type` from `direction`, then drop `direction` and `number_last4`. Backfill is idempotent; no new fixtures. Rollback is reverse migration; SQLite migration path must succeed on fresh and populated DBs.
- [x] **Dependency Discipline**: No new runtime or tooling dependencies. All work uses existing Django + HTMX + Tailwind stack.
- [x] **Template & Watcher Safety**: Confirm `npm run dev:css` before any template/class changes. Conditional classes are precomputed in views or single-line `{% with %}` blocks. HTMX targets remain `#account-preview-panel` and `#account-transactions-body` with `hx-swap="innerHTML"`.
- [x] **HTMX Failure Handling**: Inline category creation returns errors as fragment + 400 without removing the transaction form; account/transaction forms return form fragments with errors and preserve triggering elements.
- [x] **AI Accountability**: Prompt/response logs stored at `docs/ai/001-account-transaction-evolution-log.md` and referenced in the PR description.

Document evidence for every checkbox. If any item is unresolved, stop and revise the spec/plan before coding.

## Project Structure

### Documentation (this feature)

```text
specs/001-account-transaction-evolution/
├── plan.md
├── research.md          # Phase 0 output (/speckit.plan)
├── data-model.md        # Phase 1 output (/speckit.plan)
├── quickstart.md        # Phase 1 output (/speckit.plan)
├── contracts/           # Phase 1 output (/speckit.plan)
└── tasks.md             # Phase 2 output (/speckit.tasks)

### Source Code (repository root)

```text
core/
├── settings.py
├── settings_test.py
└── urls.py

financial/
├── models.py
├── forms.py
├── services/
│   ├── accounts.py
│   ├── transactions.py
│   └── formatters.py
├── views.py
├── urls.py
├── templates/financial/accounts/
│   ├── _form.html
│   ├── _preview.html
│   ├── _preview_missing.html
│   ├── detail.html
│   └── transactions/
│       ├── _body.html
│       ├── _form.html
│       └── _missing.html
├── migrations/
└── tests/

templates/
└── components/
    ├── financial/
    │   ├── account_preview_panel.html
    │   ├── account_row.html
    │   ├── account_transactions_table.html
    │   └── accounts_table.html
    └── ui/
```

**Structure Decision**: Single Django project with the `financial` app owning account/transaction logic and templates, and shared components in `templates/components` per django-cotton configuration.

## Pre-Implementation Commitments

**Tests written first**:
- `financial/tests/test_account_fields.py`: conditional field validation (`routing_number`, `interest_rate`, `account_number`).
- `financial/tests/test_transaction_sign_matrix.py`: deterministic sign matrix coverage across account types and transaction types.
- `financial/tests/test_transaction_type_restrictions.py`: disallowed transaction types rejected per account type.
- `financial/tests/test_category_uniqueness.py`: case-insensitive uniqueness with preserved casing.
- `financial/tests/test_inline_category_errors.py`: HTMX inline category add returns fragment + 400 and keeps form.
- `financial/tests/test_migrations_backfill.py`: backfill maps `direction` to `transaction_type` correctly.

**Failure condition proving spec is not satisfied**: Any of the above tests failing, or a migration failing to apply cleanly on SQLite (fresh or populated) indicates the spec requirements are unmet.

**Migration order relative to backfill**: Add new fields (`account_number`, `routing_number`, `interest_rate`, `transaction_type`, `category`) and keep `direction` first; run backfill to populate `transaction_type`; remove `direction` and `number_last4` only after successful backfill.

## Implementation Breakdown

1. **Model updates (Account)**: Add `account_number` and `routing_number` fields; deprecate `number_last4`. Implement model `clean()` to enforce: routing number only for checking/savings; interest rate only for credit card/loan/other debt; null otherwise. Keep deterministic validation and null persistence per FR-002/FR-003.
2. **Model updates (Transaction)**: Replace `direction` with `transaction_type` enum, enforce allowed transaction types per account type, and apply deterministic sign logic before save. Validate positive input amounts only (FR-006a) and persist signed amounts based on the matrix.
3. **Category entity**: Add `Category` model with `name`, `user`, `created_at`, and case-insensitive uniqueness constraint on `(user, lower(name))`. Preserve input casing while enforcing uniqueness.
4. **Migrations**: Create multi-step migrations to add nullable fields, create `Category`, add `transaction_type`, backfill from `direction`, then remove `direction` and `number_last4`. Ensure idempotent data migration (no row creation/deletion) and SQLite compatibility.
5. **Forms**: Update `AccountForm` fields to include `account_number`, `routing_number`, and `interest_rate`, with server-driven visibility flags. Update `TransactionForm` to use `transaction_type`, `category`, and absolute amount; validate positive values.
6. **Services**: Update `financial/services/transactions.py` to format signed amounts based on `transaction_type` and account type (not `direction`). Ensure formatting reflects stored signed values.
7. **Views/HTMX**: Maintain existing HTMX targets. Ensure account edit forms bind instances on GET/POST and return preview/form fragments accordingly. Add inline category add endpoint that returns dropdown updates on success or a 400 error fragment on failure.
8. **Templates**: Update transaction form and account form partials to show/hide conditional fields with server-provided flags. Keep template tags on one line and preserve `hx-target`/`hx-swap` contracts.
9. **Tests**: Implement tests listed in Pre-Implementation Commitments using SQLite settings. Add coverage for migration backfill correctness and HTMX error responses.
10. **Documentation updates**: Ensure quickstart includes migration steps and SQLite test command; ensure contracts document HTMX endpoints and error handling.

## Constitution Check (Post-Design)

- [x] Spec traceability and test-first commitments documented.
- [x] Migration/backfill sequencing specified and SQLite coverage included.
- [x] HTMX targets/swap strategies preserved and error handling defined.
- [x] No new dependencies introduced.

## Complexity Tracking

No constitution violations identified; table remains empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|





