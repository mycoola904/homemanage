from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, Optional
from decimal import Decimal
import calendar
import hashlib
import json

@dataclass(frozen=True, slots=True)
class BillPayEventSpec:
    summary: str
    description: str
    start_date: date
    end_date: date
    extended_properties: Dict[str, str]
    payload_hash: str

def _month_label(d: date) -> str:
    # mbp.month is a date; we treat it as "the month being paid"
    return f"{calendar.month_name[d.month]} {d.year}"

def build_billpay_event_spec(mbp) -> BillPayEventSpec:
    account = mbp.account
    household = account.household

    if not account.payment_due_day:
        raise ValueError("Account.payment_due_day is required for calendar sync")
    
    due_date = date(mbp.month.year, mbp.month.month, account.payment_due_day)

    # all-day event convention: end = next day
    start_date = due_date
    end_date = due_date + timedelta(days=1)

    household_label = str(household.name).upper()
    summary = f"[{household_label}] Pay {account.name}"
    extended_properties = {
        "homemanage_kind": "monthly_bill_payment",
        "homemanage_mbp_id": str(mbp.id),
        "homemanage_account_id": str(account.id),
        "homemanage_household_id": str(household.id),
    }

    # placeholder until next step
    description = _build_description(mbp)
    payload_hash = _compute_payload_hash(
        summary=summary,
        description=description,
        start_date=start_date,
        end_date=end_date,
        extended_properties=extended_properties,
    )

    return BillPayEventSpec(
        summary=summary,
        description=description,
        start_date=start_date,
        end_date=end_date,
        extended_properties=extended_properties,
        payload_hash=payload_hash,
    )

def _account_portal_url(account) -> Optional[str]:
    # Support either field name without refactors
    url = getattr(account, "online_access_url", None) or getattr(account, "url", None)
    if not url:
        return None
    url = str(url).strip()
    return url or None

def _format_money(amount: Optional[Decimal]) -> str:
    if amount is None:
        return None
    # Deterministic 2dp output
    return f"${amount:.2f}"

def _build_description(mbp) -> str:
    account = mbp.account
    household = account.household
    
    lines: list[str] = []
    lines.append(f"Household: {household.name}")
    lines.append(f"Account: {account.name}")
    lines.append(f"Month: {_month_label(mbp.month)}")
    lines.append(f"Paid: {'Yes' if mbp.paid else 'No'}")

    amt = _format_money(mbp.actual_payment_amount)
    if amt is not None:
        lines.append(f"Actual Amount: {amt}")

    portal = _account_portal_url(account)
    if portal is not None:
        lines.append(f"Portal: {portal}")
    
    return "\n".join(lines)

def _compute_payload_hash(
        *,
        summary: str,
        description: str,
        start_date: date,
        end_date: date,
        extended_properties: Dict[str, str],
 ) -> str:
    canonical =  {
        "summary": summary,
        "description": description,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        # sort_keys=True in dumps will also sort these, but we keep it explicit here to ensure the hash is consistent regardless of any future changes to the dumping logic
        "extended_properties": dict(sorted(extended_properties.items())),
    }

    serialized = json.dumps(
        canonical,
        sort_keys=True,
        separators=(",", ":"), # remove whitespace for more compact and deterministic output
        ensure_ascii=False, # allow unicode for readability (e.g. in account/household names)
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()