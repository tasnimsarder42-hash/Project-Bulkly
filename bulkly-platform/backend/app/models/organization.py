import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import String, Boolean, DateTime, Text, Integer, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base


class PlanType(str, PyEnum):
    STARTER = "starter"
    PROFESSIONAL = "professional"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    logo_url: Mapped[str] = mapped_column(String(500), nullable=True)
    plan: Mapped[str] = mapped_column(String(50), default=PlanType.STARTER, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    stripe_customer_id: Mapped[str] = mapped_column(String(100), nullable=True)
    stripe_subscription_id: Mapped[str] = mapped_column(String(100), nullable=True)
    monthly_message_limit: Mapped[int] = mapped_column(Integer, default=1000)
    messages_sent_this_month: Mapped[int] = mapped_column(Integer, default=0)
    settings: Mapped[dict] = mapped_column(JSON, default=dict)
    # Platform credentials (encrypted in production)
    whatsapp_phone_number_id: Mapped[str] = mapped_column(String(100), nullable=True)
    whatsapp_access_token: Mapped[str] = mapped_column(Text, nullable=True)
    meta_access_token: Mapped[str] = mapped_column(Text, nullable=True)
    telegram_bot_token: Mapped[str] = mapped_column(Text, nullable=True)
    sendgrid_api_key: Mapped[str] = mapped_column(Text, nullable=True)
    twilio_account_sid: Mapped[str] = mapped_column(String(100), nullable=True)
    twilio_auth_token: Mapped[str] = mapped_column(Text, nullable=True)
    twilio_from_number: Mapped[str] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    users: Mapped[list["User"]] = relationship("User", back_populates="organization")
    leads: Mapped[list["Lead"]] = relationship("Lead", back_populates="organization")
    campaigns: Mapped[list["Campaign"]] = relationship("Campaign", back_populates="organization")
