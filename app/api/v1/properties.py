from fastapi import APIRouter, HTTPException
from app.api.v1.schemas import SearchRequest, RecommendRequest, CompareRequest, MarketInsightsRequest
from app.modules.properties.ai_service import PropertyAIService
from app.modules.properties.service import PropertyService
from app.modules.properties.market_insights import MarketInsightsService

router = APIRouter(prefix='/properties', tags=['AI Property'])


@router.post('/search-ai')
async def search_ai(req: SearchRequest):
    filters = await PropertyAIService().extract_search_filters(req.query)
    results = await PropertyService().search(filters)
    return {'filters': filters, 'results': results}


@router.post('/recommend')
async def recommend(req: RecommendRequest):
    service = PropertyService()
    if req.property_ids:
        props = await service.compare(req.property_ids)
    else:
        props = await service.search({})
    ranking = await PropertyAIService().rank_recommendations(req.user_profile, props)
    return {'ranking': ranking, 'properties': props}


@router.post('/compare')
async def compare(req: CompareRequest):
    if len(req.property_ids) < 2:
        raise HTTPException(400, 'At least two property IDs are required')
    return {'properties': await PropertyService().compare(req.property_ids)}


@router.post('/market-insights')
async def market_insights(req: MarketInsightsRequest):
    return await MarketInsightsService().get(req.location, req.property_type)
