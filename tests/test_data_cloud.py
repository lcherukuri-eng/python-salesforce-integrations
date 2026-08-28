from app.oauth_client_credentials import (
    get_client_credentials_token
)

token = get_client_credentials_token()

print("ACCESS TOKEN:")
print(token.get("access_token"))

print("\nINSTANCE URL:")
print(token.get("instance_url"))

print("\nFULL RESPONSE:")
print(token)