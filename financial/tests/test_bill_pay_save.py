from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import Account, AccountStatus, AccountType, MonthlyBillPayment
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
        self.row_url = reverse("financial:bill-pay-row", args=[self.account.id])

    def test_get_edit_row_binds_existing_instance_values(self):
        MonthlyBillPayment.objects.create(
            account=self.account,
            month="2026-02-01",
            actual_payment_amount="225.50",
            paid=False,
        )

        self.client.force_login(self.user)
        response = self.client.get(self.row_url, {"month": "2026-02"}, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="225.50"')

    def test_get_edit_row_inputs_are_bound_to_save_form(self):
        self.client.force_login(self.user)
        response = self.client.get(self.row_url, {"month": "2026-02"}, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        expected_form_id = f'bill-pay-form-{self.account.id}'
        self.assertContains(response, f'id="{expected_form_id}"')
        self.assertContains(response, f'form="{expected_form_id}"')

    def test_post_creates_account_month_record(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.row_url + "?month=2026-02",
            {"actual_payment_amount": "220.00", "paid": "on"},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        payment = MonthlyBillPayment.objects.get(account=self.account, month="2026-02-01")
        self.assertEqual(str(payment.actual_payment_amount), "220.00")
        self.assertTrue(payment.paid)

    def test_post_updates_existing_without_duplicate(self):
        existing = MonthlyBillPayment.objects.create(
            account=self.account,
            month="2026-02-01",
            actual_payment_amount="190.00",
            paid=False,
        )

        self.client.force_login(self.user)
        response = self.client.post(
            self.row_url + "?month=2026-02",
            {"actual_payment_amount": "230.00", "paid": "on"},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(MonthlyBillPayment.objects.filter(account=self.account, month="2026-02-01").count(), 1)
        updated = MonthlyBillPayment.objects.get(account=self.account, month="2026-02-01")
        self.assertEqual(updated.id, existing.id)
        self.assertEqual(str(updated.actual_payment_amount), "230.00")
        self.assertTrue(updated.paid)
