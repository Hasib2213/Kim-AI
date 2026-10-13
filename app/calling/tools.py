from bson import ObjectId
from bson.errors import InvalidId

from app.database.mongodb import get_database
from app.modules.leads.service import LeadService
from app.modules.properties.service import PropertyService
from app.utils.common import stringify_id, utcnow


LISTING_QUESTION_FIELDS = {
    'dimensions': (
        ('specifications.lot_size_m2', 'lot size'),
        ('specifications.building_size_m2', 'building size'),
        ('specifications.size_m2', 'listed size'),
    ),
    'certificate': (('legal.certificate_type', 'certificate type'), ('certificate_type', 'certificate type')),
    'bedrooms': (('specifications.bedrooms', 'bedrooms'),),
    'bathrooms': (('specifications.bathrooms', 'bathrooms'),),
    'electricity': (('utilities.electricity_watt', 'electricity capacity'), ('electricity_watt', 'electricity capacity')),
    'facing': (('specifications.facing_direction', 'facing direction'), ('facing_direction', 'facing direction')),
}

QUESTION_KEYWORDS = {
    'dimensions': ('dimension', 'lot', 'land', 'building size', 'size', ' luas ', 'tanah', 'bangunan'),
    'certificate': ('certificate', 'certification', 'shm', 'hgb', 'legal', 'sertifikat'),
    'bedrooms': ('bedroom', 'bed', 'kamar tidur'),
    'bathrooms': ('bathroom', 'bath', 'toilet', 'kamar mandi'),
    'electricity': ('electricity', 'power', 'watt', 'kwh', 'listrik'),
    'facing': ('facing', 'orientation', 'direction', 'north', 'south', 'east', 'west', 'hadap'),
}


def _nested_get(data: dict, path: str):
    value = data
    for part in path.split('.'):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def _format_value(label: str, value):
    if value is None or value == '':
        return None
    if label in {'lot size', 'building size', 'listed size'}:
        return f'{label}: {value} m2'
    if label == 'electricity capacity':
        return f'{label}: {value}W'
    return f'{label}: {value}'


def _detect_requested_fields(question: str) -> list[str]:
    normalized = f' {question.lower()} '
    fields = []
    for field, keywords in QUESTION_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            fields.append(field)
    return fields


def _contact_value(prop: dict) -> str | None:
    candidates = [
        ('agent.whatsapp',),
        ('agent.phone',),
        ('owner.whatsapp',),
        ('owner.phone',),
        ('contact.whatsapp',),
        ('contact.phone',),
        ('agent_whatsapp',),
        ('owner_whatsapp',),
        ('whatsapp',),
    ]
    for paths in candidates:
        for path in paths:
            value = _nested_get(prop, path)
            if value:
                return str(value)
    return None


def _whatsapp_link(phone: str, message: str | None = None) -> str:
    number = ''.join(ch for ch in phone if ch.isdigit())
    if message:
        from urllib.parse import quote

        return f'https://wa.me/{number}?text={quote(message)}'
    return f'https://wa.me/{number}'


