"""
LEVELLY — Distress Engine
Detects financial distress using multiple signals.
Uses sustained distress logic — NOT triggered by one bad day.

IMPORTANT: These are product/demo thresholds, not regulatory standards.
"""
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from app.models.financial_profile import FinancialProfile
from app.models.distress import DistressEvent
from app.models.wallet import Wallet
from app.core.config import settings


class DistressEngine:
    """
    Evaluates financial distress using:
    - Income decline
    - Expense pressure (expense ratio)
    - Safety Wallet depletion
    - Credit pressure
    - Financial resilience score
    - Consecutive low periods (sustained distress)
    
    Output levels: LOW, MODERATE, HIGH, SEVERE
    """

    def __init__(self, db: Session):
        self.db = db

    def evaluate(self, user_id: int) -> Dict[str, Any]:
        """Run full distress evaluation for a user."""
        profile = (
            self.db.query(FinancialProfile)
            .filter(FinancialProfile.user_id == user_id)
            .first()
        )

        if not profile:
            return self._default_response(user_id)

        # Get safety wallet
        safety_wallet = (
            self.db.query(Wallet)
            .filter(
                Wallet.user_id == user_id,
                Wallet.wallet_type == "SAFETY",
                Wallet.is_active == True,
            )
            .first()
        )

        safety_balance = safety_wallet.balance if safety_wallet else 0.0
        safety_target = safety_wallet.target_amount if safety_wallet else 10000.0
        safety_depletion_pct = 0.0
        if safety_target > 0:
            safety_depletion_pct = max(0.0, 1.0 - (safety_balance / safety_target))

        # Gather inputs
        income_decline_pct = profile.income_decline_pct / 100  # convert from 0-100 to 0-1
        expense_ratio = profile.expense_to_income_ratio
        resilience_score = profile.resilience_score
        credit_pressure = profile.credit_pressure
        consecutive_low = profile.consecutive_low_periods

        # Calculate component scores (0-100 each, higher = worse)
        income_score = self._score_income_decline(income_decline_pct, consecutive_low)
        expense_score = self._score_expense_ratio(expense_ratio)
        safety_score = self._score_safety_depletion(safety_depletion_pct)
        credit_score = self._score_credit_pressure(credit_pressure)
        resilience_score_inverted = max(0, 100 - resilience_score)

        # Weighted composite distress score
        distress_score = (
            income_score * 0.35
            + expense_score * 0.25
            + safety_score * 0.20
            + credit_score * 0.10
            + resilience_score_inverted * 0.10
        )
        distress_score = round(min(100, max(0, distress_score)), 1)

        # Determine level using configurable thresholds
        distress_level = self._classify_distress(distress_score)

        # Generate signals
        signals = self._generate_signals(
            income_decline_pct, expense_ratio, safety_depletion_pct,
            credit_pressure, consecutive_low
        )

        # Recommended action
        recommended_action = self._get_recommended_action(distress_level)

        # Is this sustained?
        is_sustained = consecutive_low >= 2

        # Record event
        event = DistressEvent(
            user_id=user_id,
            distress_score=distress_score,
            distress_level=distress_level,
            income_decline_pct=income_decline_pct * 100,
            expense_ratio=expense_ratio,
            safety_depletion_pct=safety_depletion_pct * 100,
            credit_pressure=credit_pressure,
            resilience_score=resilience_score,
            consecutive_low_periods=consecutive_low,
            signals=signals,
            recommended_action=recommended_action,
            is_sustained=is_sustained,
        )
        self.db.add(event)

        # Update profile
        profile.distress_score = distress_score
        profile.distress_level = distress_level
        profile.distress_signals = signals

        self.db.commit()

        return {
            "distress_score": distress_score,
            "distress_level": distress_level,
            "signals": signals,
            "recommended_action": recommended_action,
            "is_sustained": is_sustained,
            "consecutive_low_periods": consecutive_low,
            "component_scores": {
                "income": round(income_score, 1),
                "expense": round(expense_score, 1),
                "safety": round(safety_score, 1),
                "credit": round(credit_score, 1),
            },
        }

    def _score_income_decline(self, decline_pct: float, consecutive_low: int) -> float:
        """Score income decline (0-100). Amplified by consecutive low periods."""
        base_score = min(100, decline_pct * 150)  # 67% decline = 100 score

        # Sustained distress amplification
        if consecutive_low >= 4:
            amplifier = 1.5
        elif consecutive_low >= 2:
            amplifier = 1.2
        else:
            amplifier = 1.0

        return min(100, base_score * amplifier)

    def _score_expense_ratio(self, expense_ratio: float) -> float:
        """Score expense-to-income ratio (0-100). Ratio > 1 = maximum pressure."""
        if expense_ratio >= 1.0:
            return 100.0
        return min(100, expense_ratio * 120)

    def _score_safety_depletion(self, depletion_pct: float) -> float:
        """Score safety wallet depletion (0-100)."""
        return min(100, depletion_pct * 100)

    def _score_credit_pressure(self, credit_pressure: float) -> float:
        """Score credit pressure (already 0-100)."""
        return min(100, max(0, credit_pressure))

    def _classify_distress(self, score: float) -> str:
        """Classify distress score into levels."""
        if score <= settings.DISTRESS_LOW_MAX:
            return "LOW"
        elif score <= settings.DISTRESS_MODERATE_MAX:
            return "MODERATE"
        elif score <= settings.DISTRESS_HIGH_MAX:
            return "HIGH"
        else:
            return "SEVERE"

    def _generate_signals(
        self,
        income_decline: float,
        expense_ratio: float,
        safety_depletion: float,
        credit_pressure: float,
        consecutive_low: int,
    ) -> List[str]:
        """Generate human-readable signals for the distress state."""
        signals = []

        if income_decline > 0.20:
            signals.append("income_decline")
        if income_decline > 0.35:
            signals.append("significant_income_decline")
        if consecutive_low >= 2:
            signals.append("sustained_low_income")
        if expense_ratio > 0.80:
            signals.append("expense_pressure")
        if expense_ratio > 1.0:
            signals.append("expenses_exceed_income")
        if safety_depletion > 0.30:
            signals.append("safety_buffer_depleting")
        if safety_depletion > 0.70:
            signals.append("safety_buffer_critical")
        if credit_pressure > 60:
            signals.append("credit_pressure")

        return signals

    def _get_recommended_action(self, distress_level: str) -> str:
        """Get the system-recommended action for a distress level."""
        actions = {
            "LOW": "continue_normal",
            "MODERATE": "increase_savings_priority",
            "HIGH": "pause_non_essential_spending",
            "SEVERE": "urgent_financial_guidance",
        }
        return actions.get(distress_level, "continue_normal")

    def _default_response(self, user_id: int) -> Dict[str, Any]:
        """Return default LOW distress when no profile exists."""
        return {
            "distress_score": 0.0,
            "distress_level": "LOW",
            "signals": [],
            "recommended_action": "continue_normal",
            "is_sustained": False,
            "consecutive_low_periods": 0,
            "component_scores": {"income": 0, "expense": 0, "safety": 0, "credit": 0},
        }
