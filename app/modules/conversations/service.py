from app.database.mongodb import get_database
from app.utils.common import utcnow, stringify_id


class ConversationService:
    async def get_or_create(self, user_id: str, conversation_id: str | None = None):
        db = get_database()
        if conversation_id:
            doc = await db.conversations.find_one({'conversation_id': conversation_id})
            if doc:
                return stringify_id(doc)
        cid = conversation_id or f'conv_{user_id}_{int(utcnow().timestamp())}'
        doc = {'conversation_id': cid, 'user_id': user_id, 'summary': '', 'context': {}, 'created_at': utcnow(), 'updated_at': utcnow()}
        await db.conversations.insert_one(doc)
        return stringify_id(doc)

    async def add_message(self, conversation_id: str, role: str, content: str, metadata: dict | None = None):
        db = get_database()
        await db.messages.insert_one({'conversation_id': conversation_id, 'role': role, 'content': content, 'metadata': metadata or {}, 'created_at': utcnow()})
        await db.conversations.update_one({'conversation_id': conversation_id}, {'$set': {'updated_at': utcnow()}})

    async def history(self, conversation_id: str, limit: int = 20):
        db = get_database()
        docs = await db.messages.find({'conversation_id': conversation_id}).sort('created_at', -1).limit(limit).to_list(length=limit)
        docs.reverse()
        return stringify_id(docs)
