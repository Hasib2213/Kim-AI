from app.database.mongodb import get_database
from app.ai.providers.factory import get_ai_provider


class MarketInsightsService:
    async def get(self, location: str | None = None, property_type: str | None = None):
        match = {'status': 'active'}
        if location:
            match['$or'] = [
                {'location.city': {'$regex': location, '$options': 'i'}},
                {'location.area': {'$regex': location, '$options': 'i'}},
                {'location.province': {'$regex': location, '$options': 'i'}},
            ]
        if property_type:
            match['property_type'] = {'$regex': f'^{property_type}$', '$options': 'i'}

        db = get_database()
        pipeline = [
            {'$match': match},
            {'$group': {
                '_id': None,
                'listing_count': {'$sum': 1},
                'average_price': {'$avg': '$price.amount'},
                'minimum_price': {'$min': '$price.amount'},
                'maximum_price': {'$max': '$price.amount'},
                'average_size_m2': {'$avg': '$specifications.size_m2'},
            }},
        ]
        rows = await db.properties.aggregate(pipeline).to_list(length=1)
        stats = rows[0] if rows else {'listing_count': 0}
        stats.pop('_id', None)
        if not stats.get('listing_count'):
            return {'stats': stats, 'summary': 'No matching active listings were found in the current database.'}

        ai = get_ai_provider()
        summary = await ai.generate_text(
            system='Explain the supplied real-estate database statistics. Do not claim external market trends or facts not contained in the statistics.',
            messages=[{'role': 'user', 'content': f'Location: {location}; property type: {property_type}; statistics: {stats}'}],
        )
        return {'stats': stats, 'summary': summary}
