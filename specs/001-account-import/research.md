# Phase 0 Research: Household Account Import

## Decision 1: Add `online_access_url` as `URLField(blank=True)` on `Account`
- Decision: Use Django `models.URLField(blank=True)` for the online account access URL.
- Rationale: Built-in URL validation provides deterministic, framework-native validation and keeps form/model behavior aligned with the spec (`online_access_url` blank or absolute HTTP/HTTPS URL).
- Alternatives considered:
  - `CharField` + custom validator: rejected because it duplicates framework behavior and increases maintenance surface.
  - Separate related model/table for account links: rejected as unnecessary complexity for one optional field.

## Decision 2: Implement CSV parsing with Python stdlib `csv.DictReader`
- Decision: Parse uploads using Python standard library `csv` and in-memory decoding via UTF-8 with deterministic header checks.
- Rationale: Satisfies Principle III (lean dependencies), supports CSV-only scope, and keeps parse behavior explicit and testable.
- Alternatives considered:
  - `pandas`: rejected due to unnecessary dependency and larger runtime surface.
  - Custom split-based parser: rejected for correctness and quoting/escaping edge-case risk.

## Decision 3: Enforce atomic import transaction per file
- Decision: Validate all rows first, then insert in one `transaction.atomic()` block; if any row fails validation, insert none.
- Rationale: Directly satisfies FR-006 and deterministic integrity requirements.
- Alternatives considered:
  - Best-effort partial inserts: rejected because spec requires all-or-nothing behavior.
  - Per-row transactions: rejected because it complicates rollback semantics and can violate FR-006.

## Decision 4: Household-scoped duplicate detection using case-insensitive name matching
- Decision: During validation, detect duplicates against active household existing accounts and within-upload rows using case-folded account names.
- Rationale: Satisfies FR-009 and avoids user confusion from near-identical account names.
- Alternatives considered:
  - User-scoped duplicate detection (model default): rejected because clarified requirement is household scope.
  - Allow duplicates: rejected by clarified requirement.

## Decision 5: HTMX-driven form swap in stable finance container
- Decision: Keep sidebar trigger in DOM and swap only main content/panel containers (`#financial-main-content` for navigation, `#account-import-panel` for form POST responses).
- Rationale: Matches constitution Principle IV and existing server-driven UI pattern in finance templates.
- Alternatives considered:
  - Full-page-only postback without HTMX panel swaps: rejected because spec requires explicit HTMX target/swap safety documentation.
  - Swapping sidebar or outer drawer container: rejected because it risks removing trigger elements.

## Decision 6: CSV contract values and formats are strict/canonical
- Decision: Require exact header set (including `online_access_url`), canonical enum values, ISO `YYYY-MM-DD` date format, max 5 MB and 1,000 rows.
- Rationale: Deterministic parsing/validation and lower ambiguity for internal users.
- Alternatives considered:
  - Accept multiple date formats/labels: rejected due to parsing ambiguity.
  - Optional headers with dynamic mapping: rejected due to reduced determinism and harder support.
