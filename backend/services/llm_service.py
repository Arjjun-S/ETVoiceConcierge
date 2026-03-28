import httpx
from config import get_settings

settings = get_settings()


async def chat_completion(messages: list[dict]) -> str:
    # Call OpenRouter with the requested model; keep optional headers for ranking
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }
    if settings.openrouter_referer:
        headers["HTTP-Referer"] = settings.openrouter_referer
    if settings.openrouter_title:
        headers["X-OpenRouter-Title"] = settings.openrouter_title

    payload = {
        "model": "qwen/qwen3-next-80b-a3b-instruct:free",
        "messages": messages,
        "temperature": 0.4,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=payload,
            headers=headers,
        )
        response.raise_for_status()
        data = response.json()

    choices = data.get("choices", [])
    if not choices:
        return ""
    message = choices[0].get("message", {})
    return message.get("content", "") or ""
