import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ENV_FILE = Path(__file__).resolve().parent.parent / '.env'


def get_env_val(key: str, default: str = '') -> str:
    if val := os.getenv(key):
        return val.strip()
    if ENV_FILE.exists():
        with open(ENV_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith(f'{key}='):
                    v = line.split('=', 1)[1].strip().strip('"').strip("'")
                    if v:
                        return v
    return default


backend_url = get_env_val('BACKEND_PUBLIC_URL', 'https://nephelinitic-kaiden-instinctive.ngrok-free.dev').rstrip('/')
api_key = get_env_val('RETELL_API_KEY', 'key_f58158ad0cbf5bfeeb23041b8053')
agent_id = get_env_val('RETELL_AGENT_ID', 'agent_b61408bdfd8e1c76dcaf69f117')

# Target Languages: 6 Client Languages (Indonesian, English, Chinese, Korean, Japanese, Arabic) + Hindi, Bengali, Urdu
languages_raw = get_env_val('RETELL_LANGUAGES', 'id-ID,en-US,zh-CN,ko-KR,ja-JP,ar-SA,hi-IN,ur-IN')
supported_languages = [l.strip() for l in languages_raw.split(',') if l.strip()]

tools = [
    {
        'type': 'custom',
        'name': 'search_properties',
        'url': f'{backend_url}/api/v1/calls/tools/search-properties',
        'description': 'Looks up available properties matching location, type (villa/apartment), bedrooms, or budget.',
        'parameters': {
            'type': 'object',
            'properties': {
                'query': {
                    'type': 'string',
                    'description': 'The client inquiry in any language (e.g. villa in Bali, 2 bedroom apartment, villa di Bali, apartemen SCBD)'
                }
            },
            'required': ['query']
        },
        'speak_during_execution': False,
        'speak_after_execution': True
    },
    {
        'type': 'custom',
        'name': 'answer_listing_question',
        'url': f'{backend_url}/api/v1/calls/tools/listing-question',
        'description': 'Gets details about a property (bedrooms, bathrooms, size, electricity, certificate type).',
        'parameters': {
            'type': 'object',
            'properties': {
                'property_id': {
                    'type': 'string',
                    'description': 'The property ID or title keyword (e.g. villa, apartment, SCBD)'
                },
                'question': {
                    'type': 'string',
                    'description': 'The client specific question'
                }
            },
            'required': ['property_id', 'question']
        },
        'speak_during_execution': False,
        'speak_after_execution': True
    },
    {
        'type': 'custom',
        'name': 'save_client_lead',
        'url': f'{backend_url}/api/v1/calls/tools/leads',
        'description': 'Saves an interested client contact information and property preferences (name, phone, email, budget, location, notes) into the CRM.',
        'parameters': {
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'string',
                    'description': 'Client name'
                },
                'phone': {
                    'type': 'string',
                    'description': 'Client phone or WhatsApp number'
                },
                'email': {
                    'type': 'string',
                    'description': 'Client email address if provided'
                },
                'budget': {
                    'type': 'string',
                    'description': 'Client budget range'
                },
                'location_preference': {
                    'type': 'string',
                    'description': 'Preferred city or area (e.g. Bali, SCBD Jakarta)'
                },
                'notes': {
                    'type': 'string',
                    'description': 'Any specific requirements or notes'
                }
            }
        },
        'speak_during_execution': False,
        'speak_after_execution': True
    },
    {
        'type': 'custom',
        'name': 'handoff_to_whatsapp',
        'url': f'{backend_url}/api/v1/calls/tools/handoff-whatsapp',
        'description': 'Connects caller to the agent on WhatsApp for human assistance, negotiation, or private viewings.',
        'parameters': {
            'type': 'object',
            'properties': {
                'property_id': {
                    'type': 'string',
                    'description': 'The ID or name of the property'
                },
                'reason': {
                    'type': 'string',
                    'description': 'Why handoff is needed'
                }
            },
            'required': ['property_id']
        },
        'speak_during_execution': False,
        'speak_after_execution': True
    }
]

