from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import Account, AccountStatus, AccountType, Household, HouseholdMember


User = get_user_model()


class HouseholdObjectGuardsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("guarduser", "guard@example.com", "pass-1234")
        self.household_a = Household.objects.create(name="Guard A", slug="guard-a", created_by=self.user)
        self.household_b = Household.objects.create(name="Guard B", slug="guard-b", created_by=self.user)
        HouseholdMember.objects.create(household=self.household_a, user=self.user, role=HouseholdMember.Role.OWNER, is_primary=True)
        HouseholdMember.objects.create(household=self.household_b, user=self.user, role=HouseholdMember.Role.OWNER, is_primary=False)

        self.account_a = Account.objects.create(
            user=self.user,
            household=self.household_a,
            name="Guard A Checking",
            account_type=AccountType.CHECKING,
            status=AccountStatus.ACTIVE,
            current_balance=Decimal("100.00"),
        )
        self.account_b = Account.objects.create(
            user=self.user,
            household=self.household_b,
            name="Guard B Checking",
            account_type=AccountType.CHECKING,
            status=AccountStatus.ACTIVE,
            current_balance=Decimal("200.00"),
        )

    def test_cross_household_account_detail_returns_404(self):
        self.client.force_login(self.user)
        session = self.client.session
        session["current_household_id"] = str(self.household_a.id)
        session.save()

        response = self.client.get(reverse("financial:accounts-detail", args=[self.account_b.id]))

        self.assertEqual(response.status_code, 404)

    def test_cross_household_account_preview_returns_404(self):
        self.client.force_login(self.user)
        session = self.client.session
        session["current_household_id"] = str(self.household_a.id)
        session.save()

        response = self.client.get(reverse("financial:accounts-preview", args=[self.account_b.id]), HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 404)
