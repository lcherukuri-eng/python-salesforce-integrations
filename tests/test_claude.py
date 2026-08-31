import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# models = client.models.list()
# for model in models.data:
#     print(model.id)

response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=100,
    messages=[
        {
            "role": "user",
            "content": "Say hello and tell me one fact about Salesforce."
        }
    ]
)

print(response.content[0].text)