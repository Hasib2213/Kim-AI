from fastapi import APIRouter
from app.api.v1.schemas import ChatRequest
from app.ai.orchestrator.orchestrator import AIOrchestrator

router = APIRouter(prefix='/chat', tags=['AI Chat'])


@router.post('')
async def chat(req: ChatRequest):
    return await AIOrchestrator().chat(user_id=req.user_id, message=req.message, conversation_id=req.conversation_id)
