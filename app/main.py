from fastapi import (
    FastAPI,
    BackgroundTasks,
    Depends
)
from fastapi.responses import RedirectResponse
from app.security import verify_request
from app.dependencies import get_sf_token

from app.oauth_client import (
    get_authorization_url,
    exchange_code_for_token,
    refresh_access_token
)
from app.token_store import (
    load_token,
    save_token
)
from app.api.claude import router as claude_router
from app.api.salesforce import router as salesforce_router
from app.api.data_cloud import router as data_cloud_router
from app.api.webhooks import router as webhook_router
from app.api.customer360 import router as customer360_router

app = FastAPI()

app.include_router(
    claude_router,
    prefix="/claude",
    tags=["Claude"],
    dependencies=[Depends(verify_request)]
)

app.include_router(
    salesforce_router,
    prefix="/salesforce",
    tags=["Salesforce"],
    dependencies=[Depends(verify_request)]
)

app.include_router(
    data_cloud_router,
    prefix="/datacloud",
    tags=["Data Cloud"],
    dependencies=[Depends(verify_request)]
)

app.include_router(
    webhook_router,
    prefix="/webhooks",
    tags=["Webhooks"]
)

app.include_router(
    customer360_router,
    prefix="/customer360",
    tags=["Customer360"],
    dependencies=[Depends(verify_request)]
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


