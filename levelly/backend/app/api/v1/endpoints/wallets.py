"""
LEVELLY — Wallet Endpoints (Safety Wallet Resilience Hub)
Note: Daily Wallet is deprecated/removed in the current architecture.
Financial resilience reserve is held entirely within the Safety Wallet.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.wallet import Wallet
from app.models.savings import SavingsTransaction
from app.models.audit import AuditLog

router = APIRouter()


class SafetyTargetUpdateRequest(BaseModel):
    target_amount: float


class SafetyDepositRequest(BaseModel):
    amount: float
    note: Optional[str] = "Manual Safety Wallet top-up"


@router.get("/")
def get_wallets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user's Safety Wallet and resilience reserves."""
    wallets = (
        db.query(Wallet)
        .filter(Wallet.user_id == current_user.id, Wallet.wallet_type == "SAFETY", Wallet.is_active == True)
        .all()
    )
    if not wallets:
        default_safety = Wallet(
            user_id=current_user.id,
            wallet_type="SAFETY",
            balance=8200.0,
            target_amount=10000.0,
            currency="INR",
            is_active=True,
        )
        db.add(default_safety)
        db.commit()
        db.refresh(default_safety)
        wallets = [default_safety]

    return [
        {
            "id": w.id,
            "wallet_type": w.wallet_type,
            "balance": w.balance,
            "currency": w.currency,
            "target_amount": w.target_amount,
            "progress_percentage": w.progress_percentage,
            "shortfall": max(0.0, (w.target_amount or 0.0) - w.balance),
            "surplus": max(0.0, w.balance - (w.target_amount or 0.0)),
        }
        for w in wallets
    ]


@router.get("/daily")
def get_daily_wallet():
    """
    Deprecated: Daily Wallet removed.
    Returns decommissioned status for backwards compatibility.
    """
    return {
        "status": "decommissioned",
        "message": "Daily Wallet removed in favor of Direct Bank/UPI payments with LEVELLY Pay",
        "wallet_type": "DAILY",
        "balance": 0.0,
    }


@router.get("/safety")
def get_safety_wallet(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get Safety Wallet details."""
    wallet = (
        db.query(Wallet)
        .filter(
            Wallet.user_id == current_user.id,
            Wallet.wallet_type == "SAFETY",
            Wallet.is_active == True,
        )
        .first()
    )
    if not wallet:
        wallet = Wallet(
            user_id=current_user.id,
            wallet_type="SAFETY",
            balance=8200.0,
            target_amount=10000.0,
            currency="INR",
            is_active=True,
        )
        db.add(wallet)
        db.commit()
        db.refresh(wallet)

    return {
        "id": wallet.id,
        "wallet_type": "SAFETY",
        "balance": wallet.balance,
        "target_amount": wallet.target_amount or 10000.0,
        "progress_percentage": wallet.progress_percentage,
        "currency": wallet.currency,
        "shortfall": max(0.0, (wallet.target_amount or 10000.0) - wallet.balance),
        "surplus": max(0.0, wallet.balance - (wallet.target_amount or 10000.0)),
    }


@router.put("/safety/target")
def update_safety_target(
    request: SafetyTargetUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update Safety Wallet savings target."""
    if request.target_amount < 1000:
        raise HTTPException(status_code=400, detail="Target must be at least ₹1,000")

    wallet = (
        db.query(Wallet)
        .filter(Wallet.user_id == current_user.id, Wallet.wallet_type == "SAFETY")
        .first()
    )
    if not wallet:
        wallet = Wallet(
            user_id=current_user.id,
            wallet_type="SAFETY",
            balance=8200.0,
            target_amount=request.target_amount,
            currency="INR",
            is_active=True,
        )
        db.add(wallet)
    else:
        wallet.target_amount = request.target_amount

    db.commit()
    db.refresh(wallet)
    return {
        "id": wallet.id,
        "balance": wallet.balance,
        "target_amount": wallet.target_amount,
        "progress_percentage": wallet.progress_percentage,
    }


@router.post("/safety/deposit")
def deposit_to_safety_wallet(
    request: SafetyDepositRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Manually add savings to Safety Wallet from linked bank."""
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Deposit amount must be greater than zero")

    wallet = (
        db.query(Wallet)
        .filter(Wallet.user_id == current_user.id, Wallet.wallet_type == "SAFETY")
        .first()
    )
    if not wallet:
        wallet = Wallet(
            user_id=current_user.id,
            wallet_type="SAFETY",
            balance=0.0,
            target_amount=10000.0,
            currency="INR",
            is_active=True,
        )
        db.add(wallet)
        db.flush()

    initial_balance = wallet.balance
    wallet.balance = round(wallet.balance + request.amount, 2)

    savings_txn = SavingsTransaction(
        user_id=current_user.id,
        amount=request.amount,
        transaction_type="manual_deposit",
        category_context="general",
        balance_before=initial_balance,
        balance_after=wallet.balance,
    )
    db.add(savings_txn)

    audit = AuditLog(
        user_id=current_user.id,
        event_type="safety_wallet_deposit",
        action=f"Manual deposit of ₹{request.amount} to Safety Wallet",
        entity_type="wallet",
        entity_id=wallet.id,
    )
    db.add(audit)

    db.commit()
    db.refresh(wallet)

    return {
        "wallet_id": wallet.id,
        "new_balance": wallet.balance,
        "amount_deposited": request.amount,
        "target_amount": wallet.target_amount,
        "progress_percentage": wallet.progress_percentage,
    }
