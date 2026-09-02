import os
from anthropic import AsyncAnthropic

client = AsyncAnthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

async def ask_claude(prompt: str) -> str:

    response = await client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    text_parts = []

    for block in response.content:
        if hasattr(block, "text"):
            text_parts.append(block.text)

    return "\n".join(text_parts)