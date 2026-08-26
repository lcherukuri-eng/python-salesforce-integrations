import os
import requests

from dotenv import load_dotenv

load_dotenv()

TOKEN_URL = (
    "https://orgfarm-d2ad0c3301-dev-ed.develop.my.salesforce.com"
    "/services/oauth2/token"
)


def get_client_credentials_token():

    payload = {
        "grant_type": "client_credentials",
        "client_id": os.getenv(
            "SF_CLIENT_ID"
        ),
        "client_secret": os.getenv(
            "SF_CLIENT_SECRET"
        )
    }

    headers = {
        "Content-Type":
            "application/x-www-form-urlencoded"
    }

    response = requests.post(
        TOKEN_URL,
        data=payload,
        headers=headers,
        timeout=30
    )

    return response.json()