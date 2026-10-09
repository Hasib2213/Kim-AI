# PropertyAI AI Backend — FastAPI + MongoDB

A runnable backend starter for the PropertyAI AI features discussed in the project: AI chat, natural-language property search, property recommendations/comparison, multilingual property Q&A, voice STT/TTS, Voice→AI listing extraction, photo/video AI analysis, lead qualification/scoring, Retell/Vapi outbound calling integration, call webhooks, site visits, follow-up scheduling, WhatsApp/email/SMS adapters, deterministic mortgage estimates, and analytics.

## Important

This repository is intentionally backend-only. It does not include your Next.js/Figma frontend. The API is designed to plug into the existing PropertyAI customer/admin portals.

Core AI features can run with `OPENAI_API_KEY` plus MongoDB. Calling additionally needs provider configuration such as a Retell phone number and usually an agent ID; those are resource IDs, not API keys. WhatsApp/SMS/email likewise need their provider-specific sender IDs/numbers or SMTP settings.

OpenAI usage is implemented with the Responses API. The old Assistants API is not used.

## Quick start

```bash
cp .env.example .env
# Put OPENAI_API_KEY in .env

docker compose up --build -d
docker compose exec api python scripts/seed_properties.py
```

Open Swagger:

```text
http://localhost:8000/docs
```

Health:

```text
GET http://localhost:8000/health
```

## Core endpoints

```text
POST /api/v1/chat
POST /api/v1/properties/search-ai
POST /api/v1/properties/recommend
POST /api/v1/properties/compare
POST /api/v1/voice/transcribe
POST /api/v1/voice/listing-extract
POST /api/v1/voice/tts
POST /api/v1/media-ai/image/analyze
POST /api/v1/media-ai/video/analyze
POST /api/v1/leads/qualify
POST /api/v1/calls/outbound
POST /api/v1/site-visits
POST /api/v1/followups
POST /api/v1/finance/mortgage-estimate
GET  /api/v1/analytics/overview
POST /api/v1/webhooks/retell
POST /api/v1/webhooks/vapi
```

## Example chat

```bash
curl -X POST http://localhost:8000/api/v1/chat   -H 'Content-Type: application/json'   -d '{"user_id":"demo-user","message":"Show me villas in Bali under IDR 5 billion"}'
```

## Retell calling

Set:

```text
RETELL_API_KEY=
RETELL_AGENT_ID=
RETELL_FROM_NUMBER=+1...
```

Then:

```bash
curl -X POST http://localhost:8000/api/v1/calls/outbound   -H 'Content-Type: application/json'   -d '{"provider":"retell","to_number":"+1...","customer_name":"Anisa"}'
```

Retell's outbound API also requires a valid Retell/imported `from_number`; an API key alone is not enough for PSTN calling.

## Website voice

For the existing Figma website, you have two options:

1. Call this backend's `/voice/transcribe` + `/voice/tts` endpoints from your frontend.
2. For true real-time browser voice, use Retell's web-call/widget or another realtime voice SDK and let its custom tools call these FastAPI endpoints for property search, lead updates, and site visits.

This backend includes the business/tool endpoints; it does not ship a browser JavaScript SDK because your frontend is separate.

## MongoDB collections

The app creates/uses:

```text
properties
conversations
messages
leads
calls
webhook_events
site_visits
followups
ai_runs
```

You can extend these with `ai_tool_calls`, `call_transcripts`, `call_summaries`, `media_jobs`, and audit collections as the platform grows.

## Safety/production notes

- AI extraction never publishes a listing automatically. `/voice/listing-extract` returns `requires_confirmation: true`.
- Mortgage math is deterministic code, not model-generated math.
- Property answers should be grounded in MongoDB results; do not let the model invent listing facts.
- Verify Retell/Vapi webhook signatures before production. The included webhook endpoints store payloads, but provider-specific signature validation should be enabled once you configure the exact webhook secret/signing scheme in your account.
- Add authentication/RBAC before exposing mutation endpoints publicly.
- Add idempotency keys to production webhook/action endpoints.
- For long-running video processing, move `/media-ai/video/analyze` to a durable queue/worker before high-volume use.

## Architecture

```text
Frontend
  -> FastAPI API
      -> AI Orchestrator
          -> AI Provider adapter
          -> Property/Lead/Site Visit tools
              -> Service layer
                  -> MongoDB
      -> Voice / Media AI
      -> Retell or Vapi
      -> WhatsApp / Email / SMS
```

## Tests

```bash
pytest -q
```
