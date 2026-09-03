"""
LEVELLY — Savings Engine
Handles Save-at-Pay logic with category-based percentages
adjusted by financial intelligence layer.
"""
from typing import Dict, Optional
from sqlalchemy.orm import Session

from app.models.savings import CategorySavingPolicy
from app.models.financial_profile import FinancialProfile


# Default fallback percentages if DB policy not found
DEFAULT_CATEGORY_PERCENTAGES = {
    "food": 10.0,
    "fuel": 5.0,
    "education": 8.0,
    "entertainment": 5.0,
    "shopping": 10.0,
    "family": 5.0,
    "healthcare": 5.0,
    "rent": 0.0,    # Rent is typically fixed, no save suggestion
    "bills": 0.0,   # Bills are fixed
    "other": 5.0,
}


class SavingsEngine:
    """
    Calculates save-at-pay suggestions.
    
    Base percentage comes from CategorySavingPolicy (admin-configurable).
    Effective percentage is adjusted by financial intelligence (distress level).
    """

    def __init__(self, db: Session):
        self.db = db

    def get_category_base_percentage(self, category: str) -> float:
        """Get the base saving percentage for a category from DB policy."""
        policy = (
            self.db.query(CategorySavingPolicy)
            .filter(
                CategorySavingPolicy.category == category.lower(),
                CategorySavingPolicy.is_active == True,
            )
            .first()
        )

        if policy:
            return policy.base_percentage

        return DEFAULT_CATEGORY_PERCENTAGES.get(category.lower(), 5.0)

    def get_effective_percentage(
        self, category: str, distress_level: str, user_id: int
    ) -> float:
        """
        Calculate effective save percentage based on distress level.
        
        HEALTHY: full base percentage
        MODERATE: reduced by 50%
        HIGH: reduced to minimum (capped at 5%)
        SEVERE: 0% (no savings suggestion when in crisis)
        """
        base = self.get_category_base_percentage(category)

        # Get policy limits
        policy = (
            self.db.query(CategorySavingPolicy)
            .filter(CategorySavingPolicy.category == category.lower())
            .first()
        )
        min_pct = policy.min_percentage if policy else 0.0

        if distress_level == "LOW":
            effective = base
        elif distress_level == "MODERATE":
            effective = max(min_pct, base * 0.5)
        elif distress_level == "HIGH":
            effective = max(min_pct, min(base * 0.25, 5.0))
        else:  # SEVERE
            effective = 0.0

        return round(effective, 1)

    def calculate_save_suggestion(
        self,
        amount: float,
        category: str,
        user_id: int,
        distress_level: str = "LOW",
    ) -> Dict:
        """
        Calculate the save-at-pay suggestion for a payment.
        Returns the suggestion, never forces saving.
        """
        effective_pct = self.get_effective_percentage(category, distress_level, user_id)
        suggested_save = round((amount * effective_pct) / 100, 2)

        return {
            "payment_amount": amount,
            "category": category.lower(),
            "suggested_percentage": effective_pct,
            "suggested_save_amount": suggested_save,
            "distress_level_applied": distress_level,
            "save_suggestion_available": suggested_save > 0,
        }
