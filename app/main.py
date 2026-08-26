from fastapi import (
    FastAPI,
    BackgroundTasks
)
from fastapi.responses import RedirectResponse

from app.oauth_client import (
    get_authorization_url,
    exchange_code_for_token,
    refresh_access_token
)
from app.token_store import (
    load_token,
    save_token
)
from app.salesforce_client import (
    get_accounts,
    export_accounts_to_csv,
    export_accounts_to_s3,
    analyze_accounts
)
from app.bulk_client import bulk_export_accounts

app = FastAPI()

token_data = load_token()

@app.get("/")
def home():
    return {
        "message": "Python Salesforce Integration API"
    }

@app.get("/login")
def login():
    return RedirectResponse(
        get_authorization_url()
    )

@app.get("/callback")
def callback(code: str):
    token = exchange_code_for_token(code)

    token_data["access_token"] = token["access_token"]
    token_data["refresh_token"] = token["refresh_token"]
    token_data["instance_url"] = token["instance_url"]

    save_token(token_data)

    return {
        "message": "Salesforce authentication successful"
    }

@app.get("/refresh-token")
def refresh_token():

    if not token_data:
        return {
            "error": "Login first"
        }

    token = refresh_access_token(
        token_data["refresh_token"]
    )

    token_data["access_token"] = (
        token["access_token"]
    )
    
    save_token(token_data)

    return {
        "message": "Access token refreshed"
    }

@app.get("/accounts")
def accounts():

    if not token_data:
        return {
            "error": "Login first using /login"
        }

    return get_accounts(
        token_data["access_token"],
        token_data["instance_url"]
    )

@app.get("/accounts/export")
def export_accounts():

    if not token_data:
        return {
            "error": "Login first using /login"
        }

    return export_accounts_to_csv(
        token_data["access_token"],
        token_data["instance_url"]
    )

@app.get("/accounts/export/s3")
def export_accounts_s3():

    if not token_data:
        return {
            "error":
            "Login first using /login"
        }

    return export_accounts_to_s3(
        token_data["access_token"],
        token_data["instance_url"]
    )

@app.get("/accounts/bulk-export")
def export_accounts_with_bulk_api():
    if not token_data:
        return {
            "error": "Login first using /login"
        }

    return bulk_export_accounts(
        token_data["access_token"],
        token_data["instance_url"],
    )

@app.get("/data-quality/accounts")
def account_data_quality():

    if not token_data:
        return {
            "error": "Login first using /login"
        }

    return analyze_accounts(
        token_data["access_token"],
        token_data["instance_url"]
    )

def run_s3_export():

    export_accounts_to_s3(
        token_data["access_token"],
        token_data["instance_url"]
    )

@app.get("/accounts/export/s3/background")
def export_accounts_background(
        background_tasks: BackgroundTasks
):

    if not token_data:
        return {
            "error":
                "Login first using /login"
        }

    background_tasks.add_task(
        run_s3_export
    )

    return {
        "message":
            "Background export started"
    }