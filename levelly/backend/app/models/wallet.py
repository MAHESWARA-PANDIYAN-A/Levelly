"""
LEVELLY — Wallet Models
Two wallet types: DAILY and SAFETY
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    wallet_type = Column(String(20), nullable=False)  # DAILY or SAFETY
    balance = Column(Float, default=0.0, nullable=False)
    currency = Column(String(10), default="INR")
    is_active = Column(Boolean, default=True)

    # Safety Wallet specific
    target_amount = Column(Float, nullable=True)  # Safety target

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="wallets")

    @property
    def progress_percentage(self) -> float:
        """Calculate progress towards safety target."""
        if self.wallet_type == "SAFETY" and self.target_amount and self.target_amount > 0:
            return min(round((self.balance / self.target_amount) * 100, 1), 100.0)
        return 0.0

    def __repr__(self):
        return f"<Wallet id={self.id} type={self.wallet_type} balance={self.balance}>"
