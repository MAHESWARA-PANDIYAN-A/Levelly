"""
LEVELLY — Investment Models
InvestmentProduct, InvestmentSuggestion, InvestmentConsent, InvestmentOrder
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base


class InvestmentProduct(Base):
    """
    Investment product catalog.
    Types: LIQUID_SAVINGS, GOVERNMENT_SECURITY, FIXED_INCOME, DEBT_ORIENTED, OTHER
    Never claim guaranteed returns or risk-free.
    """
    __tablename__ = "investment_products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    product_type = Column(String(50), nullable=False)  # LIQUID_SAVINGS, GOVERNMENT_SECURITY, etc.
    issuer = Column(String(255), nullable=True)
    risk_level = Column(String(20), nullable=False)  # LOW, MODERATE, HIGH
    liquidity = Column(String(50), nullable=True)  # High, Medium, Low, Locked
    holding_period = Column(String(100), nullable=True)  # e.g., "1 year", "No lock-in"
    interest_or_coupon = Column(String(100), nullable=True)  # e.g., "7.1% p.a."
    fees = Column(String(255), nullable=True)
    tax_notes = Column(Text, nullable=True)
    terms = Column(Text, nullable=True)
    min_investment = Column(Float, default=100.0)
    description = Column(Text, nullable=True)
    suitable_for = Column(Text, nullable=True)  # who it's suitable for
    active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<InvestmentProduct id={self.id} name={self.name} type={self.product_type}>"


class InvestmentSuggestion(Base):
    """Investment suggestion generated for a user by the recommendation engine."""
    __tablename__ = "investment_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("investment_products.id"), nullable=False)
    reason = Column(Text, nullable=True)
    safety_surplus_at_suggestion = Column(Float, nullable=True)
    distress_level_at_suggestion = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    user = relationship("User", back_populates="investment_suggestions")
    product = relationship("InvestmentProduct")

    def __repr__(self):
        return f"<InvestmentSuggestion user_id={self.user_id} product_id={self.product_id}>"


class InvestmentConsent(Base):
    """
    Explicit user consent for investment execution.
    MUST be confirmed before calling partner execution.
    """
    __tablename__ = "investment_consents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("investment_products.id"), nullable=False)
    suggestion_id = Column(Integer, ForeignKey("investment_suggestions.id"), nullable=True)
    amount = Column(Float, nullable=False)
    confirmed = Column(Boolean, default=False)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    terms_version = Column(String(50), default="1.0")
    consent_metadata = Column(JSON, default=dict)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="investment_consents")
    product = relationship("InvestmentProduct")

    def __repr__(self):
        return f"<InvestmentConsent id={self.id} confirmed={self.confirmed} amount={self.amount}>"


class InvestmentOrder(Base):
    """Investment order sent to partner after confirmed consent."""
    __tablename__ = "investment_orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    consent_id = Column(Integer, ForeignKey("investment_consents.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("investment_products.id"), nullable=False)
    amount = Column(Float, nullable=False)

    # Partner order details
    partner_order_id = Column(String(100), nullable=True)  # partner's reference
    partner_name = Column(String(100), nullable=True)
    order_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    partner_response = Column(JSON, default=dict)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="investment_orders")
    product = relationship("InvestmentProduct")
    consent = relationship("InvestmentConsent")

    def __repr__(self):
        return f"<InvestmentOrder id={self.id} amount={self.amount} status={self.order_status}>"
