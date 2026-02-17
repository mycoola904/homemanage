# Data Model: Subtle Row Swap Animation

## Overview
This feature introduces no persistent domain entities. It uses transient UI state attached to existing bill-pay row elements during HTMX swaps.

## Entities

### 1. BillPayRowViewState (existing rendered row)
- **Represents**: Read-only bill-pay row rendered from `financial/bill_pay/_row.html`.
- **Key fields (already present in rendered context)**:
  - `account_id` (UUID)
  - `edit_url` (includes `month` query)
  - display fields (`funding_account_display`, `actual_payment_amount_display`, `paid_label`)
- **Relationships**:
  - One-to-one per account/month with `BillPayRowEditState` representation via swap.

### 2. BillPayRowEditState (existing rendered row)
- **Represents**: Editable bill-pay row rendered from `financial/bill_pay/_row_edit.html`.
- **Key fields (already present in rendered context)**:
  - `account_id` (UUID)
  - `post_hx_url`
  - `focus_field`
  - form fields (`funding_account`, `actual_payment_amount`, `paid`)
- **Relationships**:
  - Swaps back to `BillPayRowViewState` on save/cancel success.

### 3. RowTransitionState (new transient UI state)
- **Represents**: Short-lived client-side animation marker on swapped row node.
- **Key fields**:
  - `row_dom_id` (`bill-pay-row-<account_id>`)
  - `phase` (`entering`; optional `leaving`)
  - `duration_ms` (120–180)
- **Persistence**: None (DOM-only, removed after animation completes).

## Validation Rules
- Transition state must apply only when swapped element ID matches `bill-pay-row-*`.
- Enter transition must not prevent interaction with Save/Cancel/Edit controls.
- Cleanup must remove transient classes/attributes after completion so repeat swaps re-animate deterministically.

## State Transitions
1. `BillPayRowViewState` --(GET edit via HTMX `outerHTML`)--> `BillPayRowEditState` + `RowTransitionState(entering)`
2. `BillPayRowEditState` --(POST save valid via HTMX `outerHTML`)--> `BillPayRowViewState` + `RowTransitionState(entering)`
3. `BillPayRowEditState` --(POST cancel via HTMX `outerHTML`)--> `BillPayRowViewState` + `RowTransitionState(entering)`
4. `BillPayRowEditState` --(POST invalid 422 via HTMX `outerHTML`)--> `BillPayRowEditState` + `RowTransitionState(entering)`
