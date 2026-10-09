from bson import ObjectId
from app.database.mongodb import get_database
from app.utils.common import stringify_id


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
        doc = await self.collection.find_one({'_id': ObjectId(property_id)})
        return stringify_id(doc)

    async def create(self, payload: dict):
        result = await self.collection.insert_one(payload)
        return str(result.inserted_id)

    async def compare(self, ids: list[str]):
        object_ids = [ObjectId(x) for x in ids]
        docs = await self.collection.find({'_id': {'$in': object_ids}}).to_list(length=len(ids))
        return stringify_id(docs)
