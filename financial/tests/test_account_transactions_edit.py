from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import Account, AccountStatus, AccountType, Transaction, TransactionType

User = get_user_model()


class AccountTransactionsEditTests(TestCase):
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
        self.transaction = Transaction.objects.create(
            account=self.account,
            posted_on=date(2026, 2, 10),
            description="Groceries",
            transaction_type=TransactionType.EXPENSE,
            amount="12.50",
        )
        self.edit_url = reverse(
            "financial:account-transactions-edit",
            args=[self.account.id, self.transaction.id],
        )
        self.body_url = reverse("financial:account-transactions-body", args=[self.account.id])

    def test_get_edit_form_fragment(self):
        self.client.force_login(self.user)
        response = self.client.get(self.edit_url, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn("transaction_form", body)
        self.assertIn("Groceries", body)
        self.assertIn(self.body_url, body)

    def test_post_valid_updates_transaction_and_returns_body(self):
        self.client.force_login(self.user)
        payload = {
            "posted_on": date(2026, 2, 12),
            "description": "Paycheck",
            "transaction_type": TransactionType.DEPOSIT,
            "amount": "250.00",
            "notes": "",
        }
        response = self.client.post(self.edit_url, payload, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.description, "Paycheck")
        self.assertEqual(self.transaction.transaction_type, TransactionType.DEPOSIT)
        body = response.content.decode()
        self.assertIn("Paycheck", body)
        self.assertIn("+$250.00", body)
        self.assertNotIn("transaction_form", body)

    def test_post_invalid_returns_422_and_form(self):
        self.client.force_login(self.user)
        payload = {
            "posted_on": "",
            "description": "",
            "transaction_type": "",
            "amount": "",
            "notes": "",
        }
        response = self.client.post(self.edit_url, payload, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 422)
        body = response.content.decode()
        self.assertIn("transaction_form", body)
        self.assertIn("This field is required", body)
