from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import Account, AccountStatus, AccountType, MonthlyBillPayment, Transaction
from households.models import Household, HouseholdMember


User = get_user_model()


class BillPaySaveTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alex", "alex@example.com", "pass-1234")
        self.household = Household.objects.create(name="Alex Household", slug="alex-household", created_by=self.user)
        HouseholdMember.objects.create(
            household=self.household,
            user=self.user,
            role=HouseholdMember.Role.OWNER,
            is_primary=True,
        )
        self.account = Account.objects.create(
            user=self.user,
            household=self.household,
            name="Auto Loan",
            institution="Lender",
            account_type=AccountType.LOAN,
            status=AccountStatus.ACTIVE,
            current_balance=7500,
            payment_due_day=16,
            minimum_amount_due=220,
        )
        self.funding_account = Account.objects.create(
            user=self.user,
            household=self.household,
            name="Household Checking",
            institution="Civic",
            account_type=AccountType.CHECKING,
            status=AccountStatus.ACTIVE,
            current_balance=1200,
        )
        self.row_url = reverse("financial:bill-pay-row", args=[self.account.id])

    def test_get_edit_row_binds_existing_instance_values(self):
        MonthlyBillPayment.objects.create(
            account=self.account,
            funding_account=self.funding_account,
            month="2026-02-01",
            actual_payment_amount="225.50",
            paid=False,
        )

        self.client.force_login(self.user)
        response = self.client.get(self.row_url, {"month": "2026-02"}, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="225.50"')
        self.assertContains(response, f'value="{self.funding_account.id}" selected')

    def test_get_edit_row_inputs_are_bound_to_save_form(self):
        self.client.force_login(self.user)
        response = self.client.get(self.row_url, {"month": "2026-02"}, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        expected_form_id = f'bill-pay-form-{self.account.id}'
        self.assertContains(response, f'id="{expected_form_id}"')
        self.assertContains(response, f'name="funding_account"')
        self.assertContains(response, f'form="{expected_form_id}"')
        self.assertContains(response, f'form="{expected_form_id}"')

    def test_post_creates_account_month_record(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.row_url + "?month=2026-02",
            {"funding_account": str(self.funding_account.id), "actual_payment_amount": "220.00", "paid": "on"},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        payment = MonthlyBillPayment.objects.get(account=self.account, month="2026-02-01")
        self.assertEqual(payment.funding_account_id, self.funding_account.id)
        self.assertEqual(str(payment.actual_payment_amount), "220.00")
        self.assertTrue(payment.paid)

    def test_post_updates_existing_without_duplicate(self):
        existing = MonthlyBillPayment.objects.create(
            account=self.account,
            funding_account=self.funding_account,
            month="2026-02-01",
            actual_payment_amount="190.00",
            paid=False,
        )
        next_funding = Account.objects.create(
            user=self.user,
            household=self.household,
            name="Savings Reserve",
            institution="Civic",
            account_type=AccountType.SAVINGS,
            status=AccountStatus.ACTIVE,
            current_balance=800,
        )

        self.client.force_login(self.user)
        response = self.client.post(
            self.row_url + "?month=2026-02",
            {"funding_account": str(next_funding.id), "actual_payment_amount": "230.00", "paid": "on"},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(MonthlyBillPayment.objects.filter(account=self.account, month="2026-02-01").count(), 1)
        updated = MonthlyBillPayment.objects.get(account=self.account, month="2026-02-01")
        self.assertEqual(updated.id, existing.id)
        self.assertEqual(updated.funding_account_id, next_funding.id)
        self.assertEqual(str(updated.actual_payment_amount), "230.00")
        self.assertTrue(updated.paid)

    def test_save_and_reload_shows_funding_account_display(self):
        self.client.force_login(self.user)
        post_response = self.client.post(
            self.row_url + "?month=2026-03",
            {"funding_account": str(self.funding_account.id), "actual_payment_amount": "99.99", "paid": "on"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(post_response.status_code, 200)
        self.assertContains(post_response, "Household Checking")

        get_response = self.client.get(self.row_url, {"month": "2026-03"}, HTTP_HX_REQUEST="true")
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, f'value="{self.funding_account.id}" selected')

    def test_last_write_wins_for_same_account_month(self):
        self.client.force_login(self.user)
        self.client.post(
            self.row_url + "?month=2026-04",
            {"funding_account": str(self.funding_account.id), "actual_payment_amount": "50.00", "paid": "on"},
            HTTP_HX_REQUEST="true",
        )

        second_funding = Account.objects.create(
            user=self.user,
            household=self.household,
            name="Secondary Checking",
            institution="Civic",
            account_type=AccountType.CHECKING,
            status=AccountStatus.ACTIVE,
            current_balance=500,
        )
        self.client.post(
            self.row_url + "?month=2026-04",
            {"funding_account": str(second_funding.id), "actual_payment_amount": "65.00"},
            HTTP_HX_REQUEST="true",
        )

        payment = MonthlyBillPayment.objects.get(account=self.account, month="2026-04-01")
        self.assertEqual(payment.funding_account_id, second_funding.id)
        self.assertEqual(str(payment.actual_payment_amount), "65.00")
        self.assertFalse(payment.paid)

    def test_row_save_does_not_create_transactions(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.row_url + "?month=2026-05",
            {"funding_account": str(self.funding_account.id), "actual_payment_amount": "110.00", "paid": "on"},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Transaction.objects.filter(account=self.account).count(), 0)
