import logging
from typing import Any, Dict, List

import httpx
from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


def _extract_content(data: Dict[str, Any]) -> str:
    choices = data.get("choices", [])
    if not choices:
        return ""

    message = choices[0].get("message", {})
    return (message.get("content", "") or "").strip()


def _headers() -> Dict[str, str]:
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }
    if settings.openrouter_referer:
        headers["HTTP-Referer"] = settings.openrouter_referer
    if settings.openrouter_title:
        headers["X-OpenRouter-Title"] = settings.openrouter_title
    return headers


async def _call_openrouter(payload: Dict[str, Any]) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=payload,
            headers=_headers(),
        )
        response.raise_for_status()
        return response.json()


async def _call_with_model(model: str, messages: List[Dict[str, Any]]) -> str:
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.3,
    }
    data = await _call_openrouter(payload)
    return _extract_content(data)


async def chat_completion(messages: List[Dict[str, Any]]) -> str:
    models = [
        settings.openrouter_model,
        settings.openrouter_fallback_model,
        "meta-llama/llama-3.3-70b-instruct:free",
    ]

    for model in models:
        if not model:
            continue

        try:
            content = await _call_with_model(model, messages)
            if content:
                return content
        except Exception as exc:  # pragma: no cover - network failure path
            logger.error("OpenRouter call failed for model %s: %s", model, exc)

    return ""
