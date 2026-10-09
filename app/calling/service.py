from app.core.settings import settings
from app.calling.factory import normalize_call_provider
from app.calling.factory import get_call_client
from app.database.mongodb import get_database
from app.utils.common import utcnow, stringify_id


class CallService:
    async def outbound(self, provider: str, to_number: str, *, lead_id: str | None = None, customer_name: str | None = None):
        provider = normalize_call_provider(provider)
        client = get_call_client(provider)
        if provider == 'retell':
            response = await client.create_outbound_call(to_number, metadata={'lead_id': lead_id} if lead_id else {}, dynamic_variables={'customer_name': customer_name or ''})
            provider_call_id = response.get('call_id') or response.get('id')
        else:
            response = await client.create_outbound_call(to_number, customer_name=customer_name)
            provider_call_id = response.get('id')
        db = get_database()
        doc = {'provider': provider, 'provider_call_id': provider_call_id, 'direction': 'outbound', 'lead_id': lead_id, 'to_number': to_number, 'status': 'created', 'raw': response, 'created_at': utcnow()}
        try:
            await db.calls.insert_one(doc)
        except Exception:
            pass
        return stringify_id(doc)

    async def save_webhook(self, provider: str, payload: dict):
        db = get_database()
        event_id = str(payload.get('event_id') or payload.get('id') or payload.get('call_id') or payload.get('message', {}).get('call', {}).get('id') or '')
        event = {'provider': provider, 'event_id': event_id or None, 'payload': payload, 'created_at': utcnow()}
        try:
            await db.webhook_events.insert_one(event)
        except Exception:
            pass
        return {'stored': True}
