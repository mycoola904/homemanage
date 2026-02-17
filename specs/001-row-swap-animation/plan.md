# Implementation Plan: Subtle Row Swap Animation

**Branch**: `001-row-swap-animation` | **Date**: 2026-02-17 | **Spec**: `specs/001-row-swap-animation/spec.md`
**Input**: Feature specification from `/specs/001-row-swap-animation/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add subtle 120–180ms fade/slide enter animation to bill-pay row `outerHTML` swaps when toggling view↔edit states, while preserving server-driven HTMX behavior and deterministic form handling. Implementation will use existing Django templates and bill-pay JavaScript hook points, with no schema or dependency changes.

## Technical Context

**Language/Version**: Python 3.11+ (Django), JavaScript (existing static script), HTML templates, CSS via Tailwind/DaisyUI build  
**Primary Dependencies**: Django, HTMX, Tailwind CSS, DaisyUI (existing project dependencies only)  
**Storage**: SQLite (existing app/test default); no new persistence for this feature  
**Testing**: Django test suite (`python manage.py test`), focused bill-pay HTMX interaction checks  
**Target Platform**: Server-rendered web app in modern desktop/mobile browsers with CSS transitions and HTMX  
**Project Type**: Web application (Django monolith with server-rendered templates + HTMX partials)  
**Performance Goals**: Transition starts immediately after swap and completes within 120–180ms; no perceivable delay in row edit/save/cancel flow  
**Constraints**: No migrations, no new runtime dependencies, no non-bill-pay behavior changes, preserve `hx-target`/`hx-swap` contract and trigger element continuity via stable table body container  
**Scale/Scope**: Bill-pay row view↔edit swaps only (`financial/bill_pay/_row.html` and `_row_edit.html` responses via `bill_pay_row` endpoint)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Spec Traceability**: Covered by User Story 1 and 2 plus FR-001..FR-011 in `spec.md`. Pre-implementation failing checks include: (a) row swap currently appears abrupt with no enter transition; (b) repeated toggles can be verified for absent transition-state cleanup behavior.
- [x] **Deterministic Data Plan**: No schema/model changes. Migrations: none. Fixtures: none. Rollback: revert template/CSS/JS changes only; DB state remains unchanged and reproducible.
- [x] **Dependency Discipline**: No new dependencies required. Implementation uses existing HTMX lifecycle events and existing asset pipeline.
- [x] **Template & Watcher Safety**: Watcher command is `npm run dev:css` and must be confirmed running before CSS debugging. Bill-pay swaps use `hx-target="#bill-pay-row-<account_id>"` with `hx-swap="outerHTML"`; conditional classes remain precomputed server-side or static class names, keeping Django template tags single-line.
- [x] **HTMX Failure Handling**: Validation errors return `financial/bill_pay/_row_edit.html` with status `422` and same row root `<tr id="bill-pay-row-...">`; cancel/save success returns `financial/bill_pay/_row.html`. Trigger continuity is preserved by keeping stable `tbody#bill-pay-table-body` container and row IDs intact across swaps.
- [x] **AI Accountability**: Prompt/response records for spec/clarify/plan are stored in `specs/001-row-swap-animation/` artifacts and will be referenced in PR description with links to `spec.md`, `plan.md`, and `tasks.md`.

Document evidence for every checkbox. If any item is unresolved, stop and revise the spec/plan before coding.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
```text
financial/
├── views.py
├── urls.py
├── forms.py
├── services/
│   └── bill_pay.py
├── templates/
│   └── financial/
│       └── bill_pay/
│           ├── index.html
│           ├── _table_body.html
│           ├── _row.html
│           └── _row_edit.html
└── tests/
  ├── test_bill_pay_row_keyboard_edit.py
  └── test_bill_pay_funding_account.py

static/
└── src/
  └── bill_pay_row_keyboard.js
```

**Structure Decision**: Use the existing Django web-app structure and implement within current `financial` bill-pay templates + static script; keep surface area minimal and avoid new modules.

## Phase 0: Research Plan

- Confirm HTMX row-swap animation pattern for `outerHTML` responses: apply enter class after `htmx:afterSwap`, remove temporary class after animation end/timeout.
- Confirm fallback behavior: if hook fails, server-rendered row still appears and remains functional.
- Confirm CSS strategy: subtle motion values and duration window (120–180ms) while preserving finance-tool calmness.

Research outputs are documented in `research.md`.

## Phase 1: Design & Contracts

- Data model artifacts identify transient UI state entities only (no persisted domain changes).
- Contracts document existing bill-pay HTMX endpoints and swap contracts that implementation must preserve.
- Quickstart defines watcher/test workflow and manual validation steps for row transitions.

Design outputs are documented in `data-model.md`, `contracts/bill-pay-row-animation.openapi.yaml`, and `quickstart.md`.

## Post-Design Constitution Check

- [x] **Spec Traceability**: Design artifacts map directly to FR-001..FR-011 and SC-001..SC-004.
- [x] **Deterministic Data Plan**: Still no DB mutations or migrations.
- [x] **Dependency Discipline**: Still zero new dependencies.
- [x] **Template & Watcher Safety**: Contracts and quickstart explicitly preserve `hx-target`/`hx-swap` details and require watcher confirmation.
- [x] **HTMX Failure Handling**: Contracts cover `422` error return path with stable row root and target continuity.
- [x] **AI Accountability**: Artifacts remain in spec folder for PR linking.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
