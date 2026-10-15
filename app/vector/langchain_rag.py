from langchain_core.prompts import PromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from app.vector.vector_store import hybrid_search
from langchain_core.retrievers import BaseRetriever

import asyncio

from dotenv import load_dotenv

load_dotenv()

prompt = PromptTemplate.from_template(
    """
    Answer the question using only the provided customer context.
    If the context does not contain enough information, say that you don't have enough information.

    Context:
    {context}

    Question:
    {question}
    """
)

model = ChatAnthropic(
    model="claude-sonnet-5",
    max_tokens=1000,
)

parser = StrOutputParser()

chain = prompt | model | parser


def results_to_documents(results):
    documents = []

    for customer_id, content, vector_similarity, text_rank, hybrid_score in results:
        document = Document(
            page_content=content,
            metadata={
                "customer_id": customer_id,
                "vector_similarity": vector_similarity,
                "text_rank": text_rank,
                "hybrid_score": hybrid_score,
            },
        )

        documents.append(document)

    return documents


class HybridRetriever(BaseRetriever):

    def _get_relevant_documents(self, query: str):
        results = hybrid_search(query)

        return results_to_documents(results)
    

async def generate_rag_answer(query: str):
    retriever = HybridRetriever()
    
    documents = await retriever.ainvoke(query)

    context = "\n".join(
        document.page_content
        for document in documents
    )

    answer = await chain.ainvoke(
        {
            "context": context,
            "question": query
        }
    )
    return answer

if __name__ == "__main__":
    query = "What problem is the customer having with their account?"

    answer = asyncio.run(
        generate_rag_answer(query)
    )

    print(answer)

