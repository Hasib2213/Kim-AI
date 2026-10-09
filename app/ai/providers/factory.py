from app.core.settings import settings
from app.ai.providers.openai_provider import OpenAIProvider


def get_ai_provider(name: str | None = None):
    provider = (name or settings.ai_default_provider).lower()
    if provider == 'openai':
        return OpenAIProvider()
    raise NotImplementedError(f'Provider {provider!r} is not wired yet. Add adapter in app/ai/providers/.')
