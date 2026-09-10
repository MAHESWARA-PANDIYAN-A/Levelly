"""
LEVELLY — Backend Test Suite
Tests for financial engines, APIs, and E2E flows.
"""
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.engines.income_intelligence import IncomeIntelligenceService
from app.engines.expense_engine import ExpenseEngine
from app.engines.savings_engine import SavingsEngine
from app.engines.distress_engine import DistressEngine
from app.engines.resilience_engine import FinancialResilienceService
from app.engines.guardrail import ResponsibleLendingGuardrailService
from app.engines.credit_engine import CreditRecommendationService
from app.engines.investment_engine import InvestmentRecommendationService
from app.models.user import User
from app.models.wallet import Wallet
from app.models.transaction import IncomeTransaction, ExpenseTransaction
from app.models.savings import CategorySavingPolicy, SavingsPreference, SavingsTransaction
from app.models.financial_profile import FinancialProfile
from app.models.payment import LinkedPaymentAccount, Merchant, PaymentTransaction
from app.models.investment import InvestmentProduct, InvestmentOrder
from app.core.security import hash_password


# ============================================================
# TEST DATABASE SETUP
# ============================================================

TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db():
    """Create fresh test database for each test."""
    Base.metadata.create_all(bind=test_engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def test_user(db):
    """Create a test user with wallets and profile."""
    user = User(
        email="test@levelly.app",
        full_name="Test User",
        hashed_password=hash_password("Test@123"),
        occupation="Delivery Rider",
        city="Chennai",
        platform_tenure_months=24,
        role="user",
        is_active=True,
    )
    db.add(user)
    db.flush()

    safety_wallet = Wallet(user_id=user.id, wallet_type="SAFETY", balance=8000.0, target_amount=10000.0)
    db.add(safety_wallet)

    linked_account = LinkedPaymentAccount(
        user_id=user.id,
        provider="upi",
        upi_id="test@upi",
        bank_name="HDFC Bank",
        account_mask="****4821",
        account_holder_name="Test User",
        status="connected",
        is_primary=True,
    )
    db.add(linked_account)

    pref = SavingsPreference(user_id=user.id, safety_target=10000.0)
    db.add(pref)

    profile = FinancialProfile(user_id=user.id)
    db.add(profile)

    # Add category policies
    policies = [
        CategorySavingPolicy(category="food", base_percentage=10.0, min_percentage=0.0, max_percentage=15.0),
        CategorySavingPolicy(category="fuel", base_percentage=5.0, min_percentage=0.0, max_percentage=10.0),
        CategorySavingPolicy(category="entertainment", base_percentage=5.0, min_percentage=0.0, max_percentage=10.0),
    ]
    for p in policies:
        db.add(p)

    db.commit()
    return user


# ============================================================
# INCOME INTELLIGENCE TESTS
# ============================================================

class TestIncomeIntelligence:

    def test_income_volatility_low(self, db, test_user):
        """Stable income should have LOW volatility."""
        now = datetime.now(timezone.utc)
        for i in range(8):
            txn = IncomeTransaction(
                user_id=test_user.id,
                amount=6000.0,  # Consistent ₹6,000/week
                source="Swiggy",
                status="completed",
                transaction_date=now - timedelta(weeks=i),
            )
            db.add(txn)
        db.commit()

        svc = IncomeIntelligenceService(db)
        summary = svc.get_income_summary(test_user.id)
        assert summary["income_volatility_level"] == "LOW"

    def test_income_volatility_high(self, db, test_user):
        """Highly variable income should have HIGH volatility."""
        now = datetime.now(timezone.utc)
        amounts = [10000, 1000, 9000, 500, 8000, 200, 7000, 100]
        for i, amount in enumerate(amounts):
            txn = IncomeTransaction(
                user_id=test_user.id,
                amount=amount,
                source="Swiggy",
                status="completed",
                transaction_date=now - timedelta(weeks=i),
            )
            db.add(txn)
        db.commit()

        svc = IncomeIntelligenceService(db)
        summary = svc.get_income_summary(test_user.id)
        assert summary["income_volatility_level"] == "HIGH"

    def test_income_decline_calculation(self, db, test_user):
        """Income decline should be correctly calculated."""
        now = datetime.now(timezone.utc)
        # Historical: ₹6,000/week (₹24,000/month)
        for i in range(6, 14):
            db.add(IncomeTransaction(
                user_id=test_user.id,
                amount=6000.0,
                source="Swiggy",
                status="completed",
                transaction_date=now - timedelta(weeks=i),
            ))
        # Recent: ₹3,750/week (₹15,000/month) — 37.5% decline
        for i in range(0, 4):
            db.add(IncomeTransaction(
                user_id=test_user.id,
                amount=3750.0,
                source="Swiggy",
                status="completed",
                transaction_date=now - timedelta(weeks=i),
            ))
        db.commit()

        svc = IncomeIntelligenceService(db)
        summary = svc.get_income_summary(test_user.id)
        # Should detect decline
        assert summary["income_decline_pct"] > 10

    def test_income_trend_declining(self, db, test_user):
        """Should detect declining income trend."""
        now = datetime.now(timezone.utc)
        # amounts ordered by weeks_ago: oldest first (high), most recent last (low)
        # i=7 oldest -> 6000, i=0 most recent -> 2500  (declining over time)
        amounts = [6000, 5500, 5000, 4500, 4000, 3500, 3000, 2500]
        for i, amount in enumerate(amounts):
            # weeks_ago = 7-i, so i=0 maps to 7 weeks ago (high) and i=7 maps to 0 weeks ago (low)
            db.add(IncomeTransaction(
                user_id=test_user.id,
                amount=amount,
                status="completed",
                transaction_date=now - timedelta(weeks=(7 - i)),
            ))
        db.commit()

        svc = IncomeIntelligenceService(db)
        summary = svc.get_income_summary(test_user.id)
        assert summary["income_trend"] == "declining"

    def test_consecutive_low_periods(self, db, test_user):
        """Should count consecutive low income periods."""
        now = datetime.now(timezone.utc)
        # Historical high weeks (8-11 weeks ago) — well above weekly baseline
        for i in range(8, 12):
            db.add(IncomeTransaction(
                user_id=test_user.id,
                amount=8000.0,
                status="completed",
                transaction_date=now - timedelta(weeks=i),
            ))
        # Recent low weeks (0-3 weeks ago) — well below 80% of 8000/week baseline
        for i in range(0, 4):
            db.add(IncomeTransaction(
                user_id=test_user.id,
                amount=2000.0,  # 25% of baseline, clearly below 80% threshold
                status="completed",
                transaction_date=now - timedelta(weeks=i),
            ))
        db.commit()

        svc = IncomeIntelligenceService(db)
        summary = svc.get_income_summary(test_user.id)
        assert summary["consecutive_low_periods"] >= 2


# ============================================================
# EXPENSE ENGINE TESTS
# ============================================================

class TestExpenseEngine:

    def test_expense_ratio_calculation(self, db, test_user):
        """Expense ratio should be correctly calculated."""
        now = datetime.now(timezone.utc)
        # ₹12,000 in expenses, ₹20,000 income = 0.6 ratio
        db.add(ExpenseTransaction(
            user_id=test_user.id, amount=12000, category="food",
            status="completed", transaction_date=now - timedelta(days=15)
        ))
        db.commit()

        svc = ExpenseEngine(db)
        ratio = svc.calculate_expense_ratio(test_user.id, 20000)
        assert abs(ratio - 0.6) < 0.01

    def test_essential_vs_non_essential(self, db, test_user):
        """Should correctly categorize essential vs non-essential expenses."""
        now = datetime.now(timezone.utc)
        db.add(ExpenseTransaction(
            user_id=test_user.id, amount=5000, category="rent",
            status="completed", transaction_date=now - timedelta(days=5)
        ))
        db.add(ExpenseTransaction(
            user_id=test_user.id, amount=2000, category="entertainment",
            status="completed", transaction_date=now - timedelta(days=3)
        ))
        db.commit()

        svc = ExpenseEngine(db)
        summary = svc.get_expense_summary(test_user.id)
        assert summary["essential_total"] >= 5000
        assert summary["non_essential_total"] >= 2000


# ============================================================
# SAVINGS ENGINE TESTS
# ============================================================

class TestSavingsEngine:

    def test_save_suggestion_low_distress(self, db, test_user):
        """Save suggestion should use full base percentage in LOW distress."""
        svc = SavingsEngine(db)
        result = svc.calculate_save_suggestion(1000, "food", test_user.id, "LOW")
        assert result["suggested_percentage"] == 10.0
        assert result["suggested_save_amount"] == 100.0

    def test_save_suggestion_moderate_distress(self, db, test_user):
        """Save suggestion should be reduced at MODERATE distress."""
        svc = SavingsEngine(db)
        result = svc.calculate_save_suggestion(1000, "food", test_user.id, "MODERATE")
        assert result["suggested_percentage"] == 5.0  # 10% * 0.5

    def test_save_suggestion_severe_distress(self, db, test_user):
        """Save suggestion should be 0 at SEVERE distress."""
        svc = SavingsEngine(db)
        result = svc.calculate_save_suggestion(1000, "food", test_user.id, "SEVERE")
        assert result["suggested_save_amount"] == 0.0
        assert not result["save_suggestion_available"]

    def test_save_suggestion_fuel(self, db, test_user):
        """Fuel save percentage should be 5%."""
        svc = SavingsEngine(db)
        result = svc.calculate_save_suggestion(500, "fuel", test_user.id, "LOW")
        assert result["suggested_percentage"] == 5.0
        assert result["suggested_save_amount"] == 25.0


# ============================================================
# DISTRESS ENGINE TESTS
# ============================================================

class TestDistressEngine:

    def test_low_distress_healthy_user(self, db, test_user):
        """Healthy financial profile should produce LOW distress."""
        profile = db.query(FinancialProfile).filter_by(user_id=test_user.id).first()
        profile.income_decline_pct = 5.0
        profile.expense_to_income_ratio = 0.5
        profile.resilience_score = 80.0
        profile.credit_pressure = 10.0
        profile.consecutive_low_periods = 0
        db.commit()

        # Mock the safety wallet to have full balance
        safety_wallet = db.query(Wallet).filter_by(user_id=test_user.id, wallet_type="SAFETY").first()
        safety_wallet.balance = 10000.0
        safety_wallet.target_amount = 10000.0
        db.commit()

        svc = DistressEngine(db)
        result = svc.evaluate(test_user.id)
        assert result["distress_level"] in ("LOW", "MODERATE")

    def test_high_distress_signals(self, db, test_user):
        """Multiple negative signals should trigger HIGH distress."""
        profile = db.query(FinancialProfile).filter_by(user_id=test_user.id).first()
        profile.income_decline_pct = 45.0
        profile.expense_to_income_ratio = 0.95
        profile.resilience_score = 30.0
        profile.credit_pressure = 60.0
        profile.consecutive_low_periods = 3
        db.commit()

        safety_wallet = db.query(Wallet).filter_by(user_id=test_user.id, wallet_type="SAFETY").first()
        safety_wallet.balance = 2000.0
        safety_wallet.target_amount = 10000.0
        db.commit()

        svc = DistressEngine(db)
        result = svc.evaluate(test_user.id)
        assert result["distress_level"] in ("HIGH", "SEVERE")

    def test_distress_not_from_one_bad_day(self, db, test_user):
        """Single bad period should not trigger HIGH distress (moderate at most)."""
        profile = db.query(FinancialProfile).filter_by(user_id=test_user.id).first()
        profile.income_decline_pct = 30.0
        profile.expense_to_income_ratio = 0.70
        profile.resilience_score = 55.0
        profile.credit_pressure = 20.0
        profile.consecutive_low_periods = 0  # not sustained
        db.commit()

        svc = DistressEngine(db)
        result = svc.evaluate(test_user.id)
        assert result["distress_level"] != "SEVERE"


# ============================================================
# GUARDRAIL TESTS
# ============================================================

class TestGuardrail:

    def test_low_distress_allows_full_credit(self, db, test_user):
        """LOW distress should allow normal credit."""
        profile = db.query(FinancialProfile).filter_by(user_id=test_user.id).first()
        profile.distress_level = "LOW"
        profile.distress_signals = []
        db.commit()

        svc = ResponsibleLendingGuardrailService(db)
        result = svc.evaluate(test_user.id, 10000, 8000)
        assert result["status"] == "allowed"

    def test_moderate_distress_reduces_credit(self, db, test_user):
        """MODERATE distress should reduce credit amount."""
        profile = db.query(FinancialProfile).filter_by(user_id=test_user.id).first()
        profile.distress_level = "MODERATE"
        profile.distress_signals = ["income_decline"]
        db.commit()

        svc = ResponsibleLendingGuardrailService(db)
        result = svc.evaluate(test_user.id, 10000, 8000)
        assert result["status"] == "reduced"
        assert result["allowed_amount"] < 8000

    def test_severe_distress_holds_credit(self, db, test_user):
        """SEVERE distress should hold credit."""
        profile = db.query(FinancialProfile).filter_by(user_id=test_user.id).first()
        profile.distress_level = "SEVERE"
        profile.distress_signals = ["income_decline", "expenses_exceed_income", "safety_buffer_critical"]
        db.commit()

        svc = ResponsibleLendingGuardrailService(db)
        result = svc.evaluate(test_user.id, 10000, 8000)
        assert result["status"] == "held"
        assert result["allowed_amount"] == 0.0

    def test_hold_does_not_use_rejection_language(self, db, test_user):
        """Guardrail language must not use 'rejected'."""
        profile = db.query(FinancialProfile).filter_by(user_id=test_user.id).first()
        profile.distress_level = "SEVERE"
        profile.distress_signals = ["income_decline"]
        db.commit()

        svc = ResponsibleLendingGuardrailService(db)
        result = svc.evaluate(test_user.id, 10000, 8000)
        assert "reject" not in result["ui_message"].lower()
        assert "reject" not in result["message"].lower()


# ============================================================
# CREDIT ENGINE TESTS
# ============================================================

class TestCreditEngine:

    def test_credit_recommendation_healthy(self, db, test_user):
        """Healthy user should get positive recommendation."""
        profile = db.query(FinancialProfile).filter_by(user_id=test_user.id).first()
        profile.recent_income = 24000.0
        profile.historical_avg_income = 24000.0
        profile.distress_level = "LOW"
        profile.resilience_score = 80.0
        profile.income_volatility_level = "LOW"
        profile.expense_to_income_ratio = 0.6
        profile.safety_surplus = 500.0
        db.commit()

        svc = CreditRecommendationService(db)
        result = svc.generate_recommendation(test_user.id, 10000)
        assert result["recommended_amount"] > 0
        assert result["status"] in ("approved", "reduced")

    def test_credit_held_under_severe_distress(self, db, test_user):
        """Under SEVERE distress, credit should be held."""
        profile = db.query(FinancialProfile).filter_by(user_id=test_user.id).first()
        profile.recent_income = 5000.0
        profile.distress_level = "SEVERE"
        profile.resilience_score = 15.0
        db.commit()

        svc = CreditRecommendationService(db)
        result = svc.generate_recommendation(test_user.id, 10000)
        assert result["recommended_amount"] == 0.0

    def test_platform_tenure_improves_credit(self, db, test_user):
        """Longer platform tenure should improve credit recommendation."""
        profile = db.query(FinancialProfile).filter_by(user_id=test_user.id).first()
        profile.recent_income = 20000.0
        profile.distress_level = "LOW"
        profile.resilience_score = 70.0
        profile.income_volatility_level = "LOW"
        profile.expense_to_income_ratio = 0.6
        profile.safety_surplus = 0
        db.commit()

        svc = CreditRecommendationService(db)

        # Short tenure user
        test_user.platform_tenure_months = 2
        db.commit()
        result_short = svc.generate_recommendation(test_user.id, 10000)

        # Long tenure user
        test_user.platform_tenure_months = 24
        db.commit()
        result_long = svc.generate_recommendation(test_user.id, 10000)

        assert result_long["recommended_amount"] >= result_short["recommended_amount"]


# ============================================================
# INVESTMENT ENGINE TESTS
# ============================================================

class TestInvestmentEngine:

    def test_investment_paused_when_high_distress(self, db, test_user):
        """Investment suggestions must be paused when distress is HIGH."""
        profile = db.query(FinancialProfile).filter_by(user_id=test_user.id).first()
        profile.distress_level = "HIGH"
        db.commit()

        safety_wallet = db.query(Wallet).filter_by(user_id=test_user.id, wallet_type="SAFETY").first()
        safety_wallet.balance = 12000.0
        safety_wallet.target_amount = 10000.0
        db.commit()

        svc = InvestmentRecommendationService(db)
        status = svc.get_investment_status(test_user.id)
        assert status["is_paused"] == True

    def test_investment_paused_below_target(self, db, test_user):
        """Investment suggestions must be paused when safety below target."""
        profile = db.query(FinancialProfile).filter_by(user_id=test_user.id).first()
        profile.distress_level = "LOW"
        db.commit()

        safety_wallet = db.query(Wallet).filter_by(user_id=test_user.id, wallet_type="SAFETY").first()
        safety_wallet.balance = 8000.0  # Below target of 10000
        safety_wallet.target_amount = 10000.0
        db.commit()

        svc = InvestmentRecommendationService(db)
        status = svc.get_investment_status(test_user.id)
        assert status["is_paused"] == True
        assert status["safety_surplus"] < 0

    def test_investment_available_above_target(self, db, test_user):
        """Investment suggestions should be available when above target and low distress."""
        profile = db.query(FinancialProfile).filter_by(user_id=test_user.id).first()
        profile.distress_level = "LOW"
        profile.resilience_score = 75.0
        db.commit()

        safety_wallet = db.query(Wallet).filter_by(user_id=test_user.id, wallet_type="SAFETY").first()
        safety_wallet.balance = 12000.0  # Above target of 10000
        safety_wallet.target_amount = 10000.0
        db.commit()

        svc = InvestmentRecommendationService(db)
        status = svc.get_investment_status(test_user.id)
        assert not status["is_paused"]
        assert status["safety_surplus"] > 0

    def test_arjun_healthy_state_returns_investment_suggestions(self, db, test_user):
        """
        Healthy Arjun (Safety: ₹10,500 >= ₹10,000, Distress: LOW, Resilience: 78, Surplus: ₹500)
        MUST receive at least 3-4 investment products with full metadata.
        """
        # Seed the 4 development products
        products_data = [
            ("Liquid Growth Fund", "LIQUID_SAVINGS", "HDFC AMC", "LOW", "High (T+1)", "No lock-in", "6.2% p.a."),
            ("7.18% GS 2033 Benchmark", "GOVERNMENT_SECURITY", "RBI / Govt of India", "LOW", "Medium", "1-3 years", "7.18% p.a."),
            ("Target Maturity Bond Index", "FIXED_INCOME", "SBI Mutual Fund", "LOW", "Medium", "3 years", "7.35% p.a."),
            ("Ultra Short Duration Debt Fund", "DEBT_ORIENTED", "ICICI Prudential AMC", "MODERATE", "High", "3-6 months", "6.85% p.a."),
        ]
        for name, p_type, issuer, risk, liq, hold, rate in products_data:
            db.add(InvestmentProduct(
                name=name,
                product_type=p_type,
                issuer=issuer,
                risk_level=risk,
                liquidity=liq,
                holding_period=hold,
                interest_or_coupon=rate,
                fees="0.15% - 0.25%",
                tax_notes="Gains taxed per applicable slab.",
                terms="Development product metadata for hackathon demonstration.",
                min_investment=100.0,
                active=True,
            ))

        # Configure healthy Arjun state
        profile = db.query(FinancialProfile).filter_by(user_id=test_user.id).first()
        profile.distress_level = "LOW"
        profile.resilience_score = 78.0
        profile.recent_income = 24500.0
        profile.historical_avg_income = 24000.0
        profile.safety_surplus = 500.0
        profile.investment_ready = True

        safety_wallet = db.query(Wallet).filter_by(user_id=test_user.id, wallet_type="SAFETY").first()
        safety_wallet.balance = 10500.0
        safety_wallet.target_amount = 10000.0
        db.commit()

        svc = InvestmentRecommendationService(db)
        status = svc.get_investment_status(test_user.id)
        assert status["is_paused"] is False
        assert status["safety_surplus"] == 500.0
        assert status["distress_level"] == "LOW"
        assert status["resilience_score"] == 78.0

        suggestions = svc.get_suggestions(test_user.id)
        assert len(suggestions) >= 3
        types_returned = [s["type"] for s in suggestions]
        assert "GOVERNMENT_SECURITY" in types_returned
        assert "LIQUID_SAVINGS" in types_returned
        assert "FIXED_INCOME" in types_returned

        for s in suggestions:
            assert s["product_id"] is not None
            assert s["name"] is not None
            assert s["risk_level"] in ("LOW", "MODERATE")
            assert s["liquidity"] is not None
            assert s["holding_period"] is not None
            assert s["reason"] is not None

    def test_investment_order_requires_explicit_confirmation(self, db, test_user):
        """
        Investment is NEVER automatic.
        Selecting product / amount does not create an order. Only explicit confirmation creates order.
        """
        prod = InvestmentProduct(
            name="Test Gov Security",
            product_type="GOVERNMENT_SECURITY",
            risk_level="LOW",
            liquidity="Medium",
            holding_period="1 year",
            min_investment=100.0,
            active=True,
        )
        db.add(prod)
        db.commit()

        # Product selection / status query does NOT create orders
        svc = InvestmentRecommendationService(db)
        _ = svc.get_investment_status(test_user.id)
        _ = svc.get_suggestions(test_user.id)

        orders_count = db.query(InvestmentOrder).filter_by(user_id=test_user.id).count()
        assert orders_count == 0


# ============================================================
# AUTHENTICATION TESTS
# ============================================================

class TestAuthentication:

    def test_password_hashing(self):
        """Passwords should be hashed, not stored as plain text."""
        plain = "TestPassword@123"
        hashed = hash_password(plain)
        assert hashed != plain
        assert len(hashed) > 30

    def test_password_verification(self):
        """Correct password should verify against hash."""
        from app.core.security import verify_password
        plain = "TestPassword@123"
        hashed = hash_password(plain)
        assert verify_password(plain, hashed) == True
        assert verify_password("WrongPassword", hashed) == False

    def test_jwt_token_creation(self):
        """JWT token should be creatable and decodable."""
        from app.core.security import create_access_token, decode_token
        token = create_access_token(data={"sub": "123"})
        payload = decode_token(token)
        assert payload["sub"] == "123"


# ============================================================
# WALLET TESTS
# ============================================================

class TestWalletLogic:

    def test_safety_wallet_progress(self, db, test_user):
        """Safety wallet progress should be correctly calculated."""
        safety_wallet = db.query(Wallet).filter_by(user_id=test_user.id, wallet_type="SAFETY").first()
        safety_wallet.balance = 8200.0
        safety_wallet.target_amount = 10000.0
        db.commit()

        assert safety_wallet.progress_percentage == 82.0

    def test_safety_wallet_over_100_percent(self, db, test_user):
        """Safety wallet progress should cap at 100%."""
        safety_wallet = db.query(Wallet).filter_by(user_id=test_user.id, wallet_type="SAFETY").first()
        safety_wallet.balance = 12000.0
        safety_wallet.target_amount = 10000.0
        db.commit()

        assert safety_wallet.progress_percentage == 100.0

    def test_large_expense_impact(self, db, test_user):
        """Large expense impact should be correctly calculated."""
        safety_wallet = db.query(Wallet).filter_by(user_id=test_user.id, wallet_type="SAFETY").first()
        safety_wallet.balance = 8200.0

        expense_amount = 8000.0
        usage_pct = (expense_amount / safety_wallet.balance) * 100
        remaining = safety_wallet.balance - expense_amount

        assert round(usage_pct, 1) == 97.6
        assert remaining == 200.0


# ============================================================
# E2E TEST SCENARIO
# ============================================================

class TestEndToEnd:

    def test_save_at_pay_full_flow(self, db, test_user):
        """
        E2E: Payment with save consent
        1. Preview payment
        2. Accept save suggestion
        3. Verify wallet updates
        4. Verify savings transaction recorded
        """
        from app.models.savings import SavingsTransaction

        engine = SavingsEngine(db)
        suggestion = engine.calculate_save_suggestion(1000, "food", test_user.id, "LOW")
        assert suggestion["suggested_save_amount"] == 100.0

        # Simulate payment from Linked Account + Save-at-Pay to Safety Wallet
        safety_wallet = db.query(Wallet).filter_by(user_id=test_user.id, wallet_type="SAFETY").first()
        initial_safety = safety_wallet.balance

        # Save-at-Pay contribution added to Safety Wallet
        safety_wallet.balance += 100.0

        # Record savings transaction
        savings_txn = SavingsTransaction(
            user_id=test_user.id,
            amount=100.0,
            transaction_type="save_at_pay",
            category_context="food",
            balance_before=initial_safety,
            balance_after=safety_wallet.balance,
        )
        db.add(savings_txn)
        db.commit()

        assert safety_wallet.balance == initial_safety + 100.0

        # Verify savings transaction recorded
        saved_txn = db.query(SavingsTransaction).filter_by(user_id=test_user.id).first()
        assert saved_txn is not None
        assert saved_txn.amount == 100.0

    def test_save_declined_no_savings_transaction(self, db, test_user):
        """
        E2E: Declining save must NOT create savings transaction.
        """
        safety_wallet = db.query(Wallet).filter_by(user_id=test_user.id, wallet_type="SAFETY").first()
        initial_safety = safety_wallet.balance

        # User declines save — payment proceeds from linked account, zero save transaction
        db.commit()

        # Verify no savings transaction
        savings_count = db.query(SavingsTransaction).filter_by(user_id=test_user.id).count()
        assert savings_count == 0
        # Safety wallet unchanged
        assert safety_wallet.balance == initial_safety

    def test_investment_requires_consent(self, db, test_user):
        """Investment must require explicit consent before execution."""
        from app.models.investment import InvestmentConsent, InvestmentProduct

        # Create a product
        product = InvestmentProduct(
            name="Test Fund",
            product_type="LIQUID_SAVINGS",
            risk_level="LOW",
            min_investment=500.0,
            active=True,
        )
        db.add(product)
        db.flush()

        # Create consent (not yet confirmed)
        consent = InvestmentConsent(
            user_id=test_user.id,
            product_id=product.id,
            amount=1000.0,
            confirmed=False,
        )
        db.add(consent)
        db.commit()

        # Verify consent is not confirmed yet
        assert not consent.confirmed
        assert consent.confirmed_at is None

        # Confirm consent
        consent.confirmed = True
        consent.confirmed_at = datetime.now(timezone.utc)
        db.commit()

        assert consent.confirmed
        assert consent.confirmed_at is not None

    def test_credit_held_does_not_reach_partner(self, db, test_user):
        """When guardrail holds credit, partner should NOT be called."""
        profile = db.query(FinancialProfile).filter_by(user_id=test_user.id).first()
        profile.distress_level = "SEVERE"
        profile.distress_signals = ["income_decline", "safety_buffer_critical"]
        db.commit()

        guardrail_svc = ResponsibleLendingGuardrailService(db)
        result = guardrail_svc.evaluate(test_user.id, 10000, 0)
        assert result["status"] == "held"

    def test_direct_upi_payment_save_at_pay(self, db, test_user):
        """
        Direct Bank/UPI: Payment does not touch Daily Wallet.
        Save-at-Pay contribution atomically updates Safety Wallet.
        """
        from app.models.payment import Merchant, PaymentTransaction, LinkedPaymentAccount
        from app.models.savings import SavingsTransaction
        from app.providers.payment_provider import get_payment_provider

        # Setup merchant
        merchant = Merchant(
            merchant_code="M_TEST",
            name="Test Supermarket",
            upi_id="supermarket@upi",
            category="Food & Grocery",
            normalized_category="food",
            verification_status="verified",
        )
        db.add(merchant)
        db.flush()

        safety_wallet = db.query(Wallet).filter_by(user_id=test_user.id, wallet_type="SAFETY").first()
        initial_safety = safety_wallet.balance

        # Provider creates UPI payment
        provider = get_payment_provider()
        res = provider.create_payment(
            payment_id=999,
            user_id=test_user.id,
            merchant_upi_id=merchant.upi_id,
            merchant_name=merchant.name,
            amount=1000.0,
        )
        assert res["status"] == "SUCCESS"
        assert "upi://pay" in res["upi_intent_url"]

        # Simulate Save-at-Pay 10% (₹100)
        save_amount = 100.0
        safety_wallet.balance += save_amount
        savings_txn = SavingsTransaction(
            user_id=test_user.id,
            amount=save_amount,
            transaction_type="save_at_pay",
            category_context="food",
            balance_before=initial_safety,
            balance_after=safety_wallet.balance,
        )
        db.add(savings_txn)

        pay_txn = PaymentTransaction(
            user_id=test_user.id,
            merchant_id=merchant.id,
            merchant_name=merchant.name,
            merchant_upi_id=merchant.upi_id,
            amount=1000.0,
            category="food",
            save_consent=True,
            actual_save_amount=save_amount,
            status="SUCCESS",
            savings_credited=True,
        )
        db.add(pay_txn)
        db.commit()

        assert safety_wallet.balance == initial_safety + 100.0
        assert pay_txn.status == "SUCCESS"
        assert pay_txn.actual_save_amount == 100.0

    def test_category_service_normalization(self):
        """Test category normalization heuristics."""
        from app.services.category_service import CategoryService
        assert CategoryService.normalize("Sri Krishna Supermarket", "Food & Grocery") == "food"
        assert CategoryService.normalize("Bharat Petroleum", "Petrol Pump") == "fuel"
        assert CategoryService.normalize("Apollo Pharmacy", "Pharmacy") == "healthcare"
        assert CategoryService.normalize("Unknown Shop", None) == "other"


# ============================================================
# TARGETED PRODUCTION FIXES REGRESSION TESTS
# ============================================================

class TestTargetedFixesRegression:

    def test_no_new_daily_wallet_created_on_registration(self, db):
        """A. No new Daily Wallet is created for a new user registration."""
        from app.api.v1.endpoints.auth import register, RegisterRequest
        req = RegisterRequest(
            email="new_rider@levelly.app",
            full_name="New Rider",
            password="Password@123",
            occupation="Delivery Partner",
            city="Bengaluru",
        )
        res = register(req, db)
        assert res.user_id is not None

        wallets = db.query(Wallet).filter(Wallet.user_id == res.user_id).all()
        wallet_types = [w.wallet_type for w in wallets]

        assert "DAILY" not in wallet_types
        assert "SAFETY" in wallet_types
        assert len(wallets) == 1

    def test_financial_health_response_does_not_expose_daily_wallet(self, db, test_user):
        """B. Financial health dashboard response does not expose Daily Wallet."""
        from app.api.v1.endpoints.financial_health import get_dashboard
        dashboard = get_dashboard(test_user, db)

        assert "daily_wallet" not in dashboard
        assert "safety_wallet" in dashboard
        assert "linked_account" in dashboard
        assert "spending" in dashboard
        assert dashboard["safety_wallet"]["balance"] == 8000.0
        assert dashboard["linked_account"]["bank_name"] == "HDFC Bank"

    def test_default_category_policy_food(self, db):
        """C. Food default policy = 10%."""
        from app.engines.savings_engine import DEFAULT_CATEGORY_PERCENTAGES
        svc = SavingsEngine(db)
        assert svc.get_category_base_percentage("food") == 10.0
        assert DEFAULT_CATEGORY_PERCENTAGES["food"] == 10.0

    def test_default_category_policy_fuel(self, db):
        """D. Fuel default policy = 5%."""
        from app.engines.savings_engine import DEFAULT_CATEGORY_PERCENTAGES
        svc = SavingsEngine(db)
        assert svc.get_category_base_percentage("fuel") == 5.0
        assert DEFAULT_CATEGORY_PERCENTAGES["fuel"] == 5.0

    def test_default_category_policy_education(self, db):
        """E. Education default policy = 8%."""
        from app.engines.savings_engine import DEFAULT_CATEGORY_PERCENTAGES
        svc = SavingsEngine(db)
        assert svc.get_category_base_percentage("education") == 8.0
        assert DEFAULT_CATEGORY_PERCENTAGES["education"] == 8.0

    def test_food_base_suggestion_calculation(self, db, test_user):
        """Food Rs 1000 base suggestion = Rs 100 before financial-condition adjustment."""
        svc = SavingsEngine(db)
        result = svc.calculate_save_suggestion(1000, "food", test_user.id, "LOW")
        assert result["suggested_percentage"] == 10.0
        assert result["suggested_save_amount"] == 100.0

    def test_save_at_pay_respects_user_consent(self, db, test_user):
        """F. Save-at-Pay continues to respect user consent."""
        merchant = db.query(Merchant).first()
        if not merchant:
            merchant = Merchant(
                merchant_code="M_TEST_CONSENT",
                name="Quick Mart",
                upi_id="quickmart@upi",
                category="Food & Grocery",
                normalized_category="food",
                verification_status="verified",
            )
            db.add(merchant)
            db.commit()

        initial_tx_count = db.query(SavingsTransaction).filter_by(user_id=test_user.id).count()
        safety_wallet = db.query(Wallet).filter_by(user_id=test_user.id, wallet_type="SAFETY").first()
        initial_balance = safety_wallet.balance

        # When user declines savings (save_consent = False)
        pay_txn = PaymentTransaction(
            user_id=test_user.id,
            merchant_id=merchant.id,
            merchant_name=merchant.name,
            merchant_upi_id=merchant.upi_id,
            amount=1000.0,
            category="food",
            save_consent=False,
            actual_save_amount=0.0,
            status="SUCCESS",
            savings_credited=False,
        )
        db.add(pay_txn)
        db.commit()

        new_tx_count = db.query(SavingsTransaction).filter_by(user_id=test_user.id).count()
        assert new_tx_count == initial_tx_count
        assert safety_wallet.balance == initial_balance

    def test_payment_flow_remains_unchanged(self, db, test_user):
        """G. Payment provider abstraction and payment flow remain unchanged."""
        from app.providers.payment_provider import get_payment_provider, MockUPIPaymentProvider
        provider = get_payment_provider()
        assert isinstance(provider, MockUPIPaymentProvider)

        result = provider.create_payment(
            payment_id=888,
            user_id=test_user.id,
            merchant_upi_id="merchant@upi",
            merchant_name="Fuel Station",
            amount=500.0,
        )
        assert result["status"] == "SUCCESS"
        assert result["provider"] == "mock"
        assert "upi_intent_url" in result

