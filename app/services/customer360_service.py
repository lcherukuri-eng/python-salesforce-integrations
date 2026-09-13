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
import json

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

def calculate_health_score(insights: dict):
    BASE_SCORE = 50
    CLOSED_WON_POINTS = 20
    OPEN_PIPELINE_POINTS = 20
    OPPORTUNITY_POINTS = 10

    health_score = BASE_SCORE

    if insights["closed_won_amount"] > 0:
        health_score += CLOSED_WON_POINTS

    if insights["open_pipeline_amount"] > 100000:
        health_score += OPEN_PIPELINE_POINTS

    if insights["total_opportunities"] >= 3:
        health_score += OPPORTUNITY_POINTS

    health_score = min(health_score, 100)

    if health_score >= 80:
        health_status = "Healthy"
    elif health_score >= 60:
        health_status = "Attention Required"
    else:
        health_status = "At Risk"

    return {
        "health_score": health_score,
        "health_status": health_status
    }

def build_customer_timeline(
    opportunities: list
):
    timeline = []

    for opp in opportunities:
        timeline.append(
            {
                "event": f"{opp['stage']} - {opp['name']}",
                "amount": opp["amount"],
                "date": opp["close_date"]
            }
        )

    timeline = sorted(
        timeline,
        key=lambda x: x["date"],
        reverse=True
    )

    return timeline

def build_recent_activity(
    engagements: list
):
    activity_map = {
        "Product_View": "Viewed Product",
        "product_view": "Viewed Product",
        "quote_request": "Requested Quote"
    }

    engagements = sorted(
        engagements,
        key=lambda row: row[3],
        reverse=True
    )

    activities = []

    for row in engagements[:5]:
        event_type = row[4]

        activities.append(
            {
                "activity":
                    activity_map.get(
                        event_type,
                        event_type
                    ),
                "date": row[3],
                "channel": row[2]
            }
        )

    return activities

async def get_customer_intelligence(
    account_name: str
):
    customer_360 = await get_account_360(
        account_name
    )
    
    pipeline_insight = customer_360["pipeline_insight"]
    segment = (
        "High Pipeline Accounts"
        if (
            pipeline_insight["opportunity_count"] >= 1
            and pipeline_insight["total_pipeline_amount"] > 100000
        )
        else None
    )

    website_engagements = await get_website_engagements()
    recent_activity = build_recent_activity(
        website_engagements["data"]
    )


    opportunities = customer_360["opportunities"]
    timeline = build_customer_timeline(
        opportunities
    )

    insights = customer_360["insights"]    

    health_metrics = calculate_health_score(
        insights
    )   

    prompt = f"""
    You are a Customer Success Analyst.

    Customer:
    {customer_360}

    Segment:
    {segment}

    Timeline:
    {timeline}

    Health Score:
    {health_metrics["health_score"]}

    Health Status:
    {health_metrics['health_status']}

    Recent Activity:
    {recent_activity}

    Return ONLY valid JSON.

    Format:

    {{
        "customer_overview": "",
        "pipeline_assessment": "",
        "risk_level": "",
        "confidence": "",
        "top_opportunity": "",
        "recommended_action": ""
    }}

    Determine:
    
    - risk_level: Low, Medium, High
    - confidence: Low, Medium, High

    Base your assessment on:
    - Health Score
    - Segment Membership
    - Pipeline Amount
    - Opportunity Stages
    - Recent Activity
    
    Use actual values from the data.

    Do not return markdown.
    Do not return explanations.
    Do not wrap in code blocks.
    Return JSON only.
    """

    ai_analysis = await ask_claude(
        prompt
    )

    # Remove markdown code fence if Claude adds it
    ai_analysis = ai_analysis.strip()

    if ai_analysis.startswith("```json"):
        ai_analysis = ai_analysis.replace("```json","",1)

    if ai_analysis.endswith("```"):
        ai_analysis = ai_analysis[:-3]

    ai_analysis = ai_analysis.strip()

    try:
        ai_analysis = json.loads(ai_analysis)
    except Exception as e:
        print("JSON Parse Error:", e)


    nba_prompt = f"""
    You are a Customer Success Manager.

    Customer:
    {customer_360}

    Segment:
    {segment}

    Health Score:
    {health_metrics["health_score"]}

    Timeline:
    {timeline}

    Recent Activity:
    {recent_activity}

    Provide ONE specific next best action.

    Return only one sentence.
    """

    priority_action = await ask_claude(
        nba_prompt
    )

    return {
        "account_name": account_name,
        "segment": segment,
        "health_score": health_metrics["health_score"],
        "health_status": health_metrics["health_status"],
        "timeline": timeline,
        "recent_activity": recent_activity,
        "priority_action": priority_action,
        "ai_analysis": ai_analysis,
        "customer_360": customer_360        
    }
