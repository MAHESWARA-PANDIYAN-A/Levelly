"""
LEVELLY — Investment Execution Provider Interface
Abstract adapter for investment partner integration.
MockInvestmentProvider used for local development.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime, timezone
import uuid


class InvestmentExecutionProvider(ABC):
    """
    Abstract interface for investment execution partners.
    Real regulated partners implement this interface.
    """

    @abstractmethod
    def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an investment order after explicit user consent."""
        pass

    @abstractmethod
    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get the status of an investment order."""
        pass


class MockInvestmentProvider(InvestmentExecutionProvider):
    """
    Mock investment execution provider for development.
    Simulates realistic investment partner responses.
    """

    PARTNER_NAME = "GrowSafe Securities"  # fictional demo partner

    def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a mock investment order (requires prior consent)."""
        order_id = f"GS-{uuid.uuid4().hex[:10].upper()}"

        return {
            "order_id": order_id,
            "partner": self.PARTNER_NAME,
            "status": "processing",
            "product_name": order_data.get("product_name"),
            "amount": order_data.get("amount"),
            "currency": "INR",
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "estimated_settlement": "T+1 business day",
            "message": (
                "Your investment request has been received. "
                "Settlement typically completes within 1 business day."
            ),
            "disclaimer": (
                "Investments are subject to market risks. "
                "LEVELLY facilitates the connection to the investment partner. "
                "Past performance does not indicate future returns."
            ),
            "consent_id": order_data.get("consent_id"),
        }

    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get investment order status (mock — returns processing)."""
        return {
            "order_id": order_id,
            "partner": self.PARTNER_NAME,
            "status": "processing",
            "message": "Your investment order is being processed.",
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }


def get_investment_provider(provider_name: str = "mock") -> InvestmentExecutionProvider:
    """Factory function to get the configured investment provider."""
    if provider_name == "mock":
        return MockInvestmentProvider()
    raise ValueError(f"Unknown investment provider: {provider_name}")
