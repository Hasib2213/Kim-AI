import base64
import mimetypes
from app.ai.providers.factory import get_ai_provider


async def analyze_property_image(file_path: str) -> dict:
    mime = mimetypes.guess_type(file_path)[0] or 'image/jpeg'
    encoded = base64.b64encode(open(file_path, 'rb').read()).decode('ascii')
    data_url = f'data:{mime};base64,{encoded}'
    ai = get_ai_provider()
    return await ai.analyze_image(
        image_data_url=data_url,
        prompt="Analyze this property photo. Return JSON with room_type, visible_features, amenities, furnishing, condition_notes, listing_description_draft, confidence. Do not infer exact price, legal status, address, or dimensions.",
    )
