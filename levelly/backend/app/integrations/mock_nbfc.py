"""
LEVELLY — Partner Credit Provider Interface
Abstract adapter for NBFC integration.
Local mock provided for development. Real partners implement the same interface.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import uuid


class PartnerCreditProvider(ABC):
    """
    Abstract interface for NBFC credit partners.
    All partners must implement this interface.
    The final credit decision belongs to the regulated partner.
    """

    @abstractmethod
    def check_eligibility(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if a user is eligible for credit."""
        pass

    @abstractmethod
    def get_offer(self, user_data: Dict[str, Any], amount: float) -> Dict[str, Any]:
        """Get a credit offer for an eligible user."""
        pass

    @abstractmethod
    def submit_application(self, user_data: Dict[str, Any], offer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a credit application."""
        pass

    @abstractmethod
    def get_application_status(self, application_id: str) -> Dict[str, Any]:
        """Get the status of an application."""
        pass


class MockNBFCProvider(PartnerCreditProvider):
    """
    Mock NBFC provider for local development and testing.
    Simulates realistic partner responses.
    Partner name: 'QuickCredit NBFC' (fictional demo partner)
    """

    PARTNER_NAME = "QuickCredit NBFC"
    ANNUAL_INTEREST_RATE = 18.0  # % p.a. — demo value
    PROCESSING_FEE_RATE = 0.02  # 2% of loan amount — demo value

    def check_eligibility(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check eligibility based on LEVELLY's pre-assessment."""
        levelly_recommendation = user_data.get("levelly_recommended_amount", 0)
        guardrail_status = user_data.get("guardrail_status", "held")

        if guardrail_status == "held" or levelly_recommendation <= 0:
            return {
                "eligible": False,
                "partner": self.PARTNER_NAME,
                "reason": "Pre-assessment indicates credit is not currently available",
                "partner_reference": None,
            }

        return {
            "eligible": True,
            "partner": self.PARTNER_NAME,
            "partner_reference": f"QC-{uuid.uuid4().hex[:8].upper()}",
            "max_offer": levelly_recommendation,
        }

    def get_offer(self, user_data: Dict[str, Any], amount: float) -> Dict[str, Any]:
        """Generate a credit offer."""
        if amount <= 0:
            return {"offer_available": False, "partner": self.PARTNER_NAME}

        # EMI calculation: simple formula
        monthly_rate = self.ANNUAL_INTEREST_RATE / 12 / 100
        tenure = 6  # months
        emi = (amount * monthly_rate * (1 + monthly_rate) ** tenure) / (
            (1 + monthly_rate) ** tenure - 1
        )
        processing_fee = round(amount * self.PROCESSING_FEE_RATE, 2)

        offer_expires = datetime.now(timezone.utc) + timedelta(hours=48)

        return {
            "offer_available": True,
            "partner": self.PARTNER_NAME,
            "partner_reference": f"QC-OFFER-{uuid.uuid4().hex[:8].upper()}",
            "offered_amount": round(amount, 2),
            "annual_interest_rate": self.ANNUAL_INTEREST_RATE,
            "tenure_months": tenure,
            "emi_amount": round(emi, 2),
            "processing_fee": processing_fee,
            "total_repayment": round(emi * tenure, 2),
            "offer_expires_at": offer_expires.isoformat(),
            "terms": (
                f"This offer is from {self.PARTNER_NAME}, a registered NBFC. "
                f"Interest rate: {self.ANNUAL_INTEREST_RATE}% p.a. "
                f"Processing fee: ₹{processing_fee}. "
                "Subject to partner's credit assessment and terms."
            ),
            "disclaimer": (
                "LEVELLY is not the lender. This credit is provided by the partner NBFC "
                "subject to their terms and conditions. "
                "LEVELLY's recommendation does not guarantee partner approval."
            ),
        }

    def submit_application(self, user_data: Dict[str, Any], offer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit credit application (mock — always returns processing)."""
        app_id = f"QC-APP-{uuid.uuid4().hex[:10].upper()}"
        return {
            "application_id": app_id,
            "status": "processing",
            "partner": self.PARTNER_NAME,
            "partner_reference": offer_data.get("partner_reference", ""),
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "estimated_decision_time": "24-48 hours",
            "message": "Application submitted. You will be notified when a decision is made.",
        }

    def get_application_status(self, application_id: str) -> Dict[str, Any]:
        """Get application status (mock — returns processing)."""
        return {
            "application_id": application_id,
            "status": "processing",
            "partner": self.PARTNER_NAME,
            "message": "Your application is under review.",
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }


def get_credit_provider(provider_name: str = "mock") -> PartnerCreditProvider:
    """Factory function to get the configured credit provider."""
    if provider_name == "mock":
        return MockNBFCProvider()
    # Add real provider cases here when going to production
    raise ValueError(f"Unknown credit provider: {provider_name}")
