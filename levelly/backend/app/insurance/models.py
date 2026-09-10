"""
LEVELLY IncomeShield — Insurance Models
Implements native income-protection domain entities without duplicating core LEVELLY user or financial profile data.
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    Text,
    JSON,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class InsurancePartner(Base):
    """Underwriting and claims settlement partner."""
    __tablename__ = "insurance_partners"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(64), unique=True, nullable=False, index=True)
    partner_type = Column(String(64), default="LICENSED_INSURER")
    active = Column(Boolean, default=True)
    contact_info = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    plans = relationship("InsurancePlan", back_populates="partner")
    policies = relationship("InsurancePolicy", back_populates="partner")


class InsurancePlan(Base):
    """Curated, configurable income protection plan."""
    __tablename__ = "insurance_plans"

    id = Column(Integer, primary_key=True, index=True)
    partner_id = Column(Integer, ForeignKey("insurance_partners.id"), nullable=True)
    name = Column(String(255), nullable=False)
    code = Column(String(64), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    premium = Column(Float, nullable=False)
    premium_frequency = Column(String(32), default="weekly")
    coverage_limit = Column(Float, nullable=False)
    policy_duration = Column(String(64), default="7 days")
    covered_events = Column(JSON, default=list)  # ["HEAVY_RAIN", "FLOOD", "EXTREME_HEAT", "WORK_DISRUPTION"]
    trigger_conditions = Column(JSON, default=dict)  # {"HEAVY_RAIN": "Rainfall >= 50mm in 3h", ...}
    waiting_period = Column(String(64), default="24 hours")
    exclusions = Column(JSON, default=list)
    coverage_area_rules = Column(JSON, default=dict)  # {"zones": ["Chennai Delivery Zone", ...]}
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    partner = relationship("InsurancePartner", back_populates="plans")
    policies = relationship("InsurancePolicy", back_populates="plan")
    consents = relationship("InsuranceConsent", back_populates="plan")


class InsurancePolicy(Base):
    """User-enrolled insurance policy with explicit consent."""
    __tablename__ = "insurance_policies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("insurance_plans.id"), nullable=False, index=True)
    partner_id = Column(Integer, ForeignKey("insurance_partners.id"), nullable=True)
    policy_number = Column(String(128), unique=True, nullable=False, index=True)
    status = Column(String(32), default="ACTIVE", index=True)  # ACTIVE, EXPIRED, CANCELLED, PENDING
    start_date = Column(DateTime(timezone=True), default=utcnow)
    end_date = Column(DateTime(timezone=True), nullable=False)
    premium = Column(Float, nullable=False)
    coverage_limit = Column(Float, nullable=False)
    covered_work_zone = Column(String(128), default="Chennai Delivery Zone")
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user = relationship("User")
    plan = relationship("InsurancePlan", back_populates="policies")
    partner = relationship("InsurancePartner", back_populates="policies")
    trigger_evaluations = relationship("InsuranceTriggerEvaluation", back_populates="policy")
    payouts = relationship("InsurancePayout", back_populates="policy")
    documents = relationship("InsuranceDocument", back_populates="policy")


class InsuranceConsent(Base):
    """Explicit, unbundled user consent record for policy enrollment."""
    __tablename__ = "insurance_consents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("insurance_plans.id"), nullable=False)
    terms_version = Column(String(32), default="v1.0")
    confirmed = Column(Boolean, default=False)
    confirmed_at = Column(DateTime(timezone=True), default=utcnow)

    user = relationship("User")
    plan = relationship("InsurancePlan", back_populates="consents")


class InsuranceEvent(Base):
    """External weather or environmental disruption detected in a work zone."""
    __tablename__ = "insurance_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(64), nullable=False, index=True)  # HEAVY_RAIN, FLOOD, EXTREME_HEAT, WORK_DISRUPTION
    zone = Column(String(128), nullable=False, index=True)
    start_time = Column(DateTime(timezone=True), default=utcnow)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration = Column(String(64), default="Ongoing")
    source = Column(String(128), default="IMD / Weather Telemetry")
    source_reference = Column(String(128), nullable=True)
    verification_status = Column(String(32), default="VERIFIED", index=True)  # VERIFIED, MONITORING, UNVERIFIED
    severity = Column(String(32), default="MODERATE")  # LOW, MODERATE, SEVERE
    telemetry_data = Column(JSON, default=dict)  # {"observed_rainfall_mm": 58, "duration_hours": 3}
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    evaluations = relationship("InsuranceTriggerEvaluation", back_populates="event")
    payouts = relationship("InsurancePayout", back_populates="event")


class InsuranceTriggerEvaluation(Base):
    """Deterministic policy condition evaluation against an external event."""
    __tablename__ = "insurance_trigger_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("insurance_policies.id"), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey("insurance_events.id"), nullable=False, index=True)
    trigger_type = Column(String(64), nullable=False)
    threshold = Column(String(128), nullable=False)
    observed_value = Column(String(128), nullable=False)
    required_value = Column(String(128), nullable=False)
    status = Column(String(32), default="PENDING", index=True)  # NOT_REACHED, REACHED, INVALID, PENDING
    evaluated_at = Column(DateTime(timezone=True), default=utcnow)
    reason = Column(Text, nullable=False)

    policy = relationship("InsurancePolicy", back_populates="trigger_evaluations")
    event = relationship("InsuranceEvent", back_populates="evaluations")


class InsurancePayout(Base):
    """Claim payout record issued by the insurance partner."""
    __tablename__ = "insurance_payouts"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("insurance_policies.id"), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey("insurance_events.id"), nullable=True)
    payout_id_from_partner = Column(String(128), unique=True, nullable=True, index=True)
    amount = Column(Float, nullable=True)  # None if awaiting partner confirmation
    currency = Column(String(16), default="INR")
    status = Column(String(32), default="PENDING", index=True)  # PENDING, PROCESSING, COMPLETED, FAILED, REJECTED
    reason = Column(String(255), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    destination_reference = Column(String(128), default="Linked Bank Account (Direct UPI)")
    destination_type = Column(String(64), default="LINKED_ACCOUNT")  # LINKED_ACCOUNT, SAFETY_WALLET
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    policy = relationship("InsurancePolicy", back_populates="payouts")
    event = relationship("InsuranceEvent", back_populates="payouts")


class InsuranceDocument(Base):
    """Legal schedules, policy terms, and exclusions documents."""
    __tablename__ = "insurance_documents"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("insurance_policies.id"), nullable=True, index=True)
    plan_id = Column(Integer, ForeignKey("insurance_plans.id"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    document_type = Column(String(64), default="POLICY_SCHEDULE")  # POLICY_SCHEDULE, TERMS_AND_CONDITIONS, EXCLUSIONS_GUIDE
    file_url = Column(String(512), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    policy = relationship("InsurancePolicy", back_populates="documents")
