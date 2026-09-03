"""
LEVELLY — Audit Log Model
Immutable audit trail for financial decisions and admin actions
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    actor_id = Column(Integer, nullable=True)  # who performed the action (could be admin)
    event_type = Column(String(100), nullable=False)
    # Events: payment_confirmed, save_at_pay_consent, credit_recommendation,
    #         guardrail_decision, investment_suggestion, investment_consent,
    #         investment_execution_request, admin_policy_change
    action = Column(String(255), nullable=False)
    entity_type = Column(String(100), nullable=True)  # e.g., "payment", "investment"
    entity_id = Column(Integer, nullable=True)
    extra_data = Column(JSON, default=dict)
    ip_address = Column(String(50), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs", foreign_keys=[user_id])

    def __repr__(self):
        return f"<AuditLog id={self.id} event={self.event_type}>"
