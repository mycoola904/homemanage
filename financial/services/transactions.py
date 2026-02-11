from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from financial.models import Transaction, TransactionDirection

from .formatters import format_usd


def format_signed_amount(amount, direction: str) -> str:
    sign = "-" if direction == TransactionDirection.DEBIT else "+"
    return f"{sign}{format_usd(amount)}"


def format_posted_on(posted_on) -> str:
    return posted_on.strftime("%b %d, %Y").replace(" 0", " ")


@dataclass(frozen=True, slots=True)
class TransactionRow:
    id: str
    posted_on_display: str
    description: str
    amount_display: str

    @classmethod
    def from_transaction(cls, transaction: Transaction) -> "TransactionRow":
        return cls(
            id=str(transaction.id),
            posted_on_display=format_posted_on(transaction.posted_on),
            description=transaction.description,
            amount_display=format_signed_amount(transaction.amount, transaction.direction),
        )


def serialize_transaction_rows(transactions: Iterable[Transaction]) -> List[TransactionRow]:
    """Convert queryset into deterministic row payloads for templates."""

    return [TransactionRow.from_transaction(transaction) for transaction in transactions]
