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

def get_customer_360(email):

    profile_result = (
        get_unified_profile_by_email(
            email
        )
    )

    events_result = (
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


def get_account_360(account_name):

    account = get_account_by_name(account_name)

    if "message" in account:
        return account

    opportunities = (
        get_opportunities_by_account_id(
            account["id"]
        )
    )

    insights = (
        get_customer_insights(
            account_name
        )
    )

    pipeline_insight = (
        get_pipeline_insight_by_account_id(
            account["id"]
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

    customer_360 = get_account_360(
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


def get_customer_graph_context(
    account_id: str
):
    return get_datagraph_record(
        dg_name="AccountOnlyGraph",
        record_id=account_id
    )

def log_customer_event(
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
    return send_web_clickstream_event(
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

def get_customer_context_and_log_event(
    account_id: str,
    event_id: str,
    email: str,
    contact_id: str,
    event_type: str,
    product_sku: str,
    event_value: int
):
    
    customer = get_customer_graph_context(account_id)

    event_response = log_customer_event(
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

    return {
        "customer": customer,
        "event_result": event_response
    }

async def summarize_customer_context(
    account_id: str
):
    graph_data = get_customer_graph_context(account_id)

    prompt = f"""
    You are a Salesforce Customer Success Advisor.

    Customer Data:
    {graph_data}

    Provide:

    1. Customer Overview
    2. Account Type Analysis
    3. Potential Business Interest
    4. Suggested Next Best Action
    5. Recommended Follow-up Strategy
    """

    summary = await ask_claude(prompt)

    return {
        "customer_data": graph_data,
        "summary": summary
    }

async def customer_interaction_summary(
    account_id: str,
    event_id: str,
    email: str,
    contact_id: str,
    event_type: str,
    product_sku: str,
    event_value: int
):
    customer = get_customer_graph_context(account_id)

    event_result = log_customer_event(
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

