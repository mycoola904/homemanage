# 006 Bill Pay Fast Mode — AI Prompt/Response Traceability

## Scope
- Feature: Bill Pay Fast Mode (`save -> auto-open next unpaid row`)
- Spec: `specs/001-billpay-fast-mode/spec.md`
- Plan: `specs/001-billpay-fast-mode/plan.md`
- Tasks: `specs/001-billpay-fast-mode/tasks.md`

## Prompt Sources
- `.github/prompts/speckit.specify.prompt.md`
- `.github/prompts/speckit.implement.prompt.md`

## AI-assisted decisions implemented
1. Page-scoped Fast Mode toggle with default OFF.
2. Server-driven next unpaid row selection using current on-screen order.
3. HTMX `HX-Trigger` event (`billpay:openNextRow`) payload containing next row metadata.
4. Client handler in `static/src/bill_pay_row_keyboard.js` to open next row and set focus.
5. Open-next failure behavior: inline status message in Bill Pay header area and manual continuation.

## Files touched during implementation
- `financial/services/bill_pay.py`
- `financial/views.py`
- `financial/templates/financial/bill_pay/index.html`
- `financial/templates/financial/bill_pay/_row_edit.html`
- `static/src/bill_pay_row_keyboard.js`
- `financial/tests/test_bill_pay_save.py`
- `financial/tests/test_bill_pay_row_keyboard.py`
- `financial/tests/test_bill_pay_index.py`
- `financial/tests/test_bill_pay_validation.py`
- `specs/001-billpay-fast-mode/contracts/bill-pay-fast-mode.openapi.yaml`
- `specs/001-billpay-fast-mode/quickstart.md`
- `specs/001-billpay-fast-mode/research.md`

## Validation intent
- Focused Django test runs for bill pay save/keyboard/validation/index coverage.
- Deterministic checks: no schema migration additions and no fixture changes required.
