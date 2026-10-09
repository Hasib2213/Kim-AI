from datetime import timedelta
from app.database.mongodb import get_database
from app.utils.common import utcnow


class AnalyticsService:
    async def overview(self, days: int = 30):
        db = get_database()
        since = utcnow() - timedelta(days=days)
        leads = await db.leads.count_documents({'created_at': {'$gte': since}})
        hot = await db.leads.count_documents({'created_at': {'$gte': since}, '$or': [{'temperature': 'hot'}, {'lead_score': {'$gte': 70}}]})
        calls = await db.calls.count_documents({'created_at': {'$gte': since}})
        ai_runs = await db.ai_runs.count_documents({'created_at': {'$gte': since}})
        return {'days': days, 'leads': leads, 'hot_leads': hot, 'calls': calls, 'ai_runs': ai_runs}
