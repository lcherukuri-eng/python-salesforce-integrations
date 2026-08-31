from fastapi import (
    FastAPI,
    BackgroundTasks,
    Depends
)
from fastapi.responses import RedirectResponse
from app.security import verify_request

from app.oauth_client import (
    get_authorization_url,
    exchange_code_for_token,
    refresh_access_token
)
from app.oauth_client_credentials import (
    get_client_credentials_token
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
from app.data_cloud_client import (
    get_accounts,
    get_account_by_name,
    search_account,
    get_opportunities,
    get_customer_context,
    get_customer_insights,
    get_account_pipeline_insights,
    get_ai_pipeline_summary
)
from app.api.claude import router as claude_router


app = FastAPI(
    dependencies=[Depends(verify_request)]
)

app.include_router(
    claude_router,
    prefix="/claude",
    tags=["Claude"]
)

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

@app.get("/client-credentials-token")
def client_credentials_token():

    return get_client_credentials_token()

@app.get("/accounts/client-credentials")
def get_accounts_client_credentials():

    token = get_client_credentials_token()

    return get_accounts(
        token["access_token"],
        token["instance_url"]
    )
    
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

    token = get_client_credentials_token()

    return analyze_accounts(
        token["access_token"],
        token["instance_url"]
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

@app.get("/data-cloud/accounts")
def data_cloud_accounts():

    return get_accounts()

@app.get("/data-cloud/accounts/{account_name}")
def data_cloud_account(account_name: str):

    return get_account_by_name(
        account_name
    )

@app.get("/data-cloud/search")
def search_accounts(
    q: str
):

    return search_account(q)

@app.get("/data-cloud/opportunities")
def data_cloud_opportunities():

    return get_opportunities()

@app.get("/data-cloud/customer-context/{account_name}")
def customer_context(
    account_name: str
):

    return get_customer_context(
        account_name
    )

@app.get("/data-cloud/customer-insights/{account_name}")
def customer_insights(
    account_name: str
):

    return get_customer_insights(
        account_name
    )

@app.get("/data-cloud/calculated-insights")
def calculated_insights():

    return get_account_pipeline_insights()

@app.get("/data-cloud/top-pipeline-account")
def top_pipeline_account():

    insights = get_account_pipeline_insights()

    return max(
        insights,
        key=lambda x: x["total_pipeline_amount"]
    )

@app.get("/data-cloud/ai-pipeline-summary")
def ai_pipeline_summary():

    return get_ai_pipeline_summary()