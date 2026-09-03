from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.services.claude_service import ask_claude
import json

router = APIRouter()


class DataActionRequest(BaseModel):
    customer_account_id: str = Field(alias="CustomerAccountId__c")
    opportunity_count: int = Field(alias="OpportunityCount__c")
    total_pipeline_amount: float = Field(alias="TotalPipelineAmount__c")


@router.post("/data-action")
async def data_action(payload: dict):

    print("=== DATA ACTION RECEIVED ===")
    print(json.dumps(payload, indent=2))

    return {
        "status": "success"
    }
