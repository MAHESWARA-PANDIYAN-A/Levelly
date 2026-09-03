"""
LEVELLY — Responsible Lending Guardrail Service

CRITICAL: Never use "loan rejected" language.
UI language: "Credit temporarily held" or "Let's protect your financial buffer first."

This service is the final check before any credit recommendation goes to a partner.
"""
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.models.financial_profile import FinancialProfile


class ResponsibleLendingGuardrailService:
    """
    Applies responsible lending rules based on distress level.
    
    Rules:
    - LOW distress: Normal credit recommendation
    - MODERATE: Reduce/cap recommendation
    - HIGH: Reduce strongly or temporarily hold
    - SEVERE: Hold and prioritize financial guidance
    
    The final lending decision belongs to the regulated partner.
    """

    def __init__(self, db: Session):
        self.db = db

    def evaluate(
        self,
        user_id: int,
        requested_amount: float,
        recommended_amount: float,
    ) -> Dict[str, Any]:
        """
        Evaluate whether credit should proceed, be reduced, or be held.
        Returns guardrail decision with reason codes.
        """
        profile = (
            self.db.query(FinancialProfile)
            .filter(FinancialProfile.user_id == user_id)
            .first()
        )

        if not profile:
            return self._allow_response(recommended_amount)

        distress_level = profile.distress_level
        signals = profile.distress_signals or []

        if distress_level == "LOW":
            return self._allow_response(recommended_amount)

        elif distress_level == "MODERATE":
            # Reduce to 70% of recommendation, cap at 75% of requested
            reduced = min(recommended_amount * 0.70, requested_amount * 0.75)
            reason_codes = self._get_reason_codes(signals)
            return {
                "status": "reduced",
                "allowed_amount": round(reduced, 2),
                "original_recommended": recommended_amount,
                "reason_codes": reason_codes,
                "message": "Your credit limit has been adjusted based on recent financial activity.",
                "ui_message": "Credit adjusted to protect your financial health.",
                "distress_level": distress_level,
                "guidance": "Building your Safety Wallet may improve future credit recommendations.",
            }

        elif distress_level == "HIGH":
            reason_codes = self._get_reason_codes(signals)
            # May still allow a very small amount if signals are partial
            if "expenses_exceed_income" in signals or "safety_buffer_critical" in signals:
                return self._hold_response(distress_level, reason_codes)
            else:
                # Allow a small amount
                small_amount = min(recommended_amount * 0.40, requested_amount * 0.40, 3000)
                return {
                    "status": "reduced",
                    "allowed_amount": round(small_amount, 2),
                    "original_recommended": recommended_amount,
                    "reason_codes": reason_codes,
                    "message": "Credit temporarily reduced due to financial pressure.",
                    "ui_message": "Let's protect your financial buffer first.",
                    "distress_level": distress_level,
                    "guidance": "Your recent earnings have declined. LEVELLY recommends focusing on rebuilding your Safety Wallet.",
                }

        else:  # SEVERE
            reason_codes = self._get_reason_codes(signals)
            return self._hold_response(distress_level, reason_codes)

    def _allow_response(self, amount: float) -> Dict[str, Any]:
        return {
            "status": "allowed",
            "allowed_amount": round(amount, 2),
            "original_recommended": amount,
            "reason_codes": [],
            "message": "Credit recommendation approved.",
            "ui_message": "Credit available based on your financial profile.",
            "distress_level": "LOW",
            "guidance": None,
        }

    def _hold_response(self, distress_level: str, reason_codes: List[str]) -> Dict[str, Any]:
        return {
            "status": "held",
            "allowed_amount": 0.0,
            "original_recommended": 0.0,
            "reason_codes": reason_codes,
            "message": "Credit recommendation temporarily held.",
            "ui_message": "Credit temporarily held — let's focus on your financial stability first.",
            "distress_level": distress_level,
            "guidance": (
                "Your recent income has declined significantly. "
                "LEVELLY recommends keeping your funds liquid and rebuilding your Safety Wallet. "
                "Speak with Levelly Coach for personalized guidance."
            ),
        }

    def _get_reason_codes(self, signals: List[str]) -> List[str]:
        """Map distress signals to user-friendly reason codes."""
        code_map = {
            "income_decline": "income_decline",
            "significant_income_decline": "income_decline",
            "sustained_low_income": "sustained_income_pressure",
            "expense_pressure": "expense_pressure",
            "expenses_exceed_income": "expense_pressure",
            "safety_buffer_depleting": "low_safety_buffer",
            "safety_buffer_critical": "low_safety_buffer",
            "credit_pressure": "existing_credit_pressure",
        }
        codes = list(set(code_map.get(s, s) for s in signals if s in code_map))
        return codes
