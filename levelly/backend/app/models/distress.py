"""
LEVELLY — Distress Event Model
Records distress detection events and actions
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base


class DistressEvent(Base):
    """Records each distress evaluation event."""
    __tablename__ = "distress_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    distress_score = Column(Float, nullable=False)
    distress_level = Column(String(20), nullable=False)  # LOW, MODERATE, HIGH, SEVERE

    # Input signals
    income_decline_pct = Column(Float, default=0.0)
    expense_ratio = Column(Float, default=0.0)
    safety_depletion_pct = Column(Float, default=0.0)
    credit_pressure = Column(Float, default=0.0)
    resilience_score = Column(Float, default=0.0)
    consecutive_low_periods = Column(Integer, default=0)

    # Signals list and recommended action
    signals = Column(JSON, default=list)
    recommended_action = Column(String(100), nullable=True)

    # Was this a sustained distress event?
    is_sustained = Column(Boolean, default=False)

    notes = Column(Text, nullable=True)
    evaluated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    user = relationship("User", back_populates="distress_events")

    def __repr__(self):
        return f"<DistressEvent user_id={self.user_id} level={self.distress_level} score={self.distress_score}>"
