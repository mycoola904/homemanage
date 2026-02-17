from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import Account, AccountStatus, AccountType, MonthlyBillPayment
from households.models import Household, HouseholdMember


User = get_user_model()


class BillPayRowKeyboardShortcutsTests(TestCase):
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
            name="Credit Card",
            institution="CardCo",
            account_type=AccountType.CREDIT_CARD,
            status=AccountStatus.ACTIVE,
            current_balance=-650,
            payment_due_day=9,
            minimum_amount_due=35,
        )
        self.row_url = reverse("financial:bill-pay-row", args=[self.account.id])

    def test_edit_row_contains_keyboard_intent_controls(self):
        self.client.force_login(self.user)
        response = self.client.get(self.row_url, {"month": "2026-02"}, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="keyboard_intent" value="save"')
        self.assertContains(response, 'name="focus_field" value="save"')
        self.assertContains(response, '"keyboard_intent":"cancel"')
        self.assertContains(response, '"focus_field":"cancel"')

    def test_keyboard_save_intent_persists_values(self):
        self.client.force_login(self.user)
        funding = Account.objects.create(
            user=self.user,
            household=self.household,
            name="Household Checking",
            institution="Test Bank",
            account_type=AccountType.CHECKING,
            status=AccountStatus.ACTIVE,
            current_balance=1000,
        )
        response = self.client.post(
            self.row_url + "?month=2026-02",
            {
                "funding_account": str(funding.id),
                "actual_payment_amount": "51.25",
                "paid": "on",
                "keyboard_intent": "save",
                "focus_field": "save",
            },
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        payment = MonthlyBillPayment.objects.get(account=self.account, month="2026-02-01")
        self.assertEqual(str(payment.actual_payment_amount), "51.25")
        self.assertTrue(payment.paid)

    def test_keyboard_cancel_intent_does_not_persist_posted_changes(self):
        MonthlyBillPayment.objects.create(
            account=self.account,
            month="2026-02-01",
            actual_payment_amount="12.00",
            paid=False,
        )

        self.client.force_login(self.user)
        response = self.client.post(
            self.row_url + "?month=2026-02",
            {
                "actual_payment_amount": "77.00",
                "paid": "on",
                "keyboard_intent": "cancel",
                "focus_field": "cancel",
            },
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        payment = MonthlyBillPayment.objects.get(account=self.account, month="2026-02-01")
        self.assertEqual(str(payment.actual_payment_amount), "12.00")
        self.assertFalse(payment.paid)
