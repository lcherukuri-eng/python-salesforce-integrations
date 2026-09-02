from fastapi import (
    APIRouter,
    Depends,
    BackgroundTasks
)

from app.dependencies import get_sf_token

from app.salesforce_client import (
    get_accounts,
    export_accounts_to_csv,
    export_accounts_to_s3,
    analyze_accounts
)

from app.bulk_client import bulk_export_accounts

router = APIRouter()

@router.get("/accounts")
def accounts(
    token=Depends(get_sf_token)
):
    return get_accounts(
        token["access_token"],
        token["instance_url"]
    )


@router.get("/accounts/export")
def export_accounts(
    token = Depends(get_sf_token)
):

    return export_accounts_to_csv(
        token["access_token"],
        token["instance_url"]
    )

@router.get("/accounts/export/s3")
def export_accounts_s3(
    token = Depends(get_sf_token)
):

    return export_accounts_to_s3(
        token["access_token"],
        token["instance_url"]
    )

@router.get("/accounts/bulk-export")
def export_accounts_with_bulk_api(
    token = Depends(get_sf_token)
):   

    return bulk_export_accounts(
        token["access_token"],
        token["instance_url"],
    )

@router.get("/data-quality/accounts")
def account_data_quality(
    token = Depends(get_sf_token)
):

    return analyze_accounts(
        token["access_token"],
        token["instance_url"]
    )

def run_s3_export(token):

    export_accounts_to_s3(
        token["access_token"],
        token["instance_url"]
    )

@router.get("/accounts/export/s3/background")
def export_accounts_background(
        background_tasks: BackgroundTasks,
        token=Depends(get_sf_token)
):    

    background_tasks.add_task(
        run_s3_export,
        token
    )

    return {
        "message":
            "Background export started"
    }