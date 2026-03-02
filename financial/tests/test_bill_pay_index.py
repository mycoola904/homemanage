from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import Account, AccountStatus, AccountType, MonthlyBillPayment
from households.models import Household, HouseholdMember


User = get_user_model()


class BillPayIndexTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alex", "alex@example.com", "pass-1234")
        self.household = Household.objects.create(name="Alex Household", slug="alex-household", created_by=self.user)
        HouseholdMember.objects.create(
            household=self.household,
            user=self.user,
            role=HouseholdMember.Role.OWNER,
            is_primary=True,
        )
        self.url = reverse("financial:bill-pay-index")
        self.print_url = reverse("financial:bill-pay-print")

    def test_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/auth/login/", response.headers["Location"])

    def test_filters_liability_accounts_and_sorts_due_day(self):
        Account.objects.create(
            user=self.user,
            household=self.household,
            name="Checking Household",
            institution="Civic",
            account_type=AccountType.CHECKING,
            status=AccountStatus.ACTIVE,
            current_balance=1200,
        )
        Account.objects.create(
            user=self.user,
            household=self.household,
            name="Card B",
            institution="Issuer",
            account_type=AccountType.CREDIT_CARD,
            status=AccountStatus.ACTIVE,
            current_balance=-200,
            payment_due_day=18,
            minimum_amount_due=30,
        )
        Account.objects.create(
            user=self.user,
            household=self.household,
            name="Loan A",
            institution="Lender",
            account_type=AccountType.LOAN,
            status=AccountStatus.ACTIVE,
            current_balance=4000,
            payment_due_day=5,
            minimum_amount_due=150,
        )
        Account.objects.create(
            user=self.user,
            household=self.household,
            name="Other C",
            institution="Utility",
            account_type=AccountType.OTHER,
            status=AccountStatus.ACTIVE,
            current_balance=80,
            payment_due_day=None,
            minimum_amount_due=20,
            online_access_url="https://utility.example/pay",
        )

        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        rows = response.context["rows"]
        self.assertEqual([row.name for row in rows], ["Loan A", "Card B", "Other C"])
        self.assertContains(response, "Bill Pay")
        self.assertContains(response, "https://utility.example/pay")

    def test_url_empty_state_renders_dash(self):
        Account.objects.create(
            user=self.user,
            household=self.household,
            name="Loan No URL",
            institution="Lender",
            account_type=AccountType.LOAN,
            status=AccountStatus.ACTIVE,
            current_balance=1500,
            payment_due_day=12,
            minimum_amount_due=45,
        )

        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Loan No URL")
        self.assertContains(response, "—")

    def test_fast_mode_toggle_defaults_off_on_initial_load(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="bill-pay-fast-mode"')
        self.assertNotContains(response, 'id="bill-pay-fast-mode" type="checkbox" class="checkbox checkbox-sm" checked')

    def test_fast_mode_inline_status_container_is_present(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="bill-pay-fast-mode-status"')
        self.assertContains(response, 'aria-live="polite"')

    def test_actual_payment_total_is_computed_for_selected_month(self):
        first = Account.objects.create(
            user=self.user,
            household=self.household,
            name="Loan One",
            institution="Lender",
            account_type=AccountType.LOAN,
            status=AccountStatus.ACTIVE,
            current_balance=1400,
            payment_due_day=10,
            minimum_amount_due=60,
        )
        second = Account.objects.create(
            user=self.user,
            household=self.household,
            name="Card Two",
            institution="Issuer",
            account_type=AccountType.CREDIT_CARD,
            status=AccountStatus.ACTIVE,
            current_balance=-300,
            payment_due_day=18,
            minimum_amount_due=25,
        )
        MonthlyBillPayment.objects.create(
            account=first,
            month="2026-02-01",
            actual_payment_amount="120.50",
            paid=False,
        )
        MonthlyBillPayment.objects.create(
            account=second,
            month="2026-02-01",
            actual_payment_amount="79.50",
            paid=True,
        )

        self.client.force_login(self.user)
        response = self.client.get(self.url, {"month": "2026-02"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["actual_payment_total_display"], "$200.00")
        self.assertContains(response, "Total Actual Payment: $200.00")

    def test_print_button_and_table_id_are_present(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.print_url)
        self.assertContains(response, 'id="bill-pay-table"')

    def test_print_view_uses_selected_month_records_with_total_and_columns(self):
        account = Account.objects.create(
            user=self.user,
            household=self.household,
            name="Print Loan",
            institution="Lender",
            account_type=AccountType.LOAN,
            status=AccountStatus.ACTIVE,
            current_balance=2200,
            payment_due_day=11,
            minimum_amount_due=100,
        )
        MonthlyBillPayment.objects.create(
            account=account,
            month="2026-02-01",
            actual_payment_amount="175.00",
            paid=True,
        )

        self.client.force_login(self.user)
        response = self.client.get(self.print_url, {"month": "2026-02"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Month: 2026-02")
        self.assertContains(response, "Total Actual Payment: $175.00")
        self.assertContains(response, "Account")
        self.assertContains(response, "Minimum Due")
        self.assertContains(response, "Funding Account")
        self.assertContains(response, "Actual Payment")
        self.assertContains(response, "Paid")
        self.assertNotContains(response, "Institution")
        self.assertNotContains(response, "Due Day")
        self.assertNotContains(response, "Online Access")
        self.assertNotContains(response, "Actions")
