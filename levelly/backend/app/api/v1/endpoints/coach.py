"""
LEVELLY — Coach Endpoints (Levelly Coach)
Uses Groq internally — never exposed in UI.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import asyncio

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.coach import CoachConversation
from app.models.financial_profile import FinancialProfile
from app.models.wallet import Wallet
from app.models.savings import SavingsPreference
from app.integrations.groq_client import get_coach_response

router = APIRouter()


class CoachMessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


def build_user_context(user: User, db: Session) -> dict:
    """Build structured financial context for Coach prompt."""
    profile = db.query(FinancialProfile).filter_by(user_id=user.id).first()
    safety_wallet = (
        db.query(Wallet)
        .filter(Wallet.user_id == user.id, Wallet.wallet_type == "SAFETY", Wallet.is_active == True)
        .first()
    )
    savings_pref = db.query(SavingsPreference).filter_by(user_id=user.id).first()

    safety_balance = safety_wallet.balance if safety_wallet else 0
    safety_target = safety_wallet.target_amount if safety_wallet else 10000

    # Recent coach conversations for history
    recent_convos = (
        db.query(CoachConversation)
        .filter(CoachConversation.user_id == user.id)
        .order_by(CoachConversation.created_at.desc())
        .limit(3)
        .all()
    )

    conversation_history = [
        {"user": c.user_message, "coach": c.coach_response}
        for c in reversed(recent_convos)
    ]

    return {
        "context": {
            "name": user.full_name,
            "recent_income": profile.recent_income if profile else 0,
            "historical_avg_income": profile.historical_avg_income if profile else 0,
            "income_trend": profile.income_trend if profile else "stable",
            "safety_balance": safety_balance,
            "safety_target": safety_target,
            "resilience_score": profile.resilience_score if profile else 0,
            "resilience_label": profile.resilience_label if profile else "stable",
            "distress_level": profile.distress_level if profile else "LOW",
            "distress_signals": profile.distress_signals if profile else [],
            "credit_status": None,
            "investment_paused": profile.distress_level in ("HIGH", "SEVERE") if profile else False,
            "last_nudges": [],
        },
        "conversation_history": conversation_history,
    }


@router.post("/message")
async def send_coach_message(
    request: CoachMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Send a message to Levelly Coach.
    Uses Groq internally with structured financial context.
    Falls back gracefully if AI is unavailable.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail={"code": "EMPTY_MESSAGE", "message": "Message cannot be empty"},
        )

    context_data = build_user_context(current_user, db)

    # Get AI response
    response_data = await get_coach_response(
        user_message=request.message,
        user_context=context_data["context"],
        conversation_history=context_data["conversation_history"],
    )

    # Save conversation
    conversation = CoachConversation(
        user_id=current_user.id,
        user_message=request.message,
        coach_response=response_data["response"],
        context_snapshot=context_data["context"],
        model_used=response_data.get("model"),  # internal — never shown in UI
        response_source=response_data.get("source", "ai"),
        session_id=request.session_id,
    )
    db.add(conversation)
    db.commit()

    return {
        "response": response_data["response"],
        "conversation_id": conversation.id,
        "session_id": request.session_id,
    }


@router.get("/history")
def get_coach_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 20,
    session_id: Optional[str] = None,
):
    """Get coach conversation history."""
    query = (
        db.query(CoachConversation)
        .filter(CoachConversation.user_id == current_user.id)
    )

    if session_id:
        query = query.filter(CoachConversation.session_id == session_id)

    conversations = (
        query.order_by(CoachConversation.created_at.desc()).limit(limit).all()
    )

    return [
        {
            "id": c.id,
            "user_message": c.user_message,
            "coach_response": c.coach_response,
            "session_id": c.session_id,
            "created_at": c.created_at.isoformat(),
        }
        for c in reversed(conversations)
    ]
