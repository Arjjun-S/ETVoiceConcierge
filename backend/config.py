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
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    elevenlabs_api_key: str = Field(..., alias="ELEVENLABS_API_KEY")
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
