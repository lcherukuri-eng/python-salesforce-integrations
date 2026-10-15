import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

text = "Customer cannot login to their account"

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=text
)

embedding = response.data[0].embedding

print(f"Embedding dimensions: {len(embedding)}")
print(f"First 5 values: {embedding[:5]}")