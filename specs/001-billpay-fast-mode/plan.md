# Implementation Plan: Bill Pay Fast Mode

**Branch**: `001-billpay-fast-mode` | **Date**: 2026-02-17 | **Spec**: `specs/001-billpay-fast-mode/spec.md`
**Input**: Feature specification from `/specs/001-billpay-fast-mode/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add an optional Fast Mode workflow to bill pay row saves: when enabled, a successful save returns the row in display mode and triggers client-side auto-open of the next unpaid row in current on-screen order with focus on `actual_payment_amount`. Implementation remains HTMX-first by extending the existing `bill_pay_row` POST response with a trigger payload and adding a small JavaScript handler that reuses current edit-row entry behavior.

## Technical Context

**Language/Version**: Python 3.11+ (Django 6.0.2), JavaScript (vanilla browser script)  
**Primary Dependencies**: Django, django-htmx, HTMX, Tailwind CSS, DaisyUI (existing only; no new dependencies)  
**Storage**: SQLite for local/test; production-compatible with existing relational DB setup  
**Testing**: Django test runner (`manage.py test`) with feature/unit integration tests in `financial/tests/`  
**Target Platform**: Server-rendered web app in modern desktop browsers
**Project Type**: Django monolith (server-rendered templates + HTMX partial updates)  
**Performance Goals**: Add at most one follow-up row-edit GET request per successful Fast Mode save, avoid full-table refreshes on row save, and complete save+auto-open in no more than two HTMX round trips during acceptance testing  
**Constraints**: No schema migration; no new dependency; maintain deterministic row ordering; preserve existing keyboard save/cancel behavior; respect Django single-line template tag/comment constraints  
**Scale/Scope**: One feature slice in bill pay flow (`bill_pay_row` save/edit UX), plus targeted tests and docs artifacts

## Constitution Check

- [x] **Spec Traceability**: Work maps to `spec.md` User Stories P1–P3 and FR-001..FR-011. Tests to write first (failing): Fast Mode default-off behavior, fast-mode save emits next-row instruction, no-auto-advance when disabled, no-auto-advance on validation error, no-next-row terminal behavior.
- [x] **Deterministic Data Plan**: No migrations/fixtures required. Data updates occur via existing `MonthlyBillPayment` upsert path. Rollback is code-only revert of Fast Mode signals/handler with unchanged schema.
- [x] **Dependency Discipline**: No new runtime/dev dependencies. Uses existing Django + HTMX + current static JS pipeline.
- [x] **Template & Watcher Safety**: CSS pipeline validated with `npm run build:css` (Tailwind + DaisyUI successful). For active styling/debug work, run `npm run dev:css` and confirm rebuild output. HTMX containers remain stable: row target `#bill-pay-row-<account_id>` with `outerHTML`; table target `#bill-pay-table-body` with `innerHTML`.
- [x] **HTMX Failure Handling**: Save validation errors return `_row_edit.html` with `422` to same row target; save success returns `_row.html` and optional trigger for next-row open; open-next failure leaves saved row intact, displays a subtle inline status message in the Bill Pay header area, and requires manual continuation.
- [x] **AI Accountability**: Planning/clarification decisions are recorded in `spec.md` and `research.md`; PR will reference this plan/spec and include prompt file `.github/prompts/speckit.specify.prompt.md` plus chat/session link.

Document evidence for every checkbox. If any item is unresolved, stop and revise the spec/plan before coding.

### Post-Design Re-check (after Phase 1 artifacts)

- [x] Data model and contracts align with FR-001..FR-011 and introduce no schema drift.
- [x] Contracted HTMX response behavior keeps trigger elements/targets stable.
- [x] Design keeps server as source of truth for next-row computation and failure-state signaling.

## Project Structure

### Documentation (this feature)

```text
specs/001-billpay-fast-mode/
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
financial/
├── forms.py
├── urls.py
├── views.py
├── services/bill_pay.py
├── templates/financial/bill_pay/
│   ├── index.html
│   ├── _table_body.html
│   ├── _row.html
│   └── _row_edit.html
└── tests/
  ├── test_bill_pay_save.py
  ├── test_bill_pay_row_keyboard.py
  └── test_bill_pay_validation.py

static/
├── src/bill_pay_row_keyboard.js
└── css/output.css
```

**Structure Decision**: Existing Django monolith structure is retained. Implementation is limited to `financial` bill-pay views/templates/services, one existing client JS module, and focused `financial/tests` additions.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
