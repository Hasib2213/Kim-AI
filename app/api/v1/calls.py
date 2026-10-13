from fastapi import APIRouter
from app.api.v1.schemas import (
    CallAnalyzeRequest,
    CallLeadUpsertRequest,
    CallOutcomeRequest,
    InboundCallContextRequest,
    InboundCallResolveRequest,
    ListingQuestionRequest,
    OutboundCallRequest,
    WhatsAppHandoffRequest,
)
from app.calling.service import CallService
from app.calling.analysis import CallAnalysisService
from app.calling.tools import CallToolService

router = APIRouter(prefix='/calls', tags=['AI Calling'])


@router.post('/outbound')
async def outbound(req: OutboundCallRequest):
    return await CallService().outbound(
        req.provider,
        req.to_number,
        lead_id=req.lead_id,
        customer_name=req.customer_name,
        property_id=req.property_id,
        call_reason=req.call_reason,
        max_duration_seconds=req.max_duration_seconds,
    )


@router.post('/analyze')
async def analyze(req: CallAnalyzeRequest):
    return await CallAnalysisService().summarize(req.transcript)


@router.post('/inbound/context')
async def inbound_context(req: InboundCallContextRequest):
    return await CallService().save_inbound_context(**req.model_dump())


@router.post('/inbound/resolve')
async def inbound_resolve(req: InboundCallResolveRequest):
    return await CallService().resolve_inbound_context(**req.model_dump())


@router.get('/tools/properties/{property_id}')
async def tool_property_context(property_id: str):
    return await CallToolService().property_context(property_id)


@router.post('/tools/listing-question')
async def tool_listing_question(req: ListingQuestionRequest):
    return await CallToolService().answer_listing_question(req.property_id, req.question, req.caller_phone)


@router.post('/tools/leads')
async def tool_upsert_lead(req: CallLeadUpsertRequest):
    return await CallToolService().upsert_call_lead(req.model_dump())


@router.post('/tools/handoff-whatsapp')
async def tool_handoff_whatsapp(req: WhatsAppHandoffRequest):
    return await CallToolService().handoff_to_whatsapp(**req.model_dump())


@router.post('/tools/outcomes')
async def tool_save_outcome(req: CallOutcomeRequest):
    return await CallToolService().save_call_outcome(req.model_dump())
