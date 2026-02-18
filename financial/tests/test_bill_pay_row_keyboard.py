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
        self.index_url = reverse("financial:bill-pay-index")

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

    def test_edit_row_tab_sequence_is_funding_actual_paid_save_cancel(self):
        self.client.force_login(self.user)
        response = self.client.get(self.row_url, {"month": "2026-02"}, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        html = response.content.decode("utf-8")

        funding_index = html.index('data-focus-field="funding_account"')
        actual_index = html.index('data-focus-field="actual_payment_amount"')
        paid_index = html.index('data-focus-field="paid"')
        save_index = html.index('data-focus-field="save"')
        cancel_index = html.index('data-focus-field="cancel"')

        self.assertLess(funding_index, actual_index)
        self.assertLess(actual_index, paid_index)
        self.assertLess(paid_index, save_index)
        self.assertLess(save_index, cancel_index)

    def test_edit_row_includes_fast_mode_hidden_field(self):
        self.client.force_login(self.user)
        response = self.client.get(self.row_url, {"month": "2026-02"}, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="fast_mode"')
        self.assertContains(response, 'data-fast-mode-field')

    def test_index_loads_open_next_row_handler_and_failure_message_copy(self):
        self.client.force_login(self.user)
        response = self.client.get(self.index_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "bill_pay_row_keyboard.js")
        self.assertContains(response, 'id="bill-pay-fast-mode-status"')
