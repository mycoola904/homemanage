from decimal import Decimal
from datetime import date

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from financial.models import (
    Account,
    AccountStatus,
    AccountType,
    Household,
    HouseholdMember,
    Transaction,
    TransactionType,
)


class Command(BaseCommand):
    help = "Seed deterministic households with sample finance data"

    def handle(self, *args, **options):
        user_model = get_user_model()
        user, _ = user_model.objects.get_or_create(
            username="seed-owner",
            defaults={"email": "seed-owner@example.com"},
        )

        our_household, _ = Household.objects.get_or_create(
            name="Our Household",
            defaults={"slug": "our-household", "created_by": user},
        )
        inlaw_household, _ = Household.objects.get_or_create(
            name="Mother-in-law Household",
            defaults={"slug": "mother-in-law-household", "created_by": user},
        )

        HouseholdMember.objects.get_or_create(
            household=our_household,
            user=user,
            defaults={"role": HouseholdMember.Role.OWNER, "is_primary": True},
        )
        HouseholdMember.objects.get_or_create(
            household=inlaw_household,
            user=user,
            defaults={"role": HouseholdMember.Role.OWNER, "is_primary": False},
        )

        our_checking, _ = Account.objects.get_or_create(
            household=our_household,
            user=user,
            name="Our Checking",
            defaults={
                "institution": "Civic",
                "account_type": AccountType.CHECKING,
                "status": AccountStatus.ACTIVE,
                "current_balance": Decimal("2500.00"),
            },
        )

        inlaw_savings, _ = Account.objects.get_or_create(
            household=inlaw_household,
            user=user,
            name="Inlaw Savings",
            defaults={
                "institution": "Metro",
                "account_type": AccountType.SAVINGS,
                "status": AccountStatus.ACTIVE,
                "current_balance": Decimal("8200.00"),
            },
        )

        Transaction.objects.get_or_create(
            account=our_checking,
            household=our_household,
            posted_on=date(2026, 2, 1),
            description="Payroll",
            transaction_type=TransactionType.DEPOSIT,
            defaults={"amount": Decimal("1500.00")},
        )
        Transaction.objects.get_or_create(
            account=inlaw_savings,
            household=inlaw_household,
            posted_on=date(2026, 2, 2),
            description="Interest",
            transaction_type=TransactionType.DEPOSIT,
            defaults={"amount": Decimal("25.00")},
        )

        self.stdout.write(self.style.SUCCESS("Seeded households and deterministic finance data."))
