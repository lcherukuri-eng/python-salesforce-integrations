from app.oauth_client_credentials import get_client_credentials_token

from app.services.claude_service import ask_claude

def get_sf_token():
    return get_client_credentials_token()

def get_claude_service():
    return ask_claude