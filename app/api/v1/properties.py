from fastapi import APIRouter, HTTPException
from app.api.v1.schemas import (
    SearchRequest,
    RecommendRequest,
    CompareRequest,
    MarketInsightsRequest,
    PropertyCreateRequest,
)
from app.modules.properties.ai_service import PropertyAIService
from app.modules.properties.service import PropertyService
from app.modules.properties.market_insights import MarketInsightsService

router = APIRouter(prefix='/properties', tags=['AI Property'])


@router.get('')
async def list_properties(
    property_type: str | None = None,
    listing_type: str | None = None,
    property_class: str | None = None,
    location: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    bedrooms: int | None = None,
    bathrooms: int | None = None,
    status: str | None = 'active',
):
    filters = {}
    if property_type:
        filters['property_type'] = property_type
    if listing_type:
        filters['listing_type'] = listing_type
    if property_class:
        filters['property_class'] = property_class
    if location:
        filters['location'] = location
    if min_price is not None:
        filters['min_price'] = min_price
    if max_price is not None:
        filters['max_price'] = max_price
    if bedrooms is not None:
        filters['bedrooms'] = bedrooms
    if bathrooms is not None:
        filters['bathrooms'] = bathrooms
    if status:
        filters['status'] = status
    results = await PropertyService().search(filters)
    return {'results': results}


@router.get('/{property_id}')
async def get_property(property_id: str):
    prop = await PropertyService().get(property_id)
    if not prop:
        raise HTTPException(404, 'Property not found')
    return prop


@router.post('')
async def create_property(req: PropertyCreateRequest):
    payload = req.model_dump(exclude_unset=True)
    property_id = await PropertyService().create_draft(payload)
    return {
        'id': property_id,
        'status': payload.get('status', 'draft'),
        'message': 'Property saved successfully',
    }


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
