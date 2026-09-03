"""
LEVELLY — Authentication Endpoints
Register, Login, Logout, Me
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.core.security import (
    hash_password, verify_password, create_access_token, get_current_user
)
from app.core.config import settings
from app.models.user import User
from app.models.wallet import Wallet
from app.models.savings import SavingsPreference
from app.models.financial_profile import FinancialProfile

router = APIRouter()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: str | None = None
    occupation: str | None = None
    city: str | None = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    full_name: str
    email: str
    role: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone: str | None
    role: str
    occupation: str | None
    city: str | None
    is_active: bool
    onboarding_complete: bool
    platform_tenure_months: int

    class Config:
        from_attributes = True


@router.post("/register", response_model=LoginResponse, status_code=201)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user and create their wallets."""
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "EMAIL_TAKEN", "message": "Email already registered"},
        )

    user = User(
        email=request.email,
        full_name=request.full_name,
        hashed_password=hash_password(request.password),
        phone=request.phone,
        occupation=request.occupation,
        city=request.city,
        role="user",
    )
    db.add(user)
    db.flush()

    # Create Daily and Safety wallets
    daily_wallet = Wallet(user_id=user.id, wallet_type="DAILY", balance=0.0)
    safety_wallet = Wallet(
        user_id=user.id, wallet_type="SAFETY", balance=0.0, target_amount=10000.0
    )
    db.add(daily_wallet)
    db.add(safety_wallet)

    # Create savings preference
    savings_pref = SavingsPreference(user_id=user.id, safety_target=10000.0)
    db.add(savings_pref)

    # Create empty financial profile
    profile = FinancialProfile(user_id=user.id)
    db.add(profile)

    db.commit()

    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        full_name=user.full_name,
        email=user.email,
        role=user.role,
    )


@router.post("/login", response_model=LoginResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Login with email/password. Returns JWT token."""
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "Incorrect email or password"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "ACCOUNT_INACTIVE", "message": "Account is inactive"},
        )

    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        full_name=user.full_name,
        email=user.email,
        role=user.role,
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user profile."""
    return current_user


@router.post("/logout")
def logout():
    """
    Logout (client-side token invalidation).
    JWT is stateless — client should discard the token.
    """
    return {"message": "Successfully logged out. Please discard your token."}
