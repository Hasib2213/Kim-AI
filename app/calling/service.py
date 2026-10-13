from app.core.settings import settings
from app.calling.factory import normalize_call_provider
from app.calling.factory import get_call_client
from app.database.mongodb import get_database
from app.modules.properties.service import PropertyService
from app.utils.common import utcnow, stringify_id


def _nested_get(data: dict, path: str):
    value = data
    for part in path.split('.'):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def _first_value(data: dict, *paths: str):
    for path in paths:
        value = _nested_get(data, path)
        if value not in (None, ''):
            return value
    return None


def _payload_metadata(payload: dict) -> dict:
    metadata = (
        _first_value(payload, 'metadata', 'call.metadata', 'message.call.metadata', 'data.metadata')
        or {}
    )
    if not isinstance(metadata, dict):
        return {}
    return metadata


def _payload_dynamic_variables(payload: dict) -> dict:
    variables = (
        _first_value(
            payload,
            'retell_llm_dynamic_variables',
            'call.retell_llm_dynamic_variables',
            'call.dynamic_variables',
            'message.call.retell_llm_dynamic_variables',
            'message.call.dynamicVariables',
        )
        or {}
    )
    if not isinstance(variables, dict):
        return {}
    return variables


def _extract_call_context(payload: dict) -> dict:
    metadata = _payload_metadata(payload)
    dynamic_variables = _payload_dynamic_variables(payload)
    property_id = (
        payload.get('property_id')
        or metadata.get('property_id')
        or dynamic_variables.get('property_id')
        or _first_value(payload, 'call.property_id', 'message.call.property_id', 'data.property_id')
    )
    max_duration_seconds = (
        payload.get('max_duration_seconds')
        or metadata.get('max_duration_seconds')
        or dynamic_variables.get('max_duration_seconds')
    )
    try:
        max_duration_seconds = int(max_duration_seconds) if max_duration_seconds else 180
    except (TypeError, ValueError):
        max_duration_seconds = 180
    return {
        'provider_call_id': str(
            _first_value(payload, 'call_id', 'id', 'call.id', 'message.call.id', 'data.call_id', 'data.id') or ''
        ) or None,
        'from_number': _first_value(
            payload,
            'from_number',
            'caller_number',
            'from',
            'call.from_number',
            'call.customer.number',
            'customer.number',
            'message.call.customer.number',
            'data.from_number',
        ),
        'to_number': _first_value(
            payload,
            'to_number',
            'called_number',
            'to',
            'call.to_number',
            'call.phone_number',
            'call.phoneNumber.number',
            'phoneNumber.number',
            'message.call.phoneNumber.number',
            'data.to_number',
        ),
        'direction': _first_value(payload, 'direction', 'call.direction', 'message.call.direction', 'data.direction'),
        'property_id': property_id,
        'lead_id': metadata.get('lead_id') or dynamic_variables.get('lead_id') or payload.get('lead_id'),
        'metadata': metadata,
        'max_duration_seconds': min(max(max_duration_seconds, 30), 180),
    }


