"""
LEVELLY — Financial Profile Models
Stores computed financial intelligence data per user
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class FinancialProfile(Base):
    """
    Core financial intelligence profile for each user.
    Updated by IncomeIntelligenceService and other engines.
    """
    __tablename__ = "financial_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)

    # Income Intelligence
    historical_avg_income = Column(Float, default=0.0)  # long-term average
    recent_income = Column(Float, default=0.0)           # recent window (14-28 days)
    income_trend = Column(String(20), default="stable")  # rising, stable, declining
    income_decline_pct = Column(Float, default=0.0)      # % decline from historical
    income_volatility = Column(Float, default=0.0)       # coefficient of variation
    income_volatility_level = Column(String(20), default="LOW")  # LOW, MODERATE, HIGH
    consecutive_low_periods = Column(Integer, default=0)  # sustained distress tracking

    # Expense Analysis
    monthly_expenses = Column(Float, default=0.0)
    weekly_expenses = Column(Float, default=0.0)
    essential_expenses = Column(Float, default=0.0)
    non_essential_expenses = Column(Float, default=0.0)
    expense_to_income_ratio = Column(Float, default=0.0)

    # Financial Resilience Score (0-100)
    resilience_score = Column(Float, default=0.0)
    resilience_label = Column(String(30), default="stable")  # stable, pressure, at_risk

    # Distress
    distress_score = Column(Float, default=0.0)
    distress_level = Column(String(20), default="LOW")  # LOW, MODERATE, HIGH, SEVERE
    distress_signals = Column(JSON, default=list)

    # Credit
    credit_pressure = Column(Float, default=0.0)
    platform_tenure_months = Column(Integer, default=0)

    # Investment Readiness
    safety_surplus = Column(Float, default=0.0)  # safety_balance - safety_target
    investment_ready = Column(Boolean, default=False)

    # Timestamps
    last_computed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="financial_profile")

    def __repr__(self):
        return f"<FinancialProfile user_id={self.user_id} resilience={self.resilience_score}>"


class FinancialScoreHistory(Base):
    """Historical record of financial resilience scores."""
    __tablename__ = "financial_score_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    resilience_score = Column(Float, nullable=False)
    distress_score = Column(Float, nullable=False)
    distress_level = Column(String(20), nullable=False)
    income_snapshot = Column(Float, nullable=True)
    expense_snapshot = Column(Float, nullable=True)
    safety_balance_snapshot = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    computed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    user = relationship("User", back_populates="score_history")

    def __repr__(self):
        return f"<FinancialScoreHistory user_id={self.user_id} score={self.resilience_score}>"
