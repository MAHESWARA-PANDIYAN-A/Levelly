"""
LEVELLY — Income Intelligence Service
Analyzes income history to determine trends, volatility, and earning pace.
Core to the INCOME INTELLIGENCE principle.
"""
import math
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.transaction import IncomeTransaction
from app.models.financial_profile import FinancialProfile
from app.core.config import settings


class IncomeIntelligenceService:
    """
    Aggregates and analyzes income data to power financial intelligence.

    Calculates:
    - Historical average income
    - Recent income (configurable rolling window)
    - Income trend (rising/stable/declining)
    - Income volatility (coefficient of variation)
    - Income decline percentage
    - Consecutive low-income periods (for sustained distress detection)
    """

    def __init__(self, db: Session):
        self.db = db
        self.recent_days = settings.INCOME_RECENT_DAYS
        self.historical_months = settings.INCOME_HISTORICAL_MONTHS

    @staticmethod
    def _naive(dt: datetime) -> datetime:
        """Strip timezone info for cross-database datetime comparisons."""
        if dt is None:
            return dt
        return dt.replace(tzinfo=None)

    def get_income_summary(self, user_id: int) -> Dict[str, Any]:
        """Get complete income intelligence summary for a user."""
        now = datetime.now(timezone.utc)
        recent_cutoff = now - timedelta(days=self.recent_days)
        historical_cutoff = now - timedelta(days=self.historical_months * 30)
        recent_cutoff_naive = recent_cutoff.replace(tzinfo=None)
        historical_cutoff_naive = historical_cutoff.replace(tzinfo=None)

        # All historical income (use naive cutoff for cross-DB compat)
        all_income = (
            self.db.query(IncomeTransaction)
            .filter(
                IncomeTransaction.user_id == user_id,
                IncomeTransaction.status == "completed",
            )
            .order_by(IncomeTransaction.transaction_date.asc())
            .all()
        )

        # Filter by date in Python to handle tz-naive vs tz-aware
        all_income = [
            t for t in all_income
            if self._naive(t.transaction_date) >= historical_cutoff_naive
        ]

        # Recent income
        recent_income_records = [
            t for t in all_income if self._naive(t.transaction_date) >= recent_cutoff_naive
        ]

        # Calculations
        historical_total = sum(t.amount for t in all_income)
        recent_total = sum(t.amount for t in recent_income_records)

        # Monthly averages
        months_of_data = max(1, self.historical_months)
        historical_avg_monthly = historical_total / months_of_data

        # Recent monthly pace (annualized from recent window)
        recent_monthly_pace = (recent_total / self.recent_days) * 30 if recent_income_records else 0

        # Income decline
        income_decline_pct = 0.0
        if historical_avg_monthly > 0:
            income_decline_pct = max(
                0.0,
                (historical_avg_monthly - recent_monthly_pace) / historical_avg_monthly,
            )

        # Volatility
        volatility, volatility_level = self._calculate_volatility(all_income)

        # Trend
        trend = self._calculate_trend(all_income)

        # Weekly income for chart (last 8 weeks)
        weekly_data = self._get_weekly_income(user_id, weeks=8)

        # Consecutive low periods
        consecutive_low = self._count_consecutive_low_periods(all_income, historical_avg_monthly)

        return {
            "historical_avg_income": round(historical_avg_monthly, 2),
            "recent_income": round(recent_monthly_pace, 2),
            "income_decline_pct": round(income_decline_pct * 100, 1),
            "income_trend": trend,
            "income_volatility": round(volatility, 4),
            "income_volatility_level": volatility_level,
            "consecutive_low_periods": consecutive_low,
            "weekly_data": weekly_data,
            "total_records": len(all_income),
        }

    def _calculate_volatility(self, transactions: List[IncomeTransaction]) -> tuple:
        """
        Calculate income volatility using coefficient of variation.
        CV = standard_deviation / mean
        """
        if len(transactions) < 2:
            return 0.0, "LOW"

        amounts = [t.amount for t in transactions]
        mean = sum(amounts) / len(amounts)
        if mean == 0:
            return 0.0, "LOW"

        variance = sum((x - mean) ** 2 for x in amounts) / len(amounts)
        std_dev = math.sqrt(variance)
        cv = std_dev / mean

        # Classify
        if cv <= settings.VOLATILITY_LOW_MAX:
            level = "LOW"
        elif cv <= settings.VOLATILITY_MODERATE_MAX:
            level = "MODERATE"
        else:
            level = "HIGH"

        return cv, level

    def _calculate_trend(self, transactions: List[IncomeTransaction]) -> str:
        """Determine income trend by comparing first half vs second half."""
        if len(transactions) < 4:
            return "stable"

        mid = len(transactions) // 2
        first_half_avg = sum(t.amount for t in transactions[:mid]) / mid
        second_half_avg = sum(t.amount for t in transactions[mid:]) / (len(transactions) - mid)

        if second_half_avg > first_half_avg * 1.05:
            return "rising"
        elif second_half_avg < first_half_avg * 0.90:
            return "declining"
        else:
            return "stable"

    def _get_weekly_income(self, user_id: int, weeks: int = 8) -> List[Dict]:
        """Get weekly income aggregated for chart display."""
        now = datetime.now(timezone.utc)
        result = []

        for i in range(weeks - 1, -1, -1):
            week_start = now - timedelta(weeks=i + 1)
            week_end = now - timedelta(weeks=i)

            week_total = (
                self.db.query(func.sum(IncomeTransaction.amount))
                .filter(
                    IncomeTransaction.user_id == user_id,
                    IncomeTransaction.transaction_date >= week_start,
                    IncomeTransaction.transaction_date < week_end,
                    IncomeTransaction.status == "completed",
                )
                .scalar()
            ) or 0.0

            result.append({
                "week": f"W{weeks - i}",
                "week_start": week_start.isoformat(),
                "week_end": week_end.isoformat(),
                "income": round(week_total, 2),
            })

        return result

    def _count_consecutive_low_periods(
        self, transactions: List[IncomeTransaction], baseline: float
    ) -> int:
        """
        Count consecutive weekly periods where income is materially below baseline.
        Used for sustained distress detection (not one bad day).
        """
        if not transactions or baseline <= 0:
            return 0

        # Group by week
        weeks: Dict[str, float] = {}
        for t in transactions:
            week_key = t.transaction_date.strftime("%Y-W%W")
            weeks[week_key] = weeks.get(week_key, 0) + t.amount

        if not weeks:
            return 0

        # Weekly baseline
        weekly_baseline = baseline / 4.33  # monthly to weekly

        # Count consecutive low weeks from most recent
        sorted_weeks = sorted(weeks.keys(), reverse=True)
        consecutive = 0
        for week_key in sorted_weeks:
            weekly_income = weeks[week_key]
            # "Materially below" = below 80% of weekly baseline
            if weekly_income < weekly_baseline * 0.80:
                consecutive += 1
            else:
                break

        return consecutive

    def update_financial_profile(self, user_id: int) -> Optional[FinancialProfile]:
        """Update the user's financial profile with latest income intelligence."""
        summary = self.get_income_summary(user_id)

        profile = (
            self.db.query(FinancialProfile)
            .filter(FinancialProfile.user_id == user_id)
            .first()
        )

        if not profile:
            profile = FinancialProfile(user_id=user_id)
            self.db.add(profile)

        profile.historical_avg_income = summary["historical_avg_income"]
        profile.recent_income = summary["recent_income"]
        profile.income_trend = summary["income_trend"]
        profile.income_decline_pct = summary["income_decline_pct"]
        profile.income_volatility = summary["income_volatility"]
        profile.income_volatility_level = summary["income_volatility_level"]
        profile.consecutive_low_periods = summary["consecutive_low_periods"]
        profile.last_computed_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(profile)
        return profile
