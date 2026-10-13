from app.modules.properties.repository import PropertyRepository
from app.core.settings import settings


class PropertyService:
    def __init__(self):
        self.repo = PropertyRepository()

    async def search(self, filters: dict):
        return await self.repo.search(filters, settings.max_search_results)

    async def get(self, property_id: str):
        return await self.repo.get(property_id)

    async def create_draft(self, payload: dict):
        payload = dict(payload)
        payload.setdefault('status', 'draft')
        return await self.repo.create(payload)

    async def find_by_inbound_number(self, phone: str):
        return await self.repo.find_by_inbound_number(phone)

    async def compare(self, ids: list[str]):
        return await self.repo.compare(ids)
