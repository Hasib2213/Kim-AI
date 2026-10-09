# AI Feature Coverage

## Implemented backend modules/endpoints

- AI multilingual chat assistant — `POST /api/v1/chat`
- Natural-language property search — `POST /api/v1/properties/search-ai`
- Property recommendations — `POST /api/v1/properties/recommend`
- Property comparison — `POST /api/v1/properties/compare`
- Data-grounded market insights from MongoDB inventory — `POST /api/v1/properties/market-insights`
- Speech-to-text — `POST /api/v1/voice/transcribe`
- Text-to-speech — `POST /api/v1/voice/tts`
- Voice → structured listing extraction — `POST /api/v1/voice/listing-extract`
- Property photo AI analysis — `POST /api/v1/media-ai/image/analyze`
- Property video-note speech extraction + listing extraction — `POST /api/v1/media-ai/video/analyze`
- Lead qualification + hot/warm/cold scoring — `POST /api/v1/leads/qualify`
- Human handoff request — `POST /api/v1/leads/handoff`
- Outbound AI calls through Retell or Vapi — `POST /api/v1/calls/outbound`
- Call transcript summary + qualification — `POST /api/v1/calls/analyze`
- Retell/Vapi webhook receivers — `POST /api/v1/webhooks/retell`, `/vapi`
- Site-visit creation/listing — `/api/v1/site-visits`
- Follow-up scheduling — `/api/v1/followups`
- Follow-up worker for WhatsApp, email, SMS, and voice calls — `scripts/followup_worker.py`
- Deterministic mortgage estimator — `POST /api/v1/finance/mortgage-estimate`
- AI/call/lead analytics overview — `GET /api/v1/analytics/overview`
- OpenAI usage logging — `ai_runs` MongoDB collection
- Provider abstraction layer — `app/ai/providers/`
- Retell website voice/chat widget example — `docs/retell_widget_example.html`

## Requires provider/dashboard setup in addition to API keys

- Retell: a published voice agent and a Retell/imported phone number for PSTN outbound calls.
- Vapi: assistant/phone-number resource IDs if you use Vapi calling.
- WhatsApp: Meta phone-number ID and approved WhatsApp Business setup.
- SMS: Twilio sender number plus account credentials.
- Email: SMTP server credentials.

## Deliberately not automatic

- AI-extracted property listings are returned for confirmation instead of being auto-published.
- Legal ownership, exact dimensions, property price, mortgage eligibility, and current external market facts are never inferred from photos/videos.
- Market insights only summarize the MongoDB data supplied to the service unless you add an external market-data integration.
