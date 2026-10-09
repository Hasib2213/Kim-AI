from fastapi import APIRouter
from app.api.v1 import chat, properties, voice, media, leads, calls, site_visits, followups, finance, analytics, webhooks

api_router = APIRouter()
api_router.include_router(chat.router)
api_router.include_router(properties.router)
api_router.include_router(voice.router)
api_router.include_router(media.router)
api_router.include_router(leads.router)
api_router.include_router(calls.router)
api_router.include_router(site_visits.router)
api_router.include_router(followups.router)
api_router.include_router(finance.router)
api_router.include_router(analytics.router)
api_router.include_router(webhooks.router)
