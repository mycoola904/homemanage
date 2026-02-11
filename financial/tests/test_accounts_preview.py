import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import Account, AccountStatus, AccountType

User = get_user_model()


class AccountPreviewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="alex",
            email="alex@example.com",
            password="pass-1234",
        )
        self.account = Account.objects.create(
            user=self.user,
            name="Civic Checking",
            institution="Civic Bank",
            account_type=AccountType.CHECKING,
            status=AccountStatus.ACTIVE,
            current_balance=2450.75,
            credit_limit_or_principal=5000,
            statement_close_date="2026-02-15",
            payment_due_day=12,
            notes="Primary household account",
        )
        self.url = reverse("financial:accounts-preview", args=[self.account.id])

    def test_preview_returns_allowed_fields(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Civic Checking")
        self.assertContains(response, "$2,450.75")
        self.assertContains(response, "Payment due day")
        self.assertNotContains(response, "institution", status_code=200)

    def test_preview_handles_missing_or_unowned_account(self):
        other_user = User.objects.create_user("charlie", "charlie@example.com", "pass-4321")
        self.client.force_login(other_user)
        response = self.client.get(self.url, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 404)
        self.assertIn("refresh", response.content.decode().lower())

        self.client.force_login(self.user)
        missing_url = reverse("financial:accounts-preview", args=[uuid.uuid4()])
        missing_response = self.client.get(missing_url, HTTP_HX_REQUEST="true")
        self.assertEqual(missing_response.status_code, 404)
        self.assertIn("missing", missing_response.content.decode().lower())
