from app.database.mongodb import get_database
from app.utils.common import utcnow, stringify_id


class LeadService:
    async def upsert_by_phone(self, payload: dict):
        db = get_database()
        phone = payload.get('phone')
        if not phone:
            payload = {**payload, 'created_at': utcnow(), 'updated_at': utcnow()}
            result = await db.leads.insert_one(payload)
            return str(result.inserted_id)
        await db.leads.update_one(
            {'phone': phone},
            {'$set': {**payload, 'updated_at': utcnow()}, '$setOnInsert': {'created_at': utcnow()}},
            upsert=True,
        )
        doc = await db.leads.find_one({'phone': phone})
        return stringify_id(doc)

    async def update_status(self, lead_id: str, status: str):
        from bson import ObjectId
        db = get_database()
        await db.leads.update_one({'_id': ObjectId(lead_id)}, {'$set': {'status': status, 'updated_at': utcnow()}})
        return True

    async def list(self, limit: int = 100):
        db = get_database()
        return stringify_id(await db.leads.find({}).sort('created_at', -1).limit(limit).to_list(length=limit))
