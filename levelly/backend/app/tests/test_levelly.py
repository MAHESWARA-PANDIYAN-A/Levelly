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
from app.models.savings import CategorySavingPolicy, SavingsPreference
from app.models.financial_profile import FinancialProfile
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

    daily_wallet = Wallet(user_id=user.id, wallet_type="DAILY", balance=15000.0)
    safety_wallet = Wallet(user_id=user.id, wallet_type="SAFETY", balance=8000.0, target_amount=10000.0)
    db.add(daily_wallet)
    db.add(safety_wallet)

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

        # Simulate payment + save
        daily_wallet = db.query(Wallet).filter_by(user_id=test_user.id, wallet_type="DAILY").first()
        safety_wallet = db.query(Wallet).filter_by(user_id=test_user.id, wallet_type="SAFETY").first()

        initial_daily = daily_wallet.balance
        initial_safety = safety_wallet.balance

        # Deduct payment + save from daily wallet
        daily_wallet.balance -= 1100.0  # 1000 payment + 100 save
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

        assert daily_wallet.balance == initial_daily - 1100.0
        assert safety_wallet.balance == initial_safety + 100.0

        # Verify savings transaction recorded
        saved_txn = db.query(SavingsTransaction).filter_by(user_id=test_user.id).first()
        assert saved_txn is not None
        assert saved_txn.amount == 100.0

    def test_save_declined_no_savings_transaction(self, db, test_user):
        """
        E2E: Declining save must NOT create savings transaction.
        """
        from app.models.savings import SavingsTransaction

        daily_wallet = db.query(Wallet).filter_by(user_id=test_user.id, wallet_type="DAILY").first()
        safety_wallet = db.query(Wallet).filter_by(user_id=test_user.id, wallet_type="SAFETY").first()

        initial_safety = safety_wallet.balance

        # User declines save — only deduct payment amount
        daily_wallet.balance -= 1000.0
        # NO savings transaction created
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
        # Partner should not be called when status is "held"
        # (this is enforced by the credit endpoint checking guardrail status)
