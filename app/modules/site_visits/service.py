from bson import ObjectId
from app.database.mongodb import get_database
from app.utils.common import utcnow, stringify_id


class SiteVisitService:
    async def create(self, payload: dict):
        db = get_database()
        doc = {**payload, 'status': payload.get('status', 'pending_confirmation'), 'created_at': utcnow(), 'updated_at': utcnow()}
        res = await db.site_visits.insert_one(doc)
        return str(res.inserted_id)

    async def reschedule(self, visit_id: str, scheduled_for):
        db = get_database()
        await db.site_visits.update_one({'_id': ObjectId(visit_id)}, {'$set': {'scheduled_for': scheduled_for, 'status': 'rescheduled', 'updated_at': utcnow()}})
        return True

    async def cancel(self, visit_id: str):
        db = get_database()
        await db.site_visits.update_one({'_id': ObjectId(visit_id)}, {'$set': {'status': 'cancelled', 'updated_at': utcnow()}})
        return True

    async def list_for_customer(self, customer_id: str):
        db = get_database()
        return stringify_id(await db.site_visits.find({'customer_id': customer_id}).sort('scheduled_for', 1).to_list(length=100))
