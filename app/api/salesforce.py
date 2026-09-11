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
async def accounts(
    token=Depends(get_sf_token)
):
    return await get_accounts(
        token["access_token"],
        token["instance_url"]
    )


@router.get("/accounts/export")
async def export_accounts(
    token = Depends(get_sf_token)
):

    return await export_accounts_to_csv(
        token["access_token"],
        token["instance_url"]
    )

@router.get("/accounts/export/s3")
async def export_accounts_s3(
    token = Depends(get_sf_token)
):

    return await export_accounts_to_s3(
        token["access_token"],
        token["instance_url"]
    )

@router.get("/accounts/bulk-export")
async def export_accounts_with_bulk_api(
    token = Depends(get_sf_token)
):   

    return await bulk_export_accounts(
        token["access_token"],
        token["instance_url"],
    )

@router.get("/data-quality/accounts")
async def account_data_quality(
    token = Depends(get_sf_token)
):

    return await analyze_accounts(
        token["access_token"],
        token["instance_url"]
    )

async def run_s3_export(token):

    await export_accounts_to_s3(
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