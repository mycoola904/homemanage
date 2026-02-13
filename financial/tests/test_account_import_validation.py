from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from financial.models import Account
from households.models import Household, HouseholdMember


User = get_user_model()


class AccountImportValidationTests(TestCase):
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
        HouseholdMember.objects.create(
            household=self.household,
            user=self.user,
            role=HouseholdMember.Role.OWNER,
            is_primary=True,
        )
        self.import_url = reverse("financial:accounts-import")
        self.client.force_login(self.user)

    @staticmethod
    def _headers() -> str:
        return (
            "name,institution,account_type,account_number,routing_number,interest_rate,"
            "status,current_balance,credit_limit_or_principal,statement_close_date,"
            "payment_due_day,online_access_url,notes\n"
        )

    def _post_csv(self, name: str, content: bytes, content_type: str = "text/csv"):
        upload = SimpleUploadedFile(name=name, content=content, content_type=content_type)
        return self.client.post(
            self.import_url,
            data={"import_file": upload},
            HTTP_HX_REQUEST="true",
        )

    def test_rejects_unsupported_file_type(self):
        response = self._post_csv("accounts.txt", b"not,csv\n")
        self.assertEqual(response.status_code, 422)
        self.assertContains(response, "Upload a CSV file", status_code=422)

    def test_rejects_missing_required_headers(self):
        bad_headers = "name,institution,account_type\n"
        row = "A,Metro,checking\n"
        response = self._post_csv("accounts.csv", (bad_headers + row).encode("utf-8"))
        self.assertEqual(response.status_code, 422)
        self.assertContains(response, "Missing required headers", status_code=422)

    def test_rejects_invalid_row_values_enum_date_url_and_day(self):
        row = (
            "Bad Row,Metro,checking,123456,021000021,,not_a_status,250.00,,,"
            "33,not-a-url,Note\n"
        )
        response = self._post_csv("accounts.csv", (self._headers() + row).encode("utf-8"))
        self.assertEqual(response.status_code, 422)
        self.assertContains(response, "status must use canonical values", status_code=422)
        self.assertFalse(Account.objects.filter(name="Bad Row").exists())

    def test_rejects_duplicate_names_within_upload_case_insensitive(self):
        rows = (
            "Duplicate,Metro,checking,123456,021000021,,active,250.00,,,,https://example.com,First\n"
            "duplicate,Metro,checking,123457,021000021,,active,300.00,,,,https://example.com,Second\n"
        )
        response = self._post_csv("accounts.csv", (self._headers() + rows).encode("utf-8"))
        self.assertEqual(response.status_code, 422)
        self.assertContains(response, "duplicate account name appears more than once", status_code=422)

    def test_rejects_duplicate_name_against_existing_household_case_insensitive(self):
        other_user = User.objects.create_user("jamie", "jamie@example.com", "pass-1234")
        HouseholdMember.objects.create(
            household=self.household,
            user=other_user,
            role=HouseholdMember.Role.MEMBER,
            is_primary=False,
        )
        Account.objects.create(
            user=other_user,
            household=self.household,
            name="Joint Checking",
            institution="Metro",
            account_type="checking",
            current_balance="100.00",
        )
        row = (
            "joint checking,Metro,checking,123456,021000021,,active,250.00,,,,https://example.com,Import\n"
        )
        response = self._post_csv("accounts.csv", (self._headers() + row).encode("utf-8"))
        self.assertEqual(response.status_code, 422)
        self.assertContains(response, "duplicate account name already exists", status_code=422)

    def test_rejects_files_over_size_limit(self):
        large_content = b"a" * ((5 * 1024 * 1024) + 1)
        response = self._post_csv("accounts.csv", large_content)
        self.assertEqual(response.status_code, 422)
        self.assertContains(response, "5 MB or smaller", status_code=422)

    def test_rejects_files_over_row_limit(self):
        row = "Bulk,Metro,checking,123456,021000021,,active,250.00,,,,https://example.com,Import\n"
        payload = self._headers() + (row * 1001)
        response = self._post_csv("accounts.csv", payload.encode("utf-8"))
        self.assertEqual(response.status_code, 422)
        self.assertContains(response, "maximum of 1000 data rows", status_code=422)

    def test_atomic_rollback_when_any_row_invalid(self):
        rows = (
            "Valid One,Metro,checking,123456,021000021,,active,250.00,,,,https://example.com,First\n"
            "Invalid Two,Metro,checking,123457,021000021,,bad_status,300.00,,,,https://example.com,Second\n"
        )
        response = self._post_csv("accounts.csv", (self._headers() + rows).encode("utf-8"))
        self.assertEqual(response.status_code, 422)
        self.assertFalse(Account.objects.filter(name="Valid One").exists())
        self.assertFalse(Account.objects.filter(name="Invalid Two").exists())
