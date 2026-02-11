# AI Session Log: 001-account-transactions

Date: 2026-02-11

## Scope

Design + planning artifacts for Transactions (Account detail + add via HTMX fragments).

## Prompt/Response References

- Clarification Q&A captured in specs/001-account-transactions/spec.md under "Clarifications".
- This file exists to be linked from the PR description to satisfy Constitution Principle V.

## Decisions recorded

- Amount storage: DecimalField(max_digits=10, decimal_places=2)
- Table columns: Posted On, Description, Amount
- Missing/unowned fragments: HTTP 200 with inline not found message
- posted_on default: server-side today
- direction control: radio buttons
