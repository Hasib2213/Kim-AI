from app.database.mongodb import get_database


async def ensure_indexes():
    db = get_database()
    await db.properties.create_index([('status', 1), ('property_type', 1), ('location.city', 1), ('price.amount', 1)])
    await db.properties.create_index([('status', 1), ('calling.inbound_number', 1)])
    await db.properties.create_index([('status', 1), ('calling.retell_number', 1)])
    await db.properties.create_index([('status', 1), ('calling.vapi_number', 1)])
    await db.properties.create_index([('title', 'text'), ('description', 'text'), ('location.city', 'text'), ('location.area', 'text')])
    await db.messages.create_index([('conversation_id', 1), ('created_at', -1)])
    await db.conversations.create_index([('user_id', 1), ('updated_at', -1)])
    await db.leads.create_index([('phone', 1)])
    await db.leads.create_index([('status', 1), ('created_at', -1)])
    await db.calls.create_index([('provider', 1), ('provider_call_id', 1)], unique=True, sparse=True)
    await db.followups.create_index([('status', 1), ('scheduled_for', 1)])
    await db.webhook_events.create_index([('provider', 1), ('event_id', 1)], unique=True, sparse=True)
    await db.ai_runs.create_index([('created_at', -1)])
    await db.site_visits.create_index([('customer_id', 1), ('scheduled_for', 1)])
