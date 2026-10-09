from fastapi import APIRouter
from app.api.v1.schemas import VisitCreateRequest
from app.modules.site_visits.service import SiteVisitService

router = APIRouter(prefix='/site-visits', tags=['Site Visits'])


@router.post('')
async def create(req: VisitCreateRequest):
    return {'id': await SiteVisitService().create(req.model_dump())}


@router.get('/customer/{customer_id}')
async def list_customer(customer_id: str):
    return {'results': await SiteVisitService().list_for_customer(customer_id)}
