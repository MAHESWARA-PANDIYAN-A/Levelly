"""
LEVELLY — Financial Resilience Service
Calculates the LEVELLY Financial Resilience Score (0-100).

IMPORTANT: This is NOT a CIBIL score, credit score, or government score.
It is LEVELLY's internal measure of financial health and preparedness.
"""
from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models.financial_profile import FinancialProfile, FinancialScoreHistory
from app.models.wallet import Wallet
from app.models.savings import SavingsPreference


class FinancialResilienceService:
    """
    Calculates LEVELLY Financial Resilience Score from:
    - Income stability (30%)
    - Savings progress (25%)
    - Expense control (20%)
    - Emergency readiness (15%)
    - Credit pressure (10%)
    
    Range: 0-100 (higher is better/healthier)
    """

    def __init__(self, db: Session):
        self.db = db

    def calculate_score(self, user_id: int) -> Dict[str, Any]:
        """Calculate and store the financial resilience score."""
        profile = (
            self.db.query(FinancialProfile)
            .filter(FinancialProfile.user_id == user_id)
            .first()
        )

        safety_wallet = (
            self.db.query(Wallet)
            .filter(
                Wallet.user_id == user_id,
                Wallet.wallet_type == "SAFETY",
                Wallet.is_active == True,
            )
            .first()
        )

        savings_pref = (
            self.db.query(SavingsPreference)
            .filter(SavingsPreference.user_id == user_id)
            .first()
        )

        safety_balance = safety_wallet.balance if safety_wallet else 0.0
        safety_target = savings_pref.safety_target if savings_pref else 10000.0
        if safety_wallet and safety_wallet.target_amount:
            safety_target = safety_wallet.target_amount

        # Component scores (0-100, higher = better)
        income_stability = self._score_income_stability(profile)
        savings_progress = self._score_savings_progress(safety_balance, safety_target)
        expense_control = self._score_expense_control(profile)
        emergency_readiness = self._score_emergency_readiness(safety_balance, safety_target)
        credit_health = self._score_credit_health(profile)

        # Weighted composite
        composite = (
            income_stability * 0.30
            + savings_progress * 0.25
            + expense_control * 0.20
            + emergency_readiness * 0.15
            + credit_health * 0.10
        )
        composite = round(min(100, max(0, composite)), 1)

        # Label
        label = self._get_label(composite)

        # Update profile
        if profile:
            profile.resilience_score = composite
            profile.resilience_label = label

            # Calculate safety surplus for investment readiness
            safety_surplus = safety_balance - safety_target
            profile.safety_surplus = safety_surplus
            profile.investment_ready = (
                safety_surplus > 0
                and profile.distress_level in ("LOW", "MODERATE")
                and composite >= 55
            )

        # Store history
        history_entry = FinancialScoreHistory(
            user_id=user_id,
            resilience_score=composite,
            distress_score=profile.distress_score if profile else 0.0,
            distress_level=profile.distress_level if profile else "LOW",
            income_snapshot=profile.recent_income if profile else 0.0,
            expense_snapshot=profile.monthly_expenses if profile else 0.0,
            safety_balance_snapshot=safety_balance,
        )
        self.db.add(history_entry)
        self.db.commit()

        return {
            "resilience_score": composite,
            "resilience_label": label,
            "components": {
                "income_stability": round(income_stability, 1),
                "savings_progress": round(savings_progress, 1),
                "expense_control": round(expense_control, 1),
                "emergency_readiness": round(emergency_readiness, 1),
                "credit_health": round(credit_health, 1),
            },
            "safety_balance": safety_balance,
            "safety_target": safety_target,
            "safety_progress_pct": round(
                min(100, (safety_balance / safety_target * 100)) if safety_target > 0 else 0, 1
            ),
        }

    def _score_income_stability(self, profile) -> float:
        """Higher income, lower volatility, lower decline = higher score."""
        if not profile:
            return 50.0

        # Income relative to historical
        if profile.historical_avg_income > 0:
            income_ratio = min(1.0, profile.recent_income / profile.historical_avg_income)
        else:
            income_ratio = 0.5

        # Volatility penalty
        volatility_penalty = {
            "LOW": 0,
            "MODERATE": 15,
            "HIGH": 30,
        }.get(profile.income_volatility_level, 0)

        # Trend bonus/penalty
        trend_adj = {
            "rising": 10,
            "stable": 0,
            "declining": -15,
        }.get(profile.income_trend, 0)

        score = (income_ratio * 100) - volatility_penalty + trend_adj
        return max(0, min(100, score))

    def _score_savings_progress(self, balance: float, target: float) -> float:
        """Progress towards safety target."""
        if target <= 0:
            return 0.0
        progress = min(1.0, balance / target)
        return progress * 100

    def _score_expense_control(self, profile) -> float:
        """Lower expense ratio = higher score."""
        if not profile:
            return 50.0
        ratio = profile.expense_to_income_ratio
        if ratio <= 0.5:
            return 100.0
        elif ratio <= 0.7:
            return 80.0
        elif ratio <= 0.85:
            return 60.0
        elif ratio <= 1.0:
            return 30.0
        else:
            return 0.0

    def _score_emergency_readiness(self, balance: float, target: float) -> float:
        """How ready is the emergency fund."""
        if target <= 0:
            return 0.0
        ratio = balance / target
        if ratio >= 1.0:
            return 100.0
        elif ratio >= 0.8:
            return 80.0
        elif ratio >= 0.5:
            return 55.0
        elif ratio >= 0.25:
            return 30.0
        else:
            return 10.0

    def _score_credit_health(self, profile) -> float:
        """Lower credit pressure = higher score."""
        if not profile:
            return 70.0
        return max(0, min(100, 100 - profile.credit_pressure))

    def _get_label(self, score: float) -> str:
        if score >= 75:
            return "stable"
        elif score >= 55:
            return "moderate"
        elif score >= 35:
            return "at_risk"
        else:
            return "critical"
