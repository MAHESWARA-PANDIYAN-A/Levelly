"""
LEVELLY — Savings Models
SavingsPreference, SavingsTransaction, CategorySavingPolicy
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class CategorySavingPolicy(Base):
    """
    Configurable save-at-pay percentages per expense category.
    Admins can edit these. Financial intelligence adjusts effective percentages.
    """
    __tablename__ = "category_saving_policies"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), unique=True, nullable=False)
    base_percentage = Column(Float, nullable=False)  # base policy (e.g., 10.0 for food)
    min_percentage = Column(Float, default=0.0)  # cannot go below this
    max_percentage = Column(Float, default=20.0)
    is_active = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    updated_by_admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<CategorySavingPolicy category={self.category} base={self.base_percentage}%>"


class SavingsPreference(Base):
    """User's saving preferences and safety wallet target."""
    __tablename__ = "savings_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    safety_target = Column(Float, default=10000.0)  # target balance for Safety Wallet
    save_at_pay_enabled = Column(Boolean, default=True)
    preferred_save_mode = Column(String(50), default="suggested")  # suggested, fixed, off

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="savings_preferences")

    def __repr__(self):
        return f"<SavingsPreference user_id={self.user_id} target={self.safety_target}>"


class SavingsTransaction(Base):
    """Records of Save-at-Pay contributions to Safety Wallet."""
    __tablename__ = "savings_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    source_expense_id = Column(Integer, ForeignKey("expense_transactions.id"), nullable=True)
    transaction_type = Column(String(50), default="save_at_pay")  # save_at_pay, withdrawal, deposit
    category_context = Column(String(100), nullable=True)  # which category triggered the save
    save_percentage_applied = Column(Float, nullable=True)
    balance_before = Column(Float, nullable=True)
    balance_after = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    user = relationship("User", back_populates="savings_transactions")

    def __repr__(self):
        return f"<SavingsTransaction id={self.id} amount={self.amount} type={self.transaction_type}>"
