"""
LEVELLY — Notification Model
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  # event type
    # Types: payout_received, payment_completed, save_at_pay_accepted, safety_wallet_updated,
    #        income_trend_changed, financial_pressure_detected, credit_changed,
    #        investment_suggestion_available, investment_status_changed
    priority = Column(String(20), default="normal")  # low, normal, high
    is_read = Column(Boolean, default=False)
    action_url = Column(String(255), nullable=True)  # deep link for CTA
    extra_data = Column(JSON, default=dict)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification id={self.id} type={self.notification_type} read={self.is_read}>"
