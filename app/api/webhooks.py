from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class DataActionRequest(BaseModel):
    customer_account_id: str
    opportunity_count: int
    total_pipeline_amount: float


@router.post("/data-action")
async def data_action(
    payload: DataActionRequest
):
    print("Data Action Received")
    print(payload)

    return {
        "status": "success",
        "payload": payload.model_dump()
    }