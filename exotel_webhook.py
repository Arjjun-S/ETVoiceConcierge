from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response

from config import CallerContext, get_settings

router = APIRouter(tags=["exotel"])


@router.post("/voice")
async def handle_voice_webhook(
    request: Request, settings=Depends(get_settings)
) -> Response:
    payload = await request.form() if request.headers.get("content-type", "").startswith("application/x-www-form-urlencoded") else await request.json()

    caller = CallerContext(
        call_sid=str(payload.get("CallSid", "unknown")),
        phone_number=str(payload.get("From", "unknown")),
        metadata={k: str(v) for k, v in payload.items()},
    )

    xml = f"""
<Response>
    <Say voice="female">Welcome to ET AI Concierge. Please wait while we connect you.</Say>
    <Connect>
        <Stream url="wss://your-server.com/audio-stream?callSid={caller.call_sid}"/>
    </Connect>
</Response>
"""

    return Response(content=xml.strip(), media_type="application/xml")
