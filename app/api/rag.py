from fastapi import APIRouter
from app.vector.langgraph_rag import generate_graph_answer

router = APIRouter()

@router.get("")
async def rag_answer(query: str):
    result = await generate_graph_answer(query)

    return {
        "query": query,
        "answer": result["answer"]
    }