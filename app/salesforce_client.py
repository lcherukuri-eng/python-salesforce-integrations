import requests
import pandas as pd
from app.s3_client import upload_file_to_s3
import os

API_VERSION = os.getenv(
    "SF_API_VERSION",
    "v67.0"
)

def get_accounts_dataframe(
        access_token,
        instance_url
):

    query = """
        SELECT
            Id,
            Name,
            Phone,
            Website,
            Industry
        FROM Account
        LIMIT 100
    """

    url = (
        f"{instance_url}"
        f"/services/data/{API_VERSION}"
        "/query"
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

    df = df.fillna("")

    return df

def get_accounts(
        access_token,
        instance_url
):

    df = get_accounts_dataframe(
        access_token,
        instance_url
    )

    return df.to_dict(
        orient="records"
    )

def export_accounts_to_csv(
        access_token,
        instance_url
):

    df = get_accounts_dataframe(
        access_token,
        instance_url
    )   

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

    df = get_accounts_dataframe(
        access_token,
        instance_url
    )

    file_name = "accounts_s3.csv"

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

def analyze_accounts(
        access_token,
        instance_url
):

    df = get_accounts_dataframe(
        access_token,
        instance_url
    )

    return {
        "total_accounts": int(len(df)),
        "missing_phone":
            int((df["Phone"] == "").sum()),
        "missing_website":
            int((df["Website"] == "").sum()),
        "missing_industry":
            int((df["Industry"] == "").sum()),
        "duplicate_names":
            int(df["Name"].duplicated().sum()),

        "phone_completeness_pct":
            round(
            (
                (len(df) - (df["Phone"] == "").sum())
                / len(df)
            ) * 100,
            2
        ),

        "website_completeness_pct":
            round(
            (
                (len(df) - (df["Website"] == "").sum())
                / len(df)
            ) * 100,
            2
        ),

        "industry_completeness_pct":
            round(
            (
                (len(df) - (df["Industry"] == "").sum())
                / len(df)
            ) * 100,
            2
        )

    }
