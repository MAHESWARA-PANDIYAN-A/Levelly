"""
LEVELLY — Credit Models
CreditRequest and PartnerCreditOffer
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base


class CreditRequest(Base):
    """User's credit request with LEVELLY recommendation and guardrail decision."""
    __tablename__ = "credit_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    requested_amount = Column(Float, nullable=False)
    purpose = Column(String(255), nullable=True)

    # LEVELLY recommendation
    recommended_amount = Column(Float, nullable=True)
    recommendation_status = Column(String(50), nullable=True)  # approved, reduced, held

    # Guardrail decision
    guardrail_status = Column(String(50), nullable=True)  # allowed, reduced, held
    guardrail_reason_codes = Column(JSON, default=list)
    guardrail_message = Column(Text, nullable=True)

    # Distress at time of request
    distress_level_at_request = Column(String(20), nullable=True)
    resilience_score_at_request = Column(Float, nullable=True)

    # Partner status
    partner_offer_id = Column(Integer, ForeignKey("partner_credit_offers.id"), nullable=True)
    status = Column(String(50), default="pending")  # pending, offer_received, accepted, declined, held

    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="credit_requests")
    partner_offer = relationship("PartnerCreditOffer", foreign_keys=[partner_offer_id])

    def __repr__(self):
        return f"<CreditRequest id={self.id} amount={self.requested_amount} status={self.status}>"


class PartnerCreditOffer(Base):
    """Offer from partner NBFC (mock or real)."""
    __tablename__ = "partner_credit_offers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    credit_request_id = Column(Integer, ForeignKey("credit_requests.id"), nullable=True)

    partner_name = Column(String(100), nullable=False, default="Partner NBFC")
    partner_reference = Column(String(100), nullable=True)  # partner's internal ID

    offered_amount = Column(Float, nullable=False)
    interest_rate = Column(Float, nullable=True)  # annual %
    tenure_months = Column(Integer, nullable=True)
    emi_amount = Column(Float, nullable=True)
    processing_fee = Column(Float, default=0.0)

    eligibility_status = Column(String(50), nullable=True)  # eligible, not_eligible
    offer_status = Column(String(50), default="pending")  # pending, accepted, declined, expired
    offer_terms = Column(JSON, default=dict)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<PartnerCreditOffer id={self.id} amount={self.offered_amount} partner={self.partner_name}>"
