# plan.md — Google Calendar Bill Pay Sync

## Why this design
- Keep views thin: views/commands call a single sync service.
- Keep Google API logic isolated: one client wrapper module.
- Use a dataclass “EventSpec” DTO: deterministic, testable, template-like payloads.
- Idempotency via mapping table: no duplicates, safe re-runs.

## Implementation Order (recommended)

### 1) Model + validation
1. Add validators to `Account.payment_due_day` (1–28).
2. Create new model `MonthlyBillPaymentCalendarLink` and migrate.
3. Add admin (optional) to inspect links.

### 2) Event specification (domain → DTO)
Create `financial/services/billpay_calendar.py`:
- `BillPayEventSpec` dataclass (summary, description, date, metadata, account_url, payload_hash)
- `build_billpay_event_spec(mbp: MonthlyBillPayment) -> BillPayEventSpec`
- Include household label derived from `mbp.account.household` (e.g., household name uppercased or a short code).
- Build an Account URL from `Account.url` link to the online payment portal.

Change detection:
- Compute `payload_hash` from the fields that should trigger an update:
  - household label, account name, due date, paid, actual amount, account_url

### 3) Google Calendar client wrapper (integration layer)
Create `integrations/google_calendar/client.py` (or `financial/services/google_calendar.py` if you prefer):
- `insert_event(calendar_id, event_payload) -> (event_id, etag)`
- `patch_event(calendar_id, event_id, event_payload) -> (event_id, etag)`
- `delete_event(calendar_id, event_id) -> None` (optional for later)

Keep this wrapper “dumb”:
- It receives a Python dict payload already shaped for Google.
- It handles transport errors and returns useful identifiers.

Auth strategy (this iteration):
- One OAuth connection for one Google account/calendar.
- Store refresh token in DB (encrypted if feasible).

### 4) Sync service (idempotent orchestration)
In `financial/services/billpay_calendar.py` implement:
- `sync_monthly_bill_payment(mbp: MonthlyBillPayment) -> SyncOutcome`
- `sync_monthly_bill_payments(month: date, months_ahead: int) -> SyncReport`

Behavior:
- If MBP ineligible (no due day): skip with reason.
- Build `EventSpec`
- Look for `MonthlyBillPaymentCalendarLink`:
  - If none: create event → store link
  - If exists:
    - If payload hash unchanged: do nothing
    - Else patch event → update link fields (etag/synced/hash)
  - If patch returns 404: insert new event → update link

### 5) Entry points
**Management command** (first):
- `python manage.py billpay_sync_calendar --months-ahead 6`
- Output counts (created/updated/unchanged/skipped/errors)

Optional UI:
- Add a “Sync Calendar” button near Bill Pay page (HTMX or normal POST)
- Calls the same service, displays report

### 6) Event content choices
- Use all-day events.
- Summary: `[{HOUSEHOLD}] Pay {account.name}`
- Description: multi-line details including Account URL (Account.url).
- Extended properties:
  - `homemanage_mbp_id`, `homemanage_account_id`, `homemanage_household_id`, `homemanage_kind`

### 7) Observability
- Log key outcomes at INFO:
  - created/updated/unchanged/skipped
- Log exceptions with MBP id and account id context.
- Keep reports deterministic so you can trust runs.

## Folder / module sketch

- `financial/models.py`
  - `MonthlyBillPaymentCalendarLink`
  - validators on `Account.payment_due_day`

- `financial/services/billpay_calendar.py`
  - `BillPayEventSpec`
  - `build_billpay_event_spec()`
  - `sync_monthly_bill_payment()`
  - `sync_monthly_bill_payments()`

- `integrations/google_calendar/client.py`
  - Google Calendar API calls
  - credential acquisition / token refresh (or delegated to an auth module)

- `financial/management/commands/billpay_sync_calendar.py`
  - CLI entry point

## Testing plan
- Unit test `build_billpay_event_spec()` for:
  - correct due date for a given month
  - correct summary prefix from household
  - includes Account URL
  - correct metadata keys
- Sync service tests with fake google client:
  - create on missing link
  - patch on changed hash
  - no-op on unchanged hash
  - recreate on 404
  - skip ineligible due day

## “Done” definition
- Running the management command creates/updates events correctly.
- Re-running is idempotent.
- Events include Account.URL and household label.
