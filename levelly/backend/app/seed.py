"""
LEVELLY — Database Seed Script
Creates realistic demo data for Arjun Kumar (gig worker persona).

State A (Healthy): High income, low distress, good savings
State B (Financial Pressure): Declining income, high distress, below target
The application shows whichever state the backend computes from transactions.
"""
import sys
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import engine, SessionLocal, Base
from app.core.security import hash_password
from app.models.user import User
from app.models.wallet import Wallet
from app.models.transaction import IncomeTransaction, ExpenseTransaction
from app.models.savings import SavingsPreference, SavingsTransaction, CategorySavingPolicy
from app.models.financial_profile import FinancialProfile
from app.models.investment import InvestmentProduct
from app.models.notification import Notification
from app.models.credit import CreditRequest
from app.models.audit import AuditLog
from app.models.coach import CoachConversation

# Import all models for Base
from app import models  # noqa


def seed_database():
    """Seed the database with demo data."""
    db = SessionLocal()

    try:
        print("🌱 LEVELLY Database Seeder Starting...")

        # ============================================================
        # CREATE TABLES
        # ============================================================
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)

        # ============================================================
        # CATEGORY SAVING POLICIES
        # ============================================================
        print("Creating category saving policies...")
        categories = [
            {"category": "food", "base": 10.0, "min": 0.0, "max": 15.0},
            {"category": "fuel", "base": 5.0, "min": 0.0, "max": 10.0},
            {"category": "education", "base": 8.0, "min": 0.0, "max": 12.0},
            {"category": "entertainment", "base": 5.0, "min": 0.0, "max": 10.0},
            {"category": "shopping", "base": 10.0, "min": 0.0, "max": 15.0},
            {"category": "family", "base": 5.0, "min": 0.0, "max": 10.0},
            {"category": "healthcare", "base": 5.0, "min": 0.0, "max": 10.0},
            {"category": "rent", "base": 0.0, "min": 0.0, "max": 5.0},
            {"category": "bills", "base": 0.0, "min": 0.0, "max": 5.0},
            {"category": "other", "base": 5.0, "min": 0.0, "max": 10.0},
        ]

        for cat in categories:
            existing = db.query(CategorySavingPolicy).filter_by(category=cat["category"]).first()
            if not existing:
                policy = CategorySavingPolicy(
                    category=cat["category"],
                    base_percentage=cat["base"],
                    min_percentage=cat["min"],
                    max_percentage=cat["max"],
                    description=f"Default save-at-pay percentage for {cat['category']}",
                )
                db.add(policy)

        # ============================================================
        # INVESTMENT PRODUCTS
        # ============================================================
        print("Creating investment products...")
        existing_products = db.query(InvestmentProduct).count()
        if existing_products == 0:
            products = [
                InvestmentProduct(
                    name="High-Yield Savings Account",
                    product_type="LIQUID_SAVINGS",
                    issuer="Partner Bank (Demo)",
                    risk_level="LOW",
                    liquidity="High — withdraw anytime",
                    holding_period="No lock-in",
                    interest_or_coupon="Indicative: 6-7% p.a. (subject to change)",
                    fees="No fees (Demo)",
                    tax_notes="Interest taxable as per income slab",
                    terms="Terms apply. Rates are indicative and may change.",
                    min_investment=1000.0,
                    description=(
                        "A savings account with higher-than-standard interest rates. "
                        "Fully liquid — your money is accessible at any time."
                    ),
                    suitable_for="Users who want liquidity with better returns than a standard account",
                    active=True,
                ),
                InvestmentProduct(
                    name="Government Securities (G-Sec) — Demo",
                    product_type="GOVERNMENT_SECURITY",
                    issuer="Government of India (Demo)",
                    risk_level="LOW",
                    liquidity="Medium — tradeable on secondary market",
                    holding_period="1-5 years (varies by security)",
                    interest_or_coupon="Indicative: ~7.1% p.a. (coupon varies by issuance)",
                    fees="Minimal brokerage",
                    tax_notes="Interest taxable. Capital gains may apply on sale.",
                    terms="G-Secs are issued by RBI. Demo product only — actual terms at partner.",
                    min_investment=10000.0,
                    description=(
                        "Government securities are debt instruments issued by the Central Government. "
                        "They carry no credit risk from the government. Interest rates vary by issuance."
                    ),
                    suitable_for="Users with safety surplus seeking stable returns over 1+ year",
                    active=True,
                ),
                InvestmentProduct(
                    name="Short-Duration Debt Fund — Demo",
                    product_type="DEBT_ORIENTED",
                    issuer="Demo Asset Management Co.",
                    risk_level="MODERATE",
                    liquidity="Medium — T+1 redemption",
                    holding_period="6 months to 1 year recommended",
                    interest_or_coupon="Variable — depends on market (historical range: 6-8% p.a.)",
                    fees="Exit load may apply within 3 months",
                    tax_notes="Gains taxed as per holding period — consult a tax advisor",
                    terms="Mutual fund investments are subject to market risk. Demo product only.",
                    min_investment=500.0,
                    description=(
                        "A debt-oriented mutual fund investing in short-term fixed income instruments. "
                        "Returns vary based on interest rate movements and credit quality."
                    ),
                    suitable_for="Users comfortable with moderate risk seeking better returns than FD",
                    active=True,
                ),
            ]
            for p in products:
                db.add(p)

        # ============================================================
        # ARJUN KUMAR — PRIMARY DEMO USER
        # ============================================================
        print("Creating Arjun Kumar (primary demo user)...")
        arjun = db.query(User).filter_by(email="arjun@levelly.app").first()
        if not arjun:
            arjun = User(
                email="arjun@levelly.app",
                full_name="Arjun Kumar",
                hashed_password=hash_password("Levelly@123"),
                phone="+91-9876543210",
                occupation="Food Delivery Rider",
                city="Chennai",
                platform_tenure_months=24,
                role="user",
                is_active=True,
                onboarding_complete=True,
                income_frequency="weekly",
            )
            db.add(arjun)
            db.flush()

            # Create Safety wallet (Resilience Reserve)
            safety_wallet = Wallet(
                user_id=arjun.id,
                wallet_type="SAFETY",
                balance=8200.0,
                target_amount=10000.0,
            )
            db.add(safety_wallet)

            # Linked Bank/UPI Account (Direct payment source)
            from app.models.payment import LinkedPaymentAccount, Merchant
            linked_acc = LinkedPaymentAccount(
                user_id=arjun.id,
                provider="upi",
                upi_id="arjun@upi",
                bank_name="HDFC Bank",
                account_mask="****4821",
                account_holder_name="Arjun Kumar",
                status="connected",
                is_primary=True,
            )
            db.add(linked_acc)

            # Savings preference
            savings_pref = SavingsPreference(
                user_id=arjun.id,
                safety_target=10000.0,
                save_at_pay_enabled=True,
            )
            db.add(savings_pref)

        # ============================================================
        # VERIFIED MERCHANTS (LEVELLY Pay)
        # ============================================================
        print("Creating verified merchants...")
        from app.models.payment import Merchant, LinkedPaymentAccount
        sample_merchants = [
            {"code": "M001", "name": "Sri Krishna Supermarket", "upi": "srikrishna@upi", "cat": "Food & Grocery", "norm": "food"},
            {"code": "M002", "name": "BikeCare Service Point", "upi": "bikecare@upi", "cat": "Vehicle Repair", "norm": "vehicle"},
            {"code": "M003", "name": "City Fuel Station", "upi": "cityfuel@upi", "cat": "Petrol Station", "norm": "fuel"},
            {"code": "M004", "name": "Apollo Pharmacy", "upi": "apollopharmacy@upi", "cat": "Healthcare & Pharmacy", "norm": "healthcare"},
            {"code": "M005", "name": "Royal Cafe & Bakery", "upi": "royalcafe@upi", "cat": "Restaurant", "norm": "food"},
        ]
        for m in sample_merchants:
            existing_m = db.query(Merchant).filter_by(merchant_code=m["code"]).first()
            if not existing_m:
                db.add(Merchant(
                    merchant_code=m["code"],
                    name=m["name"],
                    upi_id=m["upi"],
                    category=m["cat"],
                    normalized_category=m["norm"],
                    verification_status="verified",
                ))

        else:
            safety_wallet = db.query(Wallet).filter_by(user_id=arjun.id, wallet_type="SAFETY").first()
            if not safety_wallet:
                safety_wallet = Wallet(user_id=arjun.id, wallet_type="SAFETY", balance=8200.0, target_amount=10000.0)
                db.add(safety_wallet)

            existing_linked = db.query(LinkedPaymentAccount).filter_by(user_id=arjun.id).first()
            if not existing_linked:
                db.add(LinkedPaymentAccount(
                    user_id=arjun.id,
                    provider="upi",
                    upi_id="arjun@upi",
                    bank_name="HDFC Bank",
                    account_mask="****4821",
                    account_holder_name="Arjun Kumar",
                    status="connected",
                    is_primary=True,
                ))

        db.flush()

        # ============================================================
        # ARJUN'S INCOME HISTORY (8 weeks)
        # Healthy then declining pattern
        # ============================================================
        print("Creating income transactions...")
        existing_income = db.query(IncomeTransaction).filter_by(user_id=arjun.id).count()
        if existing_income == 0:
            now = datetime.now(timezone.utc)

            # Weeks of income — healthy then declining
            weekly_incomes = [
                # 8 weeks ago — healthy
                {"week_offset": 8, "amount": 6000, "source": "Swiggy"},   # ~24k/month
                # 7 weeks ago
                {"week_offset": 7, "amount": 6200, "source": "Swiggy"},
                # 6 weeks ago
                {"week_offset": 6, "amount": 5500, "source": "Swiggy"},
                # 5 weeks ago
                {"week_offset": 5, "amount": 6500, "source": "Zomato"},
                # 4 weeks ago — starting to decline
                {"week_offset": 4, "amount": 5250, "source": "Swiggy"},
                # 3 weeks ago
                {"week_offset": 3, "amount": 4500, "source": "Swiggy"},
                # 2 weeks ago — significant decline
                {"week_offset": 2, "amount": 3750, "source": "Zomato"},
                # Last week
                {"week_offset": 1, "amount": 3500, "source": "Swiggy"},
            ]

            for income_data in weekly_incomes:
                txn_date = now - timedelta(weeks=income_data["week_offset"])
                income_txn = IncomeTransaction(
                    user_id=arjun.id,
                    amount=income_data["amount"],
                    source=income_data["source"],
                    income_type="payout",
                    description=f"Weekly payout from {income_data['source']}",
                    status="completed",
                    transaction_date=txn_date,
                )
                db.add(income_txn)

        # ============================================================
        # ARJUN'S EXPENSE HISTORY
        # ============================================================
        print("Creating expense transactions...")
        existing_expenses = db.query(ExpenseTransaction).filter_by(user_id=arjun.id).count()
        if existing_expenses == 0:
            now = datetime.now(timezone.utc)

            expenses = [
                # Rent (monthly)
                {"days_ago": 28, "amount": 6000, "category": "rent", "desc": "Monthly rent"},
                # Bills
                {"days_ago": 25, "amount": 800, "category": "bills", "desc": "Electricity bill"},
                {"days_ago": 24, "amount": 299, "category": "bills", "desc": "Mobile recharge"},
                # Food (daily/frequent)
                {"days_ago": 27, "amount": 350, "category": "food", "desc": "Groceries", "save": 35},
                {"days_ago": 24, "amount": 180, "category": "food", "desc": "Lunch", "save": 18},
                {"days_ago": 21, "amount": 420, "category": "food", "desc": "Groceries", "save": 42},
                {"days_ago": 18, "amount": 200, "category": "food", "desc": "Dinner", "save": 20},
                {"days_ago": 14, "amount": 380, "category": "food", "desc": "Groceries", "save": 0},
                {"days_ago": 10, "amount": 160, "category": "food", "desc": "Lunch", "save": 16},
                {"days_ago": 7, "amount": 350, "category": "food", "desc": "Groceries", "save": 0},
                {"days_ago": 3, "amount": 220, "category": "food", "desc": "Dinner", "save": 22},
                # Fuel
                {"days_ago": 26, "amount": 500, "category": "fuel", "desc": "Petrol"},
                {"days_ago": 19, "amount": 600, "category": "fuel", "desc": "Petrol"},
                {"days_ago": 12, "amount": 550, "category": "fuel", "desc": "Petrol"},
                {"days_ago": 5, "amount": 580, "category": "fuel", "desc": "Petrol"},
                # Family
                {"days_ago": 22, "amount": 1200, "category": "family", "desc": "Money sent home"},
                {"days_ago": 8, "amount": 800, "category": "family", "desc": "Money sent home"},
                # Entertainment
                {"days_ago": 20, "amount": 350, "category": "entertainment", "desc": "OTT subscription + movie"},
                # Healthcare
                {"days_ago": 15, "amount": 450, "category": "healthcare", "desc": "Medical checkup"},
                # Education
                {"days_ago": 30, "amount": 999, "category": "education", "desc": "Online course"},
            ]

            for exp_data in expenses:
                save_amount = exp_data.get("save", 0)
                exp_txn = ExpenseTransaction(
                    user_id=arjun.id,
                    amount=exp_data["amount"],
                    category=exp_data["category"],
                    description=exp_data["desc"],
                    savings_added=save_amount,
                    save_consent=save_amount > 0,
                    status="completed",
                    transaction_date=now - timedelta(days=exp_data["days_ago"]),
                )
                db.add(exp_txn)

        # ============================================================
        # SAVINGS TRANSACTIONS
        # ============================================================
        print("Creating savings transactions...")
        existing_savings = db.query(SavingsTransaction).filter_by(user_id=arjun.id).count()
        if existing_savings == 0 and safety_wallet:
            now = datetime.now(timezone.utc)
            savings_entries = [
                {"days_ago": 27, "amount": 35, "cat": "food"},
                {"days_ago": 24, "amount": 18, "cat": "food"},
                {"days_ago": 21, "amount": 42, "cat": "food"},
                {"days_ago": 18, "amount": 20, "cat": "food"},
                {"days_ago": 10, "amount": 16, "cat": "food"},
                {"days_ago": 3, "amount": 22, "cat": "food"},
                # Opening deposit
                {"days_ago": 60, "amount": 5000, "cat": None, "type": "deposit"},
                {"days_ago": 45, "amount": 2000, "cat": None, "type": "deposit"},
                {"days_ago": 30, "amount": 1000, "cat": None, "type": "deposit"},
            ]

            running_balance = 0
            for s in sorted(savings_entries, key=lambda x: x["days_ago"], reverse=True):
                amount = s["amount"]
                running_balance += amount
                st = SavingsTransaction(
                    user_id=arjun.id,
                    amount=amount,
                    transaction_type=s.get("type", "save_at_pay"),
                    category_context=s.get("cat"),
                    save_percentage_applied=10.0 if s.get("cat") else None,
                    balance_before=running_balance - amount,
                    balance_after=running_balance,
                    created_at=now - timedelta(days=s["days_ago"]),
                )
                db.add(st)

        # ============================================================
        # NOTIFICATIONS
        # ============================================================
        print("Creating notifications...")
        existing_notifs = db.query(Notification).filter_by(user_id=arjun.id).count()
        if existing_notifs == 0:
            now = datetime.now(timezone.utc)
            notifications = [
                Notification(
                    user_id=arjun.id,
                    title="Income Update",
                    message="Your recent earnings are 37% below your usual range. Levelly Coach can help you plan.",
                    notification_type="income_trend_changed",
                    priority="high",
                    is_read=False,
                    action_url="/income",
                    created_at=now - timedelta(days=2),
                ),
                Notification(
                    user_id=arjun.id,
                    title="Safety Wallet Updated",
                    message="₹22 added to your Safety Wallet via Save-at-Pay. Great job!",
                    notification_type="save_at_pay_accepted",
                    priority="normal",
                    is_read=False,
                    action_url="/wallets/safety",
                    created_at=now - timedelta(days=3),
                ),
                Notification(
                    user_id=arjun.id,
                    title="Financial Guidance Available",
                    message="LEVELLY has detected some financial pressure. Levelly Coach has personalized guidance for you.",
                    notification_type="financial_pressure_detected",
                    priority="high",
                    is_read=False,
                    action_url="/coach",
                    created_at=now - timedelta(days=4),
                ),
                Notification(
                    user_id=arjun.id,
                    title="Payout Received",
                    message="₹3,500 has been added to your Daily Wallet from Swiggy.",
                    notification_type="payout_received",
                    priority="normal",
                    is_read=True,
                    action_url="/wallets",
                    created_at=now - timedelta(days=7),
                ),
                Notification(
                    user_id=arjun.id,
                    title="Credit Update",
                    message="Credit temporarily held — let's focus on your financial stability first.",
                    notification_type="credit_recommendation_changed",
                    priority="high",
                    is_read=True,
                    action_url="/credit",
                    created_at=now - timedelta(days=5),
                ),
            ]
            for n in notifications:
                db.add(n)

        # ============================================================
        # FINANCIAL PROFILE (computed state)
        # ============================================================
        print("Creating financial profile...")
        existing_profile = db.query(FinancialProfile).filter_by(user_id=arjun.id).first()
        if not existing_profile:
            profile = FinancialProfile(
                user_id=arjun.id,
                historical_avg_income=24000.0,
                recent_income=15000.0,  # State B — Financial Pressure
                income_trend="declining",
                income_decline_pct=37.5,
                income_volatility=0.22,
                income_volatility_level="MODERATE",
                consecutive_low_periods=3,
                monthly_expenses=14200.0,
                weekly_expenses=3100.0,
                essential_expenses=11500.0,
                non_essential_expenses=2700.0,
                expense_to_income_ratio=0.85,
                resilience_score=58.0,
                resilience_label="at_risk",
                distress_score=65.0,
                distress_level="HIGH",
                distress_signals=["income_decline", "sustained_low_income", "expense_pressure"],
                credit_pressure=40.0,
                platform_tenure_months=24,
                safety_surplus=-1800.0,  # 8200 - 10000 = -1800
                investment_ready=False,
                last_computed_at=datetime.now(timezone.utc),
            )
            db.add(profile)
        else:
            # Update to State B
            existing_profile.historical_avg_income = 24000.0
            existing_profile.recent_income = 15000.0
            existing_profile.income_trend = "declining"
            existing_profile.income_decline_pct = 37.5
            existing_profile.income_volatility = 0.22
            existing_profile.income_volatility_level = "MODERATE"
            existing_profile.consecutive_low_periods = 3
            existing_profile.monthly_expenses = 14200.0
            existing_profile.expense_to_income_ratio = 0.85
            existing_profile.resilience_score = 58.0
            existing_profile.resilience_label = "at_risk"
            existing_profile.distress_score = 65.0
            existing_profile.distress_level = "HIGH"
            existing_profile.distress_signals = ["income_decline", "sustained_low_income", "expense_pressure"]
            existing_profile.safety_surplus = -1800.0
            existing_profile.investment_ready = False

        # ============================================================
        # ADMIN USER
        # ============================================================
        print("Creating admin user...")
        admin = db.query(User).filter_by(email="admin@levelly.app").first()
        if not admin:
            admin = User(
                email="admin@levelly.app",
                full_name="LEVELLY Admin",
                hashed_password=hash_password("Admin@Levelly123"),
                role="admin",
                is_active=True,
                onboarding_complete=True,
            )
            db.add(admin)
            db.flush()

            # Admin wallets (required by relationships)
            db.add(Wallet(user_id=admin.id, wallet_type="DAILY", balance=0.0))
            db.add(Wallet(user_id=admin.id, wallet_type="SAFETY", balance=0.0, target_amount=10000.0))
            db.add(SavingsPreference(user_id=admin.id))
            db.add(FinancialProfile(user_id=admin.id))

        db.commit()
        print("\n✅ LEVELLY Database Seeded Successfully!")
        print("\nDemo Accounts:")
        print("  User:  arjun@levelly.app  / Levelly@123")
        print("  Admin: admin@levelly.app  / Admin@Levelly123")
        print("\nArjun's current state: State B (Financial Pressure)")
        print("  - Historical avg income: ₹24,000/month")
        print("  - Recent income: ₹15,000/month")
        print("  - Safety Wallet: ₹8,200 / ₹10,000 (82%)")
        print("  - Distress Level: HIGH")
        print("  - Resilience Score: 58/100")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
