from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP


def to_decimal(value: Decimal | float | int | str) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def format_usd(value: Decimal | float | int | str) -> str:
    """Format numeric input as USD currency with deterministic rounding."""

    amount = to_decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    sign = "-" if amount < 0 else ""
    absolute_value = abs(amount)
    return f"{sign}${absolute_value:,.2f}"
