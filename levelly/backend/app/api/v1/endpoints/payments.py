"""
LEVELLY — Payments Endpoints (Direct Bank/UPI Architecture)
Eliminates Daily Wallet requirement. Payments originate from the user's
linked Bank/UPI account directly to the merchant.
Smart Save-at-Pay provides an optional, transparent contribution to the Safety Wallet.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Any
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.wallet import Wallet
from app.models.payment import (
    LinkedPaymentAccount,
    Merchant,
    PaymentTransaction,
    QRPaymentSession,
    PaymentProviderEvent,
)
from app.models.transaction import ExpenseTransaction, Transaction
from app.models.savings import SavingsTransaction
from app.models.financial_profile import FinancialProfile
from app.models.audit import AuditLog
from app.engines.savings_engine import SavingsEngine
from app.services.category_service import CategoryService
from app.services.notification_service import NotificationService
from app.providers.payment_provider import get_payment_provider

router = APIRouter()


# ============================================================
# SCHEMAS
# ============================================================

class ScanQRRequest(BaseModel):
    qr_payload: str


class PaymentPreviewRequest(BaseModel):
    merchant_id: Optional[Any] = None
    merchant_code: Optional[str] = None
    merchant_upi_id: Optional[str] = None
    merchant_name: Optional[str] = None
    amount: float
    category: Optional[str] = None


class PaymentConfirmRequest(BaseModel):
    merchant_id: Optional[Any] = None
    merchant_code: Optional[str] = None
    merchant_upi_id: Optional[str] = None
    merchant_name: Optional[str] = None
    amount: float
    category: Optional[str] = None
    save_consent: bool = False
    suggested_save_amount: Optional[float] = None
    idempotency_key: Optional[str] = None
    description: Optional[str] = None


# ============================================================
# HELPER: GET OR CREATE USER SAFETY WALLET
# ============================================================

def _get_safety_wallet(db: Session, user_id: int) -> Wallet:
    safety_wallet = (
        db.query(Wallet)
        .filter(Wallet.user_id == user_id, Wallet.wallet_type == "SAFETY")
        .first()
    )
    if not safety_wallet:
        safety_wallet = Wallet(
            user_id=user_id,
            wallet_type="SAFETY",
            balance=8200.0,
            target_amount=10000.0,
            currency="INR",
            is_active=True,
        )
        db.add(safety_wallet)
        db.commit()
        db.refresh(safety_wallet)
    return safety_wallet


# ============================================================
# HELPER: RESOLVE MERCHANT
# ============================================================

def _resolve_merchant(db: Session, request_data: Any) -> Merchant:
    merchant = None
    if getattr(request_data, "merchant_id", None):
        try:
            m_id = int(request_data.merchant_id)
            merchant = db.query(Merchant).filter(Merchant.id == m_id).first()
        except (ValueError, TypeError):
            merchant = db.query(Merchant).filter(Merchant.merchant_code == str(request_data.merchant_id)).first()

    if not merchant and getattr(request_data, "merchant_code", None):
        merchant = db.query(Merchant).filter(Merchant.merchant_code == request_data.merchant_code).first()

    if not merchant and getattr(request_data, "merchant_upi_id", None):
        merchant = db.query(Merchant).filter(Merchant.upi_id == request_data.merchant_upi_id).first()

    if not merchant:
        # Fallback to first merchant or create on-the-fly development merchant
        name = getattr(request_data, "merchant_name", None) or "Sri Krishna Supermarket"
        upi_id = getattr(request_data, "merchant_upi_id", None) or "srikrishna@upi"
        merchant = Merchant(
            merchant_code=f"M_{uuid.uuid4().hex[:6].upper()}",
            name=name,
            upi_id=upi_id,
            category=getattr(request_data, "category", None) or "Food & Grocery",
            normalized_category=CategoryService.normalize(name, getattr(request_data, "category", None)),
            verification_status="verified",
        )
        db.add(merchant)
        db.commit()
        db.refresh(merchant)

    return merchant


# ============================================================
# ENDPOINTS
# ============================================================

@router.get("/linked-account")
def get_linked_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get user's connected Bank / UPI account.
    Security: Zero PIN/password exposure.
    """
    account = (
        db.query(LinkedPaymentAccount)
        .filter(LinkedPaymentAccount.user_id == current_user.id, LinkedPaymentAccount.is_primary == True)
        .first()
    )
    if not account:
        account = LinkedPaymentAccount(
            user_id=current_user.id,
            provider="upi",
            upi_id=f"{current_user.email.split('@')[0]}@upi" if current_user.email else "arjun@upi",
            bank_name="HDFC Bank",
            account_mask="****4821",
            account_holder_name=current_user.full_name or "Arjun Kumar",
            status="connected",
            is_primary=True,
        )
        db.add(account)
        db.commit()
        db.refresh(account)

    return {
        "id": account.id,
        "upi_id": account.upi_id,
        "bank_name": account.bank_name,
        "account_mask": account.account_mask,
        "account_holder_name": account.account_holder_name,
        "status": account.status,
        "provider": account.provider,
    }


