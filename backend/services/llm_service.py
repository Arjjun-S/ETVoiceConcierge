from openai import AsyncOpenAI
from config import get_settings

settings = get_settings()
client = AsyncOpenAI(api_key=settings.openai_api_key)


async def chat_completion(messages: list[dict]) -> str:
    # Placeholder: configure function-calling tools before production use
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.4,
    )
    return response.choices[0].message.content or ""
