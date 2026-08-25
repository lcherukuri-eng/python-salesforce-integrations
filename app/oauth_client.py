import os
import base64
import hashlib
import secrets
import requests

from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

AUTHORIZE_URL = "https://login.salesforce.com/services/oauth2/authorize"
TOKEN_URL = "https://login.salesforce.com/services/oauth2/token"

code_verifier = None


def create_code_challenge(verifier):
    digest = hashlib.sha256(verifier.encode()).digest()

    return (
        base64.urlsafe_b64encode(digest)
        .decode()
        .rstrip("=")
    )


def get_authorization_url():
    global code_verifier

    code_verifier = secrets.token_urlsafe(64)
    code_challenge = create_code_challenge(code_verifier)

    parameters = {
        "response_type": "code",
        "client_id": os.getenv("SF_CLIENT_ID"),
        "redirect_uri": os.getenv("SF_CALLBACK_URL"),
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }

    return f"{AUTHORIZE_URL}?{urlencode(parameters)}"


def exchange_code_for_token(code):
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": os.getenv("SF_CLIENT_ID"),
        "client_secret": os.getenv("SF_CLIENT_SECRET"),
        "redirect_uri": os.getenv("SF_CALLBACK_URL"),
        "code_verifier": code_verifier,
    }

    response = requests.post(
        TOKEN_URL,
        data=payload,
        timeout=30,
    )

    return response.json()