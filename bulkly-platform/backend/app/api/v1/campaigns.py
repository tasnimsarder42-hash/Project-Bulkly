import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import Campaign, Lead, User
from app.schemas import CampaignCreate, CampaignOut

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


@router.get("", response_model=list[CampaignOut])
async def list_campaigns(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Campaign).where(Campaign.org_id == current_user.org_id)
    if status:
        query = query.where(Campaign.status == status)
    query = query.order_by(Campaign.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return [CampaignOut.model_validate(c) for c in result.scalars().all()]


@router.post("", response_model=CampaignOut, status_code=201)
async def create_campaign(
    payload: CampaignCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Count recipients from target_lead_ids or all leads if empty
    if payload.target_lead_ids:
        total = len(payload.target_lead_ids)
    else:
        count_result = await db.execute(
            select(func.count(Lead.id)).where(Lead.org_id == current_user.org_id)
        )
        total = count_result.scalar()

    campaign = Campaign(
        id=str(uuid.uuid4()),
        org_id=current_user.org_id,
        created_by=current_user.id,
        total_recipients=total,
        **payload.model_dump(exclude_none=True),
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return CampaignOut.model_validate(campaign)


@router.get("/{campaign_id}", response_model=CampaignOut)
async def get_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id, Campaign.org_id == current_user.org_id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return CampaignOut.model_validate(campaign)


@router.post("/{campaign_id}/launch", response_model=dict)
async def launch_campaign(
    campaign_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id, Campaign.org_id == current_user.org_id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.status not in ("draft", "paused"):
        raise HTTPException(status_code=400, detail=f"Cannot launch a campaign with status: {campaign.status}")

    campaign.status = "running"
    campaign.started_at = datetime.now(timezone.utc)
    await db.commit()

    # Queue bulk send via Celery (imported here to avoid circular)
    background_tasks.add_task(_trigger_campaign_worker, campaign_id)
    return {"message": "Campaign launched successfully", "campaign_id": campaign_id}


@router.post("/{campaign_id}/pause", response_model=dict)
async def pause_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id, Campaign.org_id == current_user.org_id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    campaign.status = "paused"
    await db.commit()
    return {"message": "Campaign paused"}


@router.delete("/{campaign_id}", status_code=204)
async def delete_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id, Campaign.org_id == current_user.org_id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.status == "running":
        raise HTTPException(status_code=400, detail="Cannot delete a running campaign. Pause it first.")
    await db.delete(campaign)
    await db.commit()


async def _trigger_campaign_worker(campaign_id: str):
    """Placeholder: in production this dispatches a Celery task."""
    try:
        from app.workers.message_worker import run_campaign_task
        run_campaign_task.delay(campaign_id)
    except Exception:
        pass  # Celery may not be running in dev
