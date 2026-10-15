from typing import TypedDict
from langchain_core.documents import Document
from app.vector.langchain_rag import HybridRetriever
from app.vector.langchain_rag import HybridRetriever, chain

from langgraph.graph import StateGraph, START, END

import asyncio

class RAGState(TypedDict):
    question: str
    documents: list[Document]
    answer: str

retriever = HybridRetriever()

async def retrieve(state: RAGState):
    question = state["question"]

    documents = await retriever.ainvoke(question)

    return {
        "documents": documents
    }

async def generate(state: RAGState):
    question = state["question"]
    documents = state["documents"]

    context = "\n".join(
        document.page_content
        for document in documents
    )

    answer = await chain.ainvoke(
        {
            "context": context,
            "question": question
        }
    )

    return {
        "answer": answer
    }

async def fallback(state: RAGState):
    return {
        "answer": "I couldn't find relevant customer information for this question."
    }

def route_after_retrieval(state: RAGState):
    documents = state["documents"]

    if not documents:
        return "fallback"

    best_score = documents[0].metadata["hybrid_score"]

    if best_score >= 0.3:
        return "generate"

    return "fallback"


builder = StateGraph(RAGState)

builder.add_node("retrieve", retrieve)
builder.add_node("generate", generate)
builder.add_node("fallback", fallback)

builder.add_conditional_edges(
    "retrieve",
    route_after_retrieval,
    {
        "generate": "generate",
        "fallback": "fallback"
    }
)

builder.add_edge(START, "retrieve")
builder.add_edge("generate", END)
builder.add_edge("fallback", END)

graph = builder.compile()

async def generate_graph_answer(query: str):
    result = await graph.ainvoke(
        {
            "question": query
        }
    )

    return result

async def main():
    result = await generate_graph_answer(
        "What is Kubernetes container orchestration?"
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())
