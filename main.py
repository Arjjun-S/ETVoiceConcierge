from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from exotel_webhook import router as exotel_router
from websocket_server import router as websocket_router

settings = get_settings()

app = FastAPI(title="ET Voice Concierge", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(exotel_router)
app.include_router(websocket_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "et-voice-concierge"}


@app.get("/")
async def index() -> dict[str, str]:
    return {"message": "ET Voice Concierge is running", "websocket": "/audio-stream"}
