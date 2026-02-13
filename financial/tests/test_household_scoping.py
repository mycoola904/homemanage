from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import Account, AccountStatus, AccountType
from households.models import Household, HouseholdMember


User = get_user_model()


class HouseholdScopingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("scopeuser", "scope@example.com", "pass-1234")
        self.household_a = Household.objects.create(name="Scope A", slug="scope-a", created_by=self.user)
        self.household_b = Household.objects.create(name="Scope B", slug="scope-b", created_by=self.user)
        HouseholdMember.objects.create(household=self.household_a, user=self.user, role=HouseholdMember.Role.OWNER, is_primary=True)
        HouseholdMember.objects.create(household=self.household_b, user=self.user, role=HouseholdMember.Role.OWNER, is_primary=False)

        self.a_account = Account.objects.create(
            user=self.user,
            household=self.household_a,
            name="A Checking",
            account_type=AccountType.CHECKING,
            status=AccountStatus.ACTIVE,
            current_balance=100,
        )
        self.b_account = Account.objects.create(
            user=self.user,
            household=self.household_b,
            name="B Checking",
            account_type=AccountType.CHECKING,
            status=AccountStatus.ACTIVE,
            current_balance=200,
        )

    def test_accounts_index_shows_only_active_household_rows(self):
        self.client.force_login(self.user)
        session = self.client.session
        session["current_household_id"] = str(self.household_a.id)
        session.save()

        response = self.client.get(reverse("financial:accounts-index"))

        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn("A Checking", body)
        self.assertNotIn("B Checking", body)

    def test_cross_household_preview_returns_404(self):
        self.client.force_login(self.user)
        session = self.client.session
        session["current_household_id"] = str(self.household_a.id)
        session.save()

        response = self.client.get(reverse("financial:accounts-preview", args=[self.b_account.id]))

        self.assertEqual(response.status_code, 404)
