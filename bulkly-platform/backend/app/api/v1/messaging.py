import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.config import settings
from app.models import Lead, Message, Conversation
from app.schemas import SendMessageRequest
from app.api.deps import get_current_user
from app.models import User
from app.services.channel_service import ChannelService
from app.services.ai_service import AIService
from datetime import datetime, timezone

router = APIRouter(prefix="/messaging", tags=["Messaging"])
channel_service = ChannelService()
ai_service = AIService()


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, org_id: str, websocket: WebSocket):
        await websocket.accept()
        if org_id not in self.active_connections:
            self.active_connections[org_id] = []
        self.active_connections[org_id].append(websocket)

    def disconnect(self, org_id: str, websocket: WebSocket):
        if org_id in self.active_connections:
            self.active_connections[org_id].remove(websocket)
            if not self.active_connections[org_id]:
                del self.active_connections[org_id]

    async def broadcast_to_org(self, org_id: str, message: dict):
        if org_id in self.active_connections:
            for connection in self.active_connections[org_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass


ws_manager = ConnectionManager()


@router.websocket("/ws/{org_id}")
async def websocket_endpoint(websocket: WebSocket, org_id: str):
    await ws_manager.connect(org_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(org_id, websocket)


@router.post("/send", response_model=dict)
async def send_message(
    payload: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a single message to a lead via a specific channel."""
    lead_result = await db.execute(
        select(Lead).where(Lead.id == payload.lead_id, Lead.org_id == current_user.org_id)
    )
    lead = lead_result.scalar_one_or_none()
    if not lead:
        raise HTTPException(404, "Lead not found")

    # Get recipient ID for this channel
    recipient_map = {
        "whatsapp": lead.whatsapp_number or lead.phone,
        "email": lead.email,
        "sms": lead.phone,
        "telegram": lead.telegram_id,
        "instagram": lead.instagram_id,
        "facebook": lead.facebook_id,
    }
    recipient = recipient_map.get(payload.channel)
    if not recipient:
        raise HTTPException(400, f"Lead has no {payload.channel} contact info")

    # Send message
    result = await channel_service.send_message(
        channel=payload.channel,
        recipient_id=recipient,
        content=payload.content,
        media_url=payload.media_url,
    )

    # Log message
    msg = Message(
        id=str(uuid.uuid4()),
        lead_id=lead.id,
        org_id=current_user.org_id,
        channel=payload.channel,
        direction="outbound",
        recipient_id=recipient,
        content=payload.content,
        media_url=payload.media_url,
        status="sent" if result["success"] else "failed",
        external_message_id=result.get("message_id"),
    )
    db.add(msg)

    # Broadcast outgoing message to connected clients
    await ws_manager.broadcast_to_org(current_user.org_id, {
        "type": "outbound_message",
        "lead_id": lead.id,
        "channel": payload.channel,
        "content": payload.content,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    # Update lead last contact
    lead.last_contact_date = datetime.now(timezone.utc)
    await db.commit()

    return {
        "success": result["success"],
        "message_id": msg.id,
        "channel": payload.channel,
        "simulated": result.get("simulated", False),
        "error": result.get("error"),
    }


@router.post("/webhook/whatsapp", response_model=dict)
async def whatsapp_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle incoming WhatsApp Business API webhook events."""
    # Verify webhook
    params = request.query_params
    if params.get("hub.mode") == "subscribe":
        if params.get("hub.verify_token") == settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN:
            return int(params.get("hub.challenge", 0))
        raise HTTPException(403, "Verification failed")

    try:
        body = await request.json()
        entry = body.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        for msg_data in messages:
            if msg_data.get("type") != "text":
                continue

            from_number = msg_data.get("from")
            text = msg_data.get("text", {}).get("body", "")
            external_id = msg_data.get("id")

            # Find or create lead
            lead_result = await db.execute(
                select(Lead).where(Lead.whatsapp_number.contains(from_number[-9:]))
            )
            lead = lead_result.scalar_one_or_none()

            if lead:
                # Log inbound message
                inbound_msg = Message(
                    id=str(uuid.uuid4()),
                    lead_id=lead.id,
                    org_id=lead.org_id,
                    channel="whatsapp",
                    direction="inbound",
                    recipient_id=from_number,
                    content=text,
                    status="delivered",
                    external_message_id=external_id,
                )
                db.add(inbound_msg)

                # Broadcast incoming message to frontend
                await ws_manager.broadcast_to_org(lead.org_id, {
                    "type": "inbound_message",
                    "lead_id": lead.id,
                    "channel": "whatsapp",
                    "content": text,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })

                # Auto AI reply if enabled
                ai_response = await ai_service.generate_reply(
                    incoming_message=text,
                    lead_context={"name": lead.full_name, "status": lead.status,
                                  "score": lead.score, "notes": lead.notes, "company": lead.company},
                    conversation_history=[],
                    channel="whatsapp",
                )

                if not ai_response.requires_human:
                    await channel_service.send_message(
                        channel="whatsapp",
                        recipient_id=from_number,
                        content=ai_response.reply,
                    )
                    
                    # Broadcast AI reply
                    await ws_manager.broadcast_to_org(lead.org_id, {
                        "type": "outbound_message",
                        "lead_id": lead.id,
                        "channel": "whatsapp",
                        "content": ai_response.reply,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "is_ai": True
                    })

                await db.commit()

    except Exception as e:
        pass  # Never return error to Meta or webhook will be disabled

    return {"status": "ok"}


@router.get("/templates", response_model=list[dict])
async def get_message_templates(current_user: User = Depends(get_current_user)):
    """Return pre-built message templates."""
    return [
        {"id": "1", "name": "Welcome Message", "channel": "whatsapp",
         "content": "Hi {{name}}! Welcome to our service. How can we help you today? 😊"},
        {"id": "2", "name": "Follow-Up", "channel": "whatsapp",
         "content": "Hi {{name}}, just checking in! Did you get a chance to review our proposal? Let me know if you have any questions."},
        {"id": "3", "name": "Promotional Offer", "channel": "whatsapp",
         "content": "🎉 Special offer for you, {{name}}! Get 20% off today only. Reply YES to claim your discount."},
        {"id": "4", "name": "Appointment Reminder", "channel": "sms",
         "content": "Reminder: Your appointment is scheduled for tomorrow. Reply CONFIRM or CANCEL."},
        {"id": "5", "name": "Lead Nurture", "channel": "email",
         "content": "Hi {{name}},\n\nThank you for your interest in our solution. I'd love to schedule a quick 15-minute call to learn more about your needs.\n\nBest regards,\nThe Bulkly Team"},
        {"id": "6", "name": "Re-engagement", "channel": "whatsapp",
         "content": "Hi {{name}}, we miss you! 👋 Check out what's new at {{company}}. Click here to see our latest updates."},
    ]


@router.post("/broadcast", response_model=dict)
async def fire_broadcast(
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fire a bulk broadcast based on audience filter and channel."""
    channel = payload.get("channel", "whatsapp")
    audience_filter = payload.get("audience_filter", "all")
    message_content = payload.get("message", "")
    
    # Simple audience filtering
    query = select(Lead).where(Lead.org_id == current_user.org_id)
    if audience_filter == "hot":
        query = query.where(Lead.score > 80)
    elif audience_filter == "cold":
        query = query.where(Lead.status == "cold")
        
    leads_result = await db.execute(query)
    leads = leads_result.scalars().all()
    
    success_count = 0
    for lead in leads:
        recipient_map = {
            "whatsapp": lead.whatsapp_number or lead.phone,
            "email": lead.email,
            "sms": lead.phone,
        }
        recipient = recipient_map.get(channel)
        
        if recipient:
            # Inject variables
            final_content = message_content.replace("{{first_name}}", lead.full_name.split()[0]).replace("{{company}}", lead.company or "")
            
            # Send message via mock channel service
            await channel_service.send_message(
                channel=channel,
                recipient_id=recipient,
                content=final_content,
            )
            success_count += 1
            
    return {"success": True, "messages_sent": success_count, "channel": channel}
