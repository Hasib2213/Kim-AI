from fastapi import APIRouter, Request
from app.calling.service import CallService

router = APIRouter(prefix='/webhooks', tags=['Webhooks'])


@router.post('/retell')
async def retell(request: Request):
    payload = await request.json()
    return await CallService().save_webhook('retell', payload)


@router.post('/vapi')
async def vapi(request: Request):
    payload = await request.json()
    return await CallService().save_webhook('vapi', payload)
