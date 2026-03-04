from __future__ import annotations

from typing import Optional

from django.conf import settings
from django.utils import timezone

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from financial.integrations.google_calendar.models import GoogleOAuthToken

from financial.services.billpay_calendar import BillPayEventSpec

class GoogleCalendarClient:
    def __init__(self):
        self._service = None  # Lazy-Loaded

    def build_service(self):
        """
        Loads stored token from DB, refreshes if needed, and returns an authorized
        Google Calendar API service client.
        """
        if self._service is not None:
            return self._service

        token_row = GoogleOAuthToken.objects.filter(id=1).first()
        if not token_row:
            raise RuntimeError("No Google OAuth token found. Run /google/oauth/connect/ first.")

        if not token_row.refresh_token:
            raise RuntimeError(
                "No refresh_token stored. Revoke the app in Google Account permissions and re-connect."
            )

        scopes = (token_row.scopes or "").split()

        creds = Credentials(
            token=token_row.access_token,
            refresh_token=token_row.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_OAUTH_CLIENT_ID,
            client_secret=settings.GOOGLE_OAUTH_CLIENT_SECRET,
            scopes=scopes,
            expiry=token_row.token_expiry,
        )

        # Refresh if expired (or missing access token)
        needs_refresh = (not creds.token) or (creds.expired and bool(creds.refresh_token))
        if needs_refresh:
            print("GOOGLE TOKEN REFRESH HAPPENING")
            creds.refresh(Request())

            # Persist new access token + expiry
            token_row.access_token = creds.token
            token_row.token_expiry = creds.expiry
            token_row.save(update_fields=["access_token", "token_expiry", "updated_at"])

        self._service = build("calendar", "v3", credentials=creds)
        return self._service

            

    def insert_event(self, calendar_id: str, payload: dict) -> tuple[str, str | None]:
        service = self.build_service()
        event = (
            service.events()
            .insert(calendarId=calendar_id, body=payload)
            .execute()            
        )
        return event["id"], event.get("htmlLink")
        
    def patch_event(self, calendar_id: str, event_id: str, payload: dict) -> tuple[str, str | None]:
        service = self.build_service()
        event = (
            service.events()
            .patch(calendarId=calendar_id, eventId=event_id, body=payload)
            .execute()            
        )
        return event["id"], event.get("htmlLink")
    
    def delete_event(self, calendar_id: str, event_id: str) -> None:
        service = self.build_service()
        service.events().delete(
            calendarId=calendar_id, 
            eventId=event_id
            ).execute()

def build_google_event_payload(spec: BillPayEventSpec) -> dict:
    """
    Builds a Google Calendar event payload from a BillPayEventSpec.

    Args:
        spec: A BillPayEventSpec containing the details of the event.        

    Returns:
        A dictionary representing the Google Calendar event payload.
    """
    payload = {
        "summary": spec.summary,
        "description": spec.description,
        "start": {"date": spec.start_date.isoformat()},
        "end": {"date": spec.end_date.isoformat()},
        "extendedProperties": {"private": spec.extended_properties},
    }
    return payload