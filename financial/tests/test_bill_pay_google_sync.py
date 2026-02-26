from datetime import date
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from financial.models import Account, AccountType, MonthlyBillPayment
from households.models import Household, HouseholdMember
from households.services.households import CURRENT_HOUSEHOLD_SESSION_KEY


User = get_user_model()


class _GoogleNotFoundError(Exception):
    def __init__(self):
        super().__init__("Google event not found")
        self.resp = type("Resp", (), {"status": 404})()


@override_settings(GOOGLE_CALENDAR_ENABLED=True, GOOGLE_CALENDAR_ID="primary")
class BillPayGoogleSyncTests(TestCase):
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
        self.account = Account.objects.create(
            user=self.user,
            household=self.household,
            name="Visa",
            institution="Metro",
            account_type=AccountType.CREDIT_CARD,
            payment_due_day=12,
        )
        self.month = date(2026, 3, 1)
        self.url = reverse("financial:bill-pay-sync-google")

        self.client.force_login(self.user)
        session = self.client.session
        session[CURRENT_HOUSEHOLD_SESSION_KEY] = str(self.household.id)
        session.save()

    def test_recreates_event_when_existing_google_event_id_is_stale(self):
        mbp = MonthlyBillPayment.objects.create(
            account=self.account,
            month=self.month,
            paid=False,
            google_event_id="stale-event-id",
        )

        mock_client = Mock()
        mock_client.patch_event.side_effect = _GoogleNotFoundError()
        mock_client.insert_event.return_value = ("new-event-id", None)

        with patch("financial.views.GoogleCalendarClient", return_value=mock_client):
            response = self.client.post(self.url, data={"month": "2026-03"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Synced 1 new. Updated 0. Deleted 0 paid. Skipped 0.")

        mbp.refresh_from_db()
        self.assertEqual(mbp.google_event_id, "new-event-id")
        mock_client.patch_event.assert_called_once()
        mock_client.insert_event.assert_called_once()

    def test_updates_existing_event_when_google_event_id_exists(self):
        MonthlyBillPayment.objects.create(
            account=self.account,
            month=self.month,
            paid=False,
            google_event_id="existing-event-id",
        )

        mock_client = Mock()
        mock_client.patch_event.return_value = ("existing-event-id", None)

        with patch("financial.views.GoogleCalendarClient", return_value=mock_client):
            response = self.client.post(self.url, data={"month": "2026-03"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Synced 0 new. Updated 1. Deleted 0 paid. Skipped 0.")

        mock_client.patch_event.assert_called_once()
        mock_client.insert_event.assert_not_called()

    def test_deletes_event_and_clears_google_event_id_when_paid(self):
        mbp = MonthlyBillPayment.objects.create(
            account=self.account,
            month=self.month,
            paid=True,
            google_event_id="existing-event-id",
        )

        mock_client = Mock()

        with patch("financial.views.GoogleCalendarClient", return_value=mock_client):
            response = self.client.post(self.url, data={"month": "2026-03"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Synced 0 new. Updated 0. Deleted 1 paid. Skipped 0.")

        mbp.refresh_from_db()
        self.assertIsNone(mbp.google_event_id)
        mock_client.delete_event.assert_called_once_with("primary", "existing-event-id")
        mock_client.patch_event.assert_not_called()
        mock_client.insert_event.assert_not_called()
