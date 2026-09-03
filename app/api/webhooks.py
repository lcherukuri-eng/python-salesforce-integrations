from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.services.claude_service import ask_claude
import json
from app.models.data_action_models import (
    DataActionPayload,
    PipelineInsight
)
from app.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/data-action")
async def data_action(
    payload: DataActionPayload
):

    logger.info("=== DATA ACTION RECEIVED ===")

    for event in payload.events:

        current_values = PipelineInsight.model_validate(
            json.loads(event.PayloadCurrentValue)
        )

        previous_values = PipelineInsight.model_validate(
            json.loads(event.PayloadPrevValue)
        )

        logger.info(
            "Action=%s | Account=%s | CurrentPipeline=%s | "
            "PreviousPipeline=%s | OpportunityCount=%s | ChangeType=%s",
            event.ActionDeveloperName,
            current_values.customer_account_id,
            current_values.total_pipeline_amount,
            previous_values.total_pipeline_amount,
            current_values.opportunity_count,
            event.EventPrompt,
        )
        

    return {
        "status": "success"
    }