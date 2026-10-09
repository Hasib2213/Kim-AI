from app.ai.providers.factory import get_ai_provider
from app.ai.prompts.system import LEAD_QUALIFIER_SYSTEM


class LeadQualifier:
    async def qualify(self, transcript: str) -> dict:
        ai = get_ai_provider()
        result = await ai.generate_json(system=LEAD_QUALIFIER_SYSTEM, prompt=transcript)
        score = 0
        if result.get('budget_max'): score += 20
        if result.get('location'): score += 20
        if result.get('property_type'): score += 15
        if result.get('timeline'): score += 20
        if result.get('intent') in {'buy', 'rent', 'invest'}: score += 15
        if result.get('human_requested'): score += 10
        result['lead_score'] = min(score, 100)
        result['temperature'] = 'hot' if score >= 70 else 'warm' if score >= 40 else 'cold'
        return result
