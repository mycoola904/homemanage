from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import Account, AccountStatus, AccountType
from households.models import Household, HouseholdMember


User = get_user_model()


class HouseholdFinanceRoutingTests(TestCase):
    def test_household_finance_root_route_is_accessible(self):
        user = User.objects.create_user("financeuser", "financeuser@example.com", "pass-1234")
        household = Household.objects.create(name="Finance Household", slug="finance-household", created_by=user)
        HouseholdMember.objects.create(
            household=household,
            user=user,
            role=HouseholdMember.Role.OWNER,
            is_primary=True,
        )
        Account.objects.create(
            user=user,
            household=household,
            name="Routing Checking",
            account_type=AccountType.CHECKING,
            status=AccountStatus.ACTIVE,
            current_balance=Decimal("100.00"),
        )

        self.client.force_login(user)
        response = self.client.get(reverse("financial:accounts-index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Accounts")
        self.assertTrue(reverse("financial:accounts-index").startswith("/household/finance/"))
