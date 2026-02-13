from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import Account, AccountStatus, AccountType
from households.models import Household, HouseholdMember


User = get_user_model()


class HouseholdSwitchingContextResetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("switchctx", "switchctx@example.com", "pass-1234")
        self.household_a = Household.objects.create(name="Switch A", slug="switch-a", created_by=self.user)
        self.household_b = Household.objects.create(name="Switch B", slug="switch-b", created_by=self.user)
        HouseholdMember.objects.create(household=self.household_a, user=self.user, role=HouseholdMember.Role.OWNER, is_primary=True)
        HouseholdMember.objects.create(household=self.household_b, user=self.user, role=HouseholdMember.Role.OWNER, is_primary=False)

        Account.objects.create(
            user=self.user,
            household=self.household_a,
            name="A Account",
            account_type=AccountType.CHECKING,
            status=AccountStatus.ACTIVE,
            current_balance=Decimal("100.00"),
        )
        Account.objects.create(
            user=self.user,
            household=self.household_b,
            name="B Account",
            account_type=AccountType.CHECKING,
            status=AccountStatus.ACTIVE,
            current_balance=Decimal("200.00"),
        )

    def test_finance_context_resets_after_household_switch(self):
        self.client.force_login(self.user)

        session = self.client.session
        session["current_household_id"] = str(self.household_a.id)
        session.save()

        response_before = self.client.get(reverse("financial:accounts-index"))
        self.assertContains(response_before, "A Account")
        self.assertNotContains(response_before, "B Account", status_code=200)

        switch_response = self.client.post(reverse("household:switch"), {"household_id": str(self.household_b.id)})
        self.assertEqual(switch_response.status_code, 302)

        response_after = self.client.get(reverse("financial:accounts-index"))
        self.assertContains(response_after, "B Account")
        self.assertNotContains(response_after, "A Account", status_code=200)
