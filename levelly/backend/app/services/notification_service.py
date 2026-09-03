"""
LEVELLY — Notification Service
Creates and manages system notifications for financial events.
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.notification import Notification


class NotificationService:
    """Creates notifications for key financial events."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        title: str,
        message: str,
        notification_type: str,
        priority: str = "normal",
        action_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Notification:
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            action_url=action_url,
            metadata=metadata or {},
        )
        self.db.add(notif)
        self.db.commit()
        self.db.refresh(notif)
        return notif

    def payout_received(self, user_id: int, amount: float, source: str = "") -> Notification:
        return self.create(
            user_id=user_id,
            title="Payout Received",
            message=f"₹{amount:,.0f} has been added to your Daily Wallet{' from ' + source if source else ''}.",
            notification_type="payout_received",
            priority="normal",
            action_url="/wallets",
        )

    def payment_completed(self, user_id: int, amount: float, category: str) -> Notification:
        return self.create(
            user_id=user_id,
            title="Payment Completed",
            message=f"₹{amount:,.0f} payment for {category} recorded.",
            notification_type="payment_completed",
            action_url="/transactions",
        )

    def save_at_pay_accepted(self, user_id: int, save_amount: float) -> Notification:
        return self.create(
            user_id=user_id,
            title="Safety Wallet Updated",
            message=f"₹{save_amount:,.0f} added to your Safety Wallet via Save-at-Pay. Great job!",
            notification_type="save_at_pay_accepted",
            priority="normal",
            action_url="/wallets/safety",
        )

    def safety_wallet_milestone(self, user_id: int, progress_pct: float, balance: float) -> Notification:
        return self.create(
            user_id=user_id,
            title="Safety Wallet Milestone",
            message=f"Your Safety Wallet is now {progress_pct:.0f}% complete at ₹{balance:,.0f}.",
            notification_type="safety_wallet_updated",
            action_url="/wallets/safety",
        )

    def income_trend_changed(self, user_id: int, trend: str, decline_pct: float = 0) -> Notification:
        if trend == "declining" and decline_pct > 10:
            msg = f"Your recent earnings are {decline_pct:.0f}% below your usual range. Levelly Coach can help you plan."
            priority = "high"
        elif trend == "rising":
            msg = "Your income trend is improving. Keep building your Safety Wallet."
            priority = "normal"
        else:
            msg = "Your income is tracking normally."
            priority = "low"

        return self.create(
            user_id=user_id,
            title="Income Update",
            message=msg,
            notification_type="income_trend_changed",
            priority=priority,
            action_url="/income",
        )

    def financial_pressure_detected(self, user_id: int, distress_level: str) -> Notification:
        return self.create(
            user_id=user_id,
            title="Financial Guidance Available",
            message=(
                "LEVELLY has detected some financial pressure. "
                "Levelly Coach has personalized guidance for you."
            ),
            notification_type="financial_pressure_detected",
            priority="high",
            action_url="/coach",
        )

    def credit_recommendation_changed(self, user_id: int, status: str) -> Notification:
        if status == "held":
            msg = "Your credit recommendation has been temporarily adjusted. See details."
        elif status == "reduced":
            msg = "Your credit limit has been adjusted based on your financial profile."
        else:
            msg = "Credit is now available based on your financial profile."

        return self.create(
            user_id=user_id,
            title="Credit Update",
            message=msg,
            notification_type="credit_recommendation_changed",
            action_url="/credit",
        )

    def investment_suggestion_available(self, user_id: int) -> Notification:
        return self.create(
            user_id=user_id,
            title="Grow Your Surplus",
            message="Your Safety Wallet is above target. Investment options are now available.",
            notification_type="investment_suggestion_available",
            action_url="/grow",
        )

    def investment_status_changed(self, user_id: int, order_id: str, status: str) -> Notification:
        return self.create(
            user_id=user_id,
            title="Investment Update",
            message=f"Your investment request (Ref: {order_id}) status: {status}.",
            notification_type="investment_status_changed",
            action_url="/grow/orders",
        )
