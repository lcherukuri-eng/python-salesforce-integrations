import requests

from oauth_client_credentials import (
    get_client_credentials_token
)

token = get_client_credentials_token()

payload = {
    "grant_type":
        "urn:salesforce:grant-type:external:cdp",
    "subject_token":
        token["access_token"],
    "subject_token_type":
        "urn:ietf:params:oauth:token-type:access_token"
}

headers = {
    "Content-Type":
        "application/x-www-form-urlencoded"
}

response = requests.post(
    token["instance_url"]
    + "/services/a360/token",
    data=payload,
    headers=headers,
    timeout=30
)

print("STATUS:")
print(response.status_code)

print("\nBODY:")
print(response.text)
