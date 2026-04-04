import logging

import httpx

from config import get_settings


settings = get_settings()
logger = logging.getLogger(__name__)


async def transcribe_chunk(audio_chunk: bytes) -> str:
    if not audio_chunk:
        return ""

    headers = {
        "Authorization": f"Token {settings.deepgram_api_key}",
        "Content-Type": f"audio/{settings.deepgram_encoding}",
    }
    params = {
        "model": settings.deepgram_model,
        "language": "en",
        "punctuate": "true",
        "smart_format": "true",
        "encoding": settings.deepgram_encoding,
        "sample_rate": str(settings.deepgram_sample_rate),
    }

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                "https://api.deepgram.com/v1/listen",
                params=params,
                headers=headers,
                content=audio_chunk,
            )
            response.raise_for_status()

        data = response.json()
        channels = data.get("results", {}).get("channels", [])
        if not channels:
            return ""

        alternatives = channels[0].get("alternatives", [])
        if not alternatives:
            return ""

        return (alternatives[0].get("transcript") or "").strip()
    except Exception as exc:  # pragma: no cover - network failure path
        logger.error("Deepgram transcription failed: %s", exc)
        return ""
