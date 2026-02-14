from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import Account, AccountStatus, AccountType

User = get_user_model()


class AccountFieldVisibilityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alex", "alex@example.com", "pass-1234")
        self.checking = Account.objects.create(
            user=self.user,
            name="Checking",
            institution="Civic",
            account_type=AccountType.CHECKING,
            status=AccountStatus.ACTIVE,
            current_balance=Decimal("100.00"),
        )
        self.card = Account.objects.create(
            user=self.user,
            name="Card",
            institution="Civic",
            account_type=AccountType.CREDIT_CARD,
            status=AccountStatus.ACTIVE,
            current_balance=Decimal("250.00"),
        )

    def test_edit_form_shows_routing_for_checking(self):
        self.client.force_login(self.user)
        url = reverse("financial:accounts-edit", args=[self.checking.id])
        response = self.client.get(url, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn('name="routing_number"', body)
        self.assertNotIn('name="interest_rate"', body)
        self.assertNotIn('name="minimum_amount_due"', body)

    def test_edit_form_shows_interest_for_credit_card(self):
        self.client.force_login(self.user)
        url = reverse("financial:accounts-edit", args=[self.card.id])
        response = self.client.get(url, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn('name="interest_rate"', body)
        self.assertNotIn('name="routing_number"', body)
        self.assertIn('name="minimum_amount_due"', body)

    def test_post_rejects_routing_number_for_credit_card(self):
        self.client.force_login(self.user)
        url = reverse("financial:accounts-edit", args=[self.card.id])
        payload = {
            "name": "Card",
            "institution": "Civic",
            "account_type": AccountType.CREDIT_CARD,
            "account_number": "12345",
            "routing_number": "011000015",
            "interest_rate": "19.9",
            "status": AccountStatus.ACTIVE,
            "current_balance": "250.00",
            "credit_limit_or_principal": "500.00",
            "statement_close_date": "2026-02-01",
            "payment_due_day": "5",
            "notes": "",
        }
        response = self.client.post(url, payload, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 422)
        self.assertIn("Routing numbers are only for checking or savings accounts.", response.content.decode())

    def test_post_rejects_interest_rate_for_checking(self):
        self.client.force_login(self.user)
        url = reverse("financial:accounts-edit", args=[self.checking.id])
        payload = {
            "name": "Checking",
            "institution": "Civic",
            "account_type": AccountType.CHECKING,
            "account_number": "98765",
            "routing_number": "011000015",
            "interest_rate": "1.2",
            "status": AccountStatus.ACTIVE,
            "current_balance": "100.00",
            "credit_limit_or_principal": "",
            "statement_close_date": "",
            "payment_due_day": "",
            "minimum_amount_due": "",
            "notes": "",
        }
        response = self.client.post(url, payload, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 422)
        self.assertIn("Interest rates are only for credit or loan accounts.", response.content.decode())

    def test_post_rejects_minimum_amount_due_for_checking(self):
        self.client.force_login(self.user)
        url = reverse("financial:accounts-edit", args=[self.checking.id])
        payload = {
            "name": "Checking",
            "institution": "Civic",
            "account_type": AccountType.CHECKING,
            "account_number": "98765",
            "routing_number": "011000015",
            "interest_rate": "",
            "status": AccountStatus.ACTIVE,
            "current_balance": "100.00",
            "credit_limit_or_principal": "",
            "statement_close_date": "",
            "payment_due_day": "",
            "minimum_amount_due": "25.00",
            "notes": "",
        }
        response = self.client.post(url, payload, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 422)
        self.assertIn("Minimum amount due is only for liability accounts.", response.content.decode())
