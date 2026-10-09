import json
import re
from openai import AsyncOpenAI
from app.ai.providers.base import AIProvider
from app.core.settings import settings
from app.core.exceptions import ProviderConfigurationError
from app.ai.usage import log_ai_run


class OpenAIProvider(AIProvider):
    def __init__(self):
        if not settings.openai_api_key:
            raise ProviderConfigurationError('OPENAI_API_KEY is not configured', 500)
        kwargs = {'api_key': settings.openai_api_key}
        if settings.openai_base_url and settings.openai_base_url.strip():
            kwargs['base_url'] = settings.openai_base_url.strip()
        else:
            kwargs['base_url'] = 'https://api.openai.com/v1'
        self.client = AsyncOpenAI(**kwargs)

    async def generate_text(self, *, system: str, messages: list[dict], model: str | None = None) -> str:
        input_items = [{'role': 'system', 'content': system}] + messages
        selected_model = model or settings.ai_default_model
        response = await self.client.responses.create(model=selected_model, input=input_items)
        await log_ai_run(provider='openai', model=selected_model, operation='text', response=response)
        return response.output_text.strip()

    async def generate_json(self, *, system: str, prompt: str, model: str | None = None) -> dict:
        selected_model = model or settings.ai_default_model
        response = await self.client.responses.create(
            model=selected_model,
            input=[
                {'role': 'system', 'content': system + '\nReturn valid JSON only. Do not wrap it in markdown.'},
                {'role': 'user', 'content': prompt},
            ],
        )
        await log_ai_run(provider='openai', model=selected_model, operation='json', response=response)
        return self._parse_json(response.output_text)

    async def analyze_image(self, *, image_data_url: str, prompt: str, model: str | None = None) -> dict:
        selected_model = model or settings.openai_vision_model
        response = await self.client.responses.create(
            model=selected_model,
            input=[{
                'role': 'user',
                'content': [
                    {'type': 'input_text', 'text': prompt + '\nReturn valid JSON only.'},
                    {'type': 'input_image', 'image_url': image_data_url},
                ],
            }],
        )
        await log_ai_run(provider='openai', model=selected_model, operation='vision', response=response)
        return self._parse_json(response.output_text)

    @staticmethod
    def _parse_json(text: str) -> dict:
        text = text.strip()
        text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.I)
        text = re.sub(r'\s*```$', '', text)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start, end = text.find('{'), text.rfind('}')
            if start >= 0 and end > start:
                return json.loads(text[start:end + 1])
            raise
