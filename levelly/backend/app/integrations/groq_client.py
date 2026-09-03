"""
LEVELLY — Groq Client for Levelly Coach
Internal implementation detail — never expose Groq branding in UI.
The Coach is called "Levelly Coach" in all user-facing surfaces.

Fails gracefully if Groq is unavailable.
"""
from typing import Optional, Dict, Any
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

FALLBACK_RESPONSES = {
    "savings": (
        "Your Save-at-Pay feature is designed to help you build a safety buffer over time. "
        "Each time you make a payment, LEVELLY suggests adding a small amount to your Safety Wallet. "
        "This is always optional — you stay in control."
    ),
    "credit": (
        "Your credit recommendation is based on your income pattern, savings behavior, "
        "and overall financial health. When financial pressure is detected, LEVELLY may "
        "temporarily adjust the recommendation to protect your stability."
    ),
    "investment": (
        "Investment suggestions become available once your Safety Wallet reaches its target. "
        "LEVELLY will never automatically invest your money — you always confirm before anything happens."
    ),
    "distress": (
        "LEVELLY has detected some financial pressure signals in your recent income and spending. "
        "This is normal for gig workers. Your Coach is here to help you navigate this period."
    ),
    "general": (
        "I'm Levelly Coach. I'm here to help you understand your finances, explain how your "
        "Safety Wallet works, and guide you towards financial resilience. "
        "What would you like to know?"
    ),
}

SYSTEM_PROMPT = """You are Levelly Coach, the financial guidance assistant for LEVELLY, 
a financial resilience platform for gig and informal workers.

Your role is to:
- Help users understand their financial situation using the context provided
- Explain why savings suggestions, credit decisions, or investment pauses occurred
- Guide users toward building financial resilience
- Answer questions about the Safety Wallet, income patterns, and financial health

STRICT RULES:
- Never execute payments, investments, or loans
- Never override system guardrails or financial decisions
- Never invent specific interest rates, fees, tax rules, or maturity dates not in your context
- Never claim guaranteed returns or risk-free status for any investment
- Never mention Groq, LLM, AI model, or any technical implementation
- Always use warm, supportive, clear language appropriate for gig workers
- Keep responses concise and actionable (under 250 words)
- When uncertain, say you'll help them find more information rather than inventing details
- You are NOT a financial advisor. Always mention consulting a qualified financial advisor for major decisions.

User context will be provided in each message. Use it to give personalized responses.
Do not contradict the financial data provided in the context."""


def build_context_message(user_context: Dict[str, Any]) -> str:
    """Build the structured context block for the Coach prompt."""
    ctx = user_context

    lines = [
        "=== USER FINANCIAL CONTEXT ===",
        f"Name: {ctx.get('name', 'the user')}",
        f"Recent Monthly Income: ₹{ctx.get('recent_income', 0):,.0f}",
        f"Historical Average Income: ₹{ctx.get('historical_avg_income', 0):,.0f}",
        f"Income Trend: {ctx.get('income_trend', 'unknown')}",
        f"Safety Wallet Balance: ₹{ctx.get('safety_balance', 0):,.0f}",
        f"Safety Wallet Target: ₹{ctx.get('safety_target', 0):,.0f}",
        f"LEVELLY Financial Resilience Score: {ctx.get('resilience_score', 0)}/100",
        f"Financial Status: {ctx.get('resilience_label', 'unknown')}",
        f"Distress Level: {ctx.get('distress_level', 'LOW')}",
    ]

    if ctx.get('distress_signals'):
        lines.append(f"Distress Signals: {', '.join(ctx['distress_signals'])}")

    if ctx.get('credit_status'):
        lines.append(f"Credit Status: {ctx['credit_status']}")

    if ctx.get('investment_paused'):
        lines.append("Investment Suggestions: Currently paused")
    else:
        lines.append("Investment Suggestions: Available")

    if ctx.get('last_nudges'):
        lines.append(f"Recent Guidance: {'; '.join(ctx['last_nudges'])}")

    lines.append("==============================")
    return "\n".join(lines)


async def get_coach_response(
    user_message: str,
    user_context: Dict[str, Any],
    conversation_history: list = None,
) -> Dict[str, Any]:
    """
    Get a response from Levelly Coach.
    Falls back gracefully if Groq is unavailable.
    """
    if not settings.GROQ_API_KEY:
        logger.warning("GROQ_API_KEY not configured — using fallback response")
        return _get_fallback_response(user_message)

    try:
        from groq import Groq
        client = Groq(api_key=settings.GROQ_API_KEY)

        context_message = build_context_message(user_context)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"{context_message}\n\nUser question: {user_message}",
            },
        ]

        # Add conversation history if provided (last 4 exchanges)
        if conversation_history:
            history_messages = []
            for turn in conversation_history[-4:]:
                history_messages.append({"role": "user", "content": turn["user"]})
                history_messages.append({"role": "assistant", "content": turn["coach"]})
            # Insert history after system prompt but before current message
            messages = [messages[0]] + history_messages + [messages[1]]

        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=messages,
            max_tokens=400,
            temperature=0.7,
        )

        coach_reply = response.choices[0].message.content.strip()

        return {
            "response": coach_reply,
            "source": "ai",
            "model": settings.GROQ_MODEL,  # stored internally, never shown in UI
        }

    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return _get_fallback_response(user_message)


def _get_fallback_response(user_message: str) -> Dict[str, Any]:
    """Return a contextual fallback response when AI is unavailable."""
    message_lower = user_message.lower()

    if any(word in message_lower for word in ["sav", "wallet", "safety"]):
        response = FALLBACK_RESPONSES["savings"]
    elif any(word in message_lower for word in ["credit", "loan", "borrow"]):
        response = FALLBACK_RESPONSES["credit"]
    elif any(word in message_lower for word in ["invest", "grow", "return"]):
        response = FALLBACK_RESPONSES["investment"]
    elif any(word in message_lower for word in ["stress", "pressure", "distress", "income"]):
        response = FALLBACK_RESPONSES["distress"]
    else:
        response = FALLBACK_RESPONSES["general"]

    return {
        "response": response,
        "source": "fallback",
        "model": None,
    }
