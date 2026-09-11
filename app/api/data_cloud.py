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
    get_identity_resolution_by_email    
)

router = APIRouter()

@router.get("/accounts")
async def data_cloud_accounts():

    return await get_data_cloud_accounts()

@router.get("/accounts/{account_name}")
async def data_cloud_account(account_name: str):

    return await get_account_by_name(
        account_name
    )

@router.get("/search")
async def search_accounts(
    q: str
):
    return await search_account(q)

@router.get("/opportunities")
async def data_cloud_opportunities():

    return await get_opportunities()

@router.get("/customer-context/{account_name}")
async def customer_context(
    account_name: str
):

    return await get_customer_context(
        account_name
    )

@router.get("/customer-insights/{account_name}")
async def customer_insights(
    account_name: str
):
    return await get_customer_insights(
        account_name
    )

@router.get("/calculated-insights")
async def calculated_insights():

    return await get_account_pipeline_insights()

@router.get("/top-pipeline-account")
async def top_pipeline_account():

    insights = await get_account_pipeline_insights()

    return max(
        insights,
        key=lambda x: x["total_pipeline_amount"]
    )


@router.get("/ai-pipeline-summary")
async def ai_pipeline_summary():

    return await get_ai_pipeline_summary()

@router.get("/identity-resolution/summary")
async def identity_resolution_summary():
    return await get_identity_resolution_summary()

@router.post("/clickstream/test")
async def clickstream_test():
    return await send_web_clickstream_event()

@router.get("/website-engagements")
async def website_engagements():
    return await get_website_engagements()

@router.get("/identity-resolution/{email}")
async def identity_resolution_lookup(email: str):
    return await get_identity_resolution_by_email(email)
