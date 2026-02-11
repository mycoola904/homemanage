from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import Account, AccountStatus, AccountType, Category, TransactionType

User = get_user_model()


class InlineCategoryErrorTests(TestCase):
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
        self.category_url = reverse(
            "financial:account-transactions-category-new",
            args=[self.account.id],
        )

    def test_invalid_category_returns_400_with_form_errors(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.category_url,
            {
                "name": "",
                "posted_on": date(2026, 2, 11),
                "description": "Coffee",
                "transaction_type": TransactionType.EXPENSE,
                "amount": "4.50",
            },
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 400)
        body = response.content.decode()
        self.assertIn("Enter a category name.", body)
        self.assertIn("transaction_form", body)

    def test_duplicate_category_returns_400(self):
        Category.objects.create(user=self.user, name="Dining")
        self.client.force_login(self.user)
        response = self.client.post(
            self.category_url,
            {
                "name": "dining",
                "posted_on": date(2026, 2, 11),
                "description": "Lunch",
                "transaction_type": TransactionType.EXPENSE,
                "amount": "12.00",
            },
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("already have a category", response.content.decode())
