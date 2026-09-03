"""
LEVELLY — Credit Endpoints
Credit recommendation + guardrail + partner NBFC flow
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.credit import CreditRequest, PartnerCreditOffer
from app.models.financial_profile import FinancialProfile
from app.models.audit import AuditLog
from app.engines.credit_engine import CreditRecommendationService
from app.engines.guardrail import ResponsibleLendingGuardrailService
from app.integrations.mock_nbfc import get_credit_provider
from app.services.notification_service import NotificationService

router = APIRouter()


class CreditRequestBody(BaseModel):
    requested_amount: float
    purpose: Optional[str] = None


class SubmitCreditApplicationBody(BaseModel):
    credit_request_id: int
    offer_id: int


@router.post("/recommend")
def get_credit_recommendation(
    request: CreditRequestBody,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get LEVELLY's credit recommendation + guardrail evaluation.
    This is LEVELLY's view — the final decision belongs to the partner.
    """
    if request.requested_amount <= 0:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_AMOUNT", "message": "Requested amount must be positive"},
        )

    # Step 1: LEVELLY recommendation
    credit_svc = CreditRecommendationService(db)
    recommendation = credit_svc.generate_recommendation(
        current_user.id, request.requested_amount
    )

    # Step 2: Guardrail check
    guardrail_svc = ResponsibleLendingGuardrailService(db)
    guardrail = guardrail_svc.evaluate(
        current_user.id,
        request.requested_amount,
        recommendation["recommended_amount"],
    )

    # Step 3: Save credit request
    profile = db.query(FinancialProfile).filter_by(user_id=current_user.id).first()
    credit_req = CreditRequest(
        user_id=current_user.id,
        requested_amount=request.requested_amount,
        purpose=request.purpose,
        recommended_amount=recommendation["recommended_amount"],
        recommendation_status=recommendation["status"],
        guardrail_status=guardrail["status"],
        guardrail_reason_codes=guardrail["reason_codes"],
        guardrail_message=guardrail["ui_message"],
        distress_level_at_request=profile.distress_level if profile else "LOW",
        resilience_score_at_request=profile.resilience_score if profile else 0,
        status="recommendation_provided",
    )
    db.add(credit_req)

    # Audit
    audit = AuditLog(
        user_id=current_user.id,
        actor_id=current_user.id,
        event_type="credit_recommendation",
        action="recommendation_generated",
        entity_type="credit_request",
        extra_data={
            "requested": request.requested_amount,
            "recommended": recommendation["recommended_amount"],
            "guardrail_status": guardrail["status"],
        },
    )
    db.add(audit)

    # Guardrail audit
    guardrail_audit = AuditLog(
        user_id=current_user.id,
        actor_id=current_user.id,
        event_type="guardrail_decision",
        action=f"guardrail_{guardrail['status']}",
        entity_type="credit_request",
        extra_data={
            "status": guardrail["status"],
            "reason_codes": guardrail["reason_codes"],
            "distress_level": guardrail["distress_level"],
        },
    )
    db.add(guardrail_audit)
    db.commit()

    # Notification
    notif_svc = NotificationService(db)
    notif_svc.credit_recommendation_changed(current_user.id, guardrail["status"])

    return {
        "credit_request_id": credit_req.id,
        "requested_amount": request.requested_amount,
        "levelly_recommendation": {
            "recommended_amount": recommendation["recommended_amount"],
            "status": recommendation["status"],
            "reasons": recommendation["reasons"],
        },
        "guardrail": {
            "status": guardrail["status"],
            "allowed_amount": guardrail["allowed_amount"],
            "ui_message": guardrail["ui_message"],
            "reason_codes": guardrail["reason_codes"],
            "guidance": guardrail.get("guidance"),
        },
        "can_proceed_to_partner": guardrail["status"] != "held",
        "distress_level": profile.distress_level if profile else "LOW",
        "resilience_score": profile.resilience_score if profile else 0,
    }


