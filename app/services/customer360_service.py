from app.data_cloud_client import (
    get_account_by_name,
    get_opportunities_by_account_id,
    get_customer_insights,
    get_pipeline_insight_by_account_id,
    get_unified_profile_by_email,
    get_website_engagements,
    get_datagraph_record,
    send_web_clickstream_event
)

from app.services.claude_service import ( 
    ask_claude
)
import asyncio

from app.logger import get_logger

logger = get_logger(__name__)

async def get_customer_360(email):

    profile_result, events_result = await asyncio.gather(
        get_unified_profile_by_email(email),
        get_website_engagements()
    )

    profile = []

    for row in profile_result.get("data", []):
        profile.append({
            "email": row[0],
            "party_id": row[1],
            "created_date": row[2]
        })

    events = []

    for row in events_result.get("data", []):
        events.append({
            "engagement_id": row[8],
            "page_url": row[6],
            "engagement_datetime": row[3],
            "engagement_type": row[4],
            "campaign_name": row[7]
        })

    return {
        "email": email,
        "profile_found": len(profile) > 0,
        "profile": profile,
        "total_events": len(events),
        "events": events
    }


async def get_account_360(account_name):

    account = await get_account_by_name(account_name)

    if "message" in account:
        return account

    opportunities, insights, pipeline_insight = (
        await asyncio.gather(
            get_opportunities_by_account_id(
                account["id"]
            ),
            get_customer_insights(
                account_name
            ),
            get_pipeline_insight_by_account_id(
                account["id"]
            )
        )
    )

    return {
        "account": account,
        "opportunities": opportunities,
        "pipeline_insight": pipeline_insight,
        "insights": insights
    }


async def get_ai_customer_360_summary(
    account_name
):

    customer_360 = await get_account_360(
        account_name
    )

    prompt = f"""
    You are a Salesforce Customer Success Analyst.

    Analyze the following Customer 360 data.

    Customer Data:
    {customer_360}

    Provide:

    1. Customer overview
    2. Pipeline assessment
    3. Revenue opportunities
    4. Risks
    5. Recommended next actions

    Use the actual numbers.
    Keep the response under 200 words.
    """

    summary = await ask_claude(
        prompt
    )

    return {
        "account_name": account_name,
        "summary": summary
    }


async def get_customer_graph_context(
    account_id: str
):
    return await get_datagraph_record(
        dg_name="AccountOnlyGraph",
        record_id=account_id
    )

async def log_customer_event(
    event_id: str,
    email: str,
    contact_id: str,
    event_type: str,
    product_sku: str,
    event_value: int,
    page_url: str,
    source_channel: str,
    campaign_id: str
):
    return await send_web_clickstream_event(
        event_id=event_id,
        email=email,
        contact_id=contact_id,
        event_type=event_type,
        product_sku=product_sku,
        event_value=event_value,
        page_url=page_url,
        source_channel=source_channel,
        campaign_id=campaign_id
    )


async def customer_interaction_summary(
    account_id: str,
    event_id: str,
    email: str,
    contact_id: str,
    event_type: str,
    product_sku: str,
    event_value: int
):
    customer = await get_customer_graph_context(account_id)

    event_result = await log_customer_event(
        event_id=event_id,
        email=email,
        contact_id=contact_id,
        event_type=event_type,
        product_sku=product_sku,
        event_value=event_value,
        page_url="https://mcp-demo.com",
        source_channel="mcp",
        campaign_id="MCP_DEMO"
    )

    prompt = f"""
    You are a Salesforce Customer Success Advisor.

    Customer Information:
    {customer}

    Recent Activity:
    {event_type}

    Product:
    {product_sku}

    Provide:
    1. Customer Overview
    2. Buying Intent Assessment
    3. Risk Indicators
    4. Next Best Action
    5. Recommended Follow-up Message
    """

    summary = await ask_claude(prompt)

    return {
        "customer": customer,
        "event_result": event_result,
        "summary": summary
    }

