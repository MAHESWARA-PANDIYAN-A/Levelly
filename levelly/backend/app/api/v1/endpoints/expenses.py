"""
LEVELLY — Expenses Endpoints
Large expense flow with piggy-bank intervention
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.wallet import Wallet
from app.models.transaction import ExpenseTransaction
from app.models.savings import SavingsTransaction
from app.models.financial_profile import FinancialProfile
from app.models.audit import AuditLog
from app.services.notification_service import NotificationService

router = APIRouter()


class LargeExpensePreviewRequest(BaseModel):
    amount: float
    purpose: str


class LargeExpenseConfirmRequest(BaseModel):
    amount: float
    purpose: str
    use_savings: bool  # explicit confirmation to use safety wallet


@router.post("/large/preview")
def large_expense_preview(
    request: LargeExpensePreviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Preview impact of a large expense on Safety Wallet.
    Returns impact metrics for the piggy-bank intervention screen.
    """
    if request.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_AMOUNT", "message": "Expense amount must be positive"},
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

    profile = (
        db.query(FinancialProfile)
        .filter(FinancialProfile.user_id == current_user.id)
        .first()
    )

    safety_balance = safety_wallet.balance if safety_wallet else 0.0
    safety_target = safety_wallet.target_amount if safety_wallet else 10000.0

    # Calculate impact
    savings_usage_pct = 0.0
    if safety_balance > 0:
        savings_usage_pct = min(100.0, (request.amount / safety_balance) * 100)

    remaining_balance = max(0, safety_balance - request.amount)
    remaining_progress = 0.0
    if safety_target > 0:
        remaining_progress = min(100, (remaining_balance / safety_target) * 100)

    # Risk assessment
    if savings_usage_pct >= 90:
        risk_level = "critical"
        risk_message = "This will almost completely deplete your Safety Wallet."
        intervention_required = True
    elif savings_usage_pct >= 70:
        risk_level = "high"
        risk_message = "This will significantly reduce your safety buffer."
        intervention_required = True
    elif savings_usage_pct >= 40:
        risk_level = "moderate"
        risk_message = "This will reduce your safety buffer by a meaningful amount."
        intervention_required = False
    else:
        risk_level = "low"
        risk_message = "This expense has a manageable impact on your safety buffer."
        intervention_required = False

    # Check if sufficient savings
    can_use_savings = safety_balance >= request.amount
    insufficient_savings = not can_use_savings

    # Check credit availability (from profile)
    distress_level = profile.distress_level if profile else "LOW"
    credit_available = distress_level not in ("HIGH", "SEVERE")

    return {
        "requested_amount": request.amount,
        "purpose": request.purpose,
        "safety_wallet_balance": safety_balance,
        "safety_wallet_target": safety_target,
        "savings_usage_percentage": round(savings_usage_pct, 1),
        "remaining_safety_balance": round(remaining_balance, 2),
        "remaining_safety_progress": round(remaining_progress, 1),
        "risk_level": risk_level,
        "risk_message": risk_message,
        "intervention_required": intervention_required,
        "can_use_savings": can_use_savings,
        "insufficient_savings": insufficient_savings,
        "shortfall": max(0, request.amount - safety_balance),
        "partner_credit_available": credit_available,
        "distress_level": distress_level,
    }


@router.post("/large/confirm")
def large_expense_confirm(
    request: LargeExpenseConfirmRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Confirm large expense with explicit savings consent.
    Safety Wallet is NEVER debited without this explicit confirmation.
    """
    if not request.use_savings:
        return {
            "success": False,
            "message": "Expense cancelled. Safety Wallet was not used.",
            "action": "explore_alternatives",
        }

    safety_wallet = (
        db.query(Wallet)
        .filter(
            Wallet.user_id == current_user.id,
            Wallet.wallet_type == "SAFETY",
            Wallet.is_active == True,
        )
        .first()
    )

    if not safety_wallet:
        raise HTTPException(status_code=404, detail="Safety wallet not found")

    if safety_wallet.balance < request.amount:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INSUFFICIENT_SAFETY_BALANCE",
                "message": "The Safety Wallet does not contain enough funds.",
            },
        )

    # Record expense
    expense = ExpenseTransaction(
        user_id=current_user.id,
        amount=request.amount,
        category="other",
        description=request.purpose,
        is_large_expense=True,
        save_consent=False,
        status="completed",
    )
    db.add(expense)
    db.flush()

    # Debit safety wallet
    balance_before = safety_wallet.balance
    safety_wallet.balance = round(safety_wallet.balance - request.amount, 2)

    savings_txn = SavingsTransaction(
        user_id=current_user.id,
        amount=-request.amount,  # negative = withdrawal
        source_expense_id=expense.id,
        transaction_type="withdrawal",
        balance_before=balance_before,
        balance_after=safety_wallet.balance,
        notes=f"Large expense: {request.purpose}",
    )
    db.add(savings_txn)

    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        actor_id=current_user.id,
        event_type="safety_wallet_withdrawal",
        action="large_expense_confirmed",
        entity_type="expense",
        entity_id=expense.id,
        extra_data={
            "amount": request.amount,
            "purpose": request.purpose,
            "balance_before": balance_before,
            "balance_after": safety_wallet.balance,
        },
    )
    db.add(audit)
    db.commit()

    return {
        "success": True,
        "amount_used": request.amount,
        "purpose": request.purpose,
        "safety_wallet_balance": safety_wallet.balance,
        "safety_wallet_progress": safety_wallet.progress_percentage,
        "message": f"₹{request.amount:,.0f} withdrawn from Safety Wallet for {request.purpose}.",
    }
