import os

from pgvector import Vector
from dotenv import load_dotenv
from openai import OpenAI
from pgvector.psycopg import register_vector

from app.database import get_connection

from app.services.claude_service import ( 
    ask_claude
)
import asyncio

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_embedding(text: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    return response.data[0].embedding


def store_document(customer_id: str, content: str):
    embedding = get_embedding(content)

    with get_connection() as conn:
        register_vector(conn)

        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO customer_documents
                    (customer_id, content, embedding)
                VALUES (%s, %s, %s)
                """,
                (customer_id, content, embedding),
            )

def search_documents(
    query: str,
    customer_id: str | None = None,
    limit: int = 3
):
    query_embedding = Vector(get_embedding(query))

    with get_connection() as conn:
        register_vector(conn)

        with conn.cursor() as cursor:

            if customer_id:
                cursor.execute(
                    """
                    SELECT
                        customer_id,
                        content,
                        embedding <=> %s AS distance
                    FROM customer_documents
                    WHERE customer_id = %s
                    ORDER BY distance
                    LIMIT %s
                    """,
                    (query_embedding, customer_id, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT
                        customer_id,
                        content,
                        embedding <=> %s AS distance
                    FROM customer_documents
                    ORDER BY distance
                    LIMIT %s
                    """,
                    (query_embedding, limit),
                )

            return cursor.fetchall()
        

def hybrid_search(query: str, limit: int = 3):
    query_embedding = Vector(get_embedding(query))

    with get_connection() as conn:
        register_vector(conn)
        
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    customer_id,
                    content,
                    1 - (embedding <=> %s) AS vector_similarity,
                    ts_rank(
                        search_vector,
                        plainto_tsquery('english', %s)
                    ) AS text_rank,
                    (
                        0.7 * (1 - (embedding <=> %s))
                        +
                        0.3 * ts_rank(
                            search_vector,
                            plainto_tsquery('english', %s)
                        )
                    ) AS hybrid_score
                FROM customer_documents
                ORDER BY hybrid_score DESC
                LIMIT %s
                """,
                (query_embedding, query, query_embedding, query, limit),
            )

            return cursor.fetchall()
        
        
def build_context(results):
    context = "\n".join(
        content
        for customer_id, content, vector_similarity, text_rank, hybrid_score
        in results
    )

    return context
    

async def generate_rag_answer(query: str):
    results = hybrid_search(query)

    context = build_context(results)

    prompt = f"""
    Answer the question using only the provided customer context.
    If the context does not contain enough information, say that you don't have enough information.

    Context:
    {context}

    Question:
    {query}
    """

    answer = await ask_claude(prompt)

    return answer
    

if __name__ == "__main__":
    answer = asyncio.run(
        generate_rag_answer(
            "What problem is the customer having with their account?"
        )
    )
    print(answer)
    