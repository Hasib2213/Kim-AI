from fastapi import APIRouter
from app.api.v1.schemas import LeadQualifyRequest, HandoffRequest
from app.modules.leads.qualification import LeadQualifier
from app.modules.leads.service import LeadService
from app.modules.leads.handoff import HumanHandoffService

router = APIRouter(prefix='/leads', tags=['Lead AI'])


@router.post('/qualify')
async def qualify(req: LeadQualifyRequest):
    return await LeadQualifier().qualify(req.transcript)


@router.get('')
async def list_leads():
    return {'results': await LeadService().list()}


@router.post('/handoff')
async def handoff(req: HandoffRequest):
    return {'handoff_id': await HumanHandoffService().request(lead_id=req.lead_id, reason=req.reason, preferred_agent_id=req.preferred_agent_id)}
