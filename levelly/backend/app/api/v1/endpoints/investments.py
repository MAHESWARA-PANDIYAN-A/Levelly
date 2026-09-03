"""
LEVELLY — Investment Endpoints
Suggestions, consent workflow, execution
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.investment import (
    InvestmentProduct, InvestmentConsent, InvestmentOrder, InvestmentSuggestion
)
from app.models.audit import AuditLog
from app.engines.investment_engine import InvestmentRecommendationService
from app.integrations.mock_investment_provider import get_investment_provider
from app.services.notification_service import NotificationService

router = APIRouter()


class InvestmentConsentRequest(BaseModel):
    product_id: int
    suggestion_id: Optional[int] = None
    amount: float
    terms_accepted: bool


class InvestmentConfirmRequest(BaseModel):
    consent_id: int


@router.get("/status")
def get_investment_status(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get investment readiness status."""
    svc = InvestmentRecommendationService(db)
    return svc.get_investment_status(current_user.id)


@router.get("/suggestions")
def get_investment_suggestions(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get personalized investment suggestions."""
    svc = InvestmentRecommendationService(db)
    status = svc.get_investment_status(current_user.id)

    if status["is_paused"]:
        return {
            "paused": True,
            "pause_reason": status["pause_reason"],
            "suggestions": [],
            "safety_balance": status["safety_balance"],
            "safety_target": status["safety_target"],
        }

    suggestions = svc.get_suggestions(current_user.id)

    return {
        "paused": False,
        "suggestions": suggestions,
        "safety_surplus": status["safety_surplus"],
        "available_for_investment": status["available_for_investment"],
    }


@router.get("/products/{product_id}")
def get_product_details(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get detailed information about an investment product."""
    product = (
        db.query(InvestmentProduct)
        .filter(InvestmentProduct.id == product_id, InvestmentProduct.active == True)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return {
        "id": product.id,
        "name": product.name,
        "type": product.product_type,
        "issuer": product.issuer,
        "risk_level": product.risk_level,
        "liquidity": product.liquidity,
        "holding_period": product.holding_period,
        "interest_or_coupon": product.interest_or_coupon,
        "fees": product.fees,
        "tax_notes": product.tax_notes,
        "terms": product.terms,
        "min_investment": product.min_investment,
        "description": product.description,
        "suitable_for": product.suitable_for,
    }


@router.post("/consent")
def create_investment_consent(
    request: InvestmentConsentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create investment consent record.
    Consent is not yet confirmed — user must explicitly confirm.
    """
    if not request.terms_accepted:
        raise HTTPException(
            status_code=400,
            detail={"code": "TERMS_NOT_ACCEPTED", "message": "Please accept the terms to proceed"},
        )

    if request.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_AMOUNT", "message": "Investment amount must be positive"},
        )

    product = (
        db.query(InvestmentProduct)
        .filter(InvestmentProduct.id == request.product_id, InvestmentProduct.active == True)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Investment product not found")

    if request.amount < product.min_investment:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "BELOW_MINIMUM",
                "message": f"Minimum investment for this product is ₹{product.min_investment:,.0f}",
            },
        )

    # Check investment readiness
    svc = InvestmentRecommendationService(db)
    status = svc.get_investment_status(current_user.id)
    if status["is_paused"]:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVESTMENT_PAUSED",
                "message": status["pause_reason"],
            },
        )

    consent = InvestmentConsent(
        user_id=current_user.id,
        product_id=request.product_id,
        suggestion_id=request.suggestion_id,
        amount=request.amount,
        confirmed=False,
        terms_version="1.0",
        consent_metadata={"terms_accepted": True},
    )
    db.add(consent)

    audit = AuditLog(
        user_id=current_user.id,
        actor_id=current_user.id,
        event_type="investment_consent",
        action="consent_created",
        entity_type="investment",
        extra_data={"product_id": request.product_id, "amount": request.amount},
    )
    db.add(audit)
    db.commit()

    return {
        "consent_id": consent.id,
        "product_id": product.id,
        "product_name": product.name,
        "amount": request.amount,
        "confirmed": False,
        "message": "Please review and confirm to proceed with your investment.",
        "warning": "Investments involve risk. Please review all product details before confirming.",
    }


@router.post("/confirm/{consent_id}")
def confirm_investment(
    consent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    EXPLICIT investment confirmation. Triggers partner execution.
    Cannot be called without a valid, unconfirmed consent record.
    """
    consent = (
        db.query(InvestmentConsent)
        .filter(
            InvestmentConsent.id == consent_id,
            InvestmentConsent.user_id == current_user.id,
        )
        .first()
    )

    if not consent:
        raise HTTPException(status_code=404, detail="Consent not found")

    if consent.confirmed:
        raise HTTPException(
            status_code=400,
            detail={"code": "ALREADY_CONFIRMED", "message": "This consent has already been confirmed"},
        )

    # Re-check investment readiness at time of execution
    svc = InvestmentRecommendationService(db)
    status = svc.get_investment_status(current_user.id)
    if status["is_paused"]:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVESTMENT_PAUSED", "message": status["pause_reason"]},
        )

    product = db.query(InvestmentProduct).filter_by(id=consent.product_id).first()

    # Confirm consent
    consent.confirmed = True
    consent.confirmed_at = datetime.now(timezone.utc)
    db.flush()

    # Submit to investment partner
    provider = get_investment_provider(settings.INVESTMENT_PROVIDER)
    order_data = {
        "consent_id": consent.id,
        "product_id": product.id,
        "product_name": product.name,
        "amount": consent.amount,
        "user_id": current_user.id,
    }
    partner_response = provider.create_order(order_data)

    # Record order
    order = InvestmentOrder(
        user_id=current_user.id,
        consent_id=consent.id,
        product_id=product.id,
        amount=consent.amount,
        partner_order_id=partner_response.get("order_id"),
        partner_name=partner_response.get("partner"),
        order_status="processing",
        partner_response=partner_response,
    )
    db.add(order)

    # Audit
    audit = AuditLog(
        user_id=current_user.id,
        actor_id=current_user.id,
        event_type="investment_execution_request",
        action="investment_confirmed_and_submitted",
        entity_type="investment",
        extra_data={
            "consent_id": consent_id,
            "product_id": product.id,
            "amount": consent.amount,
            "order_id": partner_response.get("order_id"),
        },
    )
    db.add(audit)
    db.commit()

    # Notify
    notif_svc = NotificationService(db)
    notif_svc.investment_status_changed(
        current_user.id, partner_response.get("order_id", str(order.id)), "submitted"
    )

    return {
        "success": True,
        "order_id": order.id,
        "partner_order_id": partner_response.get("order_id"),
        "product_name": product.name,
        "amount": consent.amount,
        "status": "processing",
        "message": partner_response.get("message"),
        "disclaimer": partner_response.get("disclaimer"),
    }


@router.get("/orders")
def get_investment_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 10,
):
    """Get investment order history."""
    orders = (
        db.query(InvestmentOrder)
        .filter(InvestmentOrder.user_id == current_user.id)
        .order_by(InvestmentOrder.created_at.desc())
        .limit(limit)
        .all()
    )

    result = []
    for o in orders:
        product = db.query(InvestmentProduct).filter_by(id=o.product_id).first()
        result.append({
            "id": o.id,
            "product_name": product.name if product else "Unknown",
            "amount": o.amount,
            "status": o.order_status,
            "partner_order_id": o.partner_order_id,
            "created_at": o.created_at.isoformat(),
        })

    return result
