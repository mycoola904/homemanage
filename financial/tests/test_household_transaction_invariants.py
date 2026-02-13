from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import Account, AccountStatus, AccountType, Household, HouseholdMember, Transaction, TransactionType


User = get_user_model()


class HouseholdTransactionInvariantTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("invariant", "invariant@example.com", "pass-1234")
        self.household_a = Household.objects.create(name="Invariant A", slug="invariant-a", created_by=self.user)
        self.household_b = Household.objects.create(name="Invariant B", slug="invariant-b", created_by=self.user)
        HouseholdMember.objects.create(household=self.household_a, user=self.user, role=HouseholdMember.Role.OWNER, is_primary=True)
        HouseholdMember.objects.create(household=self.household_b, user=self.user, role=HouseholdMember.Role.OWNER, is_primary=False)

        self.account_a = Account.objects.create(
            user=self.user,
            household=self.household_a,
            name="Invariant A Checking",
            account_type=AccountType.CHECKING,
            status=AccountStatus.ACTIVE,
            current_balance=Decimal("100.00"),
        )
        self.account_b = Account.objects.create(
            user=self.user,
            household=self.household_b,
            name="Invariant B Checking",
            account_type=AccountType.CHECKING,
            status=AccountStatus.ACTIVE,
            current_balance=Decimal("200.00"),
        )

    def test_transaction_household_is_derived_from_selected_account(self):
        transaction = Transaction.objects.create(
            account=self.account_a,
            household=self.household_b,
            posted_on=date(2026, 2, 10),
            description="Invariant check",
            transaction_type=TransactionType.EXPENSE,
            amount=Decimal("15.00"),
        )

        self.assertEqual(transaction.household_id, self.account_a.household_id)

    def test_transaction_edit_rejects_cross_household_account_selection(self):
        transaction = Transaction.objects.create(
            account=self.account_a,
            household=self.household_a,
            posted_on=date(2026, 2, 10),
            description="Before edit",
            transaction_type=TransactionType.EXPENSE,
            amount=Decimal("15.00"),
        )

        self.client.force_login(self.user)
        session = self.client.session
        session["current_household_id"] = str(self.household_a.id)
        session.save()

        response = self.client.post(
            reverse("financial:account-transactions-edit", args=[self.account_a.id, transaction.id]),
            {
                "account": str(self.account_b.id),
                "posted_on": "2026-02-10",
                "description": "Attempted cross-household edit",
                "transaction_type": "expense",
                "amount": "20.00",
            },
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 422)
        self.assertContains(response, "Select a valid choice", status_code=422)
        transaction.refresh_from_db()
        self.assertEqual(transaction.account_id, self.account_a.id)
        self.assertEqual(transaction.household_id, self.household_a.id)
