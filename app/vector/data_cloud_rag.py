from app.data_cloud_client import search_customer_support_documents

from app.services.claude_service import ask_claude

async def data_cloud_rag(
    question: str,
    top_k: int = 5
):
    documents = await search_customer_support_documents(
        question,
        top_k
    )

    context = build_data_cloud_context(documents)

    prompt = f"""
Answer the question using only the provided customer context.
If the context does not contain enough information, say that you don't have enough information.

Context:
{context}

Question:
{question}
"""

    answer = await ask_claude(prompt)

    return {
        "question": question,
        "answer": answer,
        "documents": documents
    }

def build_data_cloud_context(documents: list[dict]) -> str:
    context_parts = []

    for document in documents:
        context_parts.append(
            f"""
Source: {document["source"]}
Content: {document["chunk"]}
""".strip()
        )

    return "\n\n".join(context_parts)