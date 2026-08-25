import requests
import pandas as pd
from app.s3_client import upload_file_to_s3

def get_accounts(access_token, instance_url):

    query = "SELECT Id, Name FROM Account LIMIT 10"

    url = (
        f"{instance_url}"
        "/services/data/v65.0/query"
    )

    headers = {
        "Authorization":
            f"Bearer {access_token}"
    }

    response = requests.get(
        url,
        headers=headers,
        params={"q": query}
    )

    records = response.json()["records"]
    df = pd.DataFrame(records)

    # Remove Salesforce metadata column    
    if "attributes" in df.columns:
        df = df.drop(columns=["attributes"])
    return df.to_dict(orient="records")

def export_accounts_to_csv(
        access_token,
        instance_url
):

    query = "SELECT Id, Name FROM Account LIMIT 100"

    url = (
        f"{instance_url}"
        "/services/data/v65.0/query"
    )

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(
        url,
        headers=headers,
        params={"q": query}
    )

    records = response.json()["records"]

    df = pd.DataFrame(records)

    if "attributes" in df.columns:
        df = df.drop(columns=["attributes"])

    df.to_csv(
        "accounts.csv",
        index=False
    )

    return {
        "message": "accounts.csv generated successfully",
        "records_exported": len(df)
    }

def export_accounts_to_s3(
        access_token,
        instance_url
):

    query = (
        "SELECT Id, Name "
        "FROM Account LIMIT 100"
    )

    url = (
        f"{instance_url}"
        "/services/data/v65.0/query"
    )

    headers = {
        "Authorization":
            f"Bearer {access_token}"
    }

    response = requests.get(
        url,
        headers=headers,
        params={"q": query}
    )

    records = response.json()["records"]

    df = pd.DataFrame(records)

    if "attributes" in df.columns:
        df = df.drop(
            columns=["attributes"]
        )

    file_name = "accounts.csv"

    df.to_csv(
        file_name,
        index=False
    )

    upload_file_to_s3(file_name)

    return {
        "message":
            "accounts exported "
            "and uploaded to S3",
        "records_exported":
            len(df)
    }
