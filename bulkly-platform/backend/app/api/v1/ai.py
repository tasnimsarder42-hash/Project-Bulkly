import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import Lead, Conversation, User
from app.schemas import AIReplyRequest, AIReplyResponse, AIChatRequest, AIChatResponse
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["AI Engine"])
ai_service = AIService()


@router.post("/reply", response_model=AIReplyResponse)
async def generate_ai_reply(
    payload: AIReplyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Analyze incoming message and generate a context-aware AI reply."""
    # Fetch lead context
    lead_result = await db.execute(
        select(Lead).where(Lead.id == payload.lead_id, Lead.org_id == current_user.org_id)
    )
    lead = lead_result.scalar_one_or_none()
    if not lead:
        raise HTTPException(404, "Lead not found")

    # Fetch conversation history
    conv_result = await db.execute(
        select(Conversation).where(
            Conversation.lead_id == payload.lead_id,
            Conversation.channel == payload.channel,
        )
    )
    conversation = conv_result.scalar_one_or_none()
    history = conversation.messages if conversation else []

    response = await ai_service.generate_reply(
        incoming_message=payload.incoming_message,
        lead_context={
            "name": lead.full_name,
            "company": lead.company,
            "status": lead.status,
            "score": lead.score,
            "notes": lead.notes,
        },
        conversation_history=history,
        channel=payload.channel,
    )

    # Update lead sentiment
    lead.sentiment = response.sentiment
    lead.buying_intent = response.buying_intent_score
    await db.commit()

    return response


@router.post("/chat", response_model=AIChatResponse)
async def ai_assistant_chat(
    payload: AIChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """General Bulkly AI assistant chat for users."""
    response = await ai_service.chat_with_assistant(
        message=payload.message,
        user_context={
            "name": current_user.full_name,
            "role": current_user.role,
        },
        context=payload.context or {},
    )
    return response


@router.post("/qualify-lead/{lead_id}", response_model=dict)
async def qualify_lead(
    lead_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Run AI lead qualification to score and segment the lead."""
    lead_result = await db.execute(
        select(Lead).where(Lead.id == lead_id, Lead.org_id == current_user.org_id)
    )
    lead = lead_result.scalar_one_or_none()
    if not lead:
        raise HTTPException(404, "Lead not found")

    qualification = await ai_service.qualify_lead(lead)
    lead.score = qualification["score"]
    lead.ai_summary = qualification["summary"]
    lead.sentiment = qualification["sentiment"]
    lead.buying_intent = qualification["buying_intent"]
    await db.commit()

    return qualification


@router.post("/generate-campaign-copy", response_model=dict)
async def generate_campaign_copy(
    payload: dict,
    current_user: User = Depends(get_current_user),
):
    """Generate AI-powered campaign message copy."""
    copy = await ai_service.generate_campaign_copy(
        product=payload.get("product", ""),
        audience=payload.get("audience", ""),
        goal=payload.get("goal", "sales"),
        tone=payload.get("tone", "professional"),
        channel=payload.get("channel", "whatsapp"),
    )
    return {"copy": copy}
