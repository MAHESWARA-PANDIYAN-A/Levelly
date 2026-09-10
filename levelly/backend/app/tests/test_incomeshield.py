"""
LEVELLY — IncomeShield Native Insurance Module Test Suite
Covers unit, integration, and end-to-end parametric insurance flows.
"""
import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

from app.core.database import Base
from app.models.user import User
from app.models.wallet import Wallet
from app.models.financial_profile import FinancialProfile
from app.models.transaction import IncomeTransaction
from app.models.savings import SavingsTransaction
from app.core.security import hash_password
from app.insurance.models import (
    InsurancePartner,
    InsurancePlan,
    InsuranceConsent,
    InsuranceEvent,
    InsurancePayout,
)
from app.insurance.services.insurance_service import InsuranceService
from app.insurance.services.income_impact_service import InsuranceIncomeImpactService
from app.insurance.services.trigger_service import InsuranceTriggerService
from app.insurance.services.payout_service import InsurancePayoutService


TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db():
    """Create fresh in-memory SQLite database for each test."""
    Base.metadata.create_all(bind=test_engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def partner(db):
    """Seed insurance partner."""
    p = InsurancePartner(
        name="Tata AIG Parametric Protect",
        code="mock_partner_01",
        partner_type="LICENSED_INSURER",
        active=True,
    )
    db.add(p)
    db.commit()
    return p


@pytest.fixture
def test_user(db):
    """Create a verified test user with Safety Wallet."""
    user = User(
        email="arjun.delivery@levelly.app",
        full_name="Arjun Kumar",
        hashed_password=hash_password("Arjun@123"),
        occupation="Delivery Partner",
        city="Chennai",
        platform_tenure_months=18,
        role="user",
        is_active=True,
    )
    db.add(user)
    db.flush()

    # Safety Wallet with current balance ₹8,200 and target ₹10,000
    wallet = Wallet(user_id=user.id, wallet_type="SAFETY", balance=8200.0, target_amount=10000.0)
    db.add(wallet)

    profile = FinancialProfile(user_id=user.id, resilience_score=58.0, distress_level="LOW")
    db.add(profile)

    # Seed 4 weeks of income
    now = datetime.now(timezone.utc)
    for i in range(4):
        txn = IncomeTransaction(
            user_id=user.id,
            amount=6800.0,  # ~ ₹6,800/week
            source="Swiggy",
            status="completed",
            transaction_date=now - timedelta(weeks=i),
        )
        db.add(txn)

    db.commit()
    return user


@pytest.fixture
def standard_plan(db, partner):
    """Seed Standard IncomeShield Plan."""
    plan = InsurancePlan(
        partner_id=partner.id,
        name="Standard IncomeShield",
        code="INCSH_STANDARD",
        description="Comprehensive parametric protection against intense rain, waterlogging, and extreme heatwaves.",
        premium=49.0,
        premium_frequency="WEEKLY",
        coverage_limit=2500.0,
        policy_duration="7_DAYS",
        waiting_period="0_HOURS",
        covered_events=["HEAVY_RAIN", "FLOOD", "EXTREME_HEAT", "WORK_DISRUPTION"],
        trigger_conditions={
            "rainfall_mm_threshold": 35.0,
            "duration_hours_threshold": 2.0,
            "heat_index_celsius": 42.0,
        },
        exclusions=["Pre-announced civic strikes", "Willful non-operation", "Off-platform work"],
        coverage_area_rules={"zones": ["Chennai Delivery Zone", "OMR-ECR Corridor", "Tambaram-Porur"]},
        active=True,
    )
    db.add(plan)
    db.commit()
    return plan


class TestIncomeShieldPlansAndConsent:

    def test_plan_retrieval(self, db, standard_plan):
        """Verify plan retrieval returns correct terms and active status."""
        svc = InsuranceService(db)
        plans = svc.get_plans()
        assert len(plans) == 1
        assert plans[0].name == "Standard IncomeShield"
        assert plans[0].coverage_limit == 2500.0
        assert plans[0].premium == 49.0

    def test_purchase_requires_explicit_consent(self, db, test_user, standard_plan):
        """Purchase must fail if terms_accepted is False."""
        svc = InsuranceService(db)
        with pytest.raises(HTTPException) as exc_info:
            svc.purchase_policy(
                user_id=test_user.id,
                plan_id=standard_plan.id,
                terms_accepted=False,
            )
        assert exc_info.value.status_code == 400
        assert "Explicit user consent" in exc_info.value.detail

    def test_purchase_with_consent_creates_active_policy(self, db, test_user, standard_plan):
        """Purchase with explicit consent creates ACTIVE policy and consent record."""
        svc = InsuranceService(db)
        policy = svc.purchase_policy(
            user_id=test_user.id,
            plan_id=standard_plan.id,
            terms_accepted=True,
            terms_version="2026.1",
        )
        assert policy.status == "ACTIVE"
        assert policy.user_id == test_user.id
        assert policy.coverage_limit == standard_plan.coverage_limit
        assert policy.premium == standard_plan.premium
        assert policy.policy_number.startswith("INCSH-")

        # Verify consent record
        consent = db.query(InsuranceConsent).filter_by(user_id=test_user.id).first()
        assert consent is not None
        assert consent.confirmed is True
        assert consent.terms_version == "2026.1"

    def test_repurchase_replaces_active_policy(self, db, test_user, standard_plan):
        """User purchasing new policy smoothly supersedes previous active policy."""
        svc = InsuranceService(db)
        p1 = svc.purchase_policy(user_id=test_user.id, plan_id=standard_plan.id, terms_accepted=True)
        assert p1.status == "ACTIVE"

        p2 = svc.purchase_policy(user_id=test_user.id, plan_id=standard_plan.id, terms_accepted=True)
        assert p2.status == "ACTIVE"

        db.refresh(p1)
        assert p1.status == "EXPIRED"


class TestIncomeImpactEngine:

    def test_income_impact_reuses_existing_income_intelligence(self, db, test_user):
        """Calculates expected earnings, disrupted earnings, and impact gap without inventing arbitrary payouts."""
        impact_svc = InsuranceIncomeImpactService(db)
        impact = impact_svc.calculate_estimated_impact(test_user.id)

        assert impact["user_id"] == test_user.id
        assert impact["expected_daily_income"] > 0
        assert impact["estimated_disrupted_income"] < impact["expected_daily_income"]
        assert impact["estimated_income_impact"] == round(
            impact["expected_daily_income"] - impact["estimated_disrupted_income"], 2
        )
        assert "earning history" in impact["disclaimer"].lower()


class TestParametricTriggerEvaluation:

    def test_disruption_below_threshold_trigger_not_reached(self, db, test_user, standard_plan):
        """
        External event detected below threshold:
        Trigger evaluation status is NOT_REACHED.
        NO payout must be created!
        """
        ins_svc = InsuranceService(db)
        policy = ins_svc.purchase_policy(user_id=test_user.id, plan_id=standard_plan.id, terms_accepted=True)

        # Light rain: 20mm (threshold is 50mm)
        event = InsuranceEvent(
            event_type="HEAVY_RAIN",
            zone="Chennai Delivery Zone",
            duration=1.0,
            source="MockWeatherService",
            verification_status="VERIFIED",
            telemetry_data={"observed_rainfall_mm": 20.0, "threshold_rainfall_mm": 50.0},
        )
        db.add(event)
        db.commit()

        trigger_svc = InsuranceTriggerService(db)
        evaluation = trigger_svc.evaluate_policy_for_event(
            policy_id=policy.id,
            event_id=event.id,
        )

        assert evaluation.status == "NOT_REACHED"
        assert "did not satisfy" in evaluation.reason

        # Verify NO payout was created
        payouts = db.query(InsurancePayout).filter_by(policy_id=policy.id).all()
        assert len(payouts) == 0

    def test_disruption_exceeding_threshold_trigger_reached(self, db, test_user, standard_plan):
        """
        External event exceeds threshold:
        Trigger evaluation is REACHED.
        Payout is initiated in PROCESSING status (governed by partner limit).
        """
        ins_svc = InsuranceService(db)
        policy = ins_svc.purchase_policy(user_id=test_user.id, plan_id=standard_plan.id, terms_accepted=True)

        # Severe rain: 58mm over 3.2 hours (threshold is 50mm)
        event = InsuranceEvent(
            event_type="HEAVY_RAIN",
            zone="Chennai Delivery Zone",
            duration=3.2,
            source="MockWeatherService",
            verification_status="VERIFIED",
            telemetry_data={"observed_rainfall_mm": 58.0, "threshold_rainfall_mm": 50.0},
        )
        db.add(event)
        db.commit()

        trigger_svc = InsuranceTriggerService(db)
        evaluation = trigger_svc.evaluate_policy_for_event(
            policy_id=policy.id,
            event_id=event.id,
        )

        assert evaluation.status == "REACHED"

        # Verify payout created in PROCESSING status
        payout = db.query(InsurancePayout).filter_by(policy_id=policy.id, event_id=event.id).first()
        assert payout is not None
        assert payout.status == "PROCESSING"
        assert payout.amount == 750.0  # mock partner capped amount <= coverage_limit


class TestPayoutAndSafetyWalletGuidance:

    def test_payout_completion_and_optional_safety_wallet_allocation(self, db, test_user, standard_plan):
        """
        Verify payout completion settles payout, and user can explicitly
        allocate a chosen amount into their EXISTING Safety Wallet.
        """
        ins_svc = InsuranceService(db)
        policy = ins_svc.purchase_policy(user_id=test_user.id, plan_id=standard_plan.id, terms_accepted=True)

        event = InsuranceEvent(
            event_type="HEAVY_RAIN",
            zone="Chennai Delivery Zone",
            duration=3.0,
            verification_status="VERIFIED",
            telemetry_data={"observed_rainfall_mm": 60.0, "threshold_rainfall_mm": 50.0},
        )
        db.add(event)
        db.flush()

        trigger_svc = InsuranceTriggerService(db)
        trigger_svc.evaluate_policy_for_event(policy.id, event.id)

        payout = db.query(InsurancePayout).filter_by(policy_id=policy.id).first()
        assert payout.status == "PROCESSING"

        # Settle payout
        payout_svc = InsurancePayoutService(db)
        settled_payout = payout_svc.complete_payout(payout.id)
        assert settled_payout.status == "COMPLETED"

        # Check existing Safety Wallet before transfer: ₹8,200
        wallet = db.query(Wallet).filter_by(user_id=test_user.id, wallet_type="SAFETY").first()
        assert wallet.balance == 8200.0

        # User chooses to allocate ₹500 from the ₹750 payout into Safety Wallet
        transfer_result = payout_svc.move_to_safety_wallet(
            user_id=test_user.id,
            payout_id=settled_payout.id,
            amount=500.0,
        )

        assert transfer_result["transferred_amount"] == 500.0
        assert transfer_result["safety_wallet_balance"] == 8700.0

        # Safety Wallet updated in DB
        db.refresh(wallet)
        assert wallet.balance == 8700.0

        # Verify SavingsTransaction recorded under existing model
        stxn = db.query(SavingsTransaction).filter_by(user_id=test_user.id).first()
        assert stxn is not None
        assert stxn.amount == 500.0
        assert stxn.category_context == "incomeshield_payout"


class TestFullEndToEndJourneys:

    def test_e2e_journey_1_coverage_to_payout_and_savings(self, db, test_user, standard_plan):
        """
        Full End-to-End Test 1 (Section 61):
        Login -> Explore -> Personalized Protection -> Plan Details -> Explicit Consent ->
        Active Policy -> Disruption Event -> Monitoring -> Trigger Reached ->
        Payout Processing -> Payout Completed -> User adds to Safety Wallet.
        """
        ins_svc = InsuranceService(db)
        impact_svc = InsuranceIncomeImpactService(db)
        trigger_svc = InsuranceTriggerService(db)
        payout_svc = InsurancePayoutService(db)

        # 1. Check status (NO_POLICY)
        status = ins_svc.get_insurance_status(test_user.id)
        assert status["has_active_policy"] is False

        # 2. Get impact estimate
        impact = impact_svc.calculate_estimated_impact(test_user.id)
        assert impact["estimated_income_impact"] > 0

        # 3. Explicit Consent & Purchase
        policy = ins_svc.purchase_policy(
            user_id=test_user.id,
            plan_id=standard_plan.id,
            terms_accepted=True,
            terms_version="2026.1",
        )
        assert policy.status == "ACTIVE"

        # 4. Check status (ACTIVE)
        status = ins_svc.get_insurance_status(test_user.id)
        assert status["has_active_policy"] is True

        # 5. External Disruption
        event = InsuranceEvent(
            event_type="HEAVY_RAIN",
            zone="Chennai Delivery Zone",
            duration=3.5,
            source="MockWeatherService",
            verification_status="VERIFIED",
            telemetry_data={"observed_rainfall_mm": 55.0, "threshold_rainfall_mm": 50.0},
        )
        db.add(event)
        db.commit()

        # 6. Trigger Evaluation (REACHED)
        eval_res = trigger_svc.evaluate_policy_for_event(
            policy_id=policy.id,
            event_id=event.id,
        )
        assert eval_res.status == "REACHED"

        # 7. Payout in PROCESSING
        payout = db.query(InsurancePayout).filter_by(policy_id=policy.id).first()
        assert payout.status == "PROCESSING"

        # 8. Partner settles payout
        settled = payout_svc.complete_payout(payout.id)
        assert settled.status == "COMPLETED"
        assert settled.amount == 750.0

        # 9. Post-payout Safety Wallet transfer
        res = payout_svc.move_to_safety_wallet(
            user_id=test_user.id,
            payout_id=settled.id,
            amount=400.0,
        )
        assert res["safety_wallet_balance"] == 8600.0

    def test_e2e_journey_2_disruption_without_payout(self, db, test_user, standard_plan):
        """
        Full End-to-End Test 2 (Section 62):
        Active Policy -> Disruption -> Trigger Not Reached -> No payout created.
        Guarantees that external event alone does not create payouts.
        """
        ins_svc = InsuranceService(db)
        trigger_svc = InsuranceTriggerService(db)

        policy = ins_svc.purchase_policy(test_user.id, standard_plan.id, terms_accepted=True)

        # Mild shower that stops early
        event = InsuranceEvent(
            event_type="HEAVY_RAIN",
            zone="Chennai Delivery Zone",
            duration=0.5,
            verification_status="VERIFIED",
            telemetry_data={"observed_rainfall_mm": 18.0, "threshold_rainfall_mm": 50.0},
        )
        db.add(event)
        db.commit()

        eval_res = trigger_svc.evaluate_policy_for_event(
            policy_id=policy.id,
            event_id=event.id,
        )
        assert eval_res.status == "NOT_REACHED"

        # Payout table must be completely empty
        payout_count = db.query(InsurancePayout).count()
        assert payout_count == 0

    def test_cross_user_isolation(self, db, test_user, standard_plan):
        """Ensure User A cannot access or move User B's payout."""
        # Create second user
        user_b = User(
            email="kavitha.courier@levelly.app",
            full_name="Kavitha R",
            hashed_password=hash_password("Pass@123"),
            occupation="Courier",
            city="Chennai",
            role="user",
            is_active=True,
        )
        db.add(user_b)
        db.flush()
        wallet_b = Wallet(user_id=user_b.id, wallet_type="SAFETY", balance=5000.0, target_amount=10000.0)
        db.add(wallet_b)
        db.commit()

        ins_svc = InsuranceService(db)
        payout_svc = InsurancePayoutService(db)
        trigger_svc = InsuranceTriggerService(db)

        policy_a = ins_svc.purchase_policy(test_user.id, standard_plan.id, terms_accepted=True)
        event = InsuranceEvent(
            event_type="HEAVY_RAIN",
            zone="Chennai Delivery Zone",
            verification_status="VERIFIED",
            telemetry_data={"observed_rainfall_mm": 55.0, "threshold_rainfall_mm": 50.0},
        )
        db.add(event)
        db.flush()

        trigger_svc.evaluate_policy_for_event(policy_a.id, event.id)
        payout_a = db.query(InsurancePayout).filter_by(policy_id=policy_a.id).first()
        payout_svc.complete_payout(payout_a.id)

        # User B attempts to access User A's payout
        with pytest.raises(HTTPException) as exc_info:
            payout_svc.move_to_safety_wallet(
                user_id=user_b.id,
                payout_id=payout_a.id,
                amount=500.0,
            )
        assert exc_info.value.status_code == 403


# ============================================================
# PART A — PLAN-FIRST FLOW & STATE PROGRESSION TESTS
# ============================================================

class TestPlanFirstFlowAndState:
    """
    Validates that IncomeShield plan selection happens FIRST before personalized info,
    and tests distinct state lifecycle:
    NO_POLICY -> PLAN_SELECTED -> PURCHASE_REVIEW -> ACTIVE
    """

    def test_state_lifecycle_no_policy_to_plan_selected(self, db, test_user, standard_plan):
        """User begins with NO_POLICY. Selecting a plan transitions to PLAN_SELECTED."""
        ins_svc = InsuranceService(db)

        # 1. Initially NO_POLICY
        state_info = ins_svc.get_user_insurance_state(test_user.id)
        assert state_info["state"] == "NO_POLICY"
        assert state_info["selected_plan_id"] is None

        # 2. Select Plan
        res = ins_svc.select_plan(test_user.id, standard_plan.id)
        assert res["state"] == "PLAN_SELECTED"
        assert res["selected_plan_id"] == standard_plan.id

        # 3. State is now PLAN_SELECTED
        updated_state = ins_svc.get_user_insurance_state(test_user.id)
        assert updated_state["state"] == "PLAN_SELECTED"
        assert updated_state["selected_plan_id"] == standard_plan.id

    def test_plan_details_retrieval(self, db, standard_plan):
        """Plan details can be retrieved by plan_id."""
        ins_svc = InsuranceService(db)
        plan = ins_svc.get_plan(standard_plan.id)
        assert plan.id == standard_plan.id
        assert plan.name == "Standard IncomeShield"
        assert plan.premium == standard_plan.premium
        assert plan.coverage_limit == standard_plan.coverage_limit

    def test_personalized_protection_after_plan_selection(self, db, test_user, standard_plan):
        """
        Personalized protection must only be evaluated for the selected plan
        and match Arjun's benchmarks:
        Average Daily: ₹1,050, Weekly: ₹6,800, Disrupted: ₹300, Estimated Impact: ₹750
        """
        impact_svc = InsuranceIncomeImpactService(db)
        impact = impact_svc.calculate_personalized_plan_impact(
            user_id=test_user.id,
            plan=standard_plan,
            zone="Chennai Delivery Zone",
        )

        assert impact["expected_daily_income"] == 1050.0
        assert impact["typical_weekly_income"] == 6800.0
        assert impact["estimated_disrupted_income"] == 300.0
        assert impact["estimated_income_impact"] == 750.0
        assert "not your guaranteed insurance payout" in impact["disclaimer"].lower()
        assert impact["example_event"]["selected_plan"] == standard_plan.name
        assert impact["example_event"]["covered_area"] == "Chennai work zone"

    def test_change_plan_updates_draft_policy(self, db, test_user, partner, standard_plan):
        """User can change plan from Standard to Basic without creating orphan active policies."""
        basic_plan = InsurancePlan(
            partner_id=partner.id,
            name="Basic IncomeShield",
            code="INCSH_BASIC",
            description="Basic weather protection for gig workers.",
            premium=29.0,
            coverage_limit=1500.0,
            active=True,
        )
        db.add(basic_plan)
        db.commit()

        ins_svc = InsuranceService(db)

        # First select Standard
        ins_svc.select_plan(test_user.id, standard_plan.id)
        st1 = ins_svc.get_user_insurance_state(test_user.id)
        assert st1["selected_plan_id"] == standard_plan.id

        # Change to Basic
        ins_svc.select_plan(test_user.id, basic_plan.id)
        st2 = ins_svc.get_user_insurance_state(test_user.id)
        assert st2["selected_plan_id"] == basic_plan.id

    def test_purchase_activates_policy_and_reopen_shows_active(self, db, test_user, standard_plan):
        """
        After confirm protection, policy transitions to ACTIVE.
        Reopening IncomeShield returns ACTIVE policy, not the plan selection flow.
        """
        ins_svc = InsuranceService(db)

        # Select plan first
        ins_svc.select_plan(test_user.id, standard_plan.id)

        # Purchase with explicit consent
        policy = ins_svc.purchase_policy(
            user_id=test_user.id,
            plan_id=standard_plan.id,
            terms_accepted=True,
            work_zone="Chennai Delivery Zone",
        )
        assert policy.status == "ACTIVE"
        assert policy.policy_number.startswith("INCSH-")
        assert policy.covered_work_zone == "Chennai Delivery Zone"

        # Reopen status check
        status = ins_svc.get_insurance_status(test_user.id)
        assert status["has_active_policy"] is True
        assert status["insurance_state"] == "ACTIVE"
        assert status["policy"].id == policy.id
        assert status["policy"].plan.name == "Standard IncomeShield"
