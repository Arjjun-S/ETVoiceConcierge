from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response

from config import CallerContext, get_settings

router = APIRouter(tags=["exotel"])


@router.api_route("/voice", methods=["GET", "POST"])
async def handle_voice_webhook(
    request: Request, settings=Depends(get_settings)
) -> Response:
    # Accept both GET (browser check) and POST (Exotel webhook)
    payload = (
        await request.form()
        if request.method == "POST" and request.headers.get("content-type", "").startswith("application/x-www-form-urlencoded")
        else (await request.json() if request.method == "POST" else {})
    )

    caller = CallerContext(
        call_sid=str(payload.get("CallSid", "unknown")),
        phone_number=str(payload.get("From", "unknown")),
        metadata={k: str(v) for k, v in payload.items()} if payload else None,
    )

    xml = f"""
<Response>
    <Say voice="female">Welcome to ET AI Concierge</Say>
    <Connect>
        <Stream url="wss://your-server.com/audio-stream?callSid={caller.call_sid}"/>
    </Connect>
</Response>
"""

    return Response(content=xml.strip(), media_type="application/xml")
