from app.ai.providers.factory import get_ai_provider
from app.ai.prompts.system import LISTING_EXTRACTION_SYSTEM


class ListingExtractor:
    async def extract(self, transcript: str) -> dict:
        ai = get_ai_provider()
        return await ai.generate_json(system=LISTING_EXTRACTION_SYSTEM, prompt=transcript)
