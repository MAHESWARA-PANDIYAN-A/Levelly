"""
LEVELLY — Transaction Models
Base transaction, income transactions, and expense transactions
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Transaction(Base):
    """Base transaction record for all money movements."""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    transaction_type = Column(String(50), nullable=False)  # income, expense, savings, transfer
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(30), default="completed")  # pending, completed, failed, reversed
    reference_id = Column(String(100), nullable=True)  # external reference
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=True)
    save_consent = Column(Boolean, nullable=True)  # for payment transactions

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction id={self.id} type={self.transaction_type} amount={self.amount}>"


class IncomeTransaction(Base):
    """Income-specific transaction (payout from gig platform)."""
    __tablename__ = "income_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    source = Column(String(100), nullable=True)  # e.g., "Swiggy", "Zomato"
    income_type = Column(String(50), default="payout")  # payout, bonus, tip
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(30), default="completed")
    transaction_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="income_transactions")

    def __repr__(self):
        return f"<IncomeTransaction id={self.id} amount={self.amount}>"


class ExpenseTransaction(Base):
    """Expense-specific transaction."""
    __tablename__ = "expense_transactions"

    # Expense categories
    ESSENTIAL_CATEGORIES = {"food", "fuel", "rent", "bills", "healthcare", "education", "family"}
    NON_ESSENTIAL_CATEGORIES = {"entertainment", "shopping", "other"}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    category = Column(String(100), nullable=False)  # food, fuel, rent, bills, etc.
    description = Column(Text, nullable=True)
    merchant = Column(String(255), nullable=True)
    is_large_expense = Column(Boolean, default=False)  # triggered large expense flow
    savings_added = Column(Float, default=0.0)  # amount added to safety wallet via save-at-pay
    save_consent = Column(Boolean, nullable=True)  # whether user consented to save-at-pay
    transaction_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    status = Column(String(30), default="completed")

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="expense_transactions")

    @property
    def is_essential(self) -> bool:
        return self.category.lower() in self.ESSENTIAL_CATEGORIES

    def __repr__(self):
        return f"<ExpenseTransaction id={self.id} category={self.category} amount={self.amount}>"
