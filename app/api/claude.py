from fastapi import APIRouter
from app.services.claude_service import ask_claude

router = APIRouter()

@router.get("/ask")
def ask_ai(question: str):
    answer = ask_claude(question)

    return {
        "question": question,
        "answer": answer
    }