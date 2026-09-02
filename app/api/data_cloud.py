from fastapi import APIRouter

from app.data_cloud_client import (
    get_data_cloud_accounts,
    get_account_by_name,
    search_account,
    get_opportunities,
    get_customer_context,
    get_customer_insights,
    get_account_pipeline_insights,
    get_ai_pipeline_summary,
    get_identity_resolution_summary,
    send_web_clickstream_event,
    get_website_engagements,
    get_identity_resolution_by_email,
    get_customer_360
)

router = APIRouter()

@router.get("/accounts")
def data_cloud_accounts():

    return get_data_cloud_accounts()

@router.get("/accounts/{account_name}")
def data_cloud_account(account_name: str):

    return get_account_by_name(
        account_name
    )

@router.get("/search")
def search_accounts(
    q: str
):

    return search_account(q)

@router.get("/opportunities")
def data_cloud_opportunities():

    return get_opportunities()

@router.get("/customer-context/{account_name}")
def customer_context(
    account_name: str
):

    return get_customer_context(
        account_name
    )

@router.get("/customer-insights/{account_name}")
def customer_insights(
    account_name: str
):

    return get_customer_insights(
        account_name
    )

@router.get("/calculated-insights")
def calculated_insights():

    return get_account_pipeline_insights()

@router.get("/top-pipeline-account")
def top_pipeline_account():

    insights = get_account_pipeline_insights()

    return max(
        insights,
        key=lambda x: x["total_pipeline_amount"]
    )


@router.get("/ai-pipeline-summary")
async def ai_pipeline_summary():

    return await get_ai_pipeline_summary()

@router.get("/identity-resolution/summary")
def identity_resolution_summary():
    return get_identity_resolution_summary()

@router.post("/clickstream/test")
def clickstream_test():
    return send_web_clickstream_event()

@router.get("/website-engagements")
def website_engagements():
    return get_website_engagements()

@router.get("/identity-resolution/{email}")
def identity_resolution_lookup(email: str):
    return get_identity_resolution_by_email(email)

@router.get("/customer-360/{email}")
def customer_360(email: str):
    return get_customer_360(email)