from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from households.models import Household, HouseholdMember


User = get_user_model()


class AccountImportTemplateTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="alex",
            email="alex@example.com",
            password="complex-pass-123",
        )
        self.household = Household.objects.create(
            name="Alex Household",
            slug="alex-household",
            created_by=self.user,
        )
        HouseholdMember.objects.create(
            household=self.household,
            user=self.user,
            role=HouseholdMember.Role.OWNER,
            is_primary=True,
        )
        self.url = reverse("financial:accounts-import-template")

    def test_download_returns_csv_with_attachment_filename(self):
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn(
            'attachment; filename="account_import_template.csv"',
            response["Content-Disposition"],
        )

    def test_download_header_order_matches_contract(self):
        self.client.force_login(self.user)

        response = self.client.get(self.url)
        body = b"".join(response.streaming_content).decode("utf-8")
        header_line = body.splitlines()[0]

        self.assertEqual(
            header_line,
            "name,institution,account_type,account_number,routing_number,interest_rate,status,current_balance,credit_limit_or_principal,statement_close_date,payment_due_day,minimum_amount_due,online_access_url,notes",
        )
