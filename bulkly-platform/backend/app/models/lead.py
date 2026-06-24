import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, Integer, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base


class LeadStatus(str, PyEnum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"
    UNQUALIFIED = "unqualified"


class LeadSource(str, PyEnum):
    MANUAL = "manual"
    FACEBOOK_ADS = "facebook_ads"
    INSTAGRAM_ADS = "instagram_ads"
    GOOGLE_ADS = "google_ads"
    TIKTOK_ADS = "tiktok_ads"
    LINKEDIN = "linkedin"
    WEBSITE_FORM = "website_form"
    CHATBOT = "chatbot"
    IMPORT = "import"
    REFERRAL = "referral"


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    assigned_to: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)

    # Core info
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[str] = mapped_column(String(50), nullable=True, index=True)
    company: Mapped[str] = mapped_column(String(255), nullable=True)
    job_title: Mapped[str] = mapped_column(String(255), nullable=True)
    website: Mapped[str] = mapped_column(String(500), nullable=True)
    location: Mapped[str] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str] = mapped_column(String(500), nullable=True)

    # Social profiles
    whatsapp_number: Mapped[str] = mapped_column(String(50), nullable=True)
    telegram_id: Mapped[str] = mapped_column(String(100), nullable=True)
    instagram_id: Mapped[str] = mapped_column(String(100), nullable=True)
    facebook_id: Mapped[str] = mapped_column(String(100), nullable=True)
    linkedin_url: Mapped[str] = mapped_column(String(500), nullable=True)

    # CRM fields
    status: Mapped[str] = mapped_column(String(50), default=LeadStatus.NEW, nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(50), default=LeadSource.MANUAL, nullable=False)
    score: Mapped[int] = mapped_column(Integer, default=0)
    deal_value: Mapped[float] = mapped_column(Float, default=0.0)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    custom_fields: Mapped[dict] = mapped_column(JSON, default=dict)
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    # AI fields
    sentiment: Mapped[str] = mapped_column(String(50), nullable=True)
    buying_intent: Mapped[float] = mapped_column(Float, default=0.0)
    ai_summary: Mapped[str] = mapped_column(Text, nullable=True)

    # Purchase history
    total_purchases: Mapped[float] = mapped_column(Float, default=0.0)
    purchase_count: Mapped[int] = mapped_column(Integer, default=0)
    last_purchase_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Tracking
    last_contact_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    next_follow_up: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="leads")
    assigned_to_user: Mapped["User"] = relationship("User", back_populates="leads")
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="lead")
    conversations: Mapped[list["Conversation"]] = relationship("Conversation", back_populates="lead")
