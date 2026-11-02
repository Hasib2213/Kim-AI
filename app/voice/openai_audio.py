from pathlib import Path
from app.ai.providers.openai_provider import OpenAIProvider
from app.core.settings import settings


class OpenAIAudioService:
    def __init__(self):
        self.provider = OpenAIProvider()

    async def transcribe(self, file_path: str, language: str | None = None) -> str:
        kwargs = {'model': settings.openai_stt_model}
        if language:
            clean_lang = language.strip().lower()
            if clean_lang and clean_lang != 'string':
                kwargs['language'] = clean_lang
        with open(file_path, 'rb') as f:
            result = await self.provider.client.audio.transcriptions.create(file=f, **kwargs)
        return result.text

    async def synthesize(self, text: str, output_path: str, voice: str | None = None):
        valid_voices = {'alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer', 'ash', 'sage', 'coral'}
        selected_voice = settings.openai_tts_voice
        if voice:
            cleaned = voice.strip().lower()
            if cleaned in valid_voices:
                selected_voice = cleaned
        response = await self.provider.client.audio.speech.create(
            model=settings.openai_tts_model,
            voice=selected_voice,
            input=text,
        )
        Path(output_path).write_bytes(response.content)
        return output_path