@router.get("/merchants")
def get_verified_merchants(
    db: Session = Depends(get_db),
):
    """List verified merchants for demo & quick test."""
    merchants = db.query(Merchant).filter(Merchant.verification_status == "verified").all()
    return [
        {
            "id": m.id,
            "merchant_code": m.merchant_code,
            "name": m.name,
            "upi_id": m.upi_id,
            "category": m.category,
            "normalized_category": m.normalized_category,
            "verification_status": m.verification_status,
            "logo_url": m.logo_url,
        }
        for m in merchants
    ]


@router.post("/scan-qr")
def scan_qr_code(
    request: ScanQRRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Parse scanned QR code payload and resolve merchant information.
    Accepts standard UPI URIs (upi://pay?pa=...&pn=...) or test merchant codes.
    """
    payload = request.qr_payload.strip()
    merchant = None

    # Check if payload matches a merchant code or upi_id directly
    merchant = (
        db.query(Merchant)
        .filter(
            (Merchant.merchant_code == payload) |
            (Merchant.upi_id == payload)
        )
        .first()
    )

    # Parse UPI URI if applicable
    parsed_upi = None
    parsed_name = None
    if not merchant and payload.startswith("upi://pay"):
        try:
            import urllib.parse as urlparse
            parsed = urlparse.urlparse(payload)
            params = urlparse.parse_qs(parsed.query)
            parsed_upi = params.get("pa", [None])[0]
            parsed_name = params.get("pn", [None])[0]
            if parsed_upi:
                merchant = db.query(Merchant).filter(Merchant.upi_id == parsed_upi).first()
        except Exception:
            pass

    if not merchant:
        # Fallback to demo default
        merchant = db.query(Merchant).first()
        if not merchant:
            merchant = Merchant(
                merchant_code="M001",
                name=parsed_name or "Sri Krishna Supermarket",
                upi_id=parsed_upi or "srikrishna@upi",
                category="Food & Grocery",
                normalized_category="food",
                verification_status="verified",
            )
            db.add(merchant)
            db.commit()
            db.refresh(merchant)

    # Record QR session
    session = QRPaymentSession(
        user_id=current_user.id,
        qr_payload=payload,
        merchant_id=merchant.id,
        status="active",
    )
    db.add(session)
    db.commit()

    return {
        "session_id": session.id,
        "merchant": {
            "id": merchant.id,
            "merchant_code": merchant.merchant_code,
            "name": merchant.name,
            "upi_id": merchant.upi_id,
            "category": merchant.category,
            "normalized_category": merchant.normalized_category,
            "verification_status": merchant.verification_status,
        },
        "default_category": merchant.normalized_category,
    }


@router.post("/preview")
def payment_preview(
    request: PaymentPreviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Preview payment and calculate Smart Save-at-Pay recommendation.
    Frontend values are NOT trusted; backend calculates authoritative percentages.
    """
    if request.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_AMOUNT", "message": "Payment amount must be greater than zero"},
        )

    merchant = _resolve_merchant(db, request)
    category = CategoryService.normalize(merchant.name, merchant.category, request.category)

    # Query distress level from Financial Profile
    profile = (
        db.query(FinancialProfile)
        .filter(FinancialProfile.user_id == current_user.id)
        .first()
    )
    distress_level = profile.distress_level if profile else "LOW"

    # Calculate authoritative save suggestion
    engine = SavingsEngine(db)
    suggestion = engine.calculate_save_suggestion(
        amount=request.amount,
        category=category,
        user_id=current_user.id,
        distress_level=distress_level,
    )

    safety_wallet = _get_safety_wallet(db, current_user.id)
    buffer_impact_pct = (
        round((request.amount / safety_wallet.balance) * 100, 1)
        if safety_wallet.balance > 0 else 100.0
    )
    is_large_expense = request.amount >= 5000 or buffer_impact_pct >= 50.0

    return {
        "merchant": {
            "id": merchant.id,
            "merchant_code": merchant.merchant_code,
            "name": merchant.name,
            "upi_id": merchant.upi_id,
            "category": merchant.category,
            "verification_status": merchant.verification_status,
        },
        "amount": request.amount,
        "category": category,
        "suggested_percentage": suggestion["suggested_percentage"],
        "suggested_save_amount": suggestion["suggested_save_amount"],
        "total_if_save": round(request.amount + suggestion["suggested_save_amount"], 2),
        "safety_wallet_balance": safety_wallet.balance,
        "safety_wallet_target": safety_wallet.target_amount or 10000.0,
        "safety_wallet_progress": safety_wallet.progress_percentage,
        "is_large_expense": is_large_expense,
        "buffer_impact_pct": min(buffer_impact_pct, 100.0),
        "distress_level": distress_level,
    }


@router.post("/confirm")
def payment_confirm(
    request: PaymentConfirmRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Execute payment from linked Bank/UPI directly to the merchant.
    Applies optional Save-at-Pay contribution atomically to the Safety Wallet.
    Idempotent & resilient to provider retries.
    """
    if request.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_AMOUNT", "message": "Payment amount must be greater than zero"},
        )

    # Idempotency check
    idempotency_key = request.idempotency_key or f"IDEMP_{uuid.uuid4().hex}"
    existing_txn = (
        db.query(PaymentTransaction)
        .filter(PaymentTransaction.idempotency_key == idempotency_key)
        .first()
    )
    if existing_txn:
        return {
            "status": existing_txn.status,
            "payment_id": existing_txn.id,
            "provider_transaction_id": existing_txn.provider_transaction_id,
            "message": "Payment previously confirmed",
            "is_duplicate": True,
        }

    merchant = _resolve_merchant(db, request)
    category = CategoryService.normalize(merchant.name, merchant.category, request.category)

    # Backend verifies distress & authoritative savings amount
    profile = (
        db.query(FinancialProfile)
        .filter(FinancialProfile.user_id == current_user.id)
        .first()
    )
    distress_level = profile.distress_level if profile else "LOW"

    engine = SavingsEngine(db)
    suggestion = engine.calculate_save_suggestion(
        amount=request.amount,
        category=category,
        user_id=current_user.id,
        distress_level=distress_level,
    )

    actual_save_amount = (
        suggestion["suggested_save_amount"] if request.save_consent else 0.0
    )

    # Initialize payment transaction
    payment_txn = PaymentTransaction(
        user_id=current_user.id,
        merchant_id=merchant.id,
        merchant_name=merchant.name,
        merchant_upi_id=merchant.upi_id,
        amount=request.amount,
        currency="INR",
        category=category,
        save_consent=request.save_consent,
        suggested_percentage=suggestion["suggested_percentage"],
        suggested_save_amount=suggestion["suggested_save_amount"],
        actual_save_amount=actual_save_amount,
        idempotency_key=idempotency_key,
        status="PENDING",
    )
    db.add(payment_txn)
    db.flush()

    # Invoke Payment Provider
    provider = get_payment_provider()
    provider_res = provider.create_payment(
        payment_id=payment_txn.id,
        user_id=current_user.id,
        merchant_upi_id=merchant.upi_id,
        merchant_name=merchant.name,
        amount=request.amount,
        note=f"LEVELLY Pay to {merchant.name}",
        idempotency_key=idempotency_key,
    )

    payment_txn.provider = provider_res.get("provider", "mock")
    payment_txn.provider_transaction_id = provider_res.get("provider_transaction_id")
    payment_status = provider_res.get("status", "SUCCESS")
    payment_txn.status = payment_status

    safety_wallet = _get_safety_wallet(db, current_user.id)
    initial_safety = safety_wallet.balance

    # Atomic settlement when payment succeeds
    if payment_status == "SUCCESS":
        # 1. Process consented savings contribution to Safety Wallet
        if request.save_consent and actual_save_amount > 0 and not payment_txn.savings_credited:
            safety_wallet.balance = round(safety_wallet.balance + actual_save_amount, 2)
            payment_txn.savings_credited = True

            savings_txn = SavingsTransaction(
                user_id=current_user.id,
                amount=actual_save_amount,
                transaction_type="save_at_pay",
                category_context=category,
                balance_before=initial_safety,
                balance_after=safety_wallet.balance,
            )
            db.add(savings_txn)

        # 2. Record Expense transaction for financial intelligence & categorization
        expense = ExpenseTransaction(
            user_id=current_user.id,
            amount=request.amount,
            currency="INR",
            category=category,
            merchant=merchant.name,
            description=request.description or f"Payment to {merchant.name}",
            savings_added=actual_save_amount if request.save_consent else 0.0,
            save_consent=request.save_consent,
            status="completed",
        )
        db.add(expense)

        # 3. Regulatory compliance audit log
        audit = AuditLog(
            user_id=current_user.id,
            event_type="upi_payment_success",
            action=f"Paid ₹{request.amount:,.0f} to {merchant.name} (Saved ₹{actual_save_amount:,.0f})",
            entity_type="payment_transaction",
            entity_id=payment_txn.id,
            extra_data={
                "merchant_upi": merchant.upi_id,
                "amount": request.amount,
                "save_amount": actual_save_amount,
                "save_consent": request.save_consent,
                "total_impact": request.amount + actual_save_amount,
            },
        )
        db.add(audit)

        # 4. Optional notification
        if request.save_consent and actual_save_amount > 0:
            notif_svc = NotificationService(db)
            notif_svc.notify_savings_added(
                user_id=current_user.id,
                amount=actual_save_amount,
                wallet_type="SAFETY",
                safety_balance=safety_wallet.balance,
            )

    db.commit()
    db.refresh(payment_txn)
    db.refresh(safety_wallet)

    return {
        "payment_id": payment_txn.id,
        "provider_transaction_id": payment_txn.provider_transaction_id,
        "status": payment_txn.status,
        "merchant": {
            "name": merchant.name,
            "upi_id": merchant.upi_id,
        },
        "merchant_amount": request.amount,
        "save_amount": actual_save_amount if request.save_consent else 0.0,
        "total_cash_impact": request.amount + (actual_save_amount if request.save_consent else 0.0),
        "save_consent": request.save_consent,
        "safety_wallet_balance": safety_wallet.balance,
        "safety_wallet_target": safety_wallet.target_amount,
        "safety_wallet_progress": safety_wallet.progress_percentage,
        "upi_intent_url": provider_res.get("upi_intent_url"),
        "created_at": payment_txn.created_at.isoformat() if payment_txn.created_at else None,
    }


@router.post("/webhook")
def payment_webhook(
    payload: dict,
    x_signature: Optional[str] = Header(None, alias="X-Provider-Signature"),
    db: Session = Depends(get_db),
):
    """
    Webhook receiver for payment provider callbacks.
    Validates provider event and updates payment & safety wallet idempotently.
    """
    provider = get_payment_provider()
    event_result = provider.handle_webhook(payload, x_signature)

    provider_txn_id = event_result.get("provider_transaction_id")
    event_type = event_result.get("event_type", "payment.unknown")

    # Record event log
    provider_event = PaymentProviderEvent(
        provider=getattr(settings, "PAYMENT_PROVIDER", "mock"),
        event_type=event_type,
        provider_event_id=f"EVT_{uuid.uuid4().hex[:12]}",
        payload=payload,
        status="processed" if event_result.get("valid") else "error",
    )
    db.add(provider_event)

    if not event_result.get("valid"):
        db.commit()
        return {"status": "ignored", "reason": "invalid_signature"}

    # Update payment transaction if exists
    if provider_txn_id:
        txn = (
            db.query(PaymentTransaction)
            .filter(PaymentTransaction.provider_transaction_id == provider_txn_id)
            .first()
        )
        if txn:
            new_status = event_result.get("status", "SUCCESS")
            txn.status = new_status

            # If newly successful and save_consent was true, credit safety wallet
            if new_status == "SUCCESS" and txn.save_consent and txn.actual_save_amount > 0 and not txn.savings_credited:
                safety_wallet = _get_safety_wallet(db, txn.user_id)
                safety_wallet.balance = round(safety_wallet.balance + txn.actual_save_amount, 2)
                txn.savings_credited = True

                db.add(SavingsTransaction(
                    user_id=txn.user_id,
                    amount=txn.actual_save_amount,
                    transaction_type="save_at_pay",
                    category_context=txn.category,
                    balance_before=safety_wallet.balance - txn.actual_save_amount,
                    balance_after=safety_wallet.balance,
                ))

    db.commit()
    return {"status": "received", "event_type": event_type}


@router.get("/recent")
def get_recent_payments(
    limit: int = 15,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List recent payments with merchant names, categories, and Save-at-Pay contributions."""
    payments = (
        db.query(PaymentTransaction)
        .filter(PaymentTransaction.user_id == current_user.id)
        .order_by(PaymentTransaction.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": p.id,
            "merchant_name": p.merchant_name,
            "merchant_upi_id": p.merchant_upi_id,
            "amount": p.amount,
            "category": p.category,
            "save_consent": p.save_consent,
            "save_amount": p.actual_save_amount if p.save_consent else 0.0,
            "total_cash_impact": p.total_cash_impact,
            "status": p.status,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in payments
    ]
