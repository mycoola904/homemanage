import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import Account, AccountStatus, AccountType

User = get_user_model()


class AccountTransactionsMissingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alex", "alex@example.com", "pass-1234")
        self.other_user = User.objects.create_user("jamie", "jamie@example.com", "pass-9876")
        self.account = Account.objects.create(
            user=self.user,
            name="Civic Checking",
            institution="Civic",
            account_type=AccountType.CHECKING,
            status=AccountStatus.ACTIVE,
            current_balance=2450.75,
        )
        self.body_url = reverse("financial:account-transactions-body", args=[self.account.id])
        self.new_url = reverse("financial:account-transactions-new", args=[self.account.id])

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

    def test_missing_account_returns_missing_fragment(self):
        self.client.force_login(self.user)
        missing_id = uuid.uuid4()
        body_url = reverse("financial:account-transactions-body", args=[missing_id])
        new_url = reverse("financial:account-transactions-new", args=[missing_id])

        response = self.client.get(body_url, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertIn("not found", response.content.decode().lower())

        response = self.client.get(new_url, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertIn("not found", response.content.decode().lower())

        response = self.client.post(new_url, {"description": "Test"}, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertIn("not found", response.content.decode().lower())
