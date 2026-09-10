"""
LEVELLY IncomeShield — Disruption Data Provider
Provides real-time environmental and civic disruption telemetry for registered work zones.
Pluggable provider architecture (Mock provider for development, IMD / OpenWeather / Civic alerts in production).
"""
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta

from app.core.config import settings


class DisruptionDataProvider(ABC):
    """Abstract interface for external weather, environmental, and civic disruption feeds."""

    @abstractmethod
    def get_active_events(self, zone: str) -> List[Dict[str, Any]]:
        """Retrieve verified disruption events currently affecting the zone."""
        pass

    @abstractmethod
    def get_event_telemetry(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve granular telemetry (rainfall mm, peak temp, road waterlogging)."""
        pass


class MockDisruptionDataProvider(DisruptionDataProvider):
    """
    Mock telemetry provider for Chennai delivery zones.
    Simulates real-world monsoon and heatwave signals without external API dependencies.
    """

    def get_active_events(self, zone: str) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        return [
            {
                "external_event_id": "IMD-CHN-RAIN-2026",
                "event_type": "HEAVY_RAIN",
                "zone": zone or "Chennai Delivery Zone",
                "start_time": (now - timedelta(hours=2, minutes=45)).isoformat(),
                "duration": "2h 45m",
                "source": "IMD Chennai / Regional Radar Telemetry",
                "verification_status": "VERIFIED",
                "severity": "SEVERE",
                "telemetry_data": {
                    "observed_rainfall_mm": 58.0,
                    "threshold_rainfall_mm": 50.0,
                    "duration_hours": 3,
                    "affected_subzones": ["Chennai South", "OMR-ECR", "Velachery"],
                    "road_condition": "Moderate waterlogging reported on arterial delivery routes",
                },
            }
        ]

    def get_event_telemetry(self, event_id: str) -> Optional[Dict[str, Any]]:
        return {
            "event_id": event_id,
            "observed_rainfall_mm": 58.0,
            "threshold_rainfall_mm": 50.0,
            "precipitation_rate_mm_hr": 22.0,
            "wind_speed_kmh": 34.0,
            "telemetry_timestamp": datetime.now(timezone.utc).isoformat(),
        }


_disruption_instance: Optional[DisruptionDataProvider] = None


def get_disruption_data_provider() -> DisruptionDataProvider:
    """Factory function for acquiring the configured DisruptionDataProvider."""
    global _disruption_instance
    if _disruption_instance is None:
        provider_name = (settings.DISRUPTION_PROVIDER or "mock").lower()
        if provider_name == "mock":
            _disruption_instance = MockDisruptionDataProvider()
        else:
            _disruption_instance = MockDisruptionDataProvider()
    return _disruption_instance
