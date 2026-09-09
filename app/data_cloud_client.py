import requests

from app.oauth_client_credentials import (
    get_client_credentials_token
)
from app.services.claude_service import ask_claude
from app.core.request_helper import data_cloud_request
from datetime import datetime, timezone
from app.core.token_cache import TokenCache
from app.logger import get_logger

logger = get_logger(__name__)

data_cloud_token_cache = TokenCache()

def refresh_data_cloud_token():
    return get_data_cloud_token(
        force_refresh=True
    )


def get_data_cloud_token(
    force_refresh: bool = False
):
    if force_refresh:
        logger.info(
            "Force-refreshing Data Cloud token"
        )
        data_cloud_token_cache.clear()

    cached_token = data_cloud_token_cache.get_token()

    if cached_token:
        logger.info("Using cached Data Cloud token")
        return cached_token

    logger.info("Requesting Data Cloud token")

    core_token = get_client_credentials_token()

    payload = {
        "grant_type":
            "urn:salesforce:grant-type:external:cdp",
        "subject_token":
            core_token["access_token"],
        "subject_token_type":
            "urn:ietf:params:oauth:token-type:access_token",
        "dataspace": "default"
    }

    response = requests.post(
        core_token["instance_url"] + "/services/a360/token",
        data=payload,
        headers={
            "Content-Type":
                "application/x-www-form-urlencoded"
        },
        timeout=30
    )

    response.raise_for_status()

    token_data = response.json()

    logger.info("New Data Cloud token received")

    data_cloud_token_cache.set_token(
        token_data,
        token_data["expires_in"]   # 7200 seconds
    )

    return token_data


def run_query(sql):
    dc_token = get_data_cloud_token()

    tenant_url = dc_token["instance_url"]

    if not tenant_url.startswith("https://"):
        tenant_url = "https://" + tenant_url

    response = data_cloud_request(
        "POST",
        tenant_url + "/api/v2/query",
        headers={
            "Authorization":
                f"Bearer {dc_token['access_token']}",
            "Content-Type": "application/json"
        },
        json={"sql": sql},
        refresh_token=refresh_data_cloud_token
    )

    response.raise_for_status()
    return response.json()


def get_data_cloud_accounts():

    sql = """
    SELECT
        "ssot__Id__c",
        "ssot__Name__c",
        "ssot__Description__c",
        "ssot__AccountType__c"
    FROM "ssot__Account__dlm"
    LIMIT 10
    """

    result = run_query(sql)    

    accounts = []

    for row in result["data"]:

        accounts.append({
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "account_type": row[3]
    })

    return accounts


def get_account_by_name(account_name):

    sql = f"""
    SELECT
        "ssot__Id__c",
        "ssot__Name__c",
        "ssot__Description__c",
        "ssot__AccountType__c"
    FROM "ssot__Account__dlm"
    WHERE "ssot__Name__c" = '{account_name}'
    """

    result = run_query(sql)

    if not result["data"]:
        return {
            "message": "Account not found"
        }

    row = result["data"][0]

    return {
        "id": row[0],
        "name": row[1],
        "description": row[2],
        "account_type": row[3]
    }

def search_account(account_name):

    sql = f"""
    SELECT
        "ssot__Id__c",
        "ssot__Name__c",
        "ssot__Description__c",
        "ssot__AccountType__c"
    FROM "ssot__Account__dlm"
    WHERE lower("ssot__Name__c")
        LIKE lower('%{account_name}%')
    LIMIT 10
    """

    result = run_query(sql)

    accounts = []

    for row in result["data"]:
        accounts.append({
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "account_type": row[3]
        })

    return accounts