@router.post("/partner/offer")
def get_partner_offer(
    request: CreditRequestBody,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a partner NBFC credit offer after LEVELLY guardrail approval."""
    # Get latest credit request
    credit_req = (
        db.query(CreditRequest)
        .filter(
            CreditRequest.user_id == current_user.id,
            CreditRequest.status == "recommendation_provided",
        )
        .order_by(CreditRequest.created_at.desc())
        .first()
    )

    if not credit_req:
        raise HTTPException(
            status_code=400,
            detail={"code": "NO_RECOMMENDATION", "message": "Please get a recommendation first"},
        )

    if credit_req.guardrail_status == "held":
        return {
            "offer_available": False,
            "guardrail_status": "held",
            "message": "Credit temporarily held — let's focus on your financial stability first.",
            "guidance": "Speak with Levelly Coach for personalized guidance.",
        }

    allowed_amount = credit_req.recommended_amount

    # Get partner provider
    provider = get_credit_provider(settings.NBFC_PROVIDER)

    profile = db.query(FinancialProfile).filter_by(user_id=current_user.id).first()
    user_data = {
        "user_id": current_user.id,
        "levelly_recommended_amount": allowed_amount,
        "guardrail_status": credit_req.guardrail_status,
        "distress_level": profile.distress_level if profile else "LOW",
    }

    # Check eligibility
    eligibility = provider.check_eligibility(user_data)
    if not eligibility["eligible"]:
        return {
            "offer_available": False,
            "message": "Pre-assessment indicates credit is not currently available.",
        }

    # Get offer
    offer_data = provider.get_offer(user_data, allowed_amount)

    if offer_data.get("offer_available"):
        # Save offer to DB
        partner_offer = PartnerCreditOffer(
            user_id=current_user.id,
            credit_request_id=credit_req.id,
            partner_name=offer_data["partner"],
            partner_reference=offer_data["partner_reference"],
            offered_amount=offer_data["offered_amount"],
            interest_rate=offer_data.get("annual_interest_rate"),
            tenure_months=offer_data.get("tenure_months"),
            emi_amount=offer_data.get("emi_amount"),
            processing_fee=offer_data.get("processing_fee", 0),
            eligibility_status="eligible",
            offer_status="pending",
            offer_terms=offer_data,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=48),
        )
        db.add(partner_offer)
        credit_req.status = "offer_received"
        db.commit()

        return {
            "offer_available": True,
            "offer_id": partner_offer.id,
            **offer_data,
        }

    return {"offer_available": False}


@router.post("/partner/apply/{offer_id}")
def submit_credit_application(
    offer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit credit application to partner NBFC."""
    offer = (
        db.query(PartnerCreditOffer)
        .filter(
            PartnerCreditOffer.id == offer_id,
            PartnerCreditOffer.user_id == current_user.id,
        )
        .first()
    )
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    provider = get_credit_provider(settings.NBFC_PROVIDER)
    result = provider.submit_application(
        {"user_id": current_user.id},
        offer.offer_terms,
    )

    offer.offer_status = "accepted"
    offer.partner_reference = result.get("application_id", offer.partner_reference)

    credit_req = db.query(CreditRequest).filter_by(id=offer.credit_request_id).first()
    if credit_req:
        credit_req.status = "accepted"

    db.commit()

    return result


@router.get("/history")
def get_credit_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 10,
):
    """Get credit request history."""
    requests = (
        db.query(CreditRequest)
        .filter(CreditRequest.user_id == current_user.id)
        .order_by(CreditRequest.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": r.id,
            "requested_amount": r.requested_amount,
            "recommended_amount": r.recommended_amount,
            "guardrail_status": r.guardrail_status,
            "status": r.status,
            "distress_level": r.distress_level_at_request,
            "created_at": r.created_at.isoformat(),
        }
        for r in requests
    ]
