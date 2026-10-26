from fastapi import APIRouter
from app.vector.langgraph_rag import generate_graph_answer

from app.vector.data_cloud_rag import data_cloud_rag

router = APIRouter()

@router.get("")
async def rag_answer(query: str):
    result = await generate_graph_answer(query)

    return {
        "query": query,
        "answer": result["answer"]
    }

@router.get("/data-cloud")
async def data_cloud_rag_answer(
    query: str,
    top_k: int = 5
):
    return await data_cloud_rag(
        query,
        top_k
    )