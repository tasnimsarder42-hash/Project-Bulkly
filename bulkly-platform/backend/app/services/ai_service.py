import json
from typing import Optional
import google.generativeai as genai
from app.core.config import settings
from app.schemas import AIReplyResponse, AIChatResponse

genai.configure(api_key=settings.GOOGLE_API_KEY)

SYSTEM_PROMPT = """You are Bulkly AI — an expert sales and marketing assistant built into the Bulkly CRM platform.
Your job is to:
1. Analyze customer messages to detect intent, sentiment, and buying signals
2. Generate highly personalized, professional responses
3. Help sales agents close deals and manage customer relationships
4. Provide actionable recommendations

You understand the context of each conversation and remember customer history.
Always be helpful, professional, and goal-oriented.
"""

REPLY_PROMPT_TEMPLATE = """
You are analyzing an incoming message from a customer and must generate the best possible reply.

CUSTOMER CONTEXT:
Name: {name}
Company: {company}
Pipeline Status: {status}
Lead Score: {score}/100
Agent Notes: {notes}

CONVERSATION HISTORY:
{history}

INCOMING MESSAGE:
"{message}"

CHANNEL: {channel}

Respond with a JSON object containing:
{{
  "reply": "<your generated reply message>",
  "intent": "<detected intent: inquiry/complaint/purchase_intent/follow_up/objection/other>",
  "sentiment": "<positive/neutral/negative>",
  "buying_intent_score": <0.0-1.0 float>,
  "suggested_actions": ["<action1>", "<action2>"],
  "requires_human": <true/false>
}}
"""


class AIService:
    def __init__(self):
        try:
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        except Exception:
            self.model = None

    async def generate_reply(
        self,
        incoming_message: str,
        lead_context: dict,
        conversation_history: list,
        channel: str = "whatsapp",
    ) -> AIReplyResponse:
        if not self.model or not settings.GOOGLE_API_KEY:
            return self._fallback_reply(incoming_message)

        history_text = "\n".join(
            [f"[{m.get('role','user')}]: {m.get('content','')}" for m in conversation_history[-10:]]
        )
        prompt = REPLY_PROMPT_TEMPLATE.format(
            name=lead_context.get("name", "Customer"),
            company=lead_context.get("company", "N/A"),
            status=lead_context.get("status", "new"),
            score=lead_context.get("score", 0),
            notes=lead_context.get("notes", "No notes"),
            history=history_text or "No previous conversation",
            message=incoming_message,
            channel=channel,
        )

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            data = json.loads(text)
            return AIReplyResponse(**data)
        except Exception as e:
            return self._fallback_reply(incoming_message)

    async def chat_with_assistant(
        self, message: str, user_context: dict, context: dict
    ) -> AIChatResponse:
        if not self.model or not settings.GOOGLE_API_KEY:
            return AIChatResponse(
                response="I'm Bulkly AI! I'm here to help you manage leads, campaigns, and grow your business. How can I assist you today?",
                suggestions=["Show me top leads", "Create a campaign", "Analyze my performance"],
            )

        prompt = f"""{SYSTEM_PROMPT}

User: {user_context.get('name')} (Role: {user_context.get('role')})
Additional Context: {json.dumps(context)}

User Message: {message}

Provide a helpful, concise response. Also include 3 follow-up suggestion prompts as a JSON object:
{{"response": "<your response>", "suggestions": ["<suggestion1>", "<suggestion2>", "<suggestion3>"]}}
"""
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            data = json.loads(text)
            return AIChatResponse(**data)
        except Exception:
            return AIChatResponse(
                response="I understand your request. Let me help you with that right away!",
                suggestions=["View analytics", "Manage leads", "Create campaign"],
            )

    async def qualify_lead(self, lead) -> dict:
        if not self.model or not settings.GOOGLE_API_KEY:
            return {
                "score": 65,
                "summary": f"{lead.full_name} appears to be a warm lead based on available data.",
                "sentiment": "positive",
                "buying_intent": 0.6,
                "recommended_action": "Follow up with a personalized demo offer",
            }

        prompt = f"""Qualify this sales lead and return a JSON assessment:
Lead: {lead.full_name}, Company: {lead.company}, Status: {lead.status}
Notes: {lead.notes}

Return: {{"score": 0-100, "summary": "...", "sentiment": "positive/neutral/negative",
"buying_intent": 0.0-1.0, "recommended_action": "..."}}"""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(text)
        except Exception:
            return {"score": 50, "summary": "Qualification pending", "sentiment": "neutral",
                    "buying_intent": 0.5, "recommended_action": "Schedule follow-up call"}

    async def generate_campaign_copy(
        self, product: str, audience: str, goal: str, tone: str, channel: str
    ) -> str:
        if not self.model or not settings.GOOGLE_API_KEY:
            return f"Hi {{{{name}}}}, we have an exciting offer on {product} just for you! Reply YES to learn more. 🚀"

        prompt = f"""Generate a {channel} marketing message for:
Product/Service: {product}
Target Audience: {audience}
Goal: {goal}
Tone: {tone}
Channel: {channel}

Rules: Keep it short, personalized (use {{{{name}}}} placeholder), include a clear CTA, no spam words.
Return ONLY the message text."""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception:
            return f"Hi {{{{name}}}}, check out our latest {product} offer! Limited time only. Reply to learn more."

    def _fallback_reply(self, message: str) -> AIReplyResponse:
        return AIReplyResponse(
            reply="Thank you for reaching out! Our team will get back to you shortly.",
            intent="inquiry",
            sentiment="neutral",
            buying_intent_score=0.5,
            suggested_actions=["Schedule follow-up", "Send product info", "Assign to sales agent"],
            requires_human=False,
        )
