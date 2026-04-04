from functools import lru_cache
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env early so Settings can pick values
load_dotenv()

class Settings(BaseSettings):
    exotel_sid: str = Field(..., alias="EXOTEL_SID")
    exotel_token: str = Field(..., alias="EXOTEL_TOKEN")
    exotel_virtual_number: str = Field(..., alias="EXOTEL_VIRTUAL_NUMBER")
    deepgram_api_key: str = Field(..., alias="DEEPGRAM_API_KEY")
    openrouter_api_key: str = Field(..., alias="OPENROUTER_API_KEY")
    openrouter_model: str = Field(
        "qwen/qwen3-next-80b-a3b-instruct:free", alias="OPENROUTER_MODEL"
    )
    openrouter_fallback_model: str = Field(
        "nvidia/nemotron-3-nano-30b-a3b:free", alias="OPENROUTER_FALLBACK_MODEL"
    )
    openrouter_referer: str | None = Field(None, alias="OPENROUTER_REFERER")
    openrouter_title: str | None = Field(None, alias="OPENROUTER_TITLE")
    elevenlabs_api_key: str = Field(..., alias="ELEVENLABS_API_KEY")
    elevenlabs_voice_id: str = Field(
        "EXAVITQu4vr4xnSDxMaL", alias="ELEVENLABS_VOICE_ID"
    )
    elevenlabs_model_id: str = Field("eleven_turbo_v2_5", alias="ELEVENLABS_MODEL_ID")
    elevenlabs_output_format: str = Field("ulaw_8000", alias="ELEVENLABS_OUTPUT_FORMAT")
    public_base_url: str | None = Field(None, alias="PUBLIC_BASE_URL")
    deepgram_model: str = Field("nova-2", alias="DEEPGRAM_MODEL")
    deepgram_encoding: str = Field("mulaw", alias="DEEPGRAM_ENCODING")
    deepgram_sample_rate: int = Field(8000, alias="DEEPGRAM_SAMPLE_RATE")
    stt_min_audio_bytes: int = Field(6400, alias="STT_MIN_AUDIO_BYTES")
    supabase_url: str = Field(..., alias="SUPABASE_URL")
    supabase_service_key: str = Field(..., alias="SUPABASE_SERVICE_KEY")
    supabase_jwt_secret: str = Field(..., alias="SUPABASE_JWT_SECRET")
    log_level: str = Field("INFO", alias="LOG_LEVEL")

    class Config:
        env_file = ".env"
        populate_by_name = True
        case_sensitive = False

class CallerContext(BaseModel):
    call_sid: str
    phone_number: str
    metadata: dict[str, str] | None = None

@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[arg-type]
