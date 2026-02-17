from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import Account, AccountStatus, AccountType, MonthlyBillPayment
from households.models import Household, HouseholdMember


User = get_user_model()


class BillPayValidationTests(TestCase):
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
        self.funding_account = Account.objects.create(
            user=self.user,
            household=self.household,
            name="Household Checking",
            institution="Civic",
            account_type=AccountType.CHECKING,
            status=AccountStatus.ACTIVE,
            current_balance=500,
        )
        self.row_url = reverse("financial:bill-pay-row", args=[self.account.id])

    def test_missing_funding_account_returns_422_and_preserves_values(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.row_url + "?month=2026-02",
            {"actual_payment_amount": "22.00", "paid": "on"},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("Select a funding account.", response.content.decode())
        self.assertContains(response, 'value="22.00"', status_code=422)
        self.assertContains(response, "checked", status_code=422)

    def test_negative_amount_returns_422(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.row_url + "?month=2026-02",
            {"funding_account": str(self.funding_account.id), "actual_payment_amount": "-1.00", "paid": "on"},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("cannot be negative", response.content.decode())

    def test_paid_true_with_blank_amount_is_valid(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.row_url + "?month=2026-02",
            {"funding_account": str(self.funding_account.id), "actual_payment_amount": "", "paid": "on"},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        payment = MonthlyBillPayment.objects.get(account=self.account, month="2026-02-01")
        self.assertEqual(payment.funding_account_id, self.funding_account.id)
        self.assertIsNone(payment.actual_payment_amount)
        self.assertTrue(payment.paid)

    def test_paid_false_with_zero_amount_is_valid(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.row_url + "?month=2026-02",
            {"funding_account": str(self.funding_account.id), "actual_payment_amount": "0.00"},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        payment = MonthlyBillPayment.objects.get(account=self.account, month="2026-02-01")
        self.assertEqual(payment.funding_account_id, self.funding_account.id)
        self.assertEqual(str(payment.actual_payment_amount), "0.00")
        self.assertFalse(payment.paid)

<<<<<<< HEAD
    def test_keyboard_cancel_matches_cancel_action_non_persistence(self):
        MonthlyBillPayment.objects.create(
            account=self.account,
            month="2026-02-01",
            actual_payment_amount="44.00",
            paid=False,
=======
    def test_closed_account_cannot_be_selected_as_new_funding_option(self):
        closed_funding = Account.objects.create(
            user=self.user,
            household=self.household,
            name="Closed Funding",
            institution="Old Bank",
            account_type=AccountType.CHECKING,
            status=AccountStatus.CLOSED,
            current_balance=0,
>>>>>>> 001-bill-pay-funding-account
        )

        self.client.force_login(self.user)
        response = self.client.post(
            self.row_url + "?month=2026-02",
<<<<<<< HEAD
            {
                "actual_payment_amount": "99.00",
                "paid": "on",
                "keyboard_intent": "cancel",
                "focus_field": "cancel",
            },
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        payment = MonthlyBillPayment.objects.get(account=self.account, month="2026-02-01")
        self.assertEqual(str(payment.actual_payment_amount), "44.00")
        self.assertFalse(payment.paid)
        self.assertContains(response, "Edit")
=======
            {"funding_account": str(closed_funding.id), "actual_payment_amount": "20.00", "paid": "on"},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("Select a valid choice.", response.content.decode())

    def test_no_active_funding_options_message_is_rendered(self):
        self.account.status = AccountStatus.CLOSED
        self.account.save(update_fields=["status", "updated_at"])
        self.funding_account.status = AccountStatus.CLOSED
        self.funding_account.save(update_fields=["status", "updated_at"])

        self.client.force_login(self.user)
        response = self.client.get(self.row_url, {"month": "2026-02"}, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No active funding accounts are available.")
>>>>>>> 001-bill-pay-funding-account
