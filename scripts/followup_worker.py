import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bson import ObjectId
from app.database.mongodb import connect_mongodb, close_mongodb, get_database
from app.modules.followups.service import FollowupService
from app.integrations.whatsapp import send_whatsapp_text
from app.integrations.email import send_email_sync
from app.integrations.sms import send_sms_sync
from app.calling.service import CallService


async def process_one(job):
    db = get_database()
    try:
        channel = job['channel']
        target = job.get('to')
        message = job.get('message') or 'Following up on your property inquiry.'
        if channel == 'whatsapp':
            await send_whatsapp_text(target, message)
        elif channel == 'email':
            await asyncio.to_thread(send_email_sync, target, 'Property follow-up', message)
        elif channel == 'sms':
            await asyncio.to_thread(send_sms_sync, target, message)
        elif channel == 'voice':
            await CallService().outbound(job.get('provider', 'retell'), target, lead_id=job.get('lead_id'), customer_name=job.get('customer_name'))
        else:
            raise ValueError(f'Unsupported followup channel: {channel}')
        await db.followups.update_one({'_id': ObjectId(job['_id'])}, {'$set': {'status': 'completed'}})
    except Exception as exc:
        await db.followups.update_one({'_id': ObjectId(job['_id'])}, {'$set': {'status': 'failed', 'error': str(exc)}})


async def main():
    await connect_mongodb()
    service = FollowupService()
    try:
        while True:
            for job in await service.due(50):
                await process_one(job)
            await asyncio.sleep(30)
    finally:
        await close_mongodb()

if __name__ == '__main__':
    asyncio.run(main())
