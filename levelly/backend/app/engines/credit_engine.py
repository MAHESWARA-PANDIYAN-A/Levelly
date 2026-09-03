"""
LEVELLY — Credit Recommendation Service
Generates credit recommendations based on financial profile.
Final lending decision belongs to the regulated partner.
"""
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models.financial_profile import FinancialProfile
from app.models.user import User


class CreditRecommendationService:
    """
    Factors considered:
    - Income consistency (volatility)
    - Platform tenure
    - Savings behavior (safety wallet progress)
    - Recent income vs historical
    - Expense pressure
    - Financial resilience score
    - Distress level
    """

    def __init__(self, db: Session):
        self.db = db
        self.MAX_CREDIT = 25000  # demo cap
        self.BASE_MULTIPLIER = 1.5  # monthly income multiplier

    def generate_recommendation(
        self, user_id: int, requested_amount: float
    ) -> Dict[str, Any]:
        """Generate a credit recommendation for the user."""
        user = self.db.query(User).filter(User.id == user_id).first()
        profile = (
            self.db.query(FinancialProfile)
            .filter(FinancialProfile.user_id == user_id)
            .first()
        )

        if not profile or not user:
            return {
                "requested_amount": requested_amount,
                "recommended_amount": 0.0,
                "status": "insufficient_data",
                "reasons": ["Insufficient financial history to make a recommendation"],
                "max_eligible": 0.0,
            }

        # Base eligibility from recent income
        base_eligible = profile.recent_income * self.BASE_MULTIPLIER

        # Score adjustments
        adjustments = []

        # Income stability
        if profile.income_volatility_level == "LOW":
            stability_multiplier = 1.10
            adjustments.append("Consistent income improves eligibility")
        elif profile.income_volatility_level == "MODERATE":
            stability_multiplier = 0.90
        else:
            stability_multiplier = 0.70
            adjustments.append("Income variability reduces eligibility")

        # Platform tenure
        tenure = user.platform_tenure_months or 0
        if tenure >= 24:
            tenure_multiplier = 1.15
            adjustments.append("Long platform tenure improves eligibility")
        elif tenure >= 12:
            tenure_multiplier = 1.05
        elif tenure >= 6:
            tenure_multiplier = 0.95
        else:
            tenure_multiplier = 0.80
            adjustments.append("Limited platform history reduces eligibility")

        # Savings behavior
        safety_pct = profile.safety_surplus  # can be negative if below target
        if safety_pct > 0:
            savings_multiplier = 1.10
            adjustments.append("Safety Wallet above target improves eligibility")
        elif profile.resilience_score >= 60:
            savings_multiplier = 1.0
        else:
            savings_multiplier = 0.85
            adjustments.append("Building Safety Wallet will improve eligibility")

        # Distress penalty
        distress_multipliers = {
            "LOW": 1.0,
            "MODERATE": 0.75,
            "HIGH": 0.40,
            "SEVERE": 0.0,
        }
        distress_multiplier = distress_multipliers.get(profile.distress_level, 1.0)

        if profile.distress_level in ("HIGH", "SEVERE"):
            adjustments.append("Financial pressure currently limits credit recommendation")

        # Expense pressure
        if profile.expense_to_income_ratio > 0.85:
            expense_multiplier = 0.80
            adjustments.append("High expense ratio reduces recommendation")
        else:
            expense_multiplier = 1.0

        # Calculate recommended amount
        recommended = (
            base_eligible
            * stability_multiplier
            * tenure_multiplier
            * savings_multiplier
            * distress_multiplier
            * expense_multiplier
        )
        recommended = min(recommended, self.MAX_CREDIT)
        recommended = max(0, round(recommended, -2))  # round to nearest 100

        # Status
        if recommended <= 0:
            status = "held"
        elif recommended >= requested_amount:
            status = "approved"
        elif recommended >= requested_amount * 0.5:
            status = "reduced"
        else:
            status = "significantly_reduced"

        return {
            "requested_amount": requested_amount,
            "recommended_amount": recommended,
            "max_eligible": min(recommended, self.MAX_CREDIT),
            "status": status,
            "reasons": adjustments,
            "distress_level": profile.distress_level,
            "resilience_score": profile.resilience_score,
            "income_basis": profile.recent_income,
        }
