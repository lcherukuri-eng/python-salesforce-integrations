import os

from fastapi import Header, HTTPException

def verify_request(
    x_api_key: str = Header(None),
    x_sf_org_id: str = Header(None)
):
    expected_key = os.getenv("API_KEY")
    expected_org = os.getenv("SF_ORG_ID")

    if (
        x_api_key != expected_key
        or x_sf_org_id != expected_org
    ):
        raise HTTPException(
            status_code=403,
            detail="Unauthorized"
        )
