# Bill Pay Feature upgrade

## Target UX evolution

Based on the current table columns for billpay, I want to make friendliest “minimal change” upgrade for:
- Click in any editable cell → row enters edit mode automatically (same server-rendered edit row you already have).
- Focus lands in the clicked field.
- Tab / Shift+Tab moves through editable controls in the row.
- Enter saves (optional), Esc cancels (optional).
- Saving can keep your current HTMX “swap the row back” behavior.

## Feature evolution plan
### Phase 1 — Inline “click-to-edit row” (smallest change)

**Goal:** Don’t redesign the backend; reuse the existing “row edit partial” endpoint.

**1. Make editable cells clickable**
- In the read-only row partial, wrap the editable display values (Funding Account, Actual Payment, Paid) in something like:
	- a ```<button type="button">…</button>``` styled to look like plain text, or
	- a ```<span role="button" tabindex="0">…</span>``` (button is better for accessibility).
- Add HTMX attributes to those elements:
	- hx-get="/household/finance/bill-pay/<id>/row/?month=YYYY-MM"
	- hx-target="#bill-pay-row-<id>"
	- hx-swap="outerHTML"
- This mirrors what the Edit button already does. 
**2. Pass “which field was clicked” so you can focus it
-

Append a querystring like ?month=2026-02&focus=actual_payment (or funding_account / paid).

Your server renders the edit row and marks the correct input as autofocus.

Keep the existing Edit button

Still useful for mouse users, and it’s your fallback if something’s weird.

Acceptance criteria

Clicking Funding Account / Actual Payment / Paid turns that row into edit mode (only that row).

Cursor is in the relevant control immediately.

Phase 2 — Keyboard-friendly row editing (tab order + enter/esc)

Goal: Make it fast without adding frameworks.

Ensure proper tab order

In the edit row partial: order controls as

Funding Account <select>

Actual Payment <input>

Paid <input type="checkbox">

Save button

Cancel button

Default browser Tab will now “move in the row” naturally.

Enter = save (optional but nice)

Put the row’s edit controls inside a <form> and ensure Save is a submit button.

Add a small JS snippet: if focus is inside that row and user presses Enter, submit the form (with check to avoid Enter inside <select> doing something annoying).

Esc = cancel

Add a keydown listener that triggers your “cancel” HTMX action (which would re-fetch the read-only row partial).

Acceptance criteria

Tab cycles through the row’s fields in a sensible order.

Enter saves (at least from the payment input).

Esc cancels.

Phase 3 — Quality-of-life improvements (still “HTMX-first”)

Goal: Make it feel polished and safe.

Auto-save on blur (optional)

If a user edits Actual Payment and tabs out of the row, you can either:

keep explicit Save (safer), or

auto-save when leaving the row (fastest).

I’d keep explicit Save unless you add a clear “dirty state” indicator.

Dirty state + visual affordance

When the edit row is active, add a subtle background highlight.

When changes occur, enable Save button + show “Unsaved” badge.

“Save & Next”

After saving one row, automatically put the next unpaid row into edit mode and focus Actual Payment.

This is huge for paying a list of bills quickly.

Optimistic UI messaging

On save, show a small toast (“Saved”) or inline status update in the row.

Acceptance criteria

Paying several bills is a fast, repeatable rhythm: click → type → tab → space → enter → next.

Implementation notes (important constraints)

Your current architecture is already row-targeted HTMX swapping by id="bill-pay-row-..." 

billpay

 — lean into that. Don’t jump to a full client-side grid.

The “focus the clicked field” trick is easiest if you:

pass focus= to the server, and

render autofocus on the matching input in the returned edit-r