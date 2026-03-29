import logging
from typing import Any, Dict, List

import httpx
from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


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


async def _fallback_reasoning(messages: List[Dict[str, Any]]) -> str:
    fallback_model = "nvidia/nemotron-3-nano-30b-a3b:free"

    try:
        first = await _call_openrouter(
            {
                "model": fallback_model,
                "messages": messages,
                "reasoning": {"enabled": True},
            }
        )
        first_msg = first.get("choices", [{}])[0].get("message", {})
        if not first_msg:
            return ""

        chained_messages: List[Dict[str, Any]] = messages + [
            {
                "role": "assistant",
                "content": first_msg.get("content"),
                "reasoning_details": first_msg.get("reasoning_details"),
            },
            {
                "role": "user",
                "content": "Are you sure? Think carefully and finalize the answer.",
            },
        ]

        second = await _call_openrouter(
            {
                "model": fallback_model,
                "messages": chained_messages,
                "reasoning": {"enabled": True},
            }
        )
        second_msg = second.get("choices", [{}])[0].get("message", {})
        return second_msg.get("content") or first_msg.get("content") or ""
    except Exception as exc:  # pragma: no cover - network failure path
        logger.error("Fallback OpenRouter call failed: %s", exc)
        return ""


async def chat_completion(messages: List[Dict[str, Any]]) -> str:
    payload = {
        "model": "qwen/qwen3-next-80b-a3b-instruct:free",
        "messages": messages,
        "temperature": 0.4,
    }

    try:
        data = await _call_openrouter(payload)
        choices = data.get("choices", [])
        if choices:
            message = choices[0].get("message", {})
            content = message.get("content", "") or ""
            if content:
                return content
    except Exception as exc:  # pragma: no cover - network failure path
        logger.error("Primary OpenRouter call failed: %s", exc)

    return await _fallback_reasoning(messages)
