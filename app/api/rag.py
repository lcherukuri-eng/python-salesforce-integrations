from fastapi import APIRouter
from app.vector.langchain_rag import generate_rag_answer

router = APIRouter()

@router.get("")
async def rag_answer(query: str):
    answer = await generate_rag_answer(query)

    return {
        "query": query,
        "answer": answer
    }