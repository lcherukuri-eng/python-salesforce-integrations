import time
from io import StringIO

import pandas as pd
import requests
import os
from app.s3_client import upload_file_to_s3

API_VERSION = os.getenv(
    "SF_API_VERSION",
    "v67.0"
)


def bulk_export_accounts(access_token, instance_url):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Create Bulk API query job
    jobs_url = (
        f"{instance_url}/services/data/"
        f"{API_VERSION}/jobs/query"
    )

    job_response = requests.post(
        jobs_url,
        headers=headers,
        json={
            "operation": "query",
            "query": "SELECT Id, Name FROM Account",
            "contentType": "CSV",
        },
        timeout=30,
    )
    job_response.raise_for_status()

    job_id = job_response.json()["id"]

    # Poll until processing finishes
    status_url = f"{jobs_url}/{job_id}"

    for _ in range(30):
        status_response = requests.get(
            status_url,
            headers=headers,
            timeout=30,
        )
        status_response.raise_for_status()

        state = status_response.json()["state"]

        if state == "JobComplete":
            break

        if state in {"Failed", "Aborted"}:
            raise RuntimeError(
                f"Bulk job {job_id} ended with state {state}"
            )

        time.sleep(2)
    else:
        raise TimeoutError(
            f"Bulk job {job_id} did not finish"
        )

    # Download CSV results
    results_url = f"{status_url}/results"

    results_response = requests.get(
        results_url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "text/csv",
        },
        timeout=30,
    )
    results_response.raise_for_status()

    dataframe = pd.read_csv(
        StringIO(results_response.text)
    )

    file_name = "accounts_bulk.csv"
    dataframe.to_csv(file_name, index=False)

    s3_result = upload_file_to_s3(file_name)

    return {
        "message": "Bulk account export completed and uploaded to S3",
        "job_id": job_id,
        "records_exported": len(dataframe),
        "file_name": file_name,
        "s3_result": s3_result,
    }