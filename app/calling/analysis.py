from app.ai.providers.factory import get_ai_provider
from app.modules.leads.qualification import LeadQualifier


class CallAnalysisService:
    async def summarize(self, transcript: str) -> dict:
        ai = get_ai_provider()
        summary = await ai.generate_json(
            system='Analyze a real-estate phone call. Use only transcript facts. Return JSON only.',
            prompt=(
                'Return fields: summary, outcome, customer_intent, property_interest, callback_requested, '
                'site_visit_requested, human_requested, objections, next_action.\nTRANSCRIPT:\n' + transcript
            ),
        )
        qualification = await LeadQualifier().qualify(transcript)
        return {'summary': summary, 'qualification': qualification}
