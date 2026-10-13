from bson import ObjectId
from bson.errors import InvalidId
from app.database.mongodb import get_database
from app.utils.common import stringify_id


def _phone_variants(phone: str):
    digits = ''.join(ch for ch in phone if ch.isdigit())
    variants = {phone}
    if digits:
        variants.add(digits)
        variants.add(f'+{digits}')
    return list(variants)


class PropertyRepository:
    @property
    def collection(self):
        return get_database().properties

    async def search(self, filters: dict, limit: int = 20):
        query = {'status': 'active'}
        if v := filters.get('property_type'):
            query['property_type'] = {'$regex': f'^{v}$', '$options': 'i'}
        if v := filters.get('listing_type'):
            query['listing_type'] = {'$regex': f'^{v}$', '$options': 'i'}
        if v := filters.get('property_class'):
            query['property_class'] = {'$regex': f'^{v}$', '$options': 'i'}
        if v := filters.get('location'):
            query['$or'] = [
                {'location.city': {'$regex': v, '$options': 'i'}},
                {'location.area': {'$regex': v, '$options': 'i'}},
                {'location.province': {'$regex': v, '$options': 'i'}},
                {'location.district': {'$regex': v, '$options': 'i'}},
            ]
        price_q = {}
        if filters.get('min_price') is not None:
            price_q['$gte'] = filters['min_price']
        if filters.get('max_price') is not None:
            price_q['$lte'] = filters['max_price']
        if price_q:
            query['price.amount'] = price_q
        if filters.get('bedrooms') is not None:
            query['specifications.bedrooms'] = {'$gte': filters['bedrooms']}
        if filters.get('bathrooms') is not None:
            query['specifications.bathrooms'] = {'$gte': filters['bathrooms']}
        if filters.get('min_size_m2') is not None:
            query['specifications.size_m2'] = {'$gte': filters['min_size_m2']}
        if amenities := filters.get('amenities'):
            query['amenities'] = {'$all': amenities}
        docs = await self.collection.find(query).limit(limit).to_list(length=limit)
        return stringify_id(docs)

    async def get(self, property_id: str):
        try:
            object_id = ObjectId(property_id)
        except InvalidId:
            return None
        doc = await self.collection.find_one({'_id': object_id})
        return stringify_id(doc)

    async def create(self, payload: dict):
        result = await self.collection.insert_one(payload)
        return str(result.inserted_id)

    async def find_by_inbound_number(self, phone: str):
        values = _phone_variants(phone)
        query = {
            'status': 'active',
            '$or': [
                {'calling.inbound_number': {'$in': values}},
                {'calling.retell_number': {'$in': values}},
                {'calling.vapi_number': {'$in': values}},
                {'inbound_call_number': {'$in': values}},
                {'contact.call_number': {'$in': values}},
            ],
        }
        doc = await self.collection.find_one(query)
        return stringify_id(doc)

    async def compare(self, ids: list[str]):
        object_ids = []
        for x in ids:
            try:
                object_ids.append(ObjectId(x))
            except InvalidId:
                continue
        docs = await self.collection.find({'_id': {'$in': object_ids}}).to_list(length=len(ids))
        return stringify_id(docs)
