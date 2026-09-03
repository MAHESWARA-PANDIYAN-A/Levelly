"""
LEVELLY — Nudges Endpoints
Backend-generated financial guidance nudges
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.financial_profile import FinancialProfile
from app.models.wallet import Wallet
from app.engines.expense_engine import ExpenseEngine

router = APIRouter()


@router.get("/")
def get_nudges(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get personalized financial nudges based on current financial state.
    Nudges are generated from backend conditions, not hardcoded.
    """
    profile = (
        db.query(FinancialProfile)
        .filter(FinancialProfile.user_id == current_user.id)
        .first()
    )

    safety_wallet = (
        db.query(Wallet)
        .filter(
            Wallet.user_id == current_user.id,
            Wallet.wallet_type == "SAFETY",
            Wallet.is_active == True,
        )
        .first()
    )

    nudges = []

    if not profile:
        return {"nudges": nudges}

    monthly_income = profile.recent_income or 1

    # Income nudges
    if profile.income_decline_pct > 10:
        nudges.append({
            "type": "income_decline",
            "priority": "high",
            "message": f"Your recent earnings are {profile.income_decline_pct:.0f}% below your usual range.",
            "cta": "View income details",
            "cta_url": "/income",
            "icon": "trending-down",
        })

    if profile.income_trend == "declining" and profile.consecutive_low_periods >= 2:
        nudges.append({
            "type": "sustained_decline",
            "priority": "high",
            "message": "Income has been below your average for several weeks. Let's plan ahead.",
            "cta": "Talk to Levelly Coach",
            "cta_url": "/coach",
            "icon": "alert-circle",
        })

    # Safety Wallet nudges
    if safety_wallet:
        shortfall = (safety_wallet.target_amount or 10000) - safety_wallet.balance
        if 0 < shortfall <= 5000:
            nudges.append({
                "type": "safety_target_close",
                "priority": "normal",
                "message": f"You're ₹{shortfall:,.0f} away from your Safety Wallet target.",
                "cta": "Make a payment with Save-at-Pay",
                "cta_url": "/pay",
                "icon": "shield",
            })
        elif shortfall > 5000:
            nudges.append({
                "type": "safety_below_target",
                "priority": "normal",
                "message": f"Your Safety Wallet is ₹{shortfall:,.0f} below your target of ₹{safety_wallet.target_amount:,.0f}.",
                "cta": "Build your safety buffer",
                "cta_url": "/wallets/safety",
                "icon": "shield",
            })

    # Expense nudges
    expense_svc = ExpenseEngine(db)
    expense_nudges = expense_svc.generate_expense_nudges(current_user.id, monthly_income)
    nudges.extend(expense_nudges)

    # Distress nudges
    if profile.distress_level == "HIGH":
        nudges.append({
            "type": "distress_guidance",
            "priority": "high",
            "message": "Financial pressure detected. Levelly Coach can help you plan for this period.",
            "cta": "Get guidance",
            "cta_url": "/coach",
            "icon": "heart",
        })
    elif profile.distress_level == "SEVERE":
        nudges.append({
            "type": "severe_distress",
            "priority": "high",
            "message": "Your financial situation needs attention. Let's focus on stability first.",
            "cta": "Talk to Levelly Coach",
            "cta_url": "/coach",
            "icon": "alert-triangle",
        })

    # Sort by priority
    priority_order = {"high": 0, "normal": 1, "low": 2}
    nudges.sort(key=lambda x: priority_order.get(x.get("priority", "normal"), 1))

    return {"nudges": nudges[:5]}  # cap at 5 nudges
