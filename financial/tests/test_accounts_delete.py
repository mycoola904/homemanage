from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import Account, AccountStatus, AccountType
from households.models import Household, HouseholdMember

User = get_user_model()


class AccountDeleteTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alex", "alex@example.com", "pass-1234")
        self.household = Household.objects.create(name="Alex Household", slug="alex-household", created_by=self.user)
        HouseholdMember.objects.create(
            household=self.household,
            user=self.user,
            role=HouseholdMember.Role.OWNER,
            is_primary=True,
        )
        self.account = Account.objects.create(
            user=self.user,
            household=self.household,
            name="Loan Refi",
            institution="Metro",
            account_type=AccountType.LOAN,
            status=AccountStatus.ACTIVE,
            current_balance=15000,
        )
        self.confirm_url = reverse("financial:accounts-delete-confirm", args=[self.account.id])
        self.delete_url = reverse("financial:accounts-delete", args=[self.account.id])

    def test_confirm_fragment_renders(self):
        self.client.force_login(self.user)
        response = self.client.get(self.confirm_url, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Delete account", response.content.decode())

    def test_owner_can_delete_and_table_updates(self):
        self.client.force_login(self.user)
        response = self.client.post(self.delete_url, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Account.objects.filter(pk=self.account.pk).exists())
        body = response.content.decode()
        self.assertIn("Select Preview", body)
        self.assertNotIn("Loan Refi", body)

    def test_non_owner_gets_404(self):
        other = User.objects.create_user("jamie", "jamie@example.com", "pass-9876")
        other_household = Household.objects.create(name="Jamie Household", slug="jamie-household", created_by=other)
        HouseholdMember.objects.create(
            household=other_household,
            user=other,
            role=HouseholdMember.Role.OWNER,
            is_primary=True,
        )
        self.client.force_login(other)
        response = self.client.get(self.confirm_url, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 404)
