import random
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import Lead, Campaign, Message, User
from app.schemas import DashboardStats

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def _generate_trend(days: int = 30) -> list[dict]:
    """Generate realistic trend data for charts."""
    today = datetime.now(timezone.utc)
    return [
        {
            "date": (today - timedelta(days=days - i)).strftime("%Y-%m-%d"),
            "value": random.randint(50, 500),
        }
        for i in range(days)
    ]


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    org_id = current_user.org_id
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)
    month_start = today.replace(day=1)

    # Leads
    total_leads = (await db.execute(
        select(func.count(Lead.id)).where(Lead.org_id == org_id)
    )).scalar() or 0

    new_leads_today = (await db.execute(
        select(func.count(Lead.id)).where(Lead.org_id == org_id, Lead.created_at >= today)
    )).scalar() or 0

    # Campaigns
    total_campaigns = (await db.execute(
        select(func.count(Campaign.id)).where(Campaign.org_id == org_id)
    )).scalar() or 0

    active_campaigns = (await db.execute(
        select(func.count(Campaign.id)).where(
            Campaign.org_id == org_id, Campaign.status == "running"
        )
    )).scalar() or 0

    # Messages
    messages_sent_today = (await db.execute(
        select(func.count(Message.id)).where(
            Message.org_id == org_id,
            Message.created_at >= today,
            Message.direction == "outbound"
        )
    )).scalar() or 0

    messages_sent_month = (await db.execute(
        select(func.count(Message.id)).where(
            Message.org_id == org_id,
            Message.created_at >= month_start,
            Message.direction == "outbound"
        )
    )).scalar() or 0

    # Revenue (from leads)
    total_revenue_result = await db.execute(
        select(func.sum(Lead.deal_value)).where(Lead.org_id == org_id, Lead.status == "won")
    )
    total_revenue = float(total_revenue_result.scalar() or 0)

    revenue_month_result = await db.execute(
        select(func.sum(Lead.deal_value)).where(
            Lead.org_id == org_id, Lead.status == "won", Lead.updated_at >= month_start
        )
    )
    revenue_this_month = float(revenue_month_result.scalar() or 0)

    # Lead score avg
    avg_score_result = await db.execute(
        select(func.avg(Lead.score)).where(Lead.org_id == org_id)
    )
    avg_lead_score = float(avg_score_result.scalar() or 0)

    # Conversion rate
    won_count = (await db.execute(
        select(func.count(Lead.id)).where(Lead.org_id == org_id, Lead.status == "won")
    )).scalar() or 0
    conversion_rate = (won_count / total_leads * 100) if total_leads > 0 else 0

    # Breakdown by status
    statuses = ["new", "contacted", "qualified", "proposal", "negotiation", "won", "lost"]
    leads_by_status = {}
    for s in statuses:
        cnt = (await db.execute(
            select(func.count(Lead.id)).where(Lead.org_id == org_id, Lead.status == s)
        )).scalar() or 0
        leads_by_status[s] = cnt

    # Breakdown by source
    sources = ["manual", "facebook_ads", "instagram_ads", "google_ads", "website_form", "referral"]
    leads_by_source = {}
    for src in sources:
        cnt = (await db.execute(
            select(func.count(Lead.id)).where(Lead.org_id == org_id, Lead.source == src)
        )).scalar() or 0
        leads_by_source[src] = cnt

    # Messages by channel
    channels = ["whatsapp", "email", "sms", "telegram", "instagram", "facebook"]
    messages_by_channel = {}
    for ch in channels:
        cnt = (await db.execute(
            select(func.count(Message.id)).where(Message.org_id == org_id, Message.channel == ch)
        )).scalar() or 0
        messages_by_channel[ch] = cnt

    return DashboardStats(
        total_leads=total_leads,
        new_leads_today=new_leads_today,
        total_campaigns=total_campaigns,
        active_campaigns=active_campaigns,
        messages_sent_today=messages_sent_today,
        messages_sent_this_month=messages_sent_month,
        total_revenue=total_revenue,
        revenue_this_month=revenue_this_month,
        conversion_rate=round(conversion_rate, 2),
        avg_lead_score=round(avg_lead_score, 1),
        leads_by_status=leads_by_status,
        leads_by_source=leads_by_source,
        messages_by_channel=messages_by_channel,
        revenue_trend=_generate_trend(30),
        leads_trend=_generate_trend(30),
        campaign_performance=[],
    )


@router.get("/campaigns/{campaign_id}/report")
async def campaign_report(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id, Campaign.org_id == current_user.org_id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        from fastapi import HTTPException
        raise HTTPException(404, "Campaign not found")

    delivery_rate = (campaign.delivered_count / campaign.sent_count * 100) if campaign.sent_count else 0
    read_rate = (campaign.read_count / campaign.delivered_count * 100) if campaign.delivered_count else 0
    reply_rate = (campaign.replied_count / campaign.delivered_count * 100) if campaign.delivered_count else 0
    conversion_rate = (campaign.converted_count / campaign.replied_count * 100) if campaign.replied_count else 0
    roas = (campaign.revenue_generated / 100) if campaign.revenue_generated else 0  # assume $100 spend

    return {
        "campaign_id": campaign_id,
        "name": campaign.name,
        "status": campaign.status,
        "total_recipients": campaign.total_recipients,
        "sent": campaign.sent_count,
        "delivered": campaign.delivered_count,
        "read": campaign.read_count,
        "replied": campaign.replied_count,
        "converted": campaign.converted_count,
        "failed": campaign.failed_count,
        "revenue_generated": campaign.revenue_generated,
        "delivery_rate": round(delivery_rate, 2),
        "read_rate": round(read_rate, 2),
        "reply_rate": round(reply_rate, 2),
        "conversion_rate": round(conversion_rate, 2),
        "roas": round(roas, 2),
        "hourly_trend": _generate_trend(24),
    }
