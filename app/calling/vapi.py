import httpx
from app.core.settings import settings
from app.core.exceptions import ProviderConfigurationError


class VapiClient:
    def __init__(self):
        if not settings.vapi_api_key:
            raise ProviderConfigurationError('VAPI_API_KEY is not configured', 500)

    async def create_outbound_call(self, to_number: str, *, customer_name: str | None = None, metadata: dict | None = None):
        payload = {'customer': {'number': to_number}}
        if customer_name:
            payload['customer']['name'] = customer_name
        if metadata:
            payload['metadata'] = metadata
        if settings.vapi_assistant_id:
            payload['assistantId'] = settings.vapi_assistant_id
        if settings.vapi_phone_number_id:
            payload['phoneNumberId'] = settings.vapi_phone_number_id
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                f'{settings.vapi_base_url}/call',
                headers={'Authorization': f'Bearer {settings.vapi_api_key}', 'Content-Type': 'application/json'},
                json=payload,
            )
            r.raise_for_status()
            return r.json()
