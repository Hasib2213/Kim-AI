from app.database.mongodb import get_database
from app.utils.common import utcnow, stringify_id


class FollowupService:
    async def schedule(self, payload: dict):
        db = get_database()
        doc = {**payload, 'status': 'pending', 'attempt_number': payload.get('attempt_number', 1), 'created_at': utcnow()}
        result = await db.followups.insert_one(doc)
        return str(result.inserted_id)

    async def due(self, limit: int = 100):
        db = get_database()
        docs = await db.followups.find({'status': 'pending', 'scheduled_for': {'$lte': utcnow()}}).limit(limit).to_list(length=limit)
        return stringify_id(docs)
