import httpx
from typing import Optional
from app.core.config import settings


class ChannelService:
    """Multi-channel message dispatcher. Routes messages to the correct platform API."""

    async def send_message(
        self,
        channel: str,
        recipient_id: str,
        content: str,
        media_url: Optional[str] = None,
        org_credentials: Optional[dict] = None,
    ) -> dict:
        """Dispatch a message to the appropriate channel."""
        creds = org_credentials or {}
        dispatch = {
            "whatsapp": self._send_whatsapp,
            "telegram": self._send_telegram,
            "email": self._send_email,
            "sms": self._send_sms,
            "instagram": self._send_instagram,
            "facebook": self._send_facebook,
        }
        handler = dispatch.get(channel)
        if not handler:
            return {"success": False, "error": f"Unsupported channel: {channel}"}
        return await handler(recipient_id, content, media_url, creds)

    # ── WhatsApp Business Cloud API ────────────────────────────────────────────
    async def _send_whatsapp(self, to: str, content: str, media_url: Optional[str], creds: dict) -> dict:
        phone_id = creds.get("whatsapp_phone_number_id") or settings.WHATSAPP_PHONE_NUMBER_ID
        token = creds.get("whatsapp_access_token") or settings.WHATSAPP_ACCESS_TOKEN

        if not phone_id or not token:
            return {"success": False, "error": "WhatsApp credentials not configured", "simulated": True}

        url = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/{phone_id}/messages"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to.replace("+", "").replace(" ", "").replace("-", ""),
            "type": "text",
            "text": {"preview_url": False, "body": content},
        }

        if media_url:
            payload["type"] = "image"
            payload["image"] = {"link": media_url, "caption": content}
            del payload["text"]

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.post(url, headers=headers, json=payload)
                data = resp.json()
                if resp.status_code == 200:
                    return {"success": True, "message_id": data.get("messages", [{}])[0].get("id")}
                return {"success": False, "error": data.get("error", {}).get("message", "Unknown error")}
            except Exception as e:
                return {"success": False, "error": str(e)}

    # ── Telegram Bot API ───────────────────────────────────────────────────────
    async def _send_telegram(self, chat_id: str, content: str, media_url: Optional[str], creds: dict) -> dict:
        token = creds.get("telegram_bot_token") or settings.TELEGRAM_BOT_TOKEN
        if not token:
            return {"success": False, "error": "Telegram token not configured", "simulated": True}

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.post(url, json={"chat_id": chat_id, "text": content, "parse_mode": "HTML"})
                data = resp.json()
                return {"success": data.get("ok", False), "message_id": data.get("result", {}).get("message_id")}
            except Exception as e:
                return {"success": False, "error": str(e)}

    # ── Email via SendGrid ─────────────────────────────────────────────────────
    async def _send_email(self, to_email: str, content: str, media_url: Optional[str], creds: dict) -> dict:
        api_key = creds.get("sendgrid_api_key") or settings.SENDGRID_API_KEY
        if not api_key:
            return {"success": False, "error": "SendGrid API key not configured", "simulated": True}

        url = "https://api.sendgrid.com/v3/mail/send"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {"email": settings.SENDGRID_FROM_EMAIL, "name": "Bulkly"},
            "subject": "Message from Bulkly",
            "content": [{"type": "text/html", "value": content}],
        }

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.post(url, headers=headers, json=payload)
                return {"success": resp.status_code in (200, 202), "status_code": resp.status_code}
            except Exception as e:
                return {"success": False, "error": str(e)}

    # ── SMS via Twilio ─────────────────────────────────────────────────────────
    async def _send_sms(self, to: str, content: str, media_url: Optional[str], creds: dict) -> dict:
        account_sid = creds.get("twilio_account_sid") or settings.TWILIO_ACCOUNT_SID
        auth_token = creds.get("twilio_auth_token") or settings.TWILIO_AUTH_TOKEN
        from_num = creds.get("twilio_from_number") or settings.TWILIO_FROM_NUMBER

        if not all([account_sid, auth_token, from_num]):
            return {"success": False, "error": "Twilio credentials not configured", "simulated": True}

        url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.post(
                    url,
                    auth=(account_sid, auth_token),
                    data={"From": from_num, "To": to, "Body": content},
                )
                data = resp.json()
                return {"success": resp.status_code == 201, "message_id": data.get("sid")}
            except Exception as e:
                return {"success": False, "error": str(e)}

    # ── Instagram & Facebook (Meta Graph API) ─────────────────────────────────
    async def _send_instagram(self, recipient_id: str, content: str, media_url: Optional[str], creds: dict) -> dict:
        token = creds.get("meta_access_token") or settings.META_ACCESS_TOKEN
        if not token:
            return {"success": False, "error": "Meta access token not configured", "simulated": True}

        url = "https://graph.facebook.com/v19.0/me/messages"
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.post(
                    url,
                    params={"access_token": token},
                    json={"recipient": {"id": recipient_id}, "message": {"text": content}},
                )
                data = resp.json()
                return {"success": "message_id" in data, "message_id": data.get("message_id")}
            except Exception as e:
                return {"success": False, "error": str(e)}

    async def _send_facebook(self, recipient_id: str, content: str, media_url: Optional[str], creds: dict) -> dict:
        return await self._send_instagram(recipient_id, content, media_url, creds)
