# Research: Bill Pay

Date: 2026-02-13  
Spec: specs/001-bill-pay/spec.md

This document consolidates Phase 0 decisions for implementing Bill Pay in the `financial` app with deterministic server-rendered behavior and HTMX row updates.

## Decisions

### Month persistence model

- Decision: Add a dedicated monthly persistence model keyed by `(account, month)` where `month` is normalized to the first calendar day of the selected month.
- Rationale: This preserves historical month edits, prevents duplicate account-month records, and supports the clarified rule that users can edit past months without auto-carry-forward.
- Alternatives considered:
  - Store bill-pay fields on `Account`: rejected because account-level fields cannot represent monthly history.
  - Store month as string (`YYYY-MM`): rejected in favor of date semantics and simpler ORM querying.

### Hard month boundary with historical editing

- Decision: Enforce no carry-forward between months while allowing users to navigate to prior months and edit data in that selected month.
- Rationale: Matches clarifications and keeps monthly accounting deterministic: edits apply only to the targeted account-month record.
- Alternatives considered:
  - Auto-carry unpaid into new month: rejected per clarified requirement.
  - Current-month only: rejected because users need to reconcile prior months later.

### Liability row selection and deterministic ordering

- Decision: Select rows from liability accounts only (`credit_card`, `loan`, `other`) and order by due-day ascending with null due-day values rendered after non-null due days, then tie-break by account name and account id.
- Rationale: Meets functional sorting requirements and guarantees stable ordering across requests and databases.
- Alternatives considered:
  - Default DB null ordering: rejected due to cross-database variability.
  - Python-side sorting only: rejected as unnecessary when ORM can deterministically sort.

### Row-level HTMX save contract

- Decision: Use explicit per-row Save only; POST returns updated row fragment (`200`) on success and row fragment with inline validation errors (`422`) on failure.
- Rationale: Aligns with existing app patterns and clarified save semantics while keeping table container stable.
- Alternatives considered:
  - Auto-save on blur/toggle: rejected by clarification.
  - Save-all table action: rejected for MVP complexity and conflict with row-save requirement.

### Validation semantics for paid vs amount

- Decision: `paid` is independent from `actual_payment_amount`; allow `paid=true` with blank or `0.00` amount, but reject negative amounts.
- Rationale: Matches clarified business rule while preserving guardrails against invalid negative values.
- Alternatives considered:
  - Require positive amount when paid: rejected by clarification.
  - Auto-set paid based on amount: rejected to preserve explicit user intent.

### Test and fixture determinism

- Decision: Add focused Django `TestCase` coverage with explicit month fixtures and deterministic date inputs under SQLite test settings.
- Rationale: Satisfies constitution deterministic requirements and existing repository testing conventions.
- Alternatives considered:
  - Large shared fixture-only approach: rejected due to brittle maintenance and weaker scenario focus.
