from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.db import transaction

from financial.models import Account, AccountStatus, AccountType


REQUIRED_HEADERS = [
    "name",
    "institution",
    "account_type",
    "account_number",
    "routing_number",
    "interest_rate",
    "status",
    "current_balance",
    "credit_limit_or_principal",
    "statement_close_date",
    "payment_due_day",
    "minimum_amount_due",
    "online_access_url",
    "notes",
]

MAX_IMPORT_ROWS = 1000
CANONICAL_ACCOUNT_TYPES = {choice[0] for choice in AccountType.choices}
CANONICAL_STATUSES = {choice[0] for choice in AccountStatus.choices}


class AccountImportValidationError(Exception):
    def __init__(self, errors: list[str]):
        super().__init__("Account import validation failed.")
        self.errors = errors


@dataclass(frozen=True)
class AccountImportResult:
    total_rows: int
    imported_rows: int
    rejected_rows: int
    errors: list[str]


def _to_optional_decimal(value: str) -> Decimal | None:
    value = (value or "").strip()
    if not value:
        return None
    return Decimal(value)


def _to_decimal_or_zero(value: str) -> Decimal:
    value = (value or "").strip()
    if not value:
        return Decimal("0")
    return Decimal(value)


def _to_optional_int(value: str) -> int | None:
    value = (value or "").strip()
    if not value:
        return None
    return int(value)


def _to_optional_date(value: str) -> date | None:
    value = (value or "").strip()
    if not value:
        return None
    return date.fromisoformat(value)


def _validate_online_access_url(value: str) -> None:
    value = (value or "").strip()
    if not value:
        return
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("online_access_url must be an absolute http/https URL.")


def parse_account_import_rows(uploaded_file) -> list[dict[str, str]]:
    uploaded_file.seek(0)
    decoded = uploaded_file.read().decode("utf-8-sig")
    buffer = io.StringIO(decoded)
    reader = csv.DictReader(buffer)
    if reader.fieldnames is None:
        raise AccountImportValidationError(["Import file must include a header row."])

    actual_headers = [header.strip() for header in reader.fieldnames]
    if actual_headers != REQUIRED_HEADERS:
        missing_headers = [header for header in REQUIRED_HEADERS if header not in actual_headers]
        unexpected_headers = [header for header in actual_headers if header not in REQUIRED_HEADERS]
        details: list[str] = []
        if missing_headers:
            details.append(f"Missing required headers: {', '.join(missing_headers)}")
        if unexpected_headers:
            details.append(f"Unexpected headers: {', '.join(unexpected_headers)}")
        raise AccountImportValidationError([
            "CSV headers must exactly match the required template order.",
            *details,
        ])

    parsed_rows: list[dict[str, str]] = []
    for row in reader:
        parsed_rows.append({key.strip(): (value or "").strip() for key, value in row.items()})
    return parsed_rows


def import_accounts_from_csv(*, uploaded_file, user, household) -> AccountImportResult:
    rows = parse_account_import_rows(uploaded_file)
    if not rows:
        raise AccountImportValidationError(["Import file has no data rows."])
    if len(rows) > MAX_IMPORT_ROWS:
        raise AccountImportValidationError([
            f"Import file exceeds the maximum of {MAX_IMPORT_ROWS} data rows.",
        ])

    errors: list[str] = []
    existing_household_names = {
        name.casefold()
        for name in Account.objects.filter(household=household).values_list("name", flat=True)
    }
    seen_names: set[str] = set()

    pending_accounts: list[Account] = []
    for index, row in enumerate(rows, start=1):
        try:
            name = row["name"].strip()
            if not name:
                raise ValueError("name is required.")

            account_type = row["account_type"].strip()
            if account_type not in CANONICAL_ACCOUNT_TYPES:
                raise ValueError(
                    "account_type must use canonical values: "
                    f"{', '.join(sorted(CANONICAL_ACCOUNT_TYPES))}."
                )

            status = row["status"].strip() or AccountStatus.ACTIVE
            if status not in CANONICAL_STATUSES:
                raise ValueError(
                    "status must use canonical values: "
                    f"{', '.join(sorted(CANONICAL_STATUSES))}."
                )

            normalized_name = name.casefold()
            if normalized_name in existing_household_names:
                raise ValueError("duplicate account name already exists in active household.")
            if normalized_name in seen_names:
                raise ValueError("duplicate account name appears more than once in this upload.")

            payment_due_day = _to_optional_int(row["payment_due_day"])
            if payment_due_day is not None and not 1 <= payment_due_day <= 31:
                raise ValueError("payment_due_day must be between 1 and 31.")

            statement_close_date = _to_optional_date(row["statement_close_date"])

            _validate_online_access_url(row["online_access_url"])

            account = Account(
                user=user,
                household=household,
                name=name,
                institution=row["institution"],
                account_type=account_type,
                account_number=row["account_number"] or None,
                routing_number=row["routing_number"] or None,
                interest_rate=_to_optional_decimal(row["interest_rate"]),
                status=status,
                current_balance=_to_decimal_or_zero(row["current_balance"]),
                credit_limit_or_principal=_to_optional_decimal(row["credit_limit_or_principal"]),
                statement_close_date=statement_close_date,
                payment_due_day=payment_due_day,
                minimum_amount_due=_to_optional_decimal(row["minimum_amount_due"]),
                online_access_url=row["online_access_url"],
                notes=row["notes"],
            )
            account.full_clean()
            pending_accounts.append(account)
            seen_names.add(normalized_name)
        except (ValidationError, ValueError) as exc:
            errors.append(f"Row {index}: {exc}")

    if errors:
        raise AccountImportValidationError(errors)

    imported_rows = 0
    with transaction.atomic():
        for account in pending_accounts:
            account.save()
            imported_rows += 1

    return AccountImportResult(
        total_rows=len(rows),
        imported_rows=imported_rows,
        rejected_rows=0,
        errors=[],
    )
