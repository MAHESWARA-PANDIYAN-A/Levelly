"""
LEVELLY — User Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.savings import SavingsPreference
from app.models.wallet import Wallet

router = APIRouter()


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    occupation: Optional[str] = None
    city: Optional[str] = None
    income_frequency: Optional[str] = None
    onboarding_complete: Optional[bool] = None
    platform_tenure_months: Optional[int] = None


class UpdateSafetyTargetRequest(BaseModel):
    target_amount: float


@router.get("/profile")
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user profile."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "phone": current_user.phone,
        "role": current_user.role,
        "occupation": current_user.occupation,
        "city": current_user.city,
        "platform_tenure_months": current_user.platform_tenure_months,
        "income_frequency": current_user.income_frequency,
        "onboarding_complete": current_user.onboarding_complete,
        "created_at": current_user.created_at.isoformat(),
    }


@router.patch("/profile")
def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user profile."""
    for field, value in request.model_dump(exclude_none=True).items():
        setattr(current_user, field, value)
    db.commit()
    return {"message": "Profile updated"}


@router.put("/safety-target")
def update_safety_target(
    request: UpdateSafetyTargetRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update Safety Wallet target amount."""
    if request.target_amount <= 0:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_TARGET", "message": "Safety target must be greater than 0"},
        )

    # Update wallet target
    safety_wallet = (
        db.query(Wallet)
        .filter(Wallet.user_id == current_user.id, Wallet.wallet_type == "SAFETY")
        .first()
    )
    if safety_wallet:
        safety_wallet.target_amount = request.target_amount

    # Update savings preference
    pref = (
        db.query(SavingsPreference)
        .filter(SavingsPreference.user_id == current_user.id)
        .first()
    )
    if pref:
        pref.safety_target = request.target_amount

    db.commit()
    return {"message": "Safety target updated", "new_target": request.target_amount}
