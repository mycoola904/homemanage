from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import Account, AccountStatus, AccountType
from households.models import Household, HouseholdMember


User = get_user_model()


class BillPayRowKeyboardTests(TestCase):
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

    def test_edit_row_contains_required_tab_order_controls(self):
        self.client.force_login(self.user)
        response = self.client.get(self.row_url, {"month": "2026-02"}, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-focus-field="funding_account"')
        self.assertContains(response, 'data-tab-order="1"')
        self.assertContains(response, 'data-focus-field="actual_payment_amount"')
        self.assertContains(response, 'data-tab-order="2"')
        self.assertContains(response, 'data-focus-field="paid"')
        self.assertContains(response, 'data-tab-order="3"')
        self.assertContains(response, 'data-focus-field="save"')
        self.assertContains(response, 'data-tab-order="4"')
        self.assertContains(response, 'data-focus-field="cancel"')
        self.assertContains(response, 'data-tab-order="5"')

    def test_validation_error_row_defaults_focus_to_actual_payment(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.row_url + "?month=2026-02",
            {"actual_payment_amount": "-1.00", "paid": "on"},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 422)
        self.assertContains(response, 'data-initial-focus-field="actual_payment_amount"', status_code=422)

    def test_edit_row_includes_animation_hook_attributes(self):
        self.client.force_login(self.user)
        response = self.client.get(self.row_url, {"month": "2026-02"}, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-billpay-animate-row')
        self.assertContains(response, 'class="billpay-row-transition"')
