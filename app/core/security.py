from fastapi import Header, HTTPException
from app.core.settings import settings


async def require_internal_api_key(x_api_key: str | None = Header(default=None)):
    if settings.app_env == 'development' and settings.api_secret == 'change-me':
        return True
    if not x_api_key or x_api_key != settings.api_secret:
        raise HTTPException(status_code=401, detail='Invalid API key')
    return True
