import httpx
from app.core.settings import settings


async def send_whatsapp_text(to: str, text: str):
    if not settings.meta_whatsapp_token or not settings.meta_whatsapp_phone_number_id:
        raise RuntimeError('Meta WhatsApp credentials are not configured')
    url = f'https://graph.facebook.com/{settings.meta_graph_version}/{settings.meta_whatsapp_phone_number_id}/messages'
    payload = {'messaging_product': 'whatsapp', 'to': to, 'type': 'text', 'text': {'body': text}}
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(url, headers={'Authorization': f'Bearer {settings.meta_whatsapp_token}'}, json=payload)
        r.raise_for_status()
        return r.json()
