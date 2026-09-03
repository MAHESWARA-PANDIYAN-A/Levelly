"""
LEVELLY — Income Endpoints
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.transaction import IncomeTransaction
from app.models.wallet import Wallet
from app.engines.income_intelligence import IncomeIntelligenceService
from app.engines.expense_engine import ExpenseEngine
from app.engines.resilience_engine import FinancialResilienceService
from app.engines.distress_engine import DistressEngine
from app.services.notification_service import NotificationService
from app.models.audit import AuditLog

router = APIRouter()


class AddIncomeRequest(BaseModel):
    amount: float
    source: str = "platform_payout"
    income_type: str = "payout"
    description: Optional[str] = None


@router.post("/")
def add_income(
    request: AddIncomeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Record a new income/payout transaction."""
    if request.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_AMOUNT", "message": "Income amount must be positive"},
        )

    income_txn = IncomeTransaction(
        user_id=current_user.id,
        amount=request.amount,
        source=request.source,
        income_type=request.income_type,
        description=request.description,
        status="completed",
        transaction_date=datetime.now(timezone.utc),
    )
    db.add(income_txn)

    # Add to daily wallet
    daily_wallet = (
        db.query(Wallet)
        .filter(
            Wallet.user_id == current_user.id,
            Wallet.wallet_type == "DAILY",
            Wallet.is_active == True,
        )
        .first()
    )
    if daily_wallet:
        daily_wallet.balance = round(daily_wallet.balance + request.amount, 2)

    # Audit
    audit = AuditLog(
        user_id=current_user.id,
        actor_id=current_user.id,
        event_type="income_recorded",
        action="payout_received",
        entity_type="income",
        extra_data={"amount": request.amount, "source": request.source},
    )
    db.add(audit)
    db.commit()

    # Refresh intelligence asynchronously (or synchronously here for simplicity)
    try:
        income_svc = IncomeIntelligenceService(db)
        income_svc.update_financial_profile(current_user.id)

        expense_svc = ExpenseEngine(db)
        profile = db.query(__import__('app.models.financial_profile', fromlist=['FinancialProfile']).FinancialProfile).filter_by(user_id=current_user.id).first()
        if profile:
            expense_svc.update_financial_profile(current_user.id, profile.recent_income or request.amount)

        distress_svc = DistressEngine(db)
        distress_result = distress_svc.evaluate(current_user.id)

        resilience_svc = FinancialResilienceService(db)
        resilience_svc.calculate_score(current_user.id)
    except Exception as e:
        pass  # Non-blocking

    # Notifications
    notif_svc = NotificationService(db)
    notif_svc.payout_received(current_user.id, request.amount, request.source)

    return {
        "success": True,
        "income_id": income_txn.id,
        "amount": request.amount,
        "daily_wallet_balance": daily_wallet.balance if daily_wallet else 0,
        "message": f"₹{request.amount:,.0f} added to Daily Wallet.",
    }


@router.get("/summary")
def get_income_summary(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get income intelligence summary."""
    svc = IncomeIntelligenceService(db)
    return svc.get_income_summary(current_user.id)


@router.get("/chart")
def get_income_chart(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get weekly income data for chart display."""
    svc = IncomeIntelligenceService(db)
    weekly_data = svc._get_weekly_income(current_user.id, weeks=8)

    summary = svc.get_income_summary(current_user.id)
    historical_avg = summary["historical_avg_income"]
    weekly_avg = historical_avg / 4.33 if historical_avg else 0

    return {
        "weekly_data": weekly_data,
        "weekly_average": round(weekly_avg, 2),
        "historical_monthly_average": historical_avg,
        "recent_monthly_pace": summary["recent_income"],
        "income_trend": summary["income_trend"],
        "income_volatility_level": summary["income_volatility_level"],
    }


@router.get("/transactions")
def get_income_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 20,
    offset: int = 0,
):
    """Get income transaction history."""
    transactions = (
        db.query(IncomeTransaction)
        .filter(IncomeTransaction.user_id == current_user.id)
        .order_by(IncomeTransaction.transaction_date.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        {
            "id": t.id,
            "amount": t.amount,
            "source": t.source,
            "income_type": t.income_type,
            "description": t.description,
            "status": t.status,
            "date": t.transaction_date.isoformat(),
        }
        for t in transactions
    ]
