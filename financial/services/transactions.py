from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

from django.urls import NoReverseMatch, reverse

from financial.models import Transaction

from .formatters import format_usd


def format_signed_amount(amount) -> str:
    sign = "-" if amount < 0 else "+"
    return f"{sign}{format_usd(abs(amount))}"


def format_posted_on(posted_on) -> str:
    return posted_on.strftime("%b %d, %Y").replace(" 0", " ")


def _safe_reverse(route: str, *, args: list[str]) -> str:
    try:
        return reverse(route, args=args)
    except NoReverseMatch:
        return "#"


@dataclass(frozen=True, slots=True)
class TransactionRow:
    id: str
    posted_on_display: str
    description: str
    amount_display: str
    category_label: Optional[str]
    edit_url: str

    @classmethod
    def from_transaction(cls, transaction: Transaction) -> "TransactionRow":
        return cls(
            id=str(transaction.id),
            posted_on_display=format_posted_on(transaction.posted_on),
            description=transaction.description,
            amount_display=format_signed_amount(transaction.amount),
            category_label=transaction.category.name if transaction.category else None,
            edit_url=_safe_reverse(
                "financial:account-transactions-edit",
                args=[str(transaction.account_id), str(transaction.id)],
            ),
        )


def serialize_transaction_rows(transactions: Iterable[Transaction]) -> List[TransactionRow]:
    """Convert queryset into deterministic row payloads for templates."""

    return [TransactionRow.from_transaction(transaction) for transaction in transactions]
