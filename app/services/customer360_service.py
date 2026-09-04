from app.data_cloud_client import (
    get_account_by_name,
    get_opportunities_by_account_id,
    get_customer_insights,
    get_pipeline_insight_by_account_id,
    get_unified_profile_by_email,
    get_website_engagements
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
