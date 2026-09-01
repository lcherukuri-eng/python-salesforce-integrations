from app.oauth_client_credentials import (
    get_client_credentials_token
)

def get_sf_token():
    return get_client_credentials_token()