from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, Optional
import calendar

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
    description = ""
    payload_hash = ""

    return BillPayEventSpec(
        summary=summary,
        description=description,
        start_date=start_date,
        end_date=end_date,
        extended_properties=extended_properties,
        payload_hash=payload_hash,
    )