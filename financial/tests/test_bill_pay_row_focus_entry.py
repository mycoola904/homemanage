from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import Account, AccountStatus, AccountType
from households.models import Household, HouseholdMember


User = get_user_model()


class BillPayRowFocusEntryTests(TestCase):
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
        self.index_url = reverse("financial:bill-pay-index")
        self.row_url = reverse("financial:bill-pay-row", args=[self.account.id])

    def test_display_row_contains_focus_field_edit_triggers(self):
        self.client.force_login(self.user)
        response = self.client.get(self.index_url, {"month": "2026-02"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "focus_field=funding_account")
        self.assertContains(response, "focus_field=actual_payment_amount")
        self.assertContains(response, "focus_field=paid")

    def test_get_edit_row_with_focus_field_sets_initial_focus_metadata(self):
        self.client.force_login(self.user)
        response = self.client.get(
            self.row_url,
            {"month": "2026-02", "focus_field": "funding_account"},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-billpay-edit-row')
        self.assertContains(response, 'data-initial-focus-field="funding_account"')
        self.assertIn(f'id="bill-pay-row-{self.account.id}"', response.content.decode().splitlines()[0])

    def test_get_edit_row_invalid_focus_field_defaults_to_actual_payment(self):
        self.client.force_login(self.user)
        response = self.client.get(
            self.row_url,
            {"month": "2026-02", "focus_field": "not-a-field"},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-initial-focus-field="actual_payment_amount"')
