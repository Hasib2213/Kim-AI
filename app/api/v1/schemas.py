from datetime import datetime
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    user_id: str
    message: str
    conversation_id: str | None = None


class SearchRequest(BaseModel):
    query: str


class RecommendRequest(BaseModel):
    user_profile: dict
    property_ids: list[str] = Field(default_factory=list)


class CompareRequest(BaseModel):
    property_ids: list[str]


class LeadQualifyRequest(BaseModel):
    transcript: str


class OutboundCallRequest(BaseModel):
    provider: str = 'retell'
    to_number: str
    lead_id: str | None = None
    customer_name: str | None = None


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
