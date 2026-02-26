from __future__ import annotations

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

from google_auth_oauthlib.flow import Flow

from .models import GoogleOAuthToken

# Use the minimal scope needed for creating/updating calendar events. This will allow us to sync bill pay due dates to a Google Calendar.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def _build_flow(request: HttpRequest) -> Flow:
    """
    Creates an OAuth Flow configured for out local dev redirect URI.
    In production, this will need to be updated to use the actual domain name and ensure that the redirect URI is added to the Google API Console.
    """

    client_config = {
        "web": {
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            "redirect_uris": [settings.GOOGLE_OAUTH_REDIRECT_URI],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }

    # Use the configured redirect URI from .env (must match Google Console)
    redirect_uri = settings.GOOGLE_OAUTH_REDIRECT_URI

    flow = Flow.from_client_config(
        client_config=client_config,
        scopes=SCOPES,
        redirect_uri=redirect_uri,
    )
    return flow

def google_oauth_connect(request) -> HttpResponse:
    """
    Step 1: Send user to Google consent screen to authorize our app to access their calendar.
    """
    flow = _build_flow(request)

    authorization_url, state = flow.authorization_url(
        access_type='offline', # needed for refresh token
        include_granted_scopes='true',
        prompt='consent', # force consent screen to always show (for testing - in production, you may want to only show this the first time)
    )

    request.session['google_oauth_state'] = state
    return redirect(authorization_url)

def google_oauth_callback(request) -> HttpResponse:
    """
    Step 2: Google redirects here with ?code=...&state=...
    Exchange the code for tokens and persist them.
    """
    state = request.session.get('google_oauth_state')
    if not state:
        return HttpResponse("Error: Missing OAuth state in session", status=400)
    
    flow = _build_flow(request)
    flow.fetch_token(authorization_response=request.build_absolute_uri())

    creds = flow.credentials

    defaults={
            "access_token": creds.token,
            "refresh_token": creds.refresh_token or "", # refresh_token is only returned on the first authorization, so we need to handle the case where it's not included in subsequent authorizations
            "token_expiry": creds.expiry,
            "scopes": " ".join(creds.scopes or []),
        }
    
    if creds.refresh_token:
        defaults["refresh_token"] = creds.refresh_token

    # Single-account storage: keep one row (id=1 convention)
    obj, _created = GoogleOAuthToken.objects.update_or_create(
        id=1,
        defaults=defaults
    )

    if not obj.refresh_token:
        return HttpResponse(
            "OAuth succeeded, but no refresh_token was returned. "
            "If this is a re-connect, revoke the app in yuour Google Account permissions. "
            "and try again.",
            status=200,
        )
    
    return HttpResponse(
        "Google OAuth connect successful! You can now sync your bill pay due dates to Google Calendar."
        " You can close this tab.", status=200
        )
