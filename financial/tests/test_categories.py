from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.forms import CategoryForm
from financial.models import Account, AccountStatus, AccountType, Category, TransactionType

User = get_user_model()


class CategoryFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alex", "alex@example.com", "pass-1234")
        self.other_user = User.objects.create_user("jamie", "jamie@example.com", "pass-9876")

    def test_category_name_is_case_insensitive_per_user(self):
        Category.objects.create(user=self.user, name="Groceries")

        form = CategoryForm({"name": "  groceries "}, user=self.user)

        self.assertFalse(form.is_valid())
        self.assertIn("already have a category", form.errors["name"][0])

    def test_category_name_allows_same_label_for_other_users(self):
        Category.objects.create(user=self.user, name="Groceries")
        Category.objects.create(user=self.other_user, name="Groceries")
        self.assertEqual(Category.objects.filter(name__iexact="Groceries").count(), 2)

class InlineCategoryTests(TestCase):
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

    def test_valid_category_returns_form_with_new_option(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.category_url,
            {
                "name": "Dining",
                "posted_on": date(2026, 2, 11),
                "description": "Dinner",
                "transaction_type": TransactionType.EXPENSE,
                "amount": "22.00",
            },
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn("Dining", body)
        self.assertIn("transaction_form", body)
