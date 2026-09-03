"""
LEVELLY — Payment & Merchant Models
Implements direct Bank/UPI linked account, payment transactions,
merchant registry, QR payment sessions, and provider event logs.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class LinkedPaymentAccount(Base):
    """
    User's linked Bank or UPI payment account.
    Security: NEVER store UPI PIN, bank password, ATM PIN, or OTP.
    """
    __tablename__ = "linked_payment_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    provider = Column(String(50), default="upi")  # upi, netbanking, mock
    upi_id = Column(String(100), nullable=False)  # e.g., "arjun@upi"
    bank_name = Column(String(100), default="HDFC Bank")
    account_mask = Column(String(20), default="****4821")
    account_holder_name = Column(String(100), default="Arjun Kumar")
    status = Column(String(30), default="connected")  # connected, pending, inactive
    is_primary = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="linked_payment_accounts")

    def __repr__(self):
        return f"<LinkedPaymentAccount id={self.id} upi_id={self.upi_id} status={self.status}>"


class Merchant(Base):
    """
    Predefined and verified merchant records for QR scanning and payments.
    """
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, index=True)
    merchant_code = Column(String(50), unique=True, nullable=False, index=True)  # e.g. "M001"
    name = Column(String(200), nullable=False)
    upi_id = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)  # Food & Grocery, Vehicle Repair, Fuel, etc.
    normalized_category = Column(String(50), default="food")  # food, vehicle, fuel, healthcare, etc.
    provider_reference = Column(String(100), nullable=True)
    verification_status = Column(String(50), default="verified")  # verified, unverified
    logo_url = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Merchant id={self.id} name={self.name} category={self.category}>"


class PaymentTransaction(Base):
    """
    Direct Bank/UPI Payment transaction record.
    Separates merchant payment from optional Save-at-Pay contribution.
    """
    __tablename__ = "payment_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=True, index=True)
    merchant_name = Column(String(200), nullable=False)
    merchant_upi_id = Column(String(100), nullable=False)

    amount = Column(Float, nullable=False)  # Merchant payment amount
    currency = Column(String(10), default="INR")
    category = Column(String(50), nullable=False)  # normalized category: food, fuel, vehicle, etc.

    # Smart Save-at-Pay details
    save_consent = Column(Boolean, default=False)
    suggested_percentage = Column(Float, default=0.0)
    suggested_save_amount = Column(Float, default=0.0)
    actual_save_amount = Column(Float, default=0.0)  # Added to safety wallet on payment success
    savings_credited = Column(Boolean, default=False)  # Idempotency guard

    # Provider & status
    provider = Column(String(50), default="mock")  # mock, production, razorpay, setu
    provider_transaction_id = Column(String(150), nullable=True, unique=True, index=True)
    idempotency_key = Column(String(150), nullable=True, unique=True, index=True)
    status = Column(String(30), default="PENDING")  # CREATED, PENDING, SUCCESS, FAILED, CANCELLED, REFUNDED

    extra_metadata = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="payment_transactions")
    merchant = relationship("Merchant")

    @property
    def total_cash_impact(self) -> float:
        """Total cash debited from linked bank/UPI."""
        return self.amount + (self.actual_save_amount if self.save_consent else 0.0)

    def __repr__(self):
        return f"<PaymentTransaction id={self.id} amount={self.amount} status={self.status}>"


class QRPaymentSession(Base):
    """
    Temporary QR session parsed from scanned QR payloads.
    """
    __tablename__ = "qr_payment_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    qr_payload = Column(Text, nullable=False)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=True)
    status = Column(String(30), default="active")  # active, completed, expired

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=True)

    merchant = relationship("Merchant")

    def __repr__(self):
        return f"<QRPaymentSession id={self.id} status={self.status}>"


class PaymentProviderEvent(Base):
    """
    Audit log of inbound payment provider callbacks/webhooks.
    Ensures idempotency and regulatory auditability.
    """
    __tablename__ = "payment_provider_events"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(50), nullable=False)
    event_type = Column(String(100), nullable=False)
    provider_event_id = Column(String(150), unique=True, index=True)
    payload = Column(JSON, nullable=True)
    status = Column(String(30), default="processed")  # received, processed, ignored, error

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<PaymentProviderEvent id={self.id} type={self.event_type}>"
