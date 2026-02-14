from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

from django.urls import NoReverseMatch, reverse

from financial.models import Account, AccountStatus

from .formatters import format_usd


STATUS_BADGE_CLASSES = {
    AccountStatus.ACTIVE: "badge badge-success",
    AccountStatus.CLOSED: "badge badge-neutral",
    AccountStatus.PENDING: "badge badge-warning",
}


def _safe_reverse(route: str, *, args: list[str]) -> str:
    try:
        return reverse(route, args=args)
    except NoReverseMatch:
        return "#"


@dataclass(frozen=True, slots=True)
class AccountSummaryRow:
    """Lightweight serializer consumed by the cotton table component."""

    id: str
    name: str
    institution: str
    account_type_value: str
    account_type_label: str
    online_access_url: str
    status_value: str
    status_label: str
    status_badge_class: str
    current_balance_display: str
    preview_url: str
    open_url: str
    edit_url: str
    delete_url: str

    @classmethod
    def from_account(cls, account: Account) -> "AccountSummaryRow":
        account_type_label_check = "CC" if account.account_type == "credit_card" else account.get_account_type_display()
        
        return cls(
            id=str(account.id),
            name=account.name,
            institution=account.institution,
            account_type_value=account.account_type,
            account_type_label=account_type_label_check,
            online_access_url=account.online_access_url or "",
            status_value=account.status,
            status_label=account.get_status_display(),
            status_badge_class=STATUS_BADGE_CLASSES.get(account.status, "badge"),
            current_balance_display=format_usd(account.current_balance),
            preview_url=_safe_reverse("financial:accounts-preview", args=[account.id]),
            open_url=_safe_reverse("financial:accounts-detail", args=[account.id]),
            edit_url=_safe_reverse("financial:accounts-edit", args=[account.id]),
            delete_url=_safe_reverse("financial:accounts-delete-confirm", args=[account.id]),
        )


def serialize_account_rows(accounts: Iterable[Account]) -> List[AccountSummaryRow]:
    """Convert queryset into deterministic cotton component payload."""

    return [AccountSummaryRow.from_account(account) for account in accounts]


@dataclass(frozen=True, slots=True)
class AccountPreviewDTO:
    id: str
    name: str
    institution: Optional[str]
    status_label: str
    status_badge_class: str
    current_balance_display: str
    credit_limit_display: Optional[str]
    has_credit_limit: bool
    statement_close_date_display: Optional[str]
    payment_due_day: Optional[int]
    notes: Optional[str]


def build_account_preview(account: Account) -> AccountPreviewDTO:
    credit_limit_display = (
        format_usd(account.credit_limit_or_principal)
        if account.credit_limit_or_principal is not None
        else None
    )
    if account.statement_close_date:
        statement_display = account.statement_close_date.strftime("%b %d, %Y").replace(" 0", " ")
    else:
        statement_display = None

    return AccountPreviewDTO(
        id=str(account.id),
        name=account.name,
        institution=account.institution,
        status_label=account.get_status_display(),
        status_badge_class=STATUS_BADGE_CLASSES.get(account.status, "badge"),
        current_balance_display=format_usd(account.current_balance),
        credit_limit_display=credit_limit_display,
        has_credit_limit=credit_limit_display is not None,
        statement_close_date_display=statement_display,
        payment_due_day=account.payment_due_day,
        notes=account.notes,
    )
