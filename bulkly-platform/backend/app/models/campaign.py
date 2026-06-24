import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, Integer, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base


class CampaignStatus(str, PyEnum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class CampaignType(str, PyEnum):
    BULK_BLAST = "bulk_blast"
    DRIP = "drip"
    TRIGGERED = "triggered"
    AB_TEST = "ab_test"


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(String(50), default=CampaignType.BULK_BLAST, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default=CampaignStatus.DRAFT, nullable=False, index=True)

    # Targeting
    channels: Mapped[list] = mapped_column(JSON, default=list)  # ["whatsapp","email","sms"]
    target_segments: Mapped[list] = mapped_column(JSON, default=list)
    target_tags: Mapped[list] = mapped_column(JSON, default=list)
    target_lead_ids: Mapped[list] = mapped_column(JSON, default=list)

    # Content
    message_template: Mapped[str] = mapped_column(Text, nullable=True)
    subject_line: Mapped[str] = mapped_column(String(500), nullable=True)
    media_url: Mapped[str] = mapped_column(String(500), nullable=True)
    use_ai_personalization: Mapped[bool] = mapped_column(Boolean, default=False)

    # Scheduling
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    send_speed: Mapped[str] = mapped_column(String(50), default="normal")  # slow, normal, fast
    daily_limit: Mapped[int] = mapped_column(Integer, default=200)
    delay_between_messages_ms: Mapped[int] = mapped_column(Integer, default=3000)

    # Analytics
    total_recipients: Mapped[int] = mapped_column(Integer, default=0)
    sent_count: Mapped[int] = mapped_column(Integer, default=0)
    delivered_count: Mapped[int] = mapped_column(Integer, default=0)
    read_count: Mapped[int] = mapped_column(Integer, default=0)
    replied_count: Mapped[int] = mapped_column(Integer, default=0)
    converted_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)
    revenue_generated: Mapped[float] = mapped_column(Float, default=0.0)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="campaigns")
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="campaign")