class CallService:
    async def outbound(
        self,
        provider: str,
        to_number: str,
        *,
        lead_id: str | None = None,
        customer_name: str | None = None,
        property_id: str | None = None,
        call_reason: str | None = None,
        max_duration_seconds: int = 180,
    ):
        provider = normalize_call_provider(provider)
        client = get_call_client(provider)
        metadata = {
            'lead_id': lead_id,
            'property_id': property_id,
            'call_reason': call_reason,
            'max_duration_seconds': max_duration_seconds,
        }
        metadata = {k: v for k, v in metadata.items() if v is not None}
        dynamic_variables = {
            'customer_name': customer_name or '',
            'property_id': property_id or '',
            'call_reason': call_reason or '',
            'max_duration_seconds': str(max_duration_seconds),
        }
        if provider == 'retell':
            response = await client.create_outbound_call(to_number, metadata=metadata, dynamic_variables=dynamic_variables)
            provider_call_id = response.get('call_id') or response.get('id')
        else:
            response = await client.create_outbound_call(to_number, customer_name=customer_name, metadata=metadata)
            provider_call_id = response.get('id')
        db = get_database()
        doc = {
            'provider': provider,
            'provider_call_id': provider_call_id,
            'direction': 'outbound',
            'lead_id': lead_id,
            'property_id': property_id,
            'to_number': to_number,
            'customer_name': customer_name,
            'call_reason': call_reason,
            'max_duration_seconds': max_duration_seconds,
            'status': 'created',
            'raw': response,
            'created_at': utcnow(),
        }
        try:
            await db.calls.insert_one(doc)
        except Exception:
            pass
        return stringify_id(doc)

    async def save_inbound_context(
        self,
        provider: str = 'retell',
        provider_call_id: str | None = None,
        from_number: str | None = None,
        to_number: str | None = None,
        property_id: str | None = None,
        lead_id: str | None = None,
        status: str = 'active',
        metadata: dict | None = None,
        max_duration_seconds: int = 180,
    ):
        provider = normalize_call_provider(provider)
        matched_property = None
        if not property_id and to_number:
            matched_property = await PropertyService().find_by_inbound_number(to_number)
            if matched_property:
                property_id = matched_property.get('_id')
        doc = {
            'provider': provider,
            'provider_call_id': provider_call_id,
            'direction': 'inbound',
            'lead_id': lead_id,
            'property_id': property_id,
            'from_number': from_number,
            'to_number': to_number,
            'status': status,
            'metadata': metadata or {},
            'max_duration_seconds': min(max(max_duration_seconds, 30), 180),
            'updated_at': utcnow(),
        }
        db = get_database()
        if provider_call_id:
            await db.calls.update_one(
                {'provider': provider, 'provider_call_id': provider_call_id},
                {'$set': doc, '$setOnInsert': {'created_at': utcnow()}},
                upsert=True,
            )
            saved = await db.calls.find_one({'provider': provider, 'provider_call_id': provider_call_id})
        else:
            doc['created_at'] = utcnow()
            result = await db.calls.insert_one(doc)
            saved = await db.calls.find_one({'_id': result.inserted_id})
        saved = stringify_id(saved)
        return {
            'call': saved,
            'matched_property_id': property_id,
            'matched_property': matched_property,
        }

    async def resolve_inbound_context(
        self,
        provider: str = 'retell',
        provider_call_id: str | None = None,
        from_number: str | None = None,
        to_number: str | None = None,
        property_id: str | None = None,
        payload: dict | None = None,
    ):
        payload = payload or {}
        extracted = _extract_call_context(payload) if payload else {}
        context = await self.save_inbound_context(
            provider=provider,
            provider_call_id=provider_call_id or extracted.get('provider_call_id'),
            from_number=from_number or extracted.get('from_number'),
            to_number=to_number or extracted.get('to_number'),
            property_id=property_id or extracted.get('property_id'),
            lead_id=extracted.get('lead_id'),
            status='active',
            metadata=extracted.get('metadata') or {},
            max_duration_seconds=extracted.get('max_duration_seconds') or 180,
        )
        resolved_property_id = context.get('matched_property_id')
        property_context = {'found': False, 'property_id': resolved_property_id}
        if resolved_property_id:
            from app.calling.tools import CallToolService

            property_context = await CallToolService().property_context(resolved_property_id)
        return {
            'call': context['call'],
            'property_context': property_context,
            'voice_agent_rules': [
                'Keep the call under 180 seconds.',
                'Answer only from the resolved listing data.',
                'Do not invent property dimensions, certificate status, price, ownership, electricity, or facing direction.',
                'If the data is missing or the caller asks outside listing facts, offer WhatsApp handoff to the listing agent or owner.',
            ],
            'tool_endpoints': {
                'property_context': '/api/v1/calls/tools/properties/{property_id}',
                'listing_question': '/api/v1/calls/tools/listing-question',
                'lead_upsert': '/api/v1/calls/tools/leads',
                'handoff_whatsapp': '/api/v1/calls/tools/handoff-whatsapp',
                'save_outcome': '/api/v1/calls/tools/outcomes',
            },
        }

    async def save_webhook(self, provider: str, payload: dict):
        db = get_database()
        event_id = str(payload.get('event_id') or payload.get('id') or payload.get('call_id') or payload.get('message', {}).get('call', {}).get('id') or '')
        event = {'provider': provider, 'event_id': event_id or None, 'payload': payload, 'created_at': utcnow()}
        try:
            await db.webhook_events.insert_one(event)
        except Exception:
            pass
        await self._update_call_from_webhook(provider, payload)
        return {'stored': True}

    async def _update_call_from_webhook(self, provider: str, payload: dict):
        context = _extract_call_context(payload)
        provider_call_id = context.get('provider_call_id')
        if not provider_call_id:
            return
        status = payload.get('status') or payload.get('event') or payload.get('event_type') or payload.get('type')
        transcript = payload.get('transcript') or payload.get('transcript_object') or payload.get('message', {}).get('transcript')
        duration_seconds = payload.get('duration_seconds') or payload.get('call_duration_seconds')
        property_id = context.get('property_id')
        if not property_id and context.get('to_number'):
            matched_property = await PropertyService().find_by_inbound_number(context['to_number'])
            if matched_property:
                property_id = matched_property.get('_id')
                context['direction'] = context.get('direction') or 'inbound'
        update = {
            'status': status,
            'transcript': transcript,
            'duration_seconds': duration_seconds,
            'direction': context.get('direction'),
            'from_number': context.get('from_number'),
            'to_number': context.get('to_number'),
            'property_id': property_id,
            'lead_id': context.get('lead_id'),
            'metadata': context.get('metadata') or None,
            'max_duration_seconds': context.get('max_duration_seconds'),
            'last_webhook_payload': payload,
            'updated_at': utcnow(),
        }
        update = {k: v for k, v in update.items() if v is not None}
        db = get_database()
        try:
            await db.calls.update_one(
                {'provider': provider, 'provider_call_id': str(provider_call_id)},
                {'$set': update, '$setOnInsert': {'provider': provider, 'provider_call_id': str(provider_call_id), 'created_at': utcnow()}},
                upsert=True,
            )
        except Exception:
            pass