def get_opportunities():

    sql = """
    SELECT
        "ssot__Id__c",
        "ssot__Name__c",
        "ssot__TotalAmount__c",
        "ssot__OpportunityStageId__c",
        "ssot__CloseDate__c",
        "ssot__CustomerAccountId__c"
    FROM "ssot__Opportunity__dlm"
    LIMIT 10
    """

    result = run_query(sql)

    opportunities = []

    for row in result["data"]:

        opportunities.append({
            "id": row[0],
            "name": row[1],
            "amount": float(row[2]) if row[2] else 0,
            "stage": row[3],
            "close_date": row[4],
            "account_id": row[5]
        })

    return opportunities

def get_opportunities_by_account_id(account_id):

    sql = f"""
    SELECT
        "ssot__Id__c",
        "ssot__Name__c",
        "ssot__TotalAmount__c",
        "ssot__OpportunityStageId__c",
        "ssot__CloseDate__c",
        "ssot__CustomerAccountId__c"
    FROM "ssot__Opportunity__dlm"
    WHERE "ssot__CustomerAccountId__c" = '{account_id}'
    """

    result = run_query(sql)

    opportunities = []

    for row in result["data"]:

        opportunities.append({
            "id": row[0],
            "name": row[1],
            "amount": float(row[2]) if row[2] else 0,
            "stage": row[3],
            "close_date": row[4],
            "account_id": row[5]
        })

    return opportunities

def get_customer_context(account_name):

    account = get_account_by_name(
        account_name
    )

    opportunities = (
        get_opportunities_by_account_id(
            account["id"]
        )
    )

    return {
        "account": account,
        "opportunities": opportunities
    }

def get_customer_insights(account_name):

    context = get_customer_context(account_name)

    closed_won_amount = sum(
        opp["amount"]
        for opp in context["opportunities"]
        if opp["stage"] == "Closed Won"
    )

    open_pipeline_amount = sum(
        opp["amount"]
        for opp in context["opportunities"]
        if opp["stage"] != "Closed Won"
    )

    total_pipeline = sum(
        opp["amount"]
        for opp in context["opportunities"]
    )

    return {
        "account_name": context["account"]["name"],
        "description": context["account"]["description"],
        "account_type": context["account"]["account_type"],
        "total_opportunities": len(context["opportunities"]),
        "total_pipeline": total_pipeline,
        "closed_won_amount": closed_won_amount,
        "open_pipeline_amount": open_pipeline_amount
    }

def get_account_pipeline_insights():

    sql = """
    SELECT
        ci."CustomerAccountId__c",
        a."ssot__Name__c",
        ci."OpportunityCount__c",
        ci."TotalPipelineAmount__c"
    FROM "AccountPipelineInsight__cio" ci
    JOIN "ssot__Account__dlm" a
    ON ci."CustomerAccountId__c" = a."ssot__Id__c"
    LIMIT 10
    """

    result = run_query(sql)

    insights = []

    for row in result["data"]:
        insights.append({
            "account_id": row[0],
            "account_name": row[1],
            "opportunity_count": int(float(row[2])),
            "total_pipeline_amount": float(row[3])
        })

    return insights
    
async def get_ai_pipeline_summary():

    insights = get_account_pipeline_insights()

    prompt = f"""
    You are a Salesforce Revenue Operations Analyst.

    Analyze the following pipeline metrics and produce an executive summary.

    Pipeline Data:
    {insights}

    Provide:
    1. Top account by pipeline value
    2. Accounts requiring attention
    3. Pipeline risks and opportunities
    4. Recommended next actions

    Use quantitative evidence from the data.
    Include dollar amounts when relevant.
    Use professional business language.
    Keep the response under 200 words.
    """

    return {
        "summary": await ask_claude(prompt)
    }

def get_unified_individuals():
    """
    Returns Unified Individuals created by
    Data Cloud Identity Resolution.
    """

    sql = """
    SELECT
        ssot__FirstName__c,
        ssot__LastName__c,
        ssot__PersonName__c,
        ssot__BirthDate__c,
        ssot__CreatedDate__c,
        ssot__LastModifiedDate__c
    FROM UnifiedIndividual__dlm
    LIMIT 100
    """

    return run_query(sql)


