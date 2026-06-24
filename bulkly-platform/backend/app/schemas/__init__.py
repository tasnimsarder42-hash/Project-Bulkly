from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, EmailStr, Field


# ── Auth ──────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2)
    org_name: str = Field(min_length=2)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserOut"


class RefreshRequest(BaseModel):
    refresh_token: str


# ── User ──────────────────────────────────────────────────────────────────────

class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    org_id: Optional[str]
    avatar_url: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserInviteRequest(BaseModel):
    email: EmailStr
    role: str


# ── Organization ──────────────────────────────────────────────────────────────

class OrgOut(BaseModel):
    id: str
    name: str
    slug: str
    plan: str
    logo_url: Optional[str]
    monthly_message_limit: int
    messages_sent_this_month: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── Lead ──────────────────────────────────────────────────────────────────────

class LeadCreate(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    whatsapp_number: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    location: Optional[str] = None
    source: Optional[str] = "manual"
    status: Optional[str] = "new"
    deal_value: Optional[float] = 0.0
    tags: Optional[list[str]] = []
    notes: Optional[str] = None
    assigned_to: Optional[str] = None


class LeadUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    whatsapp_number: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    status: Optional[str] = None
    score: Optional[int] = None
    deal_value: Optional[float] = None
    tags: Optional[list[str]] = None
    notes: Optional[str] = None
    assigned_to: Optional[str] = None
    next_follow_up: Optional[datetime] = None


class LeadOut(BaseModel):
    id: str
    full_name: str
    email: Optional[str]
    phone: Optional[str]
    whatsapp_number: Optional[str]
    company: Optional[str]
    job_title: Optional[str]
    location: Optional[str]
    status: str
    source: str
    score: int
    deal_value: float
    tags: list
    notes: Optional[str]
    sentiment: Optional[str]
    buying_intent: float
    ai_summary: Optional[str]
    assigned_to: Optional[str]
    last_contact_date: Optional[datetime]
    next_follow_up: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class LeadListResponse(BaseModel):
    items: list[LeadOut]
    total: int
    page: int
    page_size: int
    total_pages: int


# ── Campaign ──────────────────────────────────────────────────────────────────

class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    type: str = "bulk_blast"
    channels: list[str] = ["whatsapp"]
    target_tags: list[str] = []
    target_lead_ids: list[str] = []
    message_template: str
    subject_line: Optional[str] = None
    media_url: Optional[str] = None
    use_ai_personalization: bool = False
    scheduled_at: Optional[datetime] = None
    send_speed: str = "normal"
    daily_limit: int = 200


class CampaignOut(BaseModel):
    id: str
    name: str
    description: Optional[str]
    type: str
    status: str
    channels: list
    total_recipients: int
    sent_count: int
    delivered_count: int
    read_count: int
    replied_count: int
    converted_count: int
    failed_count: int
    revenue_generated: float
    scheduled_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Analytics ─────────────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_leads: int
    new_leads_today: int
    total_campaigns: int
    active_campaigns: int
    messages_sent_today: int
    messages_sent_this_month: int
    total_revenue: float
    revenue_this_month: float
    conversion_rate: float
    avg_lead_score: float
    leads_by_status: dict[str, int]
    leads_by_source: dict[str, int]
    messages_by_channel: dict[str, int]
    revenue_trend: list[dict]       # [{date, revenue}]
    leads_trend: list[dict]         # [{date, count}]
    campaign_performance: list[dict]


# ── AI ────────────────────────────────────────────────────────────────────────

class AIReplyRequest(BaseModel):
    lead_id: str
    incoming_message: str
    channel: str = "whatsapp"
    conversation_history: list[dict] = []


class AIReplyResponse(BaseModel):
    reply: str
    intent: str
    sentiment: str
    buying_intent_score: float
    suggested_actions: list[str]
    requires_human: bool


class AIChatRequest(BaseModel):
    message: str
    context: Optional[dict] = None


class AIChatResponse(BaseModel):
    response: str
    suggestions: list[str] = []


# ── Message Send ──────────────────────────────────────────────────────────────

class SendMessageRequest(BaseModel):
    lead_id: str
    channel: str
    content: str
    media_url: Optional[str] = None


class BulkSendRequest(BaseModel):
    campaign_id: str


TokenResponse.model_rebuild()
