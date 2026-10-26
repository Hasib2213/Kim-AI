"""
One-Time Retell Provisioning Script for Client / Production Setup
Usage:
    python scripts/provision_retell.py --url https://api.yourdomain.com
Or interactive:
    python scripts/provision_retell.py
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT_DIR / ".env"


def load_env_val(key: str) -> str:
    if not ENV_FILE.exists():
        return ""
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith(f"{key}="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def update_env_val(key: str, val: str):
    if not ENV_FILE.exists():
        return
    lines = []
    found = False
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith(f"{key}="):
                lines.append(f"{key}={val}\n")
                found = True
            else:
                lines.append(line)
    if not found:
        lines.append(f"{key}={val}\n")
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)


def post_json(url: str, data: dict, api_key: str) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"❌ Error calling {url} (Status {e.code}): {err_body}")
        sys.exit(1)


def build_tools(backend_url: str) -> list[dict]:
    return [
        {
            "type": "custom",
            "name": "search_properties",
            "url": f"{backend_url}/api/v1/calls/tools/search-properties",
            "description": "Looks up available properties matching location, type (villa/apartment), bedrooms, or budget.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The client inquiry (e.g. villa in Bali, 2 bedroom apartment, properties under 5 billion)",
                    }
                },
                "required": ["query"],
            },
            "speak_during_execution": False,
            "speak_after_execution": True,
        },
        {
            "type": "custom",
            "name": "answer_listing_question",
            "url": f"{backend_url}/api/v1/calls/tools/listing-question",
            "description": "Gets details about a property (bedrooms, bathrooms, size, electricity, certificate type).",
            "parameters": {
                "type": "object",
                "properties": {
                    "property_id": {
                        "type": "string",
                        "description": "The property ID or title keyword (e.g. villa, apartment)",
                    },
                    "question": {
                        "type": "string",
                        "description": "The client specific question",
                    },
                },
                "required": ["property_id", "question"],
            },
            "speak_during_execution": False,
            "speak_after_execution": True,
        },
        {
            "type": "custom",
            "name": "save_client_lead",
            "url": f"{backend_url}/api/v1/calls/tools/leads",
            "description": "Saves an interested client contact information and property preferences (name, phone, email, budget, location, notes) into the CRM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Client name"},
                    "phone": {"type": "string", "description": "Client phone or WhatsApp number"},
                    "email": {"type": "string", "description": "Client email address if provided"},
                    "budget": {"type": "string", "description": "Client budget range"},
                    "location_preference": {"type": "string", "description": "Preferred city or area (e.g. Bali, SCBD Jakarta)"},
                    "notes": {"type": "string", "description": "Any specific requirements or notes"},
                },
            },
            "speak_during_execution": False,
            "speak_after_execution": True,
        },
        {
            "type": "custom",
            "name": "handoff_to_whatsapp",
            "url": f"{backend_url}/api/v1/calls/tools/handoff-whatsapp",
            "description": "Connects caller to the agent on WhatsApp for human assistance, negotiation, or private viewings.",
            "parameters": {
                "type": "object",
                "properties": {
                    "property_id": {"type": "string", "description": "The ID or name of the property"},
                    "reason": {"type": "string", "description": "Why handoff is needed"},
                },
                "required": ["property_id"],
            },
            "speak_during_execution": False,
            "speak_after_execution": True,
        },
    ]


SYSTEM_PROMPT = """You are Sarah, a warm, polite, and knowledgeable real estate consultant at PropertyAI. You are speaking with a client on a live phone call.

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


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="One-Time Setup of Retell AI Voice Agent for Client / Production")
    parser.add_argument("--url", help="Backend public URL / domain (e.g. https://api.yourdomain.com or ngrok URL)")
    parser.add_argument("--api-key", help="Retell API Key (defaults to RETELL_API_KEY from .env)")
    parser.add_argument("--agent-name", default="PropertyAI Voice Assistant", help="Name for the agent")
    parser.add_argument("--voice-id", default="11labs-Adrian", help="ElevenLabs or OpenAI voice ID (multilingual)")
    parser.add_argument(
        "--languages",
        default="id-ID,en-US,zh-CN,ko-KR,ja-JP,ar-SA,hi-IN,ur-IN",
        help="Comma-separated BCP-47 language codes for speech recognition",
    )
    args = parser.parse_args()

    api_key = args.api_key or load_env_val("RETELL_API_KEY")
    if not api_key:
        api_key = input("Enter Client's RETELL_API_KEY: ").strip()

    if not api_key:
        print("❌ Error: RETELL_API_KEY is required.")
        sys.exit(1)

    backend_url = args.url or load_env_val("BACKEND_PUBLIC_URL")
    if not backend_url:
        backend_url = input("Enter Backend Public URL (e.g. https://api.clientdomain.com or ngrok URL): ").strip()

    if not backend_url:
        print("❌ Error: Backend URL is required.")
        sys.exit(1)

    backend_url = backend_url.rstrip("/")
    lang_list = [l.strip() for l in args.languages.split(",") if l.strip()]

    print("\n🚀 Starting One-Time Retell Provisioning...")
    print(f"📡 Backend URL: {backend_url}")
    print(f"🔑 API Key: {api_key[:8]}...{api_key[-4:]}")
    print(f"🌐 Languages: {lang_list}")

    # Step 1: Create LLM
    print("\n[1/3] Creating Retell LLM with human-like multilingual prompt and 4 custom tools...")
    llm_payload = {
        "begin_message": "Hello, this is Sarah from PropertyAI. How can I help you today?",
        "general_prompt": SYSTEM_PROMPT,
        "general_tools": build_tools(backend_url),
    }
    llm_resp = post_json("https://api.retellai.com/create-retell-llm", llm_payload, api_key)
    llm_id = llm_resp.get("llm_id")
    print(f"  ✅ Created LLM ID: {llm_id}")

    # Step 2: Create Agent
    print(f"\n[2/3] Creating Voice Agent '{args.agent_name}' with voice '{args.voice_id}'...")
    agent_payload = {
        "agent_name": args.agent_name,
        "voice_id": args.voice_id,
        "response_engine": {
            "type": "retell-llm",
            "llm_id": llm_id,
        },
        "language": lang_list,
        "webhook_url": f"{backend_url}/api/v1/webhooks/retell",
        "max_call_duration_ms": 180000,
    }
    agent_resp = post_json("https://api.retellai.com/create-agent", agent_payload, api_key)
    agent_id = agent_resp.get("agent_id")
    print(f"  ✅ Created Agent ID: {agent_id}")

    # Step 3: Update .env
    print("\n[3/3] Updating .env file with new RETELL_AGENT_ID...")
    update_env_val("RETELL_API_KEY", api_key)
    update_env_val("RETELL_AGENT_ID", agent_id)
    print(f"  ✅ .env updated successfully with RETELL_AGENT_ID={agent_id}")

    print("\n" + "=" * 60)
    print("🎉 SUCCESS! RETELL VOICE AGENT SETUP IS COMPLETE!")
    print("=" * 60)
    print(f"Agent Name: {args.agent_name}")
    print(f"Agent ID  : {agent_id}")
    print(f"Webhook   : {backend_url}/api/v1/webhooks/retell")
    print("\nNext Steps:")
    print("1. If using Phone Calling, assign a Phone Number in Retell dashboard and set RETELL_FROM_NUMBER in .env.")
    print("2. Run your FastAPI backend server: python -m uvicorn app.main:app --reload")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
