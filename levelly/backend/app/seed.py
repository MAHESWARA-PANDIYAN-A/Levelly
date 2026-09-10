"""
LEVELLY — Database Seed Script
Creates realistic demo data for Arjun Kumar (gig worker persona).

State A (Healthy): High income, low distress, good savings
State B (Financial Pressure): Declining income, high distress, below target
The application shows whichever state the backend computes from transactions.
"""
import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
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
        # SCHEMA CHECK (Production uses Alembic migrations)
        # ============================================================
        if settings.APP_ENV != "production":
            print("Checking schema (development fallback)...")
            Base.metadata.create_all(bind=engine)

        # ============================================================
        # CATEGORY SAVING POLICIES
        # ============================================================
        print("Creating category saving policies...")
        categories = [
            {"category": "food", "base": 10.0, "min": 0.0, "max": 20.0},
            {"category": "fuel", "base": 5.0, "min": 0.0, "max": 15.0},
            {"category": "education", "base": 8.0, "min": 0.0, "max": 15.0},
            {"category": "entertainment", "base": 5.0, "min": 0.0, "max": 15.0},
            {"category": "shopping", "base": 10.0, "min": 0.0, "max": 20.0},
            {"category": "family", "base": 5.0, "min": 0.0, "max": 15.0},
            {"category": "healthcare", "base": 5.0, "min": 0.0, "max": 15.0},
            {"category": "bills", "base": 5.0, "min": 0.0, "max": 15.0},
            {"category": "vehicle", "base": 5.0, "min": 0.0, "max": 15.0},
            {"category": "rent", "base": 0.0, "min": 0.0, "max": 5.0},
            {"category": "other", "base": 5.0, "min": 0.0, "max": 15.0},
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
            else:
                # Update default policy only if not customized by an admin
                if existing.updated_by_admin_id is None:
                    existing.base_percentage = cat["base"]
                    existing.min_percentage = cat["min"]
                    existing.max_percentage = cat["max"]
                    existing.is_active = True
        db.commit()

        # ============================================================
        # ============================================================
        # INVESTMENT PRODUCTS
        # ============================================================
        print("Creating investment products...")
        all_seed_products = [
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
                min_investment=500.0,
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
                min_investment=1000.0,
                description=(
                    "Government securities are debt instruments issued by the Central Government. "
                    "They carry no credit risk from the government. Interest rates vary by issuance."
                ),
                suitable_for="Users with safety surplus seeking stable returns over 1+ year",
                active=True,
            ),
            InvestmentProduct(
                name="Fixed-Income Term Deposit (AAA Rated) — Demo",
                product_type="FIXED_INCOME",
                issuer="HDFC / Bajaj Finance (Demo)",
                risk_level="LOW",
                liquidity="Low — 12 month tenure",
                holding_period="12 months lock-in",
                interest_or_coupon="Indicative: ~7.25% p.a.",
                fees="Nil",
                tax_notes="Interest taxable as per income slab",
                terms="Fixed interest rate locked for the entire tenure. Demo product only.",
                min_investment=1000.0,
                description="A fixed-income term deposit offering assured returns with capital safety from AAA-rated institutions.",
                suitable_for="Workers with surplus funds looking for predictable, stable returns without market risk.",
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
        for prod in all_seed_products:
            existing_prod = db.query(InvestmentProduct).filter_by(product_type=prod.product_type).first()
            if not existing_prod:
                db.add(prod)
            else:
                existing_prod.active = True
                existing_prod.name = prod.name
                existing_prod.min_investment = prod.min_investment
                existing_prod.holding_period = prod.holding_period
                existing_prod.liquidity = prod.liquidity
                existing_prod.risk_level = prod.risk_level
                existing_prod.interest_or_coupon = prod.interest_or_coupon
                existing_prod.description = prod.description
                existing_prod.suitable_for = prod.suitable_for
        db.commit()

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
                balance=10500.0,
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
            {"code": "M002", "name": "BikeCare Service", "upi": "bikecare@upi", "cat": "Vehicle Repair", "norm": "vehicle"},
            {"code": "M003", "name": "City Fuel Point", "upi": "cityfuel@upi", "cat": "Fuel", "norm": "fuel"},
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
                existing_m.name = m["name"]
                existing_m.upi_id = m["upi"]
                existing_m.category = m["cat"]
                existing_m.normalized_category = m["norm"]

        else:
            safety_wallet = db.query(Wallet).filter_by(user_id=arjun.id, wallet_type="SAFETY").first()
            if not safety_wallet:
                safety_wallet = Wallet(user_id=arjun.id, wallet_type="SAFETY", balance=10500.0, target_amount=10000.0)
                db.add(safety_wallet)
            else:
                safety_wallet.balance = 10500.0
                safety_wallet.target_amount = 10000.0

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
                recent_income=24500.0,  # Healthy Arjun State (Low Distress, Target Met)
                income_trend="stable",
                income_decline_pct=0.0,
                income_volatility=0.08,
                income_volatility_level="LOW",
                consecutive_low_periods=0,
                monthly_expenses=14200.0,
                weekly_expenses=3100.0,
                essential_expenses=11500.0,
                non_essential_expenses=2700.0,
                expense_to_income_ratio=0.58,
                resilience_score=78.0,
                resilience_label="healthy",
                distress_score=15.0,
                distress_level="LOW",
                distress_signals=[],
                credit_pressure=15.0,
                platform_tenure_months=24,
                safety_surplus=500.0,  # 10500 - 10000 = +500
                investment_ready=True,
                last_computed_at=datetime.now(timezone.utc),
            )
            db.add(profile)
        else:
            # Update to Healthy State
            existing_profile.historical_avg_income = 24000.0
            existing_profile.recent_income = 24500.0
            existing_profile.income_trend = "stable"
            existing_profile.income_decline_pct = 0.0
            existing_profile.income_volatility = 0.08
            existing_profile.income_volatility_level = "LOW"
            existing_profile.consecutive_low_periods = 0
            existing_profile.monthly_expenses = 14200.0
            existing_profile.expense_to_income_ratio = 0.58
            existing_profile.resilience_score = 78.0
            existing_profile.resilience_label = "healthy"
            existing_profile.distress_score = 15.0
            existing_profile.distress_level = "LOW"
            existing_profile.distress_signals = []
            existing_profile.safety_surplus = 500.0
            existing_profile.investment_ready = True

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

        # ============================================================
        # INCOMESHIELD INSURANCE (Plans, Partner & Telemetry)
        # ============================================================
        from app.insurance.models import InsurancePartner, InsurancePlan, InsuranceEvent
        print("Checking IncomeShield insurance plans...")
        if db.query(InsurancePlan).count() == 0:
            print("Creating IncomeShield insurance partner and plans...")
            partner = InsurancePartner(
                name="SafeWork Protection Partner",
                code="SAFEWORK-INS-01",
                partner_type="LICENSED_INSURER",
                active=True,
                contact_info={"support_email": "claims@safework-shield.in", "helpline": "1800-419-7443"},
            )
            db.add(partner)
            db.flush()

            plans = [
                InsurancePlan(
                    partner_id=partner.id,
                    name="Basic IncomeShield",
                    code="INCSH_BASIC",
                    description="Essential rainy-day and heatwave protection for high-frequency gig couriers.",
                    premium=29.0,
                    premium_frequency="weekly",
                    coverage_limit=2000.0,
                    policy_duration="7 days",
                    covered_events=["HEAVY_RAIN", "EXTREME_HEAT"],
                    trigger_conditions={
                        "HEAVY_RAIN": "Rainfall >= 50mm over 3 consecutive hours in registered delivery zone",
                        "EXTREME_HEAT": "Temperature >= 43°C during peak working hours (11:00 AM - 4:00 PM)",
                    },
                    waiting_period="24 hours",
                    exclusions=[
                        "Disruptions outside registered delivery zone",
                        "Pre-existing government curfews before policy start",
                        "Voluntary off-duty non-working hours",
                    ],
                    coverage_area_rules={
                        "primary_zone": "Chennai Delivery Zone",
                        "supported_subzones": ["Chennai Central", "Chennai South", "Chennai North", "OMR-ECR"],
                    },
                    active=True,
                ),
                InsurancePlan(
                    partner_id=partner.id,
                    name="Standard IncomeShield",
                    code="INCSH_STANDARD",
                    description="Comprehensive parametric protection covering heavy rain, urban flooding, and heatwaves.",
                    premium=49.0,
                    premium_frequency="weekly",
                    coverage_limit=5000.0,
                    policy_duration="7 days",
                    covered_events=["HEAVY_RAIN", "FLOOD", "EXTREME_HEAT"],
                    trigger_conditions={
                        "HEAVY_RAIN": "Rainfall >= 45mm over 3 consecutive hours",
                        "FLOOD": "Civic waterlogging advisory or road closure > 3 hours",
                        "EXTREME_HEAT": "Temperature >= 42°C during 11:00 AM - 4:00 PM",
                    },
                    waiting_period="24 hours",
                    exclusions=[
                        "Disruptions outside registered delivery zone",
                        "Voluntary offline status during undisrupted hours",
                    ],
                    coverage_area_rules={
                        "primary_zone": "Chennai Delivery Zone",
                        "supported_subzones": ["Chennai Central", "Chennai South", "Chennai North", "OMR-ECR", "West Chennai"],
                    },
                    active=True,
                ),
                InsurancePlan(
                    partner_id=partner.id,
                    name="Plus IncomeShield",
                    code="INCSH_PLUS",
                    description="Full-spectrum resilience coverage with expedited claim settlement and civic disruption shield.",
                    premium=79.0,
                    premium_frequency="weekly",
                    coverage_limit=10000.0,
                    policy_duration="7 days",
                    covered_events=["HEAVY_RAIN", "FLOOD", "EXTREME_HEAT", "WORK_DISRUPTION"],
                    trigger_conditions={
                        "HEAVY_RAIN": "Rainfall >= 40mm over 3 consecutive hours",
                        "FLOOD": "Waterlogging warning or road closure > 2 hours",
                        "EXTREME_HEAT": "Temperature >= 41°C during peak hours",
                        "WORK_DISRUPTION": "Civic curfew, grid collapse, or localized platform outage > 4 hours",
                    },
                    waiting_period="12 hours",
                    exclusions=[
                        "Disruptions in unverified zones without official IMD or civic telemetry",
                    ],
                    coverage_area_rules={
                        "primary_zone": "Chennai Delivery Zone",
                        "supported_subzones": ["All Chennai Metropolitan Subzones"],
                    },
                    active=True,
                ),
            ]
            for p in plans:
                db.add(p)

            # Seed demo active event
            initial_event = InsuranceEvent(
                event_type="HEAVY_RAIN",
                zone="Chennai Delivery Zone",
                start_time=datetime.now(timezone.utc) - timedelta(hours=2, minutes=45),
                duration="2h 45m",
                source="IMD Chennai Radar Telemetry",
                source_reference="IMD-RADAR-CHN-098",
                verification_status="VERIFIED",
                severity="SEVERE",
                telemetry_data={
                    "observed_rainfall_mm": 58.0,
                    "threshold_rainfall_mm": 50.0,
                    "duration_hours": 3,
                    "affected_subzones": ["Chennai South", "OMR-ECR", "Velachery", "Guindy"],
                },
            )
            db.add(initial_event)

        db.commit()
        print("\n✅ LEVELLY Database Seeded Successfully!")
        print("\nDemo Accounts:")
        print("  User:  arjun@levelly.app  / Levelly@123")
        print("  Admin: admin@levelly.app  / Admin@Levelly123")
        print("\nArjun's current state: Healthy State (Surplus Active)")
        print("  - Historical avg income: ₹24,000/month")
        print("  - Recent income: ₹24,500/month")
        print("  - Safety Wallet: ₹10,500 / ₹10,000 (105% - ₹500 surplus)")
        print("  - Distress Level: LOW")
        print("  - Resilience Score: 78/100")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
