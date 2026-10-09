from app.ai.providers.factory import get_ai_provider


class IntentRouter:
    async def detect(self, text: str) -> dict:
        ai = get_ai_provider()
        return await ai.generate_json(
            system='Classify the user request. Return JSON only.',
            prompt=f"""Choose one intent from: property_search, property_recommendation, property_compare, property_question, site_visit, mortgage_estimate, lead_capture, human_handoff, general_chat.
Return {{"intent":"...","confidence":0.0,"property_ids":[],"notes":""}}.
USER: {text}""",
        )
