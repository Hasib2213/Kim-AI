from app.ai.orchestrator.intent_router import IntentRouter
from app.ai.providers.factory import get_ai_provider
from app.ai.prompts.system import PROPERTY_ASSISTANT_SYSTEM
from app.modules.properties.ai_service import PropertyAIService
from app.modules.properties.service import PropertyService
from app.modules.conversations.service import ConversationService


class AIOrchestrator:
    def __init__(self):
        self.intent_router = IntentRouter()
        self.property_ai = PropertyAIService()
        self.properties = PropertyService()
        self.conversations = ConversationService()

    async def chat(self, *, user_id: str, message: str, conversation_id: str | None = None):
        conv = await self.conversations.get_or_create(user_id, conversation_id)
        cid = conv['conversation_id']
        await self.conversations.add_message(cid, 'user', message)
        intent = await self.intent_router.detect(message)
        tool_context = None

        if intent.get('intent') == 'property_search':
            filters = await self.property_ai.extract_search_filters(message)
            results = await self.properties.search(filters)
            tool_context = {'filters': filters, 'properties': results}
        elif intent.get('intent') == 'property_compare' and intent.get('property_ids'):
            results = await self.properties.compare(intent['property_ids'])
            tool_context = {'properties': results}

        history = await self.conversations.history(cid)
        model_messages = [{'role': x['role'], 'content': x['content']} for x in history]
        if tool_context is not None:
            model_messages.append({'role': 'system', 'content': f'GROUNDING DATA:\n{tool_context}'})
        ai = get_ai_provider()
        answer = await ai.generate_text(system=PROPERTY_ASSISTANT_SYSTEM, messages=model_messages)
        await self.conversations.add_message(cid, 'assistant', answer, {'intent': intent, 'tool_context': tool_context})
        return {'conversation_id': cid, 'intent': intent, 'answer': answer, 'data': tool_context}
