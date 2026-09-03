"""
LEVELLY — Payments Endpoints
Implements Save-at-Pay workflow:
POST /payments/preview → shows save suggestion
POST /payments/confirm → records payment + optional savings
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.wallet import Wallet
from app.models.transaction import ExpenseTransaction, Transaction
from app.models.savings import SavingsTransaction
from app.models.financial_profile import FinancialProfile
from app.models.audit import AuditLog
from app.engines.savings_engine import SavingsEngine
from app.services.notification_service import NotificationService

router = APIRouter()


class PaymentPreviewRequest(BaseModel):
    amount: float
    category: str


class PaymentConfirmRequest(BaseModel):
    amount: float
    category: str
    save_consent: bool
    description: str | None = None
    merchant: str | None = None


@router.post("/preview")
def payment_preview(
    request: PaymentPreviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Preview a payment to get Save-at-Pay suggestion.
    Returns suggested save amount — never mandatory.
    """
    if request.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_AMOUNT", "message": "Payment amount must be positive"},
        )

    # Get distress level for savings adjustment
    profile = (
        db.query(FinancialProfile)
        .filter(FinancialProfile.user_id == current_user.id)
        .first()
    )
    distress_level = profile.distress_level if profile else "LOW"

    # Get daily wallet balance
    daily_wallet = (
        db.query(Wallet)
        .filter(
            Wallet.user_id == current_user.id,
            Wallet.wallet_type == "DAILY",
            Wallet.is_active == True,
        )
        .first()
    )

    # Calculate save suggestion
    engine = SavingsEngine(db)
    suggestion = engine.calculate_save_suggestion(
        amount=request.amount,
        category=request.category,
        user_id=current_user.id,
        distress_level=distress_level,
    )

    # Get safety wallet for context
    safety_wallet = (
        db.query(Wallet)
        .filter(
            Wallet.user_id == current_user.id,
            Wallet.wallet_type == "SAFETY",
            Wallet.is_active == True,
        )
        .first()
    )

    return {
        **suggestion,
        "daily_wallet_balance": daily_wallet.balance if daily_wallet else 0,
        "safety_wallet_balance": safety_wallet.balance if safety_wallet else 0,
        "safety_wallet_target": safety_wallet.target_amount if safety_wallet else 10000,
        "safety_wallet_progress": safety_wallet.progress_percentage if safety_wallet else 0,
        "total_if_save": request.amount + suggestion["suggested_save_amount"],
    }


@router.post("/confirm")
def payment_confirm(
    request: PaymentConfirmRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Confirm payment with or without saving.
    Records payment transaction and optional savings contribution.
    Uses transactional integrity — all or nothing.
    """
    if request.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_AMOUNT", "message": "Payment amount must be positive"},
        )

    # Get wallets
    daily_wallet = (
        db.query(Wallet)
        .filter(
            Wallet.user_id == current_user.id,
            Wallet.wallet_type == "DAILY",
            Wallet.is_active == True,
        )
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

    if not daily_wallet:
        raise HTTPException(status_code=404, detail="Daily wallet not found")

    # Get distress level
    profile = (
        db.query(FinancialProfile)
        .filter(FinancialProfile.user_id == current_user.id)
        .first()
    )
    distress_level = profile.distress_level if profile else "LOW"

    # Calculate save amount
    engine = SavingsEngine(db)
    suggestion = engine.calculate_save_suggestion(
        amount=request.amount,
        category=request.category,
        user_id=current_user.id,
        distress_level=distress_level,
    )
    save_amount = suggestion["suggested_save_amount"] if request.save_consent else 0.0

    # Verify sufficient balance (payment + optional save)
    total_needed = request.amount + save_amount
    if daily_wallet.balance < request.amount:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INSUFFICIENT_DAILY_BALANCE",
                "message": "Insufficient balance in Daily Wallet",
            },
        )

    # ---- TRANSACTION START ----
    # Record expense
    expense = ExpenseTransaction(
        user_id=current_user.id,
        amount=request.amount,
        category=request.category.lower(),
        description=request.description,
        merchant=request.merchant,
        savings_added=save_amount,
        save_consent=request.save_consent,
        status="completed",
    )
    db.add(expense)
    db.flush()

    # Deduct from daily wallet
    daily_wallet.balance = round(daily_wallet.balance - request.amount, 2)

    # If save consent: add to safety wallet and record savings transaction
    savings_transaction = None
    if request.save_consent and save_amount > 0 and safety_wallet:
        # Deduct save amount from daily wallet too
        if daily_wallet.balance >= save_amount:
            daily_wallet.balance = round(daily_wallet.balance - save_amount, 2)
        else:
            save_amount = 0.0  # not enough balance for save

        if save_amount > 0:
            balance_before = safety_wallet.balance
            safety_wallet.balance = round(safety_wallet.balance + save_amount, 2)

            savings_transaction = SavingsTransaction(
                user_id=current_user.id,
                amount=save_amount,
                source_expense_id=expense.id,
                transaction_type="save_at_pay",
                category_context=request.category,
                save_percentage_applied=suggestion["suggested_percentage"],
                balance_before=balance_before,
                balance_after=safety_wallet.balance,
            )
            db.add(savings_transaction)

    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        actor_id=current_user.id,
        event_type="payment_confirmed",
        action="payment_with_save_consent",
        entity_type="payment",
        entity_id=expense.id,
        extra_data={
            "amount": request.amount,
            "category": request.category,
            "save_consent": request.save_consent,
            "save_amount": save_amount,
        },
    )
    db.add(audit)
    db.commit()
    # ---- TRANSACTION END ----

    # Send notifications
    notif_svc = NotificationService(db)
    notif_svc.payment_completed(current_user.id, request.amount, request.category)
    if request.save_consent and save_amount > 0:
        notif_svc.save_at_pay_accepted(current_user.id, save_amount)
        # Safety wallet milestone notifications
        if safety_wallet and safety_wallet.progress_percentage in [25, 50, 75, 100]:
            notif_svc.safety_wallet_milestone(
                current_user.id,
                safety_wallet.progress_percentage,
                safety_wallet.balance,
            )

    return {
        "success": True,
        "payment_amount": request.amount,
        "save_amount": save_amount,
        "save_consent": request.save_consent,
        "category": request.category,
        "expense_id": expense.id,
        "daily_wallet_balance": daily_wallet.balance,
        "safety_wallet_balance": safety_wallet.balance if safety_wallet else 0,
        "safety_wallet_progress": safety_wallet.progress_percentage if safety_wallet else 0,
        "message": (
            f"Payment of ₹{request.amount:,.0f} recorded."
            + (f" ₹{save_amount:,.0f} added to Safety Wallet." if save_amount > 0 else "")
        ),
    }
