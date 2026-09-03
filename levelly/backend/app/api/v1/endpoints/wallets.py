"""
LEVELLY — Wallet Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.wallet import Wallet
from app.models.savings import SavingsPreference

router = APIRouter()


@router.get("/")
def get_wallets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all wallets for the current user."""
    wallets = (
        db.query(Wallet)
        .filter(Wallet.user_id == current_user.id, Wallet.is_active == True)
        .all()
    )

    result = []
    for w in wallets:
        wallet_data = {
            "id": w.id,
            "wallet_type": w.wallet_type,
            "balance": w.balance,
            "currency": w.currency,
        }
        if w.wallet_type == "SAFETY":
            wallet_data["target_amount"] = w.target_amount
            wallet_data["progress_percentage"] = w.progress_percentage
        result.append(wallet_data)

    return result


@router.get("/daily")
def get_daily_wallet(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get Daily Wallet details."""
    wallet = (
        db.query(Wallet)
        .filter(
            Wallet.user_id == current_user.id,
            Wallet.wallet_type == "DAILY",
            Wallet.is_active == True,
        )
        .first()
    )
    if not wallet:
        raise HTTPException(status_code=404, detail="Daily wallet not found")

    return {
        "id": wallet.id,
        "wallet_type": "DAILY",
        "balance": wallet.balance,
        "currency": wallet.currency,
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
        raise HTTPException(status_code=404, detail="Safety wallet not found")

    return {
        "id": wallet.id,
        "wallet_type": "SAFETY",
        "balance": wallet.balance,
        "target_amount": wallet.target_amount,
        "progress_percentage": wallet.progress_percentage,
        "currency": wallet.currency,
        "shortfall": max(0, (wallet.target_amount or 0) - wallet.balance),
        "surplus": max(0, wallet.balance - (wallet.target_amount or 0)),
    }
