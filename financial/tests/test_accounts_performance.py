import time
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import Account, AccountStatus, AccountType
from households.models import Household, HouseholdMember


User = get_user_model()


class AccountsPerformanceTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="perf-user",
            email="perf@example.com",
            password="perf-pass-123",
        )
        self.household = Household.objects.create(
            name="Perf Household",
            slug="perf-household",
            created_by=self.user,
        )
        HouseholdMember.objects.create(
            household=self.household,
            user=self.user,
            role=HouseholdMember.Role.OWNER,
            is_primary=True,
        )
        self.url = reverse("financial:accounts-index")

    def test_accounts_index_renders_under_two_seconds(self):
        bulk_accounts = []
        for idx in range(40):
            bulk_accounts.append(
                Account(
                    user=self.user,
                    household=self.household,
                    name=f"Load Test Account {idx:03d}",
                    institution="Perf Bank",
                    account_type=AccountType.CHECKING if idx % 2 == 0 else AccountType.SAVINGS,
                    status=AccountStatus.ACTIVE,
                    current_balance=Decimal("100.00") + Decimal(idx),
                )
            )
        Account.objects.bulk_create(bulk_accounts)

        self.client.force_login(self.user)
        start = time.perf_counter()
        response = self.client.get(self.url)
        duration = time.perf_counter() - start

        self.assertEqual(response.status_code, 200)
        self.assertLess(
            duration,
            2.0,
            msg=f"/accounts/ took {duration:.3f}s which exceeds the 2s budget",
        )
