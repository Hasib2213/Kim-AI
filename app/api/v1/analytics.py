from fastapi import APIRouter
from app.analytics.service import AnalyticsService

router = APIRouter(prefix='/analytics', tags=['AI Analytics'])


@router.get('/overview')
async def overview(days: int = 30):
    return await AnalyticsService().overview(days)
