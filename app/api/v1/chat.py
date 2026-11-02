from fastapi import APIRouter
from app.api.v1.schemas import ChatRequest
from app.ai.orchestrator.orchestrator import AIOrchestrator
from app.modules.conversations.service import ConversationService

router = APIRouter(prefix='/chat', tags=['AI Chat'])


@router.post('')
async def chat(req: ChatRequest):
    return await AIOrchestrator().chat(user_id=req.user_id, message=req.message, conversation_id=req.conversation_id)


@router.get('/history/{conversation_id}')
async def chat_history(conversation_id: str, limit: int = 20):
    return {
        'conversation_id': conversation_id,
        'messages': await ConversationService().history(conversation_id, limit=limit),
    }
