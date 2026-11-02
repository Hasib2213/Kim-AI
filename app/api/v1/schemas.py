from typing import Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, model_validator


class RetellToolRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')

    @model_validator(mode='before')
    @classmethod
    def extract_from_retell_wrapper(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Retell wraps tool arguments inside an 'args' dictionary
            if 'args' in data and isinstance(data['args'], dict):
                data = {**data, **data['args']}
            # Extract caller phone from call object if present
            if not data.get('caller_phone') and 'call' in data and isinstance(data['call'], dict):
                data['caller_phone'] = (
                    data['call'].get('from_number')
                    or data['call'].get('customer', {}).get('number')
                    or data['call'].get('customer_number')
                )
        return data


class ChatRequest(BaseModel):
    user_id: str
    message: str
    conversation_id: str | None = None


class SearchRequest(RetellToolRequest):
    query: str = ''


class RecommendRequest(BaseModel):
    user_profile: dict
    property_ids: list[str] = Field(default_factory=list)


class CompareRequest(BaseModel):
    property_ids: list[str]


class PropertyCreateRequest(BaseModel):
    model_config = ConfigDict(extra='allow')
    title: str | None = None
    name: str | None = None
    property_type: str | None = None
    property_class: str | None = None
    listing_type: str | None = None
    price: Any | None = None
    currency: str = 'IDR'
    location: Any | None = None
    specifications: dict | None = None
    amenities: list[str] = Field(default_factory=list)
    description: str | None = None
    agent: dict | None = None
    status: str = 'draft'


class LeadQualifyRequest(BaseModel):
    transcript: str


class OutboundCallRequest(BaseModel):
    provider: str = 'retell'
    to_number: str
    lead_id: str | None = None
    customer_name: str | None = None
    property_id: str | None = None
    call_reason: str | None = None
    max_duration_seconds: int = Field(default=180, ge=30, le=180)


class InboundCallContextRequest(BaseModel):
    provider: str = 'retell'
    provider_call_id: str | None = None
    from_number: str | None = None
    to_number: str | None = None
    property_id: str | None = None
    lead_id: str | None = None
    status: str = 'active'
    metadata: dict = Field(default_factory=dict)
    max_duration_seconds: int = Field(default=180, ge=30, le=180)


class InboundCallResolveRequest(BaseModel):
    provider: str = 'retell'
    provider_call_id: str | None = None
    from_number: str | None = None
    to_number: str | None = None
    property_id: str | None = None
    payload: dict = Field(default_factory=dict)


class ListingQuestionRequest(RetellToolRequest):
    property_id: str = ''
    question: str = ''
    caller_phone: str | None = None


class CallLeadUpsertRequest(RetellToolRequest):
    phone: str | None = None
    name: str | None = None
    email: str | None = None
    property_id: str | None = None
    budget: str | None = None
    location_preference: str | None = None
    notes: str | None = None
    source: str = 'ai_call'
    status: str = 'new'
    requirements: dict = Field(default_factory=dict)


class WhatsAppHandoffRequest(RetellToolRequest):
    property_id: str = ''
    caller_phone: str | None = None
    lead_id: str | None = None
    reason: str = 'AI call fallback requested'


class CallOutcomeRequest(RetellToolRequest):
    provider: str = 'retell'
    provider_call_id: str | None = None
    lead_id: str | None = None
    property_id: str | None = None
    direction: str | None = None
    status: str = 'completed'
    duration_seconds: int | None = None
    transcript: str | None = None
    summary: dict = Field(default_factory=dict)
    qualification: dict = Field(default_factory=dict)


class VisitCreateRequest(BaseModel):
    customer_id: str
    property_id: str
    scheduled_for: datetime
    agent_id: str | None = None
    notes: str | None = None


class FollowupCreateRequest(BaseModel):
    lead_id: str
    channel: str
    scheduled_for: datetime
    message: str | None = None


class MortgageRequest(BaseModel):
    principal: float
    annual_rate_percent: float
    years: int

class MarketInsightsRequest(BaseModel):
    location: str | None = None
    property_type: str | None = None


class CallAnalyzeRequest(BaseModel):
    transcript: str


class HandoffRequest(BaseModel):
    lead_id: str
    reason: str
    preferred_agent_id: str | None = None
