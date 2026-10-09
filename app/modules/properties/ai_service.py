from app.ai.providers.factory import get_ai_provider

SEARCH_SCHEMA_PROMPT = """Convert the user's property request to JSON.
Allowed fields: property_type, listing_type, property_class, location, min_price, max_price, bedrooms, bathrooms, min_size_m2, amenities.
Use null/omit for unknown values. Prices must be numbers without punctuation. User query:
{query}"""


class PropertyAIService:
    async def extract_search_filters(self, query: str) -> dict:
        ai = get_ai_provider()
        return await ai.generate_json(system='You extract real-estate search filters. Never invent values.', prompt=SEARCH_SCHEMA_PROMPT.format(query=query))

    async def rank_recommendations(self, user_profile: dict, properties: list[dict]) -> dict:
        ai = get_ai_provider()
        return await ai.generate_json(
            system='Rank properties using only the supplied profile and property data. Return JSON with ranked_ids and reasons keyed by property id.',
            prompt=f'USER PROFILE:\n{user_profile}\n\nPROPERTIES:\n{properties}',
        )
