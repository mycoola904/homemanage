from django.db import models

class GoogleOAuthToken(models.Model):
    """
    Stores OAuth credentials for a single Google account.
    For local development, we assume one account only.
    In production, we may want to support multiple accounts, but that is not a current requirement.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    refresh_token = models.TextField()

    access_token = models.TextField(blank=True, null=True)
    token_expiry = models.DateTimeField(blank=True, null=True)

    scopes = models.TextField()  # space-separated list of scopes granted by the user

    class Meta:
        verbose_name = "Google OAuth Token"
        verbose_name_plural = "Google OAuth Tokens"