from pymongo import AsyncMongoClient
from app.core.settings import settings

_client: AsyncMongoClient | None = None


async def connect_mongodb():
    global _client
    _client = AsyncMongoClient(settings.mongodb_uri)
    await _client.admin.command('ping')


def get_database():
    if _client is None:
        raise RuntimeError('MongoDB is not connected')
    return _client[settings.mongodb_database]


async def close_mongodb():
    global _client
    if _client is not None:
        await _client.close()
        _client = None
