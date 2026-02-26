# spec.md — Google Calendar Bill Pay Sync

## Goal
Integrate Homemanage Bill Pay with Google Calendar by syncing each `MonthlyBillPayment` row to a corresponding Google Calendar event, using a deterministic, idempotent process (re-running sync updates existing events instead of creating duplicates).

This feature is **one-way sync** from Homemanage → Google Calendar.

## In Scope
- Create/update/delete Google Calendar events based on `MonthlyBillPayment`.
- Support a **single shared calendar** containing events for multiple households.
- Enforce due-day validity: `Account.payment_due_day` must be in **1–28**.
- Store a durable mapping between `MonthlyBillPayment` and Google Calendar `eventId`.
- Provide a manual sync entry point (management command; optional UI button).
- Tag events with household information (human-readable + machine-readable metadata).
- Include an **Account.URL** in the calendar event so you can jump from Google Calendar → online portal payment.

## Out of Scope (this iteration)
- Two-way sync (reading from Google Calendar to update Homemanage).
- Business-day / holiday adjustments.
- Per-user calendar connections (multi-account OAuth). This iteration targets **one** connected Google account/calendar.

## Current Domain Model (relevant)
- `Account.payment_due_day: PositiveSmallIntegerField(null=True, blank=True)`
- `Account.household: ForeignKey(Household, PROTECT)`
- `MonthlyBillPayment(account, month, actual_payment_amount, paid, ...)`
  - UniqueConstraint: `(account, month)`

## New Data Model
### `MonthlyBillPaymentCalendarLink`
One-to-one mapping from a bill-pay row to a Google event.

- `monthly_bill_payment` (OneToOneField, CASCADE, unique)
- `google_calendar_id` (CharField)
- `google_event_id` (CharField)
- `etag` (CharField, optional)
- `last_synced_at` (DateTimeField)
- `last_payload_hash` (CharField, optional; recommended for change detection)

## Eligibility Rules
A `MonthlyBillPayment` is eligible for calendar sync if:
- `account.payment_due_day` is set and in **[1, 28]**
- `month` is within the configured sync window (e.g., current month → +N months)

## Date Construction
- `due_date = date(mbp.month.year, mbp.month.month, account.payment_due_day)`
- Create an **all-day** event:
  - `start = {"date": due_date.isoformat()}`
  - `end = {"date": (due_date + timedelta(days=1)).isoformat()}`

## Google Calendar Event Shape
- Summary: prefixed with household label.
  - Example: `[HOME] Pay Chase Visa`
- Description includes:
  - Household
  - Account
  - Month (the MBP month)
  - Paid status
  - Actual payment amount (if present)
  - **Account portal URL** (from Account.url, if present) — link to the bank/utility/payment site
    - If Account.url is blank/null, omit the portal line; do not block event creation.
- Metadata: `extendedProperties.private`:
  - `homemanage_kind` = `"monthly_bill_payment"`
  - `homemanage_mbp_id` = str(MonthlyBillPayment.id)
  - `homemanage_account_id` = str(Account.id)
  - `homemanage_household_id` = str(Household.id)

Notes:
- Prefer `events.patch` for updates (partial updates), falling back to recreate if 404.
- Optionally set event `source` fields if you like, but the Account.URL in `description` is sufficient.

## Idempotency Rules
Sync is deterministic and safe to re-run:
- If a `MonthlyBillPaymentCalendarLink` exists: update (patch) the mapped event.
- If no link: create (insert) event and store mapping.
- If update fails with “Not Found” (deleted in Google): create a new event and update mapping.
- If an MBP becomes ineligible (missing due day): skip and log.

## Configuration
Add settings (names can vary; keep them centralized):
- `GOOGLE_CALENDAR_ENABLED` (bool)
- `GOOGLE_CALENDAR_ID` (default `"primary"` or a dedicated “Homemanage Bill Pay” calendar id)
- `GOOGLE_CALENDAR_SYNC_MONTHS_AHEAD` (e.g., 3 or 6)
- Account.url link to the online payment portal
- OAuth:
  - `GOOGLE_OAUTH_CLIENT_ID`
  - `GOOGLE_OAUTH_CLIENT_SECRET`
  - `GOOGLE_OAUTH_REDIRECT_URI`


## Validation / Constraints
Enforce the “day <= 28” rule at the model level:
- Add `MinValueValidator(1)` and `MaxValueValidator(28)` to `Account.payment_due_day`.
- Keep `null=True, blank=True` if some accounts do not participate in bill pay.

## Test Strategy
- Unit tests:
  - Due date construction
  - Event spec generation (summary/description/metadata)
  - Hash change behavior
- Service tests with a mocked Google client:
  - create path
  - update path
  - recreate-on-404 path
  - skip ineligible rows
- Optional: management command smoke test in dev using a test calendar.

## Acceptance Criteria
- Running sync twice creates **no duplicates**.
- Events include household label + working Account URL.
- Paid status / amount changes update events on next sync.
- Invalid due days are blocked by validation (1–28).
