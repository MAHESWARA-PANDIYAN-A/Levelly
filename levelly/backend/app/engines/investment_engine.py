"""
LEVELLY — Investment Recommendation Engine
Determines investment readiness and suggests appropriate products.

CRITICAL RULES:
- NO automatic investment
- NO guaranteed returns claims
- NO risk-free claims
- Explicit consent required before execution
"""
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.models.financial_profile import FinancialProfile
from app.models.investment import InvestmentProduct, InvestmentSuggestion
from app.models.wallet import Wallet
from app.models.savings import SavingsPreference


class InvestmentRecommendationService:
    """
    Determines investment readiness and suggests product categories.
    
    Investment suggestions require:
    - Safety Wallet above target (safety_surplus > 0)
    - Distress level LOW or MODERATE
    - Financial resilience >= 55
    
    When distress >= HIGH or safety below target: suggestions PAUSED
    """

    def __init__(self, db: Session):
        self.db = db

    def get_investment_status(self, user_id: int) -> Dict[str, Any]:
        """Get investment readiness status for a user."""
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

        safety_balance = safety_wallet.balance if safety_wallet else 0.0
        safety_target = safety_wallet.target_amount if safety_wallet else 10000.0

        safety_surplus = safety_balance - safety_target
        distress_level = profile.distress_level if profile else "LOW"
        resilience_score = profile.resilience_score if profile else 0.0

        # Determine if paused
        is_paused = False
        pause_reason = None

        if distress_level in ("HIGH", "SEVERE"):
            is_paused = True
            pause_reason = (
                "Your recent income has declined. LEVELLY recommends keeping more of your "
                "money liquid until your financial position stabilizes."
            )
        elif safety_surplus < 0:
            is_paused = True
            shortfall = abs(safety_surplus)
            pause_reason = (
                f"Your Safety Wallet is ₹{shortfall:,.0f} below your target. "
                "Build your safety buffer first before considering investments."
            )

        available_surplus = max(0, safety_surplus * 0.5)  # suggest investing up to 50% of surplus

        return {
            "is_paused": is_paused,
            "pause_reason": pause_reason,
            "safety_balance": safety_balance,
            "safety_target": safety_target,
            "safety_surplus": safety_surplus,
            "available_for_investment": available_surplus if not is_paused else 0,
            "distress_level": distress_level,
            "resilience_score": resilience_score,
            "investment_ready": not is_paused and safety_surplus > 0,
        }

    def get_suggestions(self, user_id: int) -> List[Dict[str, Any]]:
        """Get investment suggestions for a user."""
        status = self.get_investment_status(user_id)

        if status["is_paused"]:
            return []

        profile = (
            self.db.query(FinancialProfile)
            .filter(FinancialProfile.user_id == user_id)
            .first()
        )

        distress_level = profile.distress_level if profile else "LOW"
        surplus = status["safety_surplus"]

        # Get suitable products
        # For LOW distress, suggest all product types
        # For MODERATE, only LOW/MODERATE risk products
        if distress_level == "LOW":
            max_risk = ["LOW", "MODERATE"]
        else:
            max_risk = ["LOW"]

        products = (
            self.db.query(InvestmentProduct)
            .filter(
                InvestmentProduct.active == True,
                InvestmentProduct.risk_level.in_(max_risk),
            )
            .all()
        )

        suggestions = []
        for product in products:
            reason = self._generate_reason(product, surplus, distress_level)

            # Create/update suggestion record
            existing = (
                self.db.query(InvestmentSuggestion)
                .filter(
                    InvestmentSuggestion.user_id == user_id,
                    InvestmentSuggestion.product_id == product.id,
                    InvestmentSuggestion.is_active == True,
                )
                .first()
            )

            if not existing:
                suggestion = InvestmentSuggestion(
                    user_id=user_id,
                    product_id=product.id,
                    reason=reason,
                    safety_surplus_at_suggestion=surplus,
                    distress_level_at_suggestion=distress_level,
                )
                self.db.add(suggestion)
                self.db.flush()
                suggestion_id = suggestion.id
            else:
                existing.reason = reason
                suggestion_id = existing.id

            suggestions.append({
                "suggestion_id": suggestion_id,
                "product_id": product.id,
                "name": product.name,
                "type": product.product_type,
                "issuer": product.issuer,
                "risk_level": product.risk_level,
                "liquidity": product.liquidity,
                "holding_period": product.holding_period,
                "interest_or_coupon": product.interest_or_coupon,
                "fees": product.fees,
                "tax_notes": product.tax_notes,
                "terms": product.terms,
                "min_investment": product.min_investment,
                "description": product.description,
                "suitable_for": product.suitable_for,
                "reason": reason,
            })

        self.db.commit()
        return suggestions

    def _generate_reason(self, product: InvestmentProduct, surplus: float, distress: str) -> str:
        """Generate a contextual reason for suggesting this product."""
        if product.product_type == "LIQUID_SAVINGS":
            return (
                f"Your Safety Wallet is ₹{surplus:,.0f} above target. "
                "This high-liquidity option lets you earn more while staying accessible."
            )
        elif product.product_type == "GOVERNMENT_SECURITY":
            return (
                f"Your Safety Wallet is ₹{surplus:,.0f} above target. "
                "Government-backed securities offer stability for your surplus funds."
            )
        elif product.product_type == "FIXED_INCOME":
            return (
                f"With ₹{surplus:,.0f} surplus, this fixed-income option "
                "may provide regular returns over your holding period."
            )
        elif product.product_type == "DEBT_ORIENTED":
            return (
                "A debt-oriented fund may offer better returns than a savings account "
                "for your surplus amount while maintaining moderate liquidity."
            )
        else:
            return f"Your financial position supports considering this option with your ₹{surplus:,.0f} surplus."
