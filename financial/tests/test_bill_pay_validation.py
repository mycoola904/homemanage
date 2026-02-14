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
        self.row_url = reverse("financial:bill-pay-row", args=[self.account.id])

    def test_negative_amount_returns_422(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.row_url + "?month=2026-02",
            {"actual_payment_amount": "-1.00", "paid": "on"},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("cannot be negative", response.content.decode())

    def test_paid_true_with_blank_amount_is_valid(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.row_url + "?month=2026-02",
            {"actual_payment_amount": "", "paid": "on"},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        payment = MonthlyBillPayment.objects.get(account=self.account, month="2026-02-01")
        self.assertIsNone(payment.actual_payment_amount)
        self.assertTrue(payment.paid)

    def test_paid_false_with_zero_amount_is_valid(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.row_url + "?month=2026-02",
            {"actual_payment_amount": "0.00"},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        payment = MonthlyBillPayment.objects.get(account=self.account, month="2026-02-01")
        self.assertEqual(str(payment.actual_payment_amount), "0.00")
        self.assertFalse(payment.paid)
