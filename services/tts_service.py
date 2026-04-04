import logging

import httpx

from config import get_settings


settings = get_settings()
logger = logging.getLogger(__name__)


async def synthesize(text: str) -> bytes:
    cleaned = text.strip()
    if not cleaned:
        cleaned = "Can you repeat that question?"

    payload = {
        "text": cleaned,
        "model_id": settings.elevenlabs_model_id,
        "voice_settings": {
            "stability": 0.45,
            "similarity_boost": 0.75,
        },
    }
    headers = {
        "xi-api-key": settings.elevenlabs_api_key,
        "Content-Type": "application/json",
        "Accept": "application/octet-stream",
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{settings.elevenlabs_voice_id}",
                params={"output_format": settings.elevenlabs_output_format},
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            return response.content
    except Exception as exc:  # pragma: no cover - network failure path
        logger.error("ElevenLabs synthesis failed: %s", exc)
        return cleaned.encode("utf-8")
