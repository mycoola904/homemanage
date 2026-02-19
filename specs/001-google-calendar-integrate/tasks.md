# tasks.md — Google Calendar Bill Pay Sync

## Milestone 0 — Prep
- [X] Add required packages to your environment:
      - `google-api-python-client`
      - `google-auth`
      - `google-auth-oauthlib`
      - `google-auth-httplib2`
- [X] Add config placeholders to settings (and `.env`):
      - `GOOGLE_CALENDAR_ENABLED`
      - `GOOGLE_CALENDAR_ID`
      - `GOOGLE_CALENDAR_SYNC_MONTHS_AHEAD`
      - OAuth client id/secret + redirect uri

## Milestone 1 — Encode due-day rule (1–28)
- [ ] Add validators to `Account.payment_due_day`:
      - `MinValueValidator(1)`
      - `MaxValueValidator(28)`
- [ ] Add/adjust form validation (if you have account edit forms) so UI shows clear error messages.
- [ ] Write a migration (or run makemigrations) and migrate.
- [ ] Add a quick unit test for invalid values (optional but nice).

## Milestone 2 — Mapping model
- [ ] Create `MonthlyBillPaymentCalendarLink` model (OneToOne to MBP).
- [ ] Migrate.
- [ ] Add admin registration (optional).
- [ ] Add index(es) if desired (OneToOne is indexed, but add `google_event_id` index if you will query by it).

## Milestone 3 — EventSpec DTO + payload hash
- [ ] Create `financial/services/billpay_calendar.py`.
- [ ] Add `BillPayEventSpec` dataclass (frozen, slots).
- [ ] Implement `build_billpay_event_spec(mbp)`:
      - Build due date from `mbp.month` + `account.payment_due_day`
      - Household label from `account.household` (name or short code)
      - Summary + description
      - Include Account portal URL from account.url in the description (if present)
      - Build extended properties (private metadata)
      - Compute `payload_hash` from the above
- [ ] Unit test EventSpec builder.

## Milestone 4 — Google Calendar client wrapper
- [ ] Create `integrations/google_calendar/client.py`.
- [ ] Implement credential loading/refresh (one-account OAuth for now).
- [ ] Implement:
      - `insert_event(calendar_id, payload)`
      - `patch_event(calendar_id, event_id, payload)`
      - (optional) `delete_event(calendar_id, event_id)`
- [ ] Ensure errors are raised with helpful context (calendar_id, event_id).
- [ ] Add a thin mockable interface so service tests don’t hit Google.

## Milestone 5 — Sync service (idempotent)
- [ ] In `financial/services/billpay_calendar.py`, implement:
      - `sync_monthly_bill_payment(mbp) -> outcome`
      - `sync_monthly_bill_payments(start_month, months_ahead) -> report`
- [ ] Logic:
      - skip if no due day
      - build EventSpec
      - find/create mapping link
      - if hash unchanged: no-op
      - else patch event and update link
      - if patch 404: insert event and update link
- [ ] Service tests with mocked Google client.

## Milestone 6 — Management command entry point
- [ ] Create command: `billpay_sync_calendar`
- [ ] Parameters:
      - `--months-ahead` (default from settings)
      - `--month` (optional override start month)
      - `--dry-run` (optional; prints what would happen)
- [ ] Output a clean summary:
      - created / updated / unchanged / skipped / errors
- [ ] Smoke test in dev with a dedicated test calendar.

## Milestone 7 — Optional UI trigger
- [ ] Add “Sync Calendar” button to Bill Pay page.
- [ ] Call the service and show summary report.
- [ ] Consider HTMX partial to render results.

## Milestone 8 — Polish
- [ ] Create (optional) a dedicated “Homemanage Bill Pay” calendar if you don’t want to clutter primary.
- [ ] Add reminder defaults (email/popup) if desired.
- [ ] Improve event description formatting (consistent, scan-friendly).
- [ ] Add “disconnect” capability (revoke token / disable sync).
