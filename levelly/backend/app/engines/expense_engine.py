"""
LEVELLY — Expense Engine
Analyzes expense categories, calculates ratios, and generates nudges
"""
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.transaction import ExpenseTransaction
from app.models.financial_profile import FinancialProfile


ESSENTIAL_CATEGORIES = {"food", "fuel", "rent", "bills", "healthcare", "education", "family"}
NON_ESSENTIAL_CATEGORIES = {"entertainment", "shopping", "other"}
ALL_CATEGORIES = ESSENTIAL_CATEGORIES | NON_ESSENTIAL_CATEGORIES


class ExpenseEngine:
    """
    Analyzes expense data to:
    - Calculate monthly/weekly expenses
    - Categorize essential vs non-essential
    - Compute expense-to-income ratio
    - Generate expense nudges
    """

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _naive(dt: datetime) -> datetime:
        """Strip timezone for cross-DB compat (SQLite vs PostgreSQL)."""
        return dt.replace(tzinfo=None) if dt and dt.tzinfo else dt

    def get_expense_summary(self, user_id: int) -> Dict[str, Any]:
        """Get complete expense analysis for a user."""
        now = datetime.now(timezone.utc)
        month_start_naive = (now - timedelta(days=30)).replace(tzinfo=None)
        week_start_naive = (now - timedelta(days=7)).replace(tzinfo=None)
        prev_week_start_naive = (now - timedelta(days=14)).replace(tzinfo=None)

        # Monthly expenses — pull all, filter in Python for tz compat
        all_expenses = (
            self.db.query(ExpenseTransaction)
            .filter(
                ExpenseTransaction.user_id == user_id,
                ExpenseTransaction.status == "completed",
            )
            .all()
        )

        monthly_expenses = [
            e for e in all_expenses
            if self._naive(e.transaction_date) >= month_start_naive
        ]

        # Weekly expenses (current week)
        weekly_expenses = [
            e for e in monthly_expenses
            if self._naive(e.transaction_date) >= week_start_naive
        ]

        # Previous week expenses (for comparison)
        prev_weekly_expenses = [
            e for e in all_expenses
            if prev_week_start_naive <= self._naive(e.transaction_date) < week_start_naive
        ]

        # Aggregate by category
        category_totals = {}
        for exp in monthly_expenses:
            cat = exp.category.lower()
            category_totals[cat] = category_totals.get(cat, 0) + exp.amount

        # Essential vs non-essential
        essential_total = sum(
            amt for cat, amt in category_totals.items() if cat in ESSENTIAL_CATEGORIES
        )
        non_essential_total = sum(
            amt for cat, amt in category_totals.items() if cat in NON_ESSENTIAL_CATEGORIES
        )

        monthly_total = sum(e.amount for e in monthly_expenses)
        weekly_total = sum(e.amount for e in weekly_expenses)

        # Category changes (week over week)
        prev_week_cats = {}
        for exp in prev_weekly_expenses:
            cat = exp.category.lower()
            prev_week_cats[cat] = prev_week_cats.get(cat, 0) + exp.amount

        curr_week_cats = {}
        for exp in weekly_expenses:
            cat = exp.category.lower()
            curr_week_cats[cat] = curr_week_cats.get(cat, 0) + exp.amount

        category_changes = {}
        for cat in ALL_CATEGORIES:
            prev = prev_week_cats.get(cat, 0)
            curr = curr_week_cats.get(cat, 0)
            if prev > 0:
                pct_change = ((curr - prev) / prev) * 100
            else:
                pct_change = 100.0 if curr > 0 else 0.0
            category_changes[cat] = {
                "previous_week": round(prev, 2),
                "current_week": round(curr, 2),
                "change_pct": round(pct_change, 1),
            }

        return {
            "monthly_total": round(monthly_total, 2),
            "weekly_total": round(weekly_total, 2),
            "essential_total": round(essential_total, 2),
            "non_essential_total": round(non_essential_total, 2),
            "category_totals": {k: round(v, 2) for k, v in category_totals.items()},
            "category_changes": category_changes,
            "essential_pct": round((essential_total / monthly_total * 100) if monthly_total > 0 else 0, 1),
            "non_essential_pct": round((non_essential_total / monthly_total * 100) if monthly_total > 0 else 0, 1),
        }

    def calculate_expense_ratio(self, user_id: int, monthly_income: float) -> float:
        """
        expense_ratio = current_period_expenses / current_period_income
        """
        if monthly_income <= 0:
            return 1.0  # assume maximum pressure

        summary = self.get_expense_summary(user_id)
        monthly_expenses = summary["monthly_total"]

        return round(monthly_expenses / monthly_income, 3)

    def update_financial_profile(self, user_id: int, monthly_income: float) -> None:
        """Update expense fields in FinancialProfile."""
        summary = self.get_expense_summary(user_id)
        expense_ratio = self.calculate_expense_ratio(user_id, monthly_income)

        profile = (
            self.db.query(FinancialProfile)
            .filter(FinancialProfile.user_id == user_id)
            .first()
        )

        if not profile:
            profile = FinancialProfile(user_id=user_id)
            self.db.add(profile)

        profile.monthly_expenses = summary["monthly_total"]
        profile.weekly_expenses = summary["weekly_total"]
        profile.essential_expenses = summary["essential_total"]
        profile.non_essential_expenses = summary["non_essential_total"]
        profile.expense_to_income_ratio = expense_ratio

        self.db.commit()

    def generate_expense_nudges(self, user_id: int, monthly_income: float) -> List[Dict]:
        """Generate actionable expense nudges from spending patterns."""
        summary = self.get_expense_summary(user_id)
        nudges = []

        # High expense ratio
        expense_ratio = self.calculate_expense_ratio(user_id, monthly_income)
        if expense_ratio > 0.90:
            nudges.append({
                "type": "expense_pressure",
                "message": "Your expenses are very close to your current income.",
                "cta": "View expense breakdown",
                "priority": "high",
            })

        # Specific category increases
        changes = summary.get("category_changes", {})
        for cat, data in changes.items():
            if data["change_pct"] > 20 and data["current_week"] > 200:
                nudges.append({
                    "type": "category_increase",
                    "message": f"Your {cat} spending increased {data['change_pct']:.0f}% this week.",
                    "cta": f"See {cat} transactions",
                    "priority": "normal",
                })

        # High non-essential
        non_ess_pct = summary.get("non_essential_pct", 0)
        if non_ess_pct > 30 and expense_ratio > 0.7:
            nudges.append({
                "type": "non_essential_high",
                "message": "Consider delaying a non-essential payment this week.",
                "cta": "Review non-essential spending",
                "priority": "normal",
            })

        return nudges
