from fastapi import APIRouter
from app.api.v1.schemas import OutboundCallRequest, CallAnalyzeRequest
from app.calling.service import CallService
from app.calling.analysis import CallAnalysisService

router = APIRouter(prefix='/calls', tags=['AI Calling'])


@router.post('/outbound')
async def outbound(req: OutboundCallRequest):
    return await CallService().outbound(req.provider, req.to_number, lead_id=req.lead_id, customer_name=req.customer_name)


@router.post('/analyze')
async def analyze(req: CallAnalyzeRequest):
    return await CallAnalysisService().summarize(req.transcript)
