# Implementation Plan: BillPay Row Keyboard Editing

**Branch**: `[001-billpay-row-keyboard-edit]` | **Date**: 2026-02-17 | **Spec**: [specs/001-billpay-row-keyboard-edit/spec.md](specs/001-billpay-row-keyboard-edit/spec.md)
**Input**: Feature specification from `/specs/001-billpay-row-keyboard-edit/spec.md`

## Summary

Add keyboard-friendly row editing to BillPay by extending the current row-targeted HTMX flow: clicking editable row fields enters edit mode focused on the clicked field, Tab follows the required in-row order, Enter maps to Save, and Esc maps to Cancel. Keep the existing `financial:bill-pay-row` endpoint and row partial swaps (`outerHTML`) as the single server-driven edit mechanism; no backend redesign and no client-side grid architecture.

## Technical Context

**Language/Version**: Python 3.11+, Django templates, HTMX-enhanced server-rendered HTML, minimal JavaScript for focus/keyboard handling  
**Primary Dependencies**: Django, HTMX, Tailwind CSS, DaisyUI (existing only; no new packages)  
**Storage**: SQLite (existing `MonthlyBillPayment` model; no schema change planned)  
**Testing**: Django `TestCase` test suite under `financial/tests/` + targeted HTMX response assertions  
**Target Platform**: Web browsers supported by current HomeManage UI (desktop-first keyboard interactions)  
**Project Type**: Django web application (server-driven UI)  
**Performance Goals**: Preserve current row-swap latency characteristics; no extra full-table or full-page reloads for row edits  
**Constraints**: Reuse existing row edit partial endpoint and row-level HTMX swap; avoid SPA/client-side grid redesign; maintain single active row edit behavior  
**Scale/Scope**: BillPay row interaction behavior only (click-to-edit focus + keyboard navigation/save/cancel)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Spec Traceability**: Covered by [specs/001-billpay-row-keyboard-edit/spec.md](specs/001-billpay-row-keyboard-edit/spec.md) User Stories 1-3 and FR-001..FR-010. Expected pre-implementation failing coverage: click-into-field edit entry, required tab order, Enter-to-save parity, Esc-to-cancel parity.
- [x] **Deterministic Data Plan**: No migration required; existing deterministic uniqueness (`account`,`month`) remains. Reuse existing fixtures; add deterministic tests only. Rollback = code-only rollback with no schema/data mutation risk.
- [x] **Dependency Discipline**: No new dependencies, services, queues, or runtime infrastructure.
- [x] **Template & Watcher Safety**: `npm run dev:css` must be confirmed running before style debugging. HTMX containers: row target `#bill-pay-row-<account_id>` with `hx-swap="outerHTML"`; table month selector target `#bill-pay-table-body` with `hx-swap="innerHTML"`. For the HTMX BillPay row form endpoint (`financial:bill-pay-row`), the expected returned partial root element is `tr#bill-pay-row-<account_id>` for success and validation responses. Dynamic classes/attributes remain server-computed or in single-line template expressions.
- [x] **HTMX Failure Handling**: Invalid row/month/account returns `_row_missing.html` with 404; validation failures return `_row_edit.html` with 422 and keep same row target in DOM; trigger remains available after each swap.
- [x] **AI Accountability**: Prompt/response references will be recorded in this spec folder artifacts and linked in PR description with implemented spec paragraphs.

All gate checks pass. No unresolved constitutional blockers.

## Project Structure

### Documentation (this feature)

```text
specs/001-billpay-row-keyboard-edit/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── billpay-row-edit.openapi.yaml
└── tasks.md
```

### Source Code (repository root)

```text
financial/
├── urls.py
├── views.py
├── forms.py
├── templates/
│   └── financial/
│       └── bill_pay/
│           ├── index.html
│           ├── _table_body.html
│           ├── _row.html
│           ├── _row_edit.html
│           └── _row_missing.html
└── tests/
    ├── test_bill_pay_index.py
    ├── test_bill_pay_save.py
    └── test_bill_pay_validation.py

static/
└── src/ (existing frontend behavior hooks if needed)
```

**Structure Decision**: Use the existing Django app structure and extend only current BillPay row/view/template/test files. Reuse the existing row-targeted HTMX endpoint in `financial.views.bill_pay_row` and its `_row.html` / `_row_edit.html` partial workflow.

## Post-Design Constitution Re-Check

- [x] Spec traceability remains complete (no scope drift).
- [x] Determinism preserved (no new schema or nondeterministic input).
- [x] Dependency surface unchanged.
- [x] Server-driven UI preserved with explicit HTMX target/swap contracts.
- [x] Failure states remain server-rendered and row-scoped.
- [x] AI accountability location remains this feature folder + PR links.

## Complexity Tracking

No constitutional violations to justify.