def get_identity_resolution_summary():

    result = get_unified_individuals()

    profiles = []

    for row in result.get("data", []):
        profiles.append({
            "first_name": row[0],
            "last_name": row[1],
            "full_name": row[2],
            "birth_date": row[3],
            "created_date": row[4],
            "last_modified_date": row[5]
        })

    return {
        "total_unified_profiles": len(profiles),
        "profiles": profiles
    }

def send_web_clickstream_event(
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
    dc_token = get_data_cloud_token()

    tenant_url = dc_token["instance_url"]

    if not tenant_url.startswith("https://"):
        tenant_url = "https://" + tenant_url

    payload = {
        "data": [
            {
                "event_id": event_id,
                "email": email,
                "contact_id": contact_id,
                "event_type": event_type,
                "product_sku": product_sku,
                "event_value": event_value,
                "page_url": page_url,
                "source_channel": source_channel,
                "campaign_id": campaign_id,
                "event_timestamp": datetime.now(
                    timezone.utc
                ).strftime("%Y-%m-%dT%H:%M:%S.000Z")
            }
        ]
    }

    response = requests.post(
        tenant_url +
        "/api/v1/ingest/sources/Web_Clickstream_API/WebClickstreamEvent",
        json=payload,
        headers={
            "Authorization": f"Bearer {dc_token['access_token']}",
            "Content-Type": "application/json"
        },
        timeout=30
    )

    response.raise_for_status()

    return response.json()

def get_website_engagements():   

    sql = """
    SELECT
        ssot__DataSourceId__c,
        ssot__DataSourceObjectId__c,
        ssot__EngagementChannelId__c,
        ssot__EngagementDateTm__c,
        ssot__EngagementTypeId__c,
        KQ_Id__c,
        ssot__PageURL__c,
        ssot__UtmCampaignName__c,
        ssot__Id__c
    FROM ssot__WebsiteEngagement__dlm
    LIMIT 100
    """

    return run_query(sql)

def get_unified_profile_by_email(email):   

    sql = f"""
    SELECT
        ssot__EmailAddress__c,
        ssot__PartyId__c,
        ssot__CreatedDate__c
    FROM UnifiedContactPointEmail__dlm
    WHERE ssot__EmailAddress__c = '{email}'
    """

    return run_query(sql)

def get_identity_resolution_by_email(email):

    result = get_unified_profile_by_email(email)

    profiles = []

    for row in result.get("data", []):
        profiles.append({
            "email": row[0],
            "party_id": row[1],
            "created_date": row[2]
        })

    return {
        "email": email,
        "match_found": len(profiles) > 0,
        "profiles": profiles
    }


def get_pipeline_insight_by_account_id(account_id):

    sql = f"""
    SELECT
        "CustomerAccountId__c",
        "OpportunityCount__c",
        "TotalPipelineAmount__c"
    FROM "AccountPipelineInsight__cio"
    WHERE "CustomerAccountId__c" = '{account_id}'
    """

    result = run_query(sql)

    if not result["data"]:
        return None

    row = result["data"][0]

    return {
        "account_id": row[0],
        "opportunity_count": int(float(row[1])),
        "total_pipeline_amount": float(row[2])
    }


def get_datagraph_record(
    dg_name: str,
    record_id: str,
    live: bool = True
):
    dc_token = get_data_cloud_token()

    tenant_url = dc_token["instance_url"]

    if not tenant_url.startswith("https://"):
        tenant_url = "https://" + tenant_url

    endpoint = (
        f"{tenant_url}/api/v1/dataGraph/"
        f"{dg_name}/{record_id}"
    )

    print(endpoint)

    response = requests.get(
        endpoint,
        headers={
            "Authorization": f"Bearer {dc_token['access_token']}",
            "Content-Type": "application/json"
        },
        params={
            "live": str(live).lower()
        },
        timeout=30
    )

    print("STATUS:", response.status_code)
    print("BODY:", response.text)

    return {
        "status_code": response.status_code,
        "response": response.text
    }

