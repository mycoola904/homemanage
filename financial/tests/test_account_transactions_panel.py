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


class AccountTransactionsPanelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alex", "alex@example.com", "pass-1234")
        self.account = Account.objects.create(
            user=self.user,
            name="Civic Checking",
            institution="Civic",
            account_type=AccountType.CHECKING,
            status=AccountStatus.ACTIVE,
            current_balance=2450.75,
        )
        self.detail_url = reverse("financial:accounts-detail", args=[self.account.id])
        self.body_url = reverse("financial:account-transactions-body", args=[self.account.id])

    def test_empty_state_renders_in_panel_body(self):
        self.client.force_login(self.user)
        response = self.client.get(self.body_url, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No transactions yet")
        self.assertContains(response, "account_transactions_body")

    def test_transactions_render_in_deterministic_order(self):
        Transaction.objects.create(
            account=self.account,
            posted_on=date(2026, 2, 10),
            description="Grocery Run",
            direction=TransactionDirection.DEBIT,
            amount="45.55",
        )
        Transaction.objects.create(
            account=self.account,
            posted_on=date(2026, 2, 11),
            description="Paycheck",
            direction=TransactionDirection.CREDIT,
            amount="1250.00",
        )

        self.client.force_login(self.user)
        response = self.client.get(self.body_url, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn("Paycheck", body)
        self.assertIn("Grocery Run", body)
        self.assertLess(body.find("Paycheck"), body.find("Grocery Run"))
        self.assertIn("+$1,250.00", body)
        self.assertIn("-$45.55", body)
