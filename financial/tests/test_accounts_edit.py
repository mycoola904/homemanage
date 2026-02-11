from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import Account, AccountStatus, AccountType

User = get_user_model()


class AccountEditTests(TestCase):
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
        self.edit_url = reverse("financial:accounts-edit", args=[self.account.id])

    def test_get_edit_form_fragment(self):
        self.client.force_login(self.user)
        response = self.client.get(self.edit_url, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertIn("name", response.content.decode())

    def test_post_valid_updates_account_and_returns_preview(self):
        self.client.force_login(self.user)
        payload = {
            "name": "Household Checking",
            "institution": "Metro",
            "account_type": AccountType.CHECKING,
            "number_last4": "1234",
            "status": AccountStatus.ACTIVE,
            "current_balance": "3000.00",
            "credit_limit_or_principal": "",
            "statement_close_date": "",
            "payment_due_day": "",
            "notes": "Updated",
        }
        response = self.client.post(self.edit_url, payload, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.account.refresh_from_db()
        self.assertEqual(self.account.name, "Household Checking")
        body = response.content.decode()
        self.assertIn("Household Checking", body)
        self.assertIn("$3,000.00", body)
        self.assertIn('id="accounts-table"', body)
        self.assertIn('hx-swap-oob="true"', body)

    def test_invalid_data_returns_422(self):
        self.client.force_login(self.user)
        payload = {
            "name": "",
            "institution": "",
            "account_type": AccountType.CHECKING,
            "number_last4": "",
            "status": AccountStatus.ACTIVE,
            "current_balance": "3000.00",
            "credit_limit_or_principal": "",
            "statement_close_date": "",
            "payment_due_day": "",
            "notes": "",
        }
        response = self.client.post(self.edit_url, payload, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 422)
        self.assertIn("This field is required", response.content.decode())

    def test_duplicate_name_returns_validation_error(self):
        Account.objects.create(
            user=self.user,
            name="Household Checking",
            institution="Metro",
            account_type=AccountType.SAVINGS,
            status=AccountStatus.ACTIVE,
            current_balance=500,
        )
        self.client.force_login(self.user)
        payload = {
            "name": "Household Checking",
            "institution": "Metro",
            "account_type": AccountType.CHECKING,
            "number_last4": "1234",
            "status": AccountStatus.ACTIVE,
            "current_balance": "2450.75",
            "credit_limit_or_principal": "",
            "statement_close_date": "",
            "payment_due_day": "",
            "notes": "Duplicate",
        }
        response = self.client.post(self.edit_url, payload, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 422)
        self.assertIn("already have an account with this name", response.content.decode())
