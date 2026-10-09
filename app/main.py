from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.settings import settings
from app.database.mongodb import connect_mongodb, close_mongodb
from app.database.indexes import ensure_indexes


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_mongodb()
    await ensure_indexes()
    yield
    await close_mongodb()


app = FastAPI(title=settings.app_name, version='1.0.0', lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(api_router, prefix='/api/v1')


@app.get('/health')
async def health():
    return {'status': 'ok', 'service': settings.app_name}
