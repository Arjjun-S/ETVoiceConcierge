from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response
from html import escape
from urllib.parse import parse_qs, quote_plus, urlparse

from config import CallerContext, get_settings

router = APIRouter(tags=["exotel"])


def _build_stream_url(request: Request, settings, call_sid: str) -> str:
    if settings.public_base_url:
        parsed = urlparse(settings.public_base_url)
        scheme = parsed.scheme or "https"
        host = parsed.netloc or parsed.path
    else:
        scheme = request.headers.get("x-forwarded-proto", request.url.scheme or "https")
        host = request.headers.get("x-forwarded-host", request.url.netloc)

    ws_scheme = "wss" if scheme == "https" else "ws"
    return f"{ws_scheme}://{host}/audio-stream?callSid={quote_plus(call_sid)}"


@router.api_route("/voice", methods=["GET", "POST"])
async def handle_voice_webhook(
    request: Request, settings=Depends(get_settings)
) -> Response:
    # Accept both GET (browser check) and POST (Exotel webhook)
    payload: dict[str, str] = {}
    if request.method == "POST":
        content_type = request.headers.get("content-type", "")
        if content_type.startswith("application/x-www-form-urlencoded"):
            raw_body = (await request.body()).decode("utf-8", errors="ignore")
            parsed = parse_qs(raw_body, keep_blank_values=True)
            payload = {
                key: values[-1] if isinstance(values, list) and values else ""
                for key, values in parsed.items()
            }
        elif content_type.startswith("application/json"):
            json_payload = await request.json()
            payload = {k: str(v) for k, v in json_payload.items()}

    caller = CallerContext(
        call_sid=str(payload.get("CallSid", "unknown")),
        phone_number=str(payload.get("From", "unknown")),
        metadata={k: str(v) for k, v in payload.items()} if payload else None,
    )
    stream_url = _build_stream_url(request, settings, caller.call_sid)

    xml = f"""
<Response>
    <Say voice="female">Welcome to Real Estate Voice Concierge.</Say>
    <Connect>
        <Stream url="{escape(stream_url)}"/>
    </Connect>
</Response>
"""

    return Response(content=xml.strip(), media_type="application/xml")
