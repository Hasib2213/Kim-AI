from fastapi import APIRouter
from app.api.v1.schemas import FollowupCreateRequest
from app.modules.followups.service import FollowupService

router = APIRouter(prefix='/followups', tags=['AI Follow-up'])


@router.post('')
async def create(req: FollowupCreateRequest):
    return {'id': await FollowupService().schedule(req.model_dump())}


@router.get('/due')
async def due():
    return {'results': await FollowupService().due()}
