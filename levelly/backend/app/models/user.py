"""
LEVELLY — User Model
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, nullable=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="user", nullable=False)
    is_active = Column(Boolean, default=True)
    occupation = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    platform_tenure_months = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))
    onboarding_complete = Column(Boolean, default=False)
    income_frequency = Column(String(50), default="monthly")  # daily, weekly, monthly

    # Relationships
    wallets = relationship("Wallet", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    income_transactions = relationship("IncomeTransaction", back_populates="user", cascade="all, delete-orphan")
    expense_transactions = relationship("ExpenseTransaction", back_populates="user", cascade="all, delete-orphan")
    savings_preferences = relationship("SavingsPreference", back_populates="user", cascade="all, delete-orphan")
    savings_transactions = relationship("SavingsTransaction", back_populates="user", cascade="all, delete-orphan")
    financial_profile = relationship("FinancialProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    score_history = relationship("FinancialScoreHistory", back_populates="user", cascade="all, delete-orphan")
    distress_events = relationship("DistressEvent", back_populates="user", cascade="all, delete-orphan")
    credit_requests = relationship("CreditRequest", back_populates="user", cascade="all, delete-orphan")
    investment_suggestions = relationship("InvestmentSuggestion", back_populates="user", cascade="all, delete-orphan")
    investment_consents = relationship("InvestmentConsent", back_populates="user", cascade="all, delete-orphan")
    investment_orders = relationship("InvestmentOrder", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    coach_conversations = relationship("CoachConversation", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User id={self.id} email={self.email}>"
