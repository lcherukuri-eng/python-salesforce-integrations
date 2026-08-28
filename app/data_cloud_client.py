import requests

from app.oauth_client_credentials import (
    get_client_credentials_token
)


def get_data_cloud_token():
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
    return response.json()


def run_query(sql):
    dc_token = get_data_cloud_token()

    tenant_url = dc_token["instance_url"]

    if not tenant_url.startswith("https://"):
        tenant_url = "https://" + tenant_url

    response = requests.post(
        tenant_url + "/api/v2/query",
        json={"sql": sql},
        headers={
            "Authorization":
                f"Bearer {dc_token['access_token']}",
            "Content-Type": "application/json"
        },
        timeout=30
    )

    response.raise_for_status()
    return response.json()


def get_accounts():

    sql = """
    SELECT
        "Id__c",
        "Name__c",
        "Industry__c",
        "Phone__c"
    FROM "Account_Home__dll"
    LIMIT 10
    """

    result = run_query(sql)

    accounts = []

    for row in result["data"]:

        accounts.append({
            "id": row[0],
            "name": row[1],
            "industry": row[2],
            "phone": row[3]
        })

    return accounts


def get_account_by_name(account_name):

    sql = f"""
    SELECT
        "Id__c",
        "Name__c",
        "Industry__c",
        "Phone__c",
        "Description__c"
    FROM "Account_Home__dll"
    WHERE "Name__c" = '{account_name}'
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
        "industry": row[2],
        "phone": row[3],
        "description": row[4]
    }

def search_account(account_name):

    sql = f"""
    SELECT
        "Id__c",
        "Name__c",
        "Industry__c",
        "Phone__c",
        "Description__c"
    FROM "Account_Home__dll"
    WHERE lower("Name__c")
        LIKE lower('%{account_name}%')
    LIMIT 10
    """

    result = run_query(sql)

    accounts = []

    for row in result["data"]:
        accounts.append({
            "id": row[0],
            "name": row[1],
            "industry": row[2],
            "phone": row[3],
            "description": row[4]
        })

    return accounts

def get_opportunities():

    sql = """
    SELECT
        "Id__c",
        "Name__c",
        "Amount__c",
        "StageName__c",
        "CloseDate__c",
        "AccountId__c"
    FROM "Opportunity_Home__dll"
    LIMIT 10
    """

    result = run_query(sql)

    opportunities = []

    for row in result["data"]:

        opportunities.append({
            "id": row[0],
            "name": row[1],
            "amount": row[2],
            "stage": row[3],
            "close_date": row[4],
            "account_id": row[5]
        })

    return opportunities

def get_opportunities_by_account_id(account_id):

    sql = f"""
    SELECT
        "Id__c",
        "Name__c",
        "Amount__c",
        "StageName__c",
        "CloseDate__c",
        "AccountId__c"
    FROM "Opportunity_Home__dll"
    WHERE "AccountId__c" = '{account_id}'
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

    context = get_customer_context(
        account_name
    )

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
        "account_name":
            context["account"]["name"],

        "industry":
            context["account"]["industry"],

        "total_opportunities":
            len(context["opportunities"]),

        "total_pipeline":
            total_pipeline,

        "closed_won_amount":
            closed_won_amount,

        "open_pipeline_amount":
            open_pipeline_amount
    }

    