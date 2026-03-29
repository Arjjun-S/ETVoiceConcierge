from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import get_settings
from exotel_webhook import router as exotel_router
from websocket_server import router as websocket_router
from agents.orchestrator import run_agent_pipeline

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


class TestInput(BaseModel):
    text: str


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "et-voice-concierge"}


@app.get("/")
async def index() -> dict[str, str]:
    return {"message": "ET Voice Concierge is running 🚀"}


@app.post("/test")
async def test_endpoint(body: TestInput) -> dict[str, str]:
    response = await run_agent_pipeline(user_text=body.text, call_sid="test_user")
    return {"response": response}
