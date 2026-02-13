from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import Account, AccountStatus, AccountType, Household, HouseholdMember


User = get_user_model()


class HxTriggerPreservationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("hxuser", "hx@example.com", "pass-1234")
        self.household = Household.objects.create(name="HX Household", slug="hx-household", created_by=self.user)
        HouseholdMember.objects.create(household=self.household, user=self.user, role=HouseholdMember.Role.OWNER, is_primary=True)
        self.account = Account.objects.create(
            user=self.user,
            household=self.household,
            name="HX Checking",
            account_type=AccountType.CHECKING,
            status=AccountStatus.ACTIVE,
            current_balance=100,
        )

    def test_add_transaction_button_present_after_transaction_create(self):
        self.client.force_login(self.user)
        payload = {
            "posted_on": "2026-02-11",
            "description": "HTMX Preserve",
            "transaction_type": "expense",
            "amount": "10.00",
        }
        create_url = reverse("financial:account-transactions-new", args=[self.account.id])
        response = self.client.post(create_url, payload, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)

        detail_url = reverse("financial:accounts-detail", args=[self.account.id])
        detail_response = self.client.get(detail_url)
        self.assertContains(detail_response, "Add Transaction")
