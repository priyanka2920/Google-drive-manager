import os

import streamlit as st
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from config import CREDENTIALS_FILE, SCOPES, TOKEN_FILE


@st.cache_resource
def authenticate_google_drive():
    """Return valid Google OAuth credentials, refreshing or re-authenticating as needed.

    Cached as a resource so we don't re-run the OAuth flow on every Streamlit
    rerun. If the cached credentials expire mid-session and can't be silently
    refreshed, the cache is cleared so the next call re-authenticates instead
    of failing silently.
    """

    if not os.path.exists(CREDENTIALS_FILE):
        st.error(
            f"Missing `{CREDENTIALS_FILE}`. Download your OAuth client "
            "credentials from Google Cloud Console and place them here."
        )
        st.stop()

    creds = None

    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except (ValueError, OSError):
            creds = None  # corrupt/incompatible token file, fall through to re-auth

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None  # refresh token revoked/expired, need a fresh login

        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return creds


def get_fresh_credentials():
    """Fetch cached credentials, refreshing the cache if they've gone stale."""

    creds = authenticate_google_drive()

    if not creds.valid:
        authenticate_google_drive.clear()
        creds = authenticate_google_drive()

    return creds