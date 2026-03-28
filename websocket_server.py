from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from agents.orchestrator import run_agent_pipeline
from services.stt_service import transcribe_chunk
from services.tts_service import synthesize

router = APIRouter()


@router.websocket("/audio-stream")
async def audio_stream(websocket: WebSocket) -> None:
    await websocket.accept()
    call_sid = websocket.query_params.get("callSid", "unknown")

    try:
        while True:
            audio_chunk = await websocket.receive_bytes()
            user_text = await transcribe_chunk(audio_chunk)
            agent_reply = await run_agent_pipeline(user_text=user_text, call_sid=call_sid)
            reply_audio = await synthesize(agent_reply)
            await websocket.send_bytes(reply_audio)
    except WebSocketDisconnect:
        return
