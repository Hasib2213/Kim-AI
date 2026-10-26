# PropertyAI AI Backend — FastAPI + MongoDB

A runnable backend for the PropertyAI AI features: AI multilingual chat, natural-language property search, dynamic voice agent calling (Retell AI / Vapi), real-time database tools, voice STT/TTS, Voice→AI listing extraction, photo/video AI analysis, automated lead qualification/scoring, site visit scheduling, deterministic mortgage estimates, and analytics.

## Important

- **Backend-Only Service**: This repository is intentionally backend-only. The API is designed to plug into existing PropertyAI customer/admin portals (e.g., Next.js frontend).
- **Core AI Setup**: Core chat, vision, and natural language search run with `OPENAI_API_KEY` plus MongoDB.
- **Calling Features**: Integrated with **Retell AI** and **Vapi**. Telephone calls require provider configuration (Agent ID and an imported/assigned phone number).
- **Deterministic Math**: Mortgage calculations are based on exact financial formulas, avoiding LLM hallucinations.
- **Grounded Data**: Property inquiries and voice assistant responses are strictly grounded in MongoDB inventory.

---

## Quick Start

### 1. Environment Setup

```bash
cp .env.example .env
# Fill in OPENAI_API_KEY and MONGODB_URI in .env
```

### 2. Run the Backend

**Option A: Running Locally with Python**
```bash
# On Windows, run with python -m to avoid Device Guard / script policy blocks:
python -m uvicorn app.main:app --reload --port 8000
```

**Option B: Running with Docker Compose**
```bash
docker compose up --build -d
docker compose exec api python scripts/seed_properties.py
```

### 3. Interactive Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **Health Check**: `GET http://localhost:8000/health`

---

## Retell AI Voice Agent Setup

We provide an automated, one-time provisioning script that configures the entire Retell AI Voice Agent, human-like prompt (Sarah persona), and all real-time MongoDB database tools in seconds.

### One-Click Provisioning (for Development or Client Production)

Expose your backend (via your production domain or ngrok for local testing) and run:

```bash
python scripts/provision_retell.py --url https://your-domain-or-ngrok.app
```

Or provide the API key directly:
```bash
python scripts/provision_retell.py --url https://api.yourdomain.com --api-key key_xxxx
```

**What this script does automatically:**
1. Creates a Retell LLM with a warm, natural human-like persona (no robotic filler phrases).
2. Registers the 4 custom database tools with `speak_during_execution: false` for instant, natural responses:
   - `search_properties`: Live natural language search in MongoDB.
   - `answer_listing_question`: Fetches bedrooms, bathrooms, electricity, certificate type (SHM/HGB), etc.
   - `save_client_lead`: Saves caller name, phone, budget, and preferences directly into the CRM `leads` collection.
   - `handoff_to_whatsapp`: Generates a WhatsApp handoff link to the property agent.
3. Creates the Voice Agent (`PropertyAI Voice Assistant`) using `11labs-Adrian` voice and sets the Webhook URL.
4. Updates `.env` automatically with `RETELL_AGENT_ID`.

---

## Core Endpoints

### Conversational AI & Search
```text
POST /api/v1/chat                           # Multilingual conversational assistant
POST /api/v1/properties/search-ai           # Natural language property search
POST /api/v1/properties/recommend           # Profile-based recommendations
POST /api/v1/properties/compare             # Side-by-side property comparison
POST /api/v1/properties/market-insights     # Market analytics from inventory
```

### AI Calling & Real-Time Voice Tools
```text
POST /api/v1/calls/outbound                 # Trigger outbound PSTN AI phone call
POST /api/v1/calls/analyze                  # Analyze and summarize call transcript
POST /api/v1/calls/tools/search-properties  # Voice tool: Live MongoDB property search
POST /api/v1/calls/tools/listing-question   # Voice tool: Specific property facts Q&A
POST /api/v1/calls/tools/leads              # Voice tool: Save client lead to CRM
POST /api/v1/calls/tools/handoff-whatsapp   # Voice tool: WhatsApp agent handoff
POST /api/v1/calls/tools/outcomes           # Voice tool: Save call outcome
POST /api/v1/webhooks/retell                # Webhook for Retell call lifecycle events
POST /api/v1/webhooks/vapi                  # Webhook for Vapi call lifecycle events
```

