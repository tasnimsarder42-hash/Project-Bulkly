import asyncio
import random
import uuid
from datetime import datetime, timezone
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "bulkly_workers",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "app.workers.message_worker.run_campaign_task": {"queue": "campaigns"},
        "app.workers.message_worker.send_single_message": {"queue": "messages"},
    },
)


@celery_app.task(bind=True, max_retries=3, name="app.workers.message_worker.send_single_message")
def send_single_message(self, message_id: str, channel: str, recipient_id: str,
                        content: str, org_credentials: dict):
    """Send a single message with retry logic."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        from app.services.channel_service import ChannelService
        service = ChannelService()
        result = loop.run_until_complete(
            service.send_message(
                channel=channel,
                recipient_id=recipient_id,
                content=content,
                org_credentials=org_credentials,
            )
        )

        # Update message status in DB
        _update_message_status(message_id, "delivered" if result["success"] else "failed",
                               result.get("external_message_id"))
        return result
    except Exception as exc:
        self.retry(exc=exc, countdown=60 * (self.request.retries + 1))
    finally:
        loop.close()


@celery_app.task(bind=True, name="app.workers.message_worker.run_campaign_task")
def run_campaign_task(self, campaign_id: str):
    """
    Main campaign execution task.
    Implements human-like sending with:
    - Randomized delays between messages
    - Daily limit enforcement
    - Warm-up scaling
    - Queue-based delivery to avoid bursts
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_execute_campaign(campaign_id))
    finally:
        loop.close()


async def _execute_campaign(campaign_id: str):
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    from sqlalchemy import select
    from app.core.database import AsyncSessionLocal
    from app.models import Campaign, Lead, Message

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
        campaign = result.scalar_one_or_none()
        if not campaign or campaign.status != "running":
            return

        # Get target leads
        if campaign.target_lead_ids:
            leads_result = await db.execute(
                select(Lead).where(Lead.id.in_(campaign.target_lead_ids))
            )
        else:
            leads_result = await db.execute(
                select(Lead).where(Lead.org_id == campaign.org_id)
            )
        leads = leads_result.scalars().all()

        channels = campaign.channels or ["whatsapp"]
        sent = 0

        for lead in leads:
            if campaign.status != "running":
                break
            if sent >= campaign.daily_limit:
                break  # Respect daily limit

            for channel in channels:
                # Get recipient ID for channel
                recipient = _get_recipient_id(lead, channel)
                if not recipient:
                    continue

                # Personalize message
                content = campaign.message_template or ""
                content = content.replace("{{name}}", lead.full_name)
                content = content.replace("{{company}}", lead.company or "")

                # Create message record
                msg = Message(
                    id=str(uuid.uuid4()),
                    lead_id=lead.id,
                    campaign_id=campaign.id,
                    org_id=campaign.org_id,
                    channel=channel,
                    direction="outbound",
                    recipient_id=recipient,
                    content=content,
                    status="queued",
                )
                db.add(msg)
                await db.flush()

                # Dispatch to Celery with human-like delay
                send_single_message.apply_async(
                    args=[msg.id, channel, recipient, content, {}],
                    countdown=_human_delay(campaign.delay_between_messages_ms, sent),
                )

                campaign.sent_count += 1
                sent += 1

        campaign.status = "completed"
        campaign.completed_at = datetime.now(timezone.utc)
        await db.commit()


def _get_recipient_id(lead, channel: str) -> str | None:
    mapping = {
        "whatsapp": lead.whatsapp_number or lead.phone,
        "telegram": lead.telegram_id,
        "instagram": lead.instagram_id,
        "facebook": lead.facebook_id,
        "email": lead.email,
        "sms": lead.phone,
    }
    return mapping.get(channel)


def _human_delay(base_delay_ms: int, position: int) -> float:
    """Generate human-like randomized delay in seconds."""
    base = base_delay_ms / 1000
    jitter = random.uniform(0.7, 1.3)
    burst_penalty = (position % 10 == 9) and random.uniform(5, 15) or 0  # pause every 10 msgs
    return base * jitter + burst_penalty


def _update_message_status(message_id: str, status: str, external_id: str = None):
    """Sync helper to update message status."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def _update():
            from app.core.database import AsyncSessionLocal
            from app.models import Message
            from sqlalchemy import select
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(Message).where(Message.id == message_id))
                msg = result.scalar_one_or_none()
                if msg:
                    msg.status = status
                    if external_id:
                        msg.external_message_id = external_id
                    if status == "delivered":
                        msg.delivered_at = datetime.now(timezone.utc)
                    await db.commit()

        loop.run_until_complete(_update())
    except Exception:
        pass
    finally:
        loop.close()
