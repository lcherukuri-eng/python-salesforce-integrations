from fastapi import APIRouter

from app.services.customer360_service import (
    get_customer_360,
    get_account_360,
    get_ai_customer_360_summary
)

router = APIRouter()


@router.get("/customer-360/{email}")
def customer_360(email: str):
    return get_customer_360(email)


@router.get("/customer-360/account/{account_name}")
def account_customer_360(account_name: str):
    return get_account_360(account_name)


@router.get(
    "/customer-360/account/{account_name}/summary"
)
async def account_customer_360_summary(
    account_name: str
):
    return await get_ai_customer_360_summary(
        account_name
    )