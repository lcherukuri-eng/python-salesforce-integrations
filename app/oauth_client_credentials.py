import os
import requests

from dotenv import load_dotenv
from app.core.token_cache import TokenCache
from app.logger import get_logger

logger = get_logger(__name__)

load_dotenv()

salesforce_token_cache = TokenCache()

TOKEN_URL = (
    os.getenv("SF_MY_DOMAIN_URL")
    + "/services/oauth2/token"
)


def get_client_credentials_token(
    force_refresh: bool = False
):
    if force_refresh:
        logger.info(
            "Force-refreshing Salesforce token"
        )
        salesforce_token_cache.clear()

    cached_token = salesforce_token_cache.get_token()

    if cached_token:
        logger.info("Using cached Salesforce token")
        return  cached_token

    logger.info("Cache miss - requesting new Salesforce token")

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

    token_data = response.json()

    logger.info("New token received from Salesforce")

    salesforce_token_cache.set_token(token_data)   

    return token_data

def refresh_salesforce_token():
    return get_client_credentials_token(
        force_refresh=True
    )