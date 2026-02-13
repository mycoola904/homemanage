from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import Account, AccountStatus, AccountType, Transaction, TransactionType
from households.models import Household, HouseholdMember


User = get_user_model()


class HouseholdTransactionsScopeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("txscope", "txscope@example.com", "pass-1234")
        self.household_a = Household.objects.create(name="TX Scope A", slug="tx-scope-a", created_by=self.user)
        self.household_b = Household.objects.create(name="TX Scope B", slug="tx-scope-b", created_by=self.user)
        HouseholdMember.objects.create(household=self.household_a, user=self.user, role=HouseholdMember.Role.OWNER, is_primary=True)
        HouseholdMember.objects.create(household=self.household_b, user=self.user, role=HouseholdMember.Role.OWNER, is_primary=False)

        self.account_a = Account.objects.create(
            user=self.user,
            household=self.household_a,
            name="A Checking",
            account_type=AccountType.CHECKING,
            status=AccountStatus.ACTIVE,
            current_balance=Decimal("100.00"),
        )
        self.account_b = Account.objects.create(
            user=self.user,
            household=self.household_b,
            name="B Checking",
            account_type=AccountType.CHECKING,
            status=AccountStatus.ACTIVE,
            current_balance=Decimal("200.00"),
        )
        Transaction.objects.create(
            account=self.account_a,
            household=self.household_a,
            posted_on=date(2026, 2, 11),
            description="A Household Transaction",
            transaction_type=TransactionType.EXPENSE,
            amount=Decimal("10.00"),
        )
        Transaction.objects.create(
            account=self.account_b,
            household=self.household_b,
            posted_on=date(2026, 2, 12),
            description="B Household Transaction",
            transaction_type=TransactionType.EXPENSE,
            amount=Decimal("11.00"),
        )

    def test_transactions_body_shows_only_active_household_data(self):
        self.client.force_login(self.user)
        session = self.client.session
        session["current_household_id"] = str(self.household_a.id)
        session.save()

        response = self.client.get(reverse("financial:account-transactions-body", args=[self.account_a.id]), HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A Household Transaction")
        self.assertNotContains(response, "B Household Transaction", status_code=200)

    def test_cross_household_transaction_body_returns_missing_fragment(self):
        self.client.force_login(self.user)
        session = self.client.session
        session["current_household_id"] = str(self.household_a.id)
        session.save()

        response = self.client.get(reverse("financial:account-transactions-body", args=[self.account_b.id]), HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertIn("not found", response.content.decode().lower())