prompt = """You are Sarah, a warm, polite, and knowledgeable real estate consultant at PropertyAI. You are speaking with a client on a live phone call.

CRITICAL HUMAN CONVERSATION RULES:
1. ACT COMPLETELY HUMAN: Never say you are an AI, an automated assistant, a robot, or a virtual bot. Never say technical words like "database", "searching the system", "retrieving listings", "query", or "tools".
2. NEVER USE ROBOTIC FILLER PHRASES: Do not narrate your technical actions. Never say "I will check the listings available", "I am querying the database", or "I could not retrieve the listings". Answer naturally and directly, exactly like an experienced human agent talking to a client.
3. MULTILINGUAL & LOCAL LANGUAGE ADAPTATION:
   - Detect the language spoken by the caller immediately and ALWAYS reply in that exact same language.
   - Masterfully support all 9 key client and regional languages:
     * 1. Bahasa Indonesia: "Halo! Ada yang bisa saya bantu terkait properti di Bali atau Jakarta?" (Use natural terms: kamar tidur, kamar mandi, luas tanah, harga, sertifikat SHM/HGB).
     * 2. English (US/UK): "Hello! Welcome to PropertyAI. How can I help you today?"
     * 3. Chinese / Mandarin (中文): "您好！很高兴为您服务。请问您想了解巴厘岛还是雅加达的房产？"
     * 4. Korean (한국어): "안녕하세요! 발리와 자카르타의 부동산 매물에 대해 무엇을 도와드릴까요?"
     * 5. Japanese (日本語): "こんにちは！バリ島やジャカルタの不動産物件について何かお探しでしょうか？"
     * 6. Arabian / Arabic (العربية): "مرحباً بك! كيف يمكنني مساعدتك اليوم بخصوص العقارات في بالي أو جاكرتا؟"
     * 7. Hindi (हिन्दी): "नमस्ते! बाली या जकार्ता में प्रॉपर्टी के बारे में मैं आपकी क्या मदद कर सकती हूँ?"
     * 8. Bangla / Bengali (বাংলা): "হ্যালো! বালি বা জাকার্তার প্রোপার্টি সম্পর্কে আপনাকে কীভাবে সাহায্য করতে পারি?"
     * 9. Urdu (اردو): "السلام علیکم! بالی یا جکارتہ میں پراپرٹی کے بارے میں میں آپ کی کیا مدد کر سکتی ہوں؟"
   - If the caller switches languages mid-call, smoothly switch with them without comment.
4. PRESENTING PROPERTIES:
   - When a client asks what properties are available or asks for a location (e.g. "Do you have villas in Bali?", "Ada villa di Bali?", "What apartments are in Jakarta?"), quietly use 'search_properties' and present the matching options warmly in the client's language.
   - In English: "Yes! In Jakarta, we have a great 2-bedroom apartment in SCBD, South Jakarta for 850 million IDR. Would you like more details on it?"
   - In Indonesian: "Ya! Di Jakarta, kami memiliki apartemen 2 kamar tidur yang sangat nyaman di kawasan SCBD, Jakarta Selatan seharga 850 juta Rupiah. Apakah Anda ingin mengetahui rincian lebih lanjut?"
5. IF A PROPERTY OR DETAIL IS NOT AVAILABLE:
   - Never say "I could not retrieve" or "Information not available".
   - Respond gracefully like a real consultant: "Right now, we don't have an available property matching that exact request, but we frequently get new exclusive listings in Bali and Jakarta. Would you like me to connect you with our specialist on WhatsApp so they can send you new options as soon as they open up?" (spoken in the caller's language).
6. CAPTURING CLIENT LEADS:
   - When a client expresses interest in a property, asks for a viewing, or wants updates on new listings, warmly ask for their name and phone/WhatsApp number in their language.
   - Once they provide contact details or preferences, quietly call 'save_client_lead' to record their info in the system, and confirm warmly: "Thank you! I have noted down your details and requirements. Our property specialist will reach out to you shortly." (or in the caller's language).
7. ACCURACY: Answer facts about bedrooms, bathrooms, prices, electricity, and certificate types (SHM/HGB) accurately using your tools without inventing false numbers.
8. CONVERSATIONAL TONE: Keep your spoken sentences natural, friendly, concise, and easy to follow over the phone."""


def update():
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    # 1. Fetch Agent to find LLM ID and current settings
    print(f"📡 Fetching Agent {agent_id}...")
    req_agent = urllib.request.Request(f'https://api.retellai.com/get-agent/{agent_id}', headers=headers)
    with urllib.request.urlopen(req_agent) as res:
        agent_data = json.loads(res.read().decode('utf-8'))

    llm_id = agent_data.get('response_engine', {}).get('llm_id')
    if not llm_id:
        print("❌ Could not find llm_id on agent!")
        return

    print(f"🔍 Found Linked LLM ID: {llm_id}")

    # 2. Update LLM with Multilingual Prompt, English First Greeting, and Tools
    print("🧠 Updating Retell LLM with Multilingual Persona & Tools...")
    llm_payload = {
        'begin_message': 'Hello, this is Sarah from PropertyAI. How can I help you today?',
        'general_prompt': prompt,
        'general_tools': tools
    }
    req_llm = urllib.request.Request(
        f'https://api.retellai.com/update-retell-llm/{llm_id}',
        data=json.dumps(llm_payload).encode('utf-8'),
        headers=headers,
        method='PATCH'
    )
    with urllib.request.urlopen(req_llm) as res:
        print(f"  ✅ Retell LLM Updated! (Status: {res.getcode()})")

    # 3. Update Agent with Multi-Language Recognition and Webhook
    print(f"🗣️ Updating Voice Agent with Multi-Language Support {supported_languages}...")
    agent_payload = {
        'language': supported_languages,
        'webhook_url': f'{backend_url}/api/v1/webhooks/retell'
    }
    req_agent_patch = urllib.request.Request(
        f'https://api.retellai.com/update-agent/{agent_id}',
        data=json.dumps(agent_payload).encode('utf-8'),
        headers=headers,
        method='PATCH'
    )
    with urllib.request.urlopen(req_agent_patch) as res:
        updated_agent = json.loads(res.read().decode('utf-8'))
        print(f"  ✅ Retell Agent Updated! (Status: {res.getcode()})")
        print(f"  🌐 Active Languages: {updated_agent.get('language')}")
        print(f"  🔗 Webhook: {updated_agent.get('webhook_url')}")

    print("\n🎉 ALL DONE! Sarah is now fully equipped for Multilingual & Local Language conversations!")


if __name__ == '__main__':
    update()
