"""
LEVELLY IncomeShield — Insurance Provider Abstraction
Separates LEVELLY financial guidance and UI from the underwriting partner.
Supports pluggable providers (Mock for development/hackathon, Licensed Insurer for production).
"""
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta

from app.core.config import settings


class InsuranceProvider(ABC):
    """
    Abstract interface for regulated insurance partners.
    Underwriting, policy issuance, trigger verification, and payouts are governed by this interface.
    """

    @abstractmethod
    def get_plans(self) -> List[Dict[str, Any]]:
        """Retrieve available insurance plans approved by the insurer."""
        pass

    @abstractmethod
    def get_policy(self, policy_number: str) -> Optional[Dict[str, Any]]:
        """Fetch underwriting status and policy schedule from insurer."""
        pass

    @abstractmethod
    def purchase_policy(
        self,
        user_id: int,
        plan_code: str,
        work_zone: str,
        consent_confirmed: bool,
    ) -> Dict[str, Any]:
        """Issue policy schedule with partner."""
        pass

    @abstractmethod
    def evaluate_trigger(
        self,
        policy_data: Dict[str, Any],
        event_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Evaluate whether the external disruption meets the parametric threshold defined in the policy.
        Never guarantees payout unless condition is confirmed REACHED.
        """
        pass

    @abstractmethod
    def get_payout_status(self, partner_payout_id: str) -> Dict[str, Any]:
        """Query settlement status from partner."""
        pass

    @abstractmethod
    def get_documents(self, policy_number: str) -> List[Dict[str, Any]]:
        """Retrieve authentic policy schedules and terms links."""
        pass


class MockInsuranceProvider(InsuranceProvider):
    """
    Mock implementation of InsuranceProvider for local development, hackathon demos, and automated testing.
    Uses realistic Indian parametric insurance parameters.
    """

    def __init__(self):
        self.partner_name = "SafeWork Protection Partner"
        self.partner_code = "SAFEWORK-INS-01"

    def get_plans(self) -> List[Dict[str, Any]]:
        return [
            {
                "code": "INCSH_BASIC",
                "name": "Basic IncomeShield",
                "description": "Essential rainy-day and heatwave protection for high-frequency gig couriers.",
                "premium": 29.0,
                "premium_frequency": "weekly",
                "coverage_limit": 2000.0,
                "policy_duration": "7 days",
                "covered_events": ["HEAVY_RAIN", "EXTREME_HEAT"],
                "trigger_conditions": {
                    "HEAVY_RAIN": "Rainfall >= 50mm over 3 consecutive hours in registered delivery zone",
                    "EXTREME_HEAT": "Temperature >= 43°C during peak working hours (11:00 AM - 4:00 PM)",
                },
                "waiting_period": "24 hours",
                "exclusions": [
                    "Disruptions outside registered delivery zone",
                    "Pre-existing government curfews before policy start",
                    "Voluntary off-duty non-working hours",
                ],
                "coverage_area_rules": {
                    "primary_zone": "Chennai Delivery Zone",
                    "supported_subzones": ["Chennai Central", "Chennai South", "Chennai North", "OMR-ECR"],
                },
                "active": True,
            },
            {
                "code": "INCSH_STANDARD",
                "name": "Standard IncomeShield",
                "description": "Comprehensive parametric protection covering heavy rain, urban flooding, and heatwaves.",
                "premium": 49.0,
                "premium_frequency": "weekly",
                "coverage_limit": 5000.0,
                "policy_duration": "7 days",
                "covered_events": ["HEAVY_RAIN", "FLOOD", "EXTREME_HEAT"],
                "trigger_conditions": {
                    "HEAVY_RAIN": "Rainfall >= 45mm over 3 consecutive hours",
                    "FLOOD": "Civic waterlogging advisory or road closure > 3 hours",
                    "EXTREME_HEAT": "Temperature >= 42°C during 11:00 AM - 4:00 PM",
                },
                "waiting_period": "24 hours",
                "exclusions": [
                    "Disruptions outside registered delivery zone",
                    "Voluntary offline status during undisrupted hours",
                ],
                "coverage_area_rules": {
                    "primary_zone": "Chennai Delivery Zone",
                    "supported_subzones": ["Chennai Central", "Chennai South", "Chennai North", "OMR-ECR", "West Chennai"],
                },
                "active": True,
            },
            {
                "code": "INCSH_PLUS",
                "name": "Plus IncomeShield",
                "description": "Full-spectrum resilience coverage with expedited claim settlement and civic disruption shield.",
                "premium": 79.0,
                "premium_frequency": "weekly",
                "coverage_limit": 10000.0,
                "policy_duration": "7 days",
                "covered_events": ["HEAVY_RAIN", "FLOOD", "EXTREME_HEAT", "WORK_DISRUPTION"],
                "trigger_conditions": {
                    "HEAVY_RAIN": "Rainfall >= 40mm over 3 consecutive hours",
                    "FLOOD": "Waterlogging warning or road closure > 2 hours",
                    "EXTREME_HEAT": "Temperature >= 41°C during peak hours",
                    "WORK_DISRUPTION": "Civic curfew, grid collapse, or localized platform outage > 4 hours",
                },
                "waiting_period": "12 hours",
                "exclusions": [
                    "Disruptions in unverified zones without official IMD or civic telemetry",
                ],
                "coverage_area_rules": {
                    "primary_zone": "Chennai Delivery Zone",
                    "supported_subzones": ["All Chennai Metropolitan Subzones"],
                },
                "active": True,
            },
        ]

    def get_policy(self, policy_number: str) -> Optional[Dict[str, Any]]:
        return {
            "policy_number": policy_number,
            "status": "ACTIVE",
            "partner": self.partner_name,
            "verified_by_partner": True,
        }

    def purchase_policy(
        self,
        user_id: int,
        plan_code: str,
        work_zone: str,
        consent_confirmed: bool,
    ) -> Dict[str, Any]:
        if not consent_confirmed:
            raise ValueError("Explicit user consent is mandatory for insurance underwriting")

        now = datetime.now(timezone.utc)
        policy_number = f"INCSH-{now.strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
        return {
            "policy_number": policy_number,
            "partner_policy_id": f"PARTNER-{uuid.uuid4().hex[:8].upper()}",
            "partner_name": self.partner_name,
            "status": "ACTIVE",
            "issued_at": now.isoformat(),
            "start_date": now.isoformat(),
            "end_date": (now + timedelta(days=7)).isoformat(),
            "covered_work_zone": work_zone,
        }

    def evaluate_trigger(
        self,
        policy_data: Dict[str, Any],
        event_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Deterministic parametric policy rule evaluation.
        Verifies whether observed sensor/telemetry values meet the policy trigger.
        """
        event_type = event_data.get("event_type", "HEAVY_RAIN")
        telemetry = event_data.get("telemetry_data", {})

        # Default rules
        if event_type == "HEAVY_RAIN":
            observed_mm = float(telemetry.get("observed_rainfall_mm", 0.0))
            threshold_mm = float(telemetry.get("threshold_rainfall_mm", 50.0))
            if observed_mm >= threshold_mm:
                return {
                    "status": "REACHED",
                    "threshold": f"{threshold_mm:.0f}mm in 3h",
                    "observed_value": f"{observed_mm:.0f}mm",
                    "required_value": f">= {threshold_mm:.0f}mm",
                    "reason": f"Observed rainfall of {observed_mm:.0f}mm exceeded the policy trigger threshold of {threshold_mm:.0f}mm.",
                    "payout_eligible": True,
                    "suggested_payout_amount": min(750.0, policy_data.get("coverage_limit", 5000.0)),
                }
            else:
                return {
                    "status": "NOT_REACHED",
                    "threshold": f"{threshold_mm:.0f}mm in 3h",
                    "observed_value": f"{observed_mm:.0f}mm",
                    "required_value": f">= {threshold_mm:.0f}mm",
                    "reason": f"Observed rainfall of {observed_mm:.0f}mm did not satisfy the {threshold_mm:.0f}mm policy trigger.",
                    "payout_eligible": False,
                    "suggested_payout_amount": 0.0,
                }
        elif event_type == "EXTREME_HEAT":
            observed_temp = float(telemetry.get("observed_temperature_c", 40.0))
            threshold_temp = float(telemetry.get("threshold_temperature_c", 43.0))
            if observed_temp >= threshold_temp:
                return {
                    "status": "REACHED",
                    "threshold": f"{threshold_temp:.0f}°C peak",
                    "observed_value": f"{observed_temp:.0f}°C",
                    "required_value": f">= {threshold_temp:.0f}°C",
                    "reason": f"Observed peak temperature of {observed_temp:.0f}°C met the extreme heat threshold.",
                    "payout_eligible": True,
                    "suggested_payout_amount": 500.0,
                }
            else:
                return {
                    "status": "NOT_REACHED",
                    "threshold": f"{threshold_temp:.0f}°C peak",
                    "observed_value": f"{observed_temp:.0f}°C",
                    "required_value": f">= {threshold_temp:.0f}°C",
                    "reason": f"Observed temperature of {observed_temp:.0f}°C is below the {threshold_temp:.0f}°C trigger threshold.",
                    "payout_eligible": False,
                    "suggested_payout_amount": 0.0,
                }

        # Fallback
        return {
            "status": "NOT_REACHED",
            "threshold": "Policy event trigger criteria",
            "observed_value": "Conditions pending verification",
            "required_value": "Telemetry confirmation",
            "reason": "Event criteria not satisfied.",
            "payout_eligible": False,
            "suggested_payout_amount": 0.0,
        }

    def get_payout_status(self, partner_payout_id: str) -> Dict[str, Any]:
        return {
            "partner_payout_id": partner_payout_id,
            "status": "COMPLETED",
            "settled_at": datetime.now(timezone.utc).isoformat(),
            "channel": "UPI Instant Settlement",
        }

    def get_documents(self, policy_number: str) -> List[Dict[str, Any]]:
        return [
            {
                "title": f"Policy Schedule — {policy_number}",
                "document_type": "POLICY_SCHEDULE",
                "file_url": f"/api/insurance/documents/{policy_number}/schedule",
            },
            {
                "title": "Parametric Income Protection Terms & Conditions",
                "document_type": "TERMS_AND_CONDITIONS",
                "file_url": "/api/insurance/documents/terms-v1",
            },
            {
                "title": "Exclusions & Geographical Scope Guide",
                "document_type": "EXCLUSIONS_GUIDE",
                "file_url": "/api/insurance/documents/exclusions-v1",
            },
        ]


_provider_instance: Optional[InsuranceProvider] = None


def get_insurance_provider() -> InsuranceProvider:
    """Factory function for acquiring the configured InsuranceProvider."""
    global _provider_instance
    if _provider_instance is None:
        provider_name = (settings.INSURANCE_PROVIDER or "mock").lower()
        if provider_name == "mock":
            _provider_instance = MockInsuranceProvider()
        else:
            # Extensible for live licensed insurance partner APIs
            _provider_instance = MockInsuranceProvider()
    return _provider_instance
