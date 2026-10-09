from pathlib import Path
from app.ai.providers.openai_provider import OpenAIProvider
from app.core.settings import settings


class OpenAIAudioService:
    def __init__(self):
        self.provider = OpenAIProvider()

    async def transcribe(self, file_path: str, language: str | None = None) -> str:
        kwargs = {'model': settings.openai_stt_model}
        if language:
            kwargs['language'] = language
        with open(file_path, 'rb') as f:
            result = await self.provider.client.audio.transcriptions.create(file=f, **kwargs)
        return result.text

    async def synthesize(self, text: str, output_path: str, voice: str | None = None):
        response = await self.provider.client.audio.speech.create(
            model=settings.openai_tts_model,
            voice=voice or settings.openai_tts_voice,
            input=text,
        )
        Path(output_path).write_bytes(response.content)
        return output_path
