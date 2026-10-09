import httpx
from app.core.settings import settings
from app.core.exceptions import ProviderConfigurationError


class RetellClient:
    def __init__(self):
        if not settings.retell_api_key:
            raise ProviderConfigurationError('RETELL_API_KEY is not configured', 500)

    async def create_outbound_call(self, to_number: str, *, metadata: dict | None = None, dynamic_variables: dict | None = None):
        if not settings.retell_from_number:
            raise ProviderConfigurationError('RETELL_FROM_NUMBER is required', 500)
        payload = {
            'from_number': settings.retell_from_number,
            'to_number': to_number,
            'metadata': metadata or {},
            'retell_llm_dynamic_variables': dynamic_variables or {},
        }
        if settings.retell_agent_id:
            payload['override_agent_id'] = settings.retell_agent_id
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                f'{settings.retell_base_url}/v2/create-phone-call',
                headers={'Authorization': f'Bearer {settings.retell_api_key}', 'Content-Type': 'application/json'},
                json=payload,
            )
            r.raise_for_status()
            return r.json()