### Media, Leads & Finance
```text
POST /api/v1/voice/transcribe               # Speech-to-text (OpenAI Whisper)
POST /api/v1/voice/tts                      # Text-to-speech
POST /api/v1/voice/listing-extract          # Voice walkthrough notes -> Listing draft
POST /api/v1/media-ai/image/analyze         # Property image analysis
POST /api/v1/media-ai/video/analyze         # Property video note speech extraction
POST /api/v1/leads/qualify                  # Hot/Warm/Cold lead scoring
POST /api/v1/leads/handoff                  # Request human agent handoff
POST /api/v1/site-visits                    # Schedule on-site property visits
POST /api/v1/followups                      # Multi-channel follow-up scheduling
POST /api/v1/finance/mortgage-estimate      # Formula-based mortgage calculator
GET  /api/v1/analytics/overview             # Aggregate platform & call analytics
```

---

## Example Usage

### 1. Natural Language Chat
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"demo-user","message":"Show me villas in Bali under IDR 5 billion"}'
```

### 2. Trigger Outbound Phone Call
```bash
curl -X POST http://localhost:8000/api/v1/calls/outbound \
  -H 'Content-Type: application/json' \
  -d '{
    "provider": "retell",
    "to_number": "+1234567890",
    "customer_name": "Hasibul",
    "call_reason": "Inquiry about ocean view villa in Bali"
  }'
```

---

## MongoDB Collections

The application automatically manages the following collections:
- `properties`: Live real estate inventory (villas, apartments, commercial).
- `leads`: Qualified buyer/tenant profiles, budgets, and channel sources.
- `calls`: Inbound/outbound call records, provider call IDs, durations, and transcripts.
- `webhook_events`: Raw provider event payloads from telephony webhooks.
- `conversations` & `messages`: AI chat history and memory.
- `site_visits`: Scheduled walkthrough appointments.
- `followups`: Queued multi-channel outreach actions.
- `ai_runs`: LLM token usage and execution metrics.

---

## Architecture Overview

```text
Frontend (Web / Mobile / CRM)
  └─► FastAPI Backend (Port 8000)
        ├─► AI Orchestrator & Providers (OpenAI, etc.)
        ├─► Calling Engine & Webhooks (Retell AI / Vapi)
        │     └─► Real-Time Voice Tools:
        │           ├─ search_properties
        │           ├─ answer_listing_question
        │           ├─ save_client_lead
        │           └─ handoff_to_whatsapp
        ├─► Media & Voice AI (Whisper, Vision, FFmpeg)
        ├─► Multi-channel Adapters (WhatsApp, SMS, Email)
        └─► MongoDB (Atlas / Local)
```

---

## Retell AI Voice Agent Setup & Multilingual Support

The voice assistant (Sarah) supports **automatic language detection and multilingual voice handling** across all 9 target languages:
1. **Bahasa Indonesia** (`id-ID`)
2. **English** (`en-US`)
3. **Chinese / Mandarin** (`zh-CN`)
4. **Korean** (`ko-KR`)
5. **Japanese** (`ja-JP`)
6. **Arabian / Arabic** (`ar-SA`)
7. **Hindi** (`hi-IN`)
8. **Bangla / Bengali** (`বাংলা`)
9. **Urdu** (`ur-IN`)

### 1. One-Click Provisioning (New Client / Production Setup)
Creates the LLM with human persona, hooks up all 4 custom database tools, and configures multi-language speech recognition:
```bash
python scripts/provision_retell.py --url https://your-backend-domain.com
```

### 2. Updating Live Agent & Persona
Applies latest prompts, custom tools, and multilingual speech recognition settings to an existing Retell Agent:
```bash
python scripts/update_retell_dynamic.py
```

Configurable in `.env`:
```env
RETELL_LANGUAGES=id-ID,en-US,zh-CN,ko-KR,ja-JP,ar-SA,hi-IN,ur-IN
```

---

## Testing

Run unit and integration tests:
```bash
pytest -q
```

