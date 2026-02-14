import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import Account, AccountStatus, AccountType, MonthlyBillPayment
from households.models import Household, HouseholdMember


User = get_user_model()


class BillPayMonthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alex", "alex@example.com", "pass-1234")
        self.other = User.objects.create_user("jamie", "jamie@example.com", "pass-9876")

        self.household = Household.objects.create(name="Alex Household", slug="alex-household", created_by=self.user)
        HouseholdMember.objects.create(
            household=self.household,
            user=self.user,
            role=HouseholdMember.Role.OWNER,
            is_primary=True,
        )

        self.other_household = Household.objects.create(name="Jamie Household", slug="jamie-household", created_by=self.other)
        HouseholdMember.objects.create(
            household=self.other_household,
            user=self.other,
            role=HouseholdMember.Role.OWNER,
            is_primary=True,
        )

        self.account = Account.objects.create(
            user=self.user,
            household=self.household,
            name="Monthly Loan",
            institution="Lender",
            account_type=AccountType.LOAN,
            status=AccountStatus.ACTIVE,
            current_balance=5000,
            payment_due_day=8,
            minimum_amount_due=120,
        )
        self.funding_account = Account.objects.create(
            user=self.user,
            household=self.household,
            name="Household Checking",
            institution="Civic",
            account_type=AccountType.CHECKING,
            status=AccountStatus.ACTIVE,
            current_balance=900,
        )
        MonthlyBillPayment.objects.create(
            account=self.account,
            funding_account=self.funding_account,
            month="2026-01-01",
            actual_payment_amount="140.00",
            paid=True,
        )

        self.index_url = reverse("financial:bill-pay-index")
        self.body_url = reverse("financial:bill-pay-table-body")
        self.row_url = reverse("financial:bill-pay-row", args=[self.account.id])

    def test_defaults_to_current_month(self):
        self.client.force_login(self.user)
        response = self.client.get(self.index_url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("selected_month", response.context)

    def test_table_body_allows_historical_month_view(self):
        self.client.force_login(self.user)
        response = self.client.get(self.body_url, {"month": "2026-01"}, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Monthly Loan")
        self.assertContains(response, "$140.00")

    def test_invalid_month_returns_400(self):
        self.client.force_login(self.user)
        response = self.client.get(self.body_url, {"month": "2026/01"}, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid month format", response.content.decode())

    def test_missing_or_unowned_row_returns_404(self):
        self.client.force_login(self.other)
        response = self.client.get(self.row_url, {"month": "2026-02"}, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 404)

        missing_row_url = reverse("financial:bill-pay-row", args=[uuid.uuid4()])
        self.client.force_login(self.user)
        response = self.client.get(missing_row_url, {"month": "2026-02"}, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 404)

    def test_row_post_missing_or_unowned_returns_404(self):
        self.client.force_login(self.other)
        response = self.client.post(
            self.row_url + "?month=2026-02",
            {"funding_account": str(self.funding_account.id), "actual_payment_amount": "20.00", "paid": "on"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 404)
