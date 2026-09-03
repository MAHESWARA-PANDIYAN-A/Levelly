"""
LEVELLY — Financial Health Endpoints
Dashboard, resilience score, distress status
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.wallet import Wallet
from app.models.financial_profile import FinancialProfile, FinancialScoreHistory
from app.engines.income_intelligence import IncomeIntelligenceService
from app.engines.expense_engine import ExpenseEngine
from app.engines.resilience_engine import FinancialResilienceService
from app.engines.distress_engine import DistressEngine

router = APIRouter()


@router.get("/dashboard")
def get_dashboard(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Home dashboard data. Returns all key metrics for the home screen.
    The UI renders whichever state the backend returns.
    """
    profile = (
        db.query(FinancialProfile)
        .filter(FinancialProfile.user_id == current_user.id)
        .first()
    )

    wallets = (
        db.query(Wallet)
        .filter(Wallet.user_id == current_user.id, Wallet.is_active == True)
        .all()
    )

    daily_wallet = next((w for w in wallets if w.wallet_type == "DAILY"), None)
    safety_wallet = next((w for w in wallets if w.wallet_type == "SAFETY"), None)

    resilience_score = profile.resilience_score if profile else 0.0
    resilience_label = profile.resilience_label if profile else "stable"
    distress_level = profile.distress_level if profile else "LOW"
    distress_score = profile.distress_score if profile else 0.0

    # Map label to UI status
    status_map = {
        "stable": "Stable",
        "moderate": "Financial pressure detected",
        "at_risk": "Financial pressure detected",
        "critical": "High financial stress",
    }
    ui_status = status_map.get(resilience_label, "Stable")

    return {
        "user": {
            "id": current_user.id,
            "full_name": current_user.full_name,
            "occupation": current_user.occupation,
        },
        "daily_wallet": {
            "balance": daily_wallet.balance if daily_wallet else 0,
            "currency": "INR",
        },
        "safety_wallet": {
            "balance": safety_wallet.balance if safety_wallet else 0,
            "target": safety_wallet.target_amount if safety_wallet else 10000,
            "progress": safety_wallet.progress_percentage if safety_wallet else 0,
            "currency": "INR",
        },
        "resilience": {
            "score": resilience_score,
            "label": resilience_label,
            "ui_status": ui_status,
            "max_score": 100,
        },
        "distress": {
            "level": distress_level,
            "score": distress_score,
            "signals": profile.distress_signals if profile else [],
        },
        "income": {
            "historical_avg": profile.historical_avg_income if profile else 0,
            "recent_pace": profile.recent_income if profile else 0,
            "trend": profile.income_trend if profile else "stable",
            "volatility_level": profile.income_volatility_level if profile else "LOW",
            "decline_pct": profile.income_decline_pct if profile else 0,
        },
        "investment_ready": profile.investment_ready if profile else False,
    }


@router.get("/resilience")
def get_resilience_score(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current LEVELLY Financial Resilience Score."""
    svc = FinancialResilienceService(db)
    return svc.calculate_score(current_user.id)


@router.get("/distress")
def get_distress(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current distress evaluation."""
    svc = DistressEngine(db)
    return svc.evaluate(current_user.id)


@router.post("/refresh")
def refresh_intelligence(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Refresh all financial intelligence for the user.
    Runs income, expense, distress, and resilience engines.
    """
    try:
        income_svc = IncomeIntelligenceService(db)
        income_svc.update_financial_profile(current_user.id)

        profile = (
            db.query(FinancialProfile)
            .filter(FinancialProfile.user_id == current_user.id)
            .first()
        )
        recent_income = profile.recent_income if profile else 0

        expense_svc = ExpenseEngine(db)
        expense_svc.update_financial_profile(current_user.id, recent_income)

        distress_svc = DistressEngine(db)
        distress_result = distress_svc.evaluate(current_user.id)

        resilience_svc = FinancialResilienceService(db)
        resilience_result = resilience_svc.calculate_score(current_user.id)

        return {
            "success": True,
            "distress_level": distress_result["distress_level"],
            "resilience_score": resilience_result["resilience_score"],
            "message": "Financial intelligence refreshed",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/score-history")
def get_score_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 30,
):
    """Get historical resilience score records."""
    history = (
        db.query(FinancialScoreHistory)
        .filter(FinancialScoreHistory.user_id == current_user.id)
        .order_by(FinancialScoreHistory.computed_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": h.id,
            "resilience_score": h.resilience_score,
            "distress_score": h.distress_score,
            "distress_level": h.distress_level,
            "computed_at": h.computed_at.isoformat(),
        }
        for h in history
    ]


@router.get("/expense-analytics")
def get_expense_analytics(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get expense analytics for the analytics screen."""
    profile = (
        db.query(FinancialProfile)
        .filter(FinancialProfile.user_id == current_user.id)
        .first()
    )
    monthly_income = profile.recent_income if profile else 1

    svc = ExpenseEngine(db)
    summary = svc.get_expense_summary(current_user.id)
    expense_ratio = svc.calculate_expense_ratio(current_user.id, monthly_income)

    return {
        **summary,
        "expense_ratio": expense_ratio,
        "expense_ratio_pct": round(expense_ratio * 100, 1),
        "monthly_income": monthly_income,
    }
