from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import (
    Account,
    AccountStatus,
    AccountType,
    Transaction,
    TransactionDirection,
)

User = get_user_model()


class AccountTransactionsAddTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alex", "alex@example.com", "pass-1234")
        self.account = Account.objects.create(
            user=self.user,
            name="Household Checking",
            institution="Civic",
            account_type=AccountType.CHECKING,
            status=AccountStatus.ACTIVE,
            current_balance=1000,
        )
        self.new_url = reverse("financial:account-transactions-new", args=[self.account.id])
        self.body_url = reverse("financial:account-transactions-body", args=[self.account.id])

    def test_get_new_form_fragment(self):
        self.client.force_login(self.user)
        response = self.client.get(self.new_url, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertIn("transaction_form", response.content.decode())
        self.assertIn("posted_on", response.content.decode())
        self.assertIn(self.body_url, response.content.decode())

    def test_post_valid_creates_transaction_and_returns_body(self):
        self.client.force_login(self.user)
        payload = {
            "posted_on": date(2026, 2, 11),
            "description": "Grocery Run",
            "direction": TransactionDirection.DEBIT,
            "amount": "32.50",
            "notes": "",
        }
        response = self.client.post(self.new_url, payload, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Transaction.objects.filter(account=self.account).count(), 1)
        body = response.content.decode()
        self.assertIn("Grocery Run", body)
        self.assertIn("-$32.50", body)
        self.assertNotIn("transaction_form", body)

    def test_post_invalid_returns_422_and_form(self):
        self.client.force_login(self.user)
        payload = {
            "posted_on": "",
            "description": "",
            "direction": "",
            "amount": "",
            "notes": "",
        }
        response = self.client.post(self.new_url, payload, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 422)
        body = response.content.decode()
        self.assertIn("transaction_form", body)
        self.assertIn("This field is required", body)

    def test_cancel_path_returns_body_fragment(self):
        self.client.force_login(self.user)
        response = self.client.get(self.body_url, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertIn("account_transactions_body", response.content.decode())
