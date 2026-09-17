from fastapi import APIRouter, Depends
from app.dependencies import get_claude_service

router = APIRouter()

@router.get("/ask")
async def ask_ai(
    question: str,
    cluade_service=Depends(get_claude_service)
):
    answer = await cluade_service(question)

    return {
        "question": question,
        "answer": answer
    }