class CallToolService:
    async def property_context(self, property_id: str) -> dict:
        prop = await PropertyService().get(property_id)
        if not prop:
            return {'found': False, 'property_id': property_id}
        contact = _contact_value(prop)
        return {
            'found': True,
            'property_id': property_id,
            'property': prop,
            'agent_whatsapp': contact,
            'allowed_question_fields': list(LISTING_QUESTION_FIELDS.keys()),
            'fallback_rule': 'If the answer is not in property data, offer WhatsApp handoff to the listing agent or owner.',
            'max_duration_seconds': 180,
        }

    async def answer_listing_question(self, property_id: str, question: str, caller_phone: str | None = None) -> dict:
        prop = await PropertyService().get(property_id)
        if not prop:
            return {
                'answerable': False,
                'answer': 'I could not find this listing in the current property database.',
                'handoff_available': False,
            }

        requested_fields = _detect_requested_fields(question)
        if not requested_fields:
            return await self._fallback(prop, property_id, caller_phone, 'Question is outside the supported listing fields.')

        facts = []
        source_fields = []
        for field in requested_fields:
            for path, label in LISTING_QUESTION_FIELDS[field]:
                formatted = _format_value(label, _nested_get(prop, path))
                if formatted:
                    facts.append(formatted)
                    source_fields.append(path)

        if not facts:
            return await self._fallback(prop, property_id, caller_phone, 'Requested listing field is not available.')

        title = prop.get('title') or 'this listing'
        return {
            'answerable': True,
            'answer': f'For {title}, ' + '; '.join(facts) + '.',
            'source_fields': source_fields,
            'handoff_available': bool(_contact_value(prop)),
        }

    async def _fallback(self, prop: dict, property_id: str, caller_phone: str | None, reason: str) -> dict:
        contact = _contact_value(prop)
        response = {
            'answerable': False,
            'answer': 'I do not have that information in the listing details. I can connect you with the listing agent or owner on WhatsApp.',
            'reason': reason,
            'handoff_available': bool(contact),
        }
        if contact:
            message = f'Hello, I have a question about property {property_id}.'
            if caller_phone:
                message += f' My phone number is {caller_phone}.'
            response['agent_whatsapp'] = contact
            response['whatsapp_link'] = _whatsapp_link(contact, message)
        return response

    async def upsert_call_lead(self, payload: dict):
        payload = dict(payload)
        payload.setdefault('source', 'ai_call')
        payload.setdefault('status', 'new')
        return await LeadService().upsert_by_phone(payload)

    async def handoff_to_whatsapp(
        self,
        *,
        property_id: str,
        caller_phone: str | None = None,
        lead_id: str | None = None,
        reason: str = 'AI call fallback requested',
    ) -> dict:
        prop = await PropertyService().get(property_id)
        if not prop:
            return {'created': False, 'reason': 'Property not found', 'handoff_available': False}
        contact = _contact_value(prop)
        if not contact:
            return {'created': False, 'reason': 'No WhatsApp contact is configured for this listing', 'handoff_available': False}

        db = get_database()
        event = {
            'lead_id': lead_id,
            'property_id': property_id,
            'caller_phone': caller_phone,
            'reason': reason,
            'channel': 'whatsapp',
            'target': contact,
            'status': 'pending',
            'created_at': utcnow(),
        }
        result = await db.handoffs.insert_one(event)
        if lead_id:
            try:
                await db.leads.update_one(
                    {'_id': ObjectId(lead_id)},
                    {'$set': {'human_handoff_requested': True, 'handoff_reason': reason, 'updated_at': utcnow()}},
                )
            except (InvalidId, Exception):
                pass
        message = f'Hello, I have a question about property {property_id}.'
        if caller_phone:
            message += f' My phone number is {caller_phone}.'
        return {
            'created': True,
            'handoff_id': str(result.inserted_id),
            'agent_whatsapp': contact,
            'whatsapp_link': _whatsapp_link(contact, message),
            'message': message,
        }

    async def save_call_outcome(self, payload: dict) -> dict:
        db = get_database()
        payload = {k: v for k, v in payload.items() if v is not None}
        provider = payload.get('provider')
        provider_call_id = payload.get('provider_call_id')
        payload['updated_at'] = utcnow()
        if provider and provider_call_id:
            await db.calls.update_one(
                {'provider': provider, 'provider_call_id': provider_call_id},
                {'$set': payload, '$setOnInsert': {'created_at': utcnow()}},
                upsert=True,
            )
            doc = await db.calls.find_one({'provider': provider, 'provider_call_id': provider_call_id})
        else:
            payload.setdefault('created_at', utcnow())
            result = await db.calls.insert_one(payload)
            doc = await db.calls.find_one({'_id': result.inserted_id})
        return stringify_id(doc)
