import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import Account, AccountStatus, AccountType, Household, HouseholdMember

User = get_user_model()


class AccountTransactionsMissingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alex", "alex@example.com", "pass-1234")
        self.other_user = User.objects.create_user("jamie", "jamie@example.com", "pass-9876")
        self.household = Household.objects.create(name="Alex Household", slug="alex-household", created_by=self.user)
        HouseholdMember.objects.create(
            household=self.household,
            user=self.user,
            role=HouseholdMember.Role.OWNER,
            is_primary=True,
        )
        other_household = Household.objects.create(name="Jamie Household", slug="jamie-household", created_by=self.other_user)
        HouseholdMember.objects.create(
            household=other_household,
            user=self.other_user,
            role=HouseholdMember.Role.OWNER,
            is_primary=True,
        )
        self.account = Account.objects.create(
            user=self.user,
            household=self.household,
            name="Civic Checking",
            institution="Civic",
            account_type=AccountType.CHECKING,
            status=AccountStatus.ACTIVE,
            current_balance=2450.75,
        )
        self.body_url = reverse("financial:account-transactions-body", args=[self.account.id])
        self.new_url = reverse("financial:account-transactions-new", args=[self.account.id])
        self.edit_url = reverse(
            "financial:account-transactions-edit",
            args=[self.account.id, uuid.uuid4()],
        )

    def test_unowned_account_returns_missing_fragment(self):
        self.client.force_login(self.other_user)
        response = self.client.get(self.body_url, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertIn("not found", response.content.decode().lower())

        response = self.client.get(self.new_url, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertIn("not found", response.content.decode().lower())

        response = self.client.post(self.new_url, {"description": "Test"}, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertIn("not found", response.content.decode().lower())

        response = self.client.get(self.edit_url, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertIn("not found", response.content.decode().lower())

    def test_missing_account_returns_missing_fragment(self):
        self.client.force_login(self.user)
        missing_id = uuid.uuid4()
        body_url = reverse("financial:account-transactions-body", args=[missing_id])
        new_url = reverse("financial:account-transactions-new", args=[missing_id])
        edit_url = reverse(
            "financial:account-transactions-edit",
            args=[missing_id, uuid.uuid4()],
        )

        response = self.client.get(body_url, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertIn("not found", response.content.decode().lower())

        response = self.client.get(new_url, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertIn("not found", response.content.decode().lower())

        response = self.client.post(new_url, {"description": "Test"}, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertIn("not found", response.content.decode().lower())

        response = self.client.get(edit_url, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertIn("not found", response.content.decode().lower())
