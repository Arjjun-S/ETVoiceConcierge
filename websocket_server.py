import base64
import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from config import get_settings
from agents.orchestrator import run_agent_pipeline
from services.stt_service import transcribe_chunk
from services.tts_service import synthesize

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)


def _parse_text_frame(
    frame_text: str,
) -> tuple[bytes | None, str | None, bool, str | None, bool]:
    """
    Returns: (audio_chunk, user_text, should_stop, call_sid_override, json_transport)
    """
    try:
        payload = json.loads(frame_text)
    except json.JSONDecodeError:
        text = frame_text.strip()
        return None, text or None, False, None, False

    event = str(payload.get("event", "")).lower()
    if event in {"stop", "closed", "disconnect"}:
        return None, None, True, None, True

    if event in {"connected", "start"}:
        start_payload = payload.get("start", {})
        call_sid = start_payload.get("callSid") or payload.get("callSid")
        return None, None, False, str(call_sid) if call_sid else None, True

    media = payload.get("media") or payload.get("stream") or {}
    encoded_audio = media.get("payload") or payload.get("payload")
    if isinstance(encoded_audio, str) and encoded_audio:
        try:
            decoded = base64.b64decode(encoded_audio)
            return decoded, None, False, None, True
        except Exception:  # pragma: no cover - malformed media frame
            logger.warning("Failed to decode base64 media payload")

    raw_text = payload.get("text") or payload.get("transcript")
    if isinstance(raw_text, str):
        text = raw_text.strip()
        return None, text or None, False, None, True

    return None, None, False, None, True


@router.websocket("/audio-stream")
async def audio_stream(websocket: WebSocket) -> None:
    await websocket.accept()
    call_sid = websocket.query_params.get("callSid", "unknown")
    min_audio_bytes = max(512, settings.stt_min_audio_bytes)
    audio_buffer = bytearray()
    json_transport = False

    try:
        while True:
            message = await websocket.receive()

            if message.get("type") == "websocket.disconnect":
                return

            user_text: str | None = None
            audio_chunk = message.get("bytes")
            if audio_chunk:
                audio_buffer.extend(audio_chunk)

            text_frame = message.get("text")
            if text_frame:
                (
                    parsed_audio,
                    parsed_text,
                    should_stop,
                    call_sid_override,
                    parsed_is_json,
                ) = _parse_text_frame(text_frame)

                if parsed_is_json:
                    json_transport = True

                if should_stop:
                    return

                if call_sid_override:
                    call_sid = call_sid_override

                if parsed_audio:
                    audio_buffer.extend(parsed_audio)

                if parsed_text:
                    user_text = parsed_text

            if not user_text and len(audio_buffer) >= min_audio_bytes:
                user_text = await transcribe_chunk(bytes(audio_buffer))
                audio_buffer.clear()

            if not user_text:
                continue

            agent_reply = await run_agent_pipeline(user_text=user_text, call_sid=call_sid)
            reply_audio = await synthesize(agent_reply)
            if not reply_audio:
                continue

            if json_transport:
                await websocket.send_text(
                    json.dumps(
                        {
                            "event": "media",
                            "media": {
                                "payload": base64.b64encode(reply_audio).decode("ascii")
                            },
                        }
                    )
                )
            else:
                await websocket.send_bytes(reply_audio)
    except WebSocketDisconnect:
        return
