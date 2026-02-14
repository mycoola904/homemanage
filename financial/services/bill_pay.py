from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from django.db.models import Case, IntegerField, QuerySet, When
from django.db.models.functions import Lower
from django.urls import reverse

from financial.models import Account, AccountType, MonthlyBillPayment
from financial.services.formatters import format_usd

LIABILITY_TYPES = [AccountType.CREDIT_CARD, AccountType.LOAN, AccountType.OTHER]


@dataclass(frozen=True, slots=True)
class BillPayRow:
    account_id: str
    name: str
    institution: str
    payment_due_day: int | None
    payment_due_day_display: str
    minimum_amount_due_display: str
    online_access_url: str
    actual_payment_amount_display: str
    actual_payment_amount_value: str
    paid: bool
    paid_label: str
    edit_url: str
    save_url: str
    month_param: str


def normalize_month(value: date | None) -> date:
    if value is None:
        today = date.today()
        return date(today.year, today.month, 1)
    return date(value.year, value.month, 1)


def parse_month_param(month_param: str | None) -> date:
    if not month_param:
        return normalize_month(None)
    try:
        year_str, month_str = month_param.split("-", 1)
        year = int(year_str)
        month = int(month_str)
        return date(year, month, 1)
    except (TypeError, ValueError):
        raise ValueError("Invalid month format. Use YYYY-MM.")


def month_to_query_value(month: date) -> str:
    month = normalize_month(month)
    return f"{month.year:04d}-{month.month:02d}"


def liability_accounts_for_household(household) -> QuerySet[Account]:
    base = Account.objects.for_household(household).filter(account_type__in=LIABILITY_TYPES)
    return base.annotate(
        _due_day_null_order=Case(
            When(payment_due_day__isnull=True, then=1),
            default=0,
            output_field=IntegerField(),
        )
    ).order_by("_due_day_null_order", "payment_due_day", Lower("name"), "id")


def monthly_payments_by_account(accounts: QuerySet[Account], month: date) -> dict[str, MonthlyBillPayment]:
    account_ids = [account.id for account in accounts]
    if not account_ids:
        return {}
    payments = MonthlyBillPayment.objects.filter(account_id__in=account_ids, month=normalize_month(month))
    return {str(payment.account_id): payment for payment in payments}


def build_bill_pay_rows(accounts: QuerySet[Account], month: date) -> list[BillPayRow]:
    normalized_month = normalize_month(month)
    month_param = month_to_query_value(normalized_month)
    payments_map = monthly_payments_by_account(accounts, normalized_month)
    rows: list[BillPayRow] = []

    for account in accounts:
        payment = payments_map.get(str(account.id))
        amount = payment.actual_payment_amount if payment else None
        paid = bool(payment.paid) if payment else False

        rows.append(
            BillPayRow(
                account_id=str(account.id),
                name=account.name,
                institution=account.institution,
                payment_due_day=account.payment_due_day,
                payment_due_day_display=str(account.payment_due_day) if account.payment_due_day is not None else "—",
                minimum_amount_due_display=format_usd(account.minimum_amount_due) if account.minimum_amount_due is not None else "—",
                online_access_url=account.online_access_url or "",
                actual_payment_amount_display=format_usd(amount) if amount is not None else "—",
                actual_payment_amount_value=f"{amount:.2f}" if amount is not None else "",
                paid=paid,
                paid_label="Paid" if paid else "Not paid",
                edit_url=f"{reverse('financial:bill-pay-row', args=[account.id])}?month={month_param}",
                save_url=f"{reverse('financial:bill-pay-row', args=[account.id])}?month={month_param}",
                month_param=month_param,
            )
        )

    return rows


def build_bill_pay_row(*, account: Account, month: date) -> BillPayRow:
    rows = build_bill_pay_rows(Account.objects.filter(pk=account.pk), month)
    return rows[0]


def get_or_initialize_monthly_payment(*, account: Account, month: date) -> MonthlyBillPayment:
    normalized_month = normalize_month(month)
    existing = MonthlyBillPayment.objects.filter(account=account, month=normalized_month).first()
    if existing is not None:
        return existing
    return MonthlyBillPayment(account=account, month=normalized_month)


def upsert_monthly_payment(*, account: Account, month: date, actual_payment_amount: Decimal | None, paid: bool) -> MonthlyBillPayment:
    normalized_month = normalize_month(month)
    payment, _created = MonthlyBillPayment.objects.get_or_create(
        account=account,
        month=normalized_month,
        defaults={
            "actual_payment_amount": actual_payment_amount,
            "paid": paid,
        },
    )
    if payment.actual_payment_amount != actual_payment_amount or payment.paid != paid:
        payment.actual_payment_amount = actual_payment_amount
        payment.paid = paid
        payment.save(update_fields=["actual_payment_amount", "paid", "updated_at"])
    return payment
