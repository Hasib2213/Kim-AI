from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'PropertyAI AI Backend'
    app_env: str = 'development'
    debug: bool = True
    api_secret: str = 'change-me'
    cors_origins: list[str] = ['http://localhost:3000']

    mongodb_uri: str = 'mongodb://mongodb:27017'
    mongodb_database: str = 'property_ai'

    ai_default_provider: str = 'openai'
    ai_default_model: str = 'gpt-6-luna'
    openai_api_key: str | None = None
    openai_base_url: str | None = None
    openai_stt_model: str = 'gpt-4o-mini-transcribe'
    openai_tts_model: str = 'gpt-4o-mini-tts'
    openai_tts_voice: str = 'alloy'
    openai_vision_model: str = 'gpt-6-luna'

    gemini_api_key: str | None = None
    qwen_api_key: str | None = None
    deepseek_api_key: str | None = None

    retell_api_key: str | None = None
    retell_base_url: str = 'https://api.retellai.com'
    retell_agent_id: str | None = None
    retell_from_number: str | None = None
    retell_webhook_secret: str | None = None

    vapi_api_key: str | None = None
    vapi_base_url: str = 'https://api.vapi.ai'
    vapi_assistant_id: str | None = None
    vapi_phone_number_id: str | None = None

    meta_whatsapp_token: str | None = None
    meta_whatsapp_phone_number_id: str | None = None
    meta_graph_version: str = 'v24.0'

    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None
    smtp_use_tls: bool = True

    twilio_account_sid: str | None = None
    twilio_auth_token: str | None = None
    twilio_from_number: str | None = None

    media_dir: str = './storage'
    max_chat_history: int = 20
    max_search_results: int = 20
    default_currency: str = 'IDR'

    ffmpeg_binary: str = 'ffmpeg'
    ffprobe_binary: str = 'ffprobe'


@lru_cache

def get_settings() -> Settings:
    return Settings()


settings = get_settings()
