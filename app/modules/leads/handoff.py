from bson import ObjectId
from app.database.mongodb import get_database
from app.utils.common import utcnow


class HumanHandoffService:
    async def request(self, *, lead_id: str, reason: str, preferred_agent_id: str | None = None):
        db = get_database()
        event = {
            'lead_id': lead_id,
            'reason': reason,
            'preferred_agent_id': preferred_agent_id,
            'status': 'pending',
            'created_at': utcnow(),
        }
        result = await db.handoffs.insert_one(event)
        try:
            await db.leads.update_one(
                {'_id': ObjectId(lead_id)},
                {'$set': {'human_handoff_requested': True, 'handoff_reason': reason, 'updated_at': utcnow()}},
            )
        except Exception:
            pass
        return str(result.inserted_id)
