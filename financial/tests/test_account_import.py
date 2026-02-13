from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from financial.models import Account
from households.models import Household, HouseholdMember
from households.services.households import CURRENT_HOUSEHOLD_SESSION_KEY


User = get_user_model()


class AccountImportTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="alex",
            email="alex@example.com",
            password="complex-pass-123",
        )
        self.household = Household.objects.create(
            name="Alex Household",
            slug="alex-household",
            created_by=self.user,
        )
        self.alt_household = Household.objects.create(
            name="Alex Alt Household",
            slug="alex-alt-household",
            created_by=self.user,
        )
        HouseholdMember.objects.create(
            household=self.household,
            user=self.user,
            role=HouseholdMember.Role.OWNER,
            is_primary=True,
        )
        HouseholdMember.objects.create(
            household=self.alt_household,
            user=self.user,
            role=HouseholdMember.Role.OWNER,
            is_primary=False,
        )

        self.accounts_index_url = reverse("financial:accounts-index")
        self.import_url = reverse("financial:accounts-import")
        self.client.force_login(self.user)

    @staticmethod
    def _csv_payload(name: str) -> bytes:
        headers = (
            "name,institution,account_type,account_number,routing_number,interest_rate,"
            "status,current_balance,credit_limit_or_principal,statement_close_date,"
            "payment_due_day,online_access_url,notes\n"
        )
        row = (
            f"{name},Metro,checking,123456,021000021,,active,250.00,,,,"
            "https://example.com,Imported from CSV\n"
        )
        return (headers + row).encode("utf-8")

    def test_import_link_and_panel_render(self):
        response = self.client.get(self.accounts_index_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.import_url)
        self.assertContains(response, "Import")

        response = self.client.get(self.import_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="financial-main-content"')
        self.assertContains(response, 'id="account-import-panel"')

    def test_successful_csv_import_creates_accounts(self):
        upload = SimpleUploadedFile(
            name="accounts.csv",
            content=self._csv_payload("Import Checking"),
            content_type="text/csv",
        )

        response = self.client.post(
            self.import_url,
            data={"import_file": upload},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Imported 1 of 1 rows.")
        self.assertTrue(
            Account.objects.filter(
                user=self.user,
                household=self.household,
                name="Import Checking",
            ).exists()
        )

    def test_import_respects_active_household(self):
        session = self.client.session
        session[CURRENT_HOUSEHOLD_SESSION_KEY] = str(self.alt_household.id)
        session.save()

        upload = SimpleUploadedFile(
            name="accounts.csv",
            content=self._csv_payload("Alt Household Account"),
            content_type="text/csv",
        )

        response = self.client.post(
            self.import_url,
            data={"import_file": upload},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Account.objects.filter(
                user=self.user,
                household=self.alt_household,
                name="Alt Household Account",
            ).exists()
        )
        self.assertFalse(
            Account.objects.filter(
                user=self.user,
                household=self.household,
                name="Alt Household Account",
            ).exists()
        )

    def test_import_form_shows_selected_filename_placeholder(self):
        response = self.client.get(self.import_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="selected-import-filename"')
        self.assertContains(response, "No file selected")
        self.assertContains(response, "selected-import-filename")
