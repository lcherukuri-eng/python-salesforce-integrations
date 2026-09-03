from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class DataActionRequest(BaseModel):
    customer_account_id: str = Field(alias="CustomerAccountId__c")
    opportunity_count: int = Field(alias="OpportunityCount__c")
    total_pipeline_amount: float = Field(alias="TotalPipelineAmount__c")


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