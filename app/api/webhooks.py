from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class DataActionRequest(BaseModel):
    email: str
    event_type: str
    score: int


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