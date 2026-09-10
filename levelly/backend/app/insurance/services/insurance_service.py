"""
LEVELLY IncomeShield — Core Insurance Service
Coordinates policy purchasing, status retrieval, documents, and existing LEVELLY context.
"""
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.insurance.models import (
    InsurancePlan,
    InsurancePolicy,
    InsuranceConsent,
    InsurancePartner,
    InsuranceEvent,
    InsurancePayout,
    InsuranceDocument,
)
from app.insurance.integrations.provider import get_insurance_provider
from app.models.wallet import Wallet
from app.models.financial_profile import FinancialProfile
from app.models.audit import AuditLog
from app.engines.income_intelligence import IncomeIntelligenceService
from app.services.notification_service import NotificationService


class InsuranceService:
    """Core domain service for LEVELLY IncomeShield."""

    def __init__(self, db: Session):
        self.db = db
        self.provider = get_insurance_provider()
        self.notifications = NotificationService(db)

    def get_plans(self) -> List[InsurancePlan]:
        """Fetch all active insurance plans."""
        plans = (
            self.db.query(InsurancePlan)
            .filter(InsurancePlan.active == True)
            .order_by(InsurancePlan.premium.asc())
            .all()
        )
        # If DB is empty, bootstrap with provider plans
        if not plans:
            self._bootstrap_plans()
            plans = self.db.query(InsurancePlan).filter(InsurancePlan.active == True).all()
        return plans

    def _bootstrap_plans(self):
        """Seed initial plans from the provider abstraction if not yet in DB."""
        provider_plans = self.provider.get_plans()
        partner = self.db.query(InsurancePartner).first()
        if not partner:
            partner = InsurancePartner(
                name="SafeWork Protection Partner",
                code="SAFEWORK-INS-01",
                partner_type="LICENSED_INSURER",
                active=True,
                contact_info={"support_email": "claims@safework-shield.in", "helpline": "1800-419-7443"},
            )
            self.db.add(partner)
            self.db.flush()

        for p in provider_plans:
            plan = InsurancePlan(
                partner_id=partner.id,
                name=p["name"],
                code=p["code"],
                description=p["description"],
                premium=p["premium"],
                premium_frequency=p["premium_frequency"],
                coverage_limit=p["coverage_limit"],
                policy_duration=p["policy_duration"],
                covered_events=p["covered_events"],
                trigger_conditions=p["trigger_conditions"],
                waiting_period=p["waiting_period"],
                exclusions=p["exclusions"],
                coverage_area_rules=p["coverage_area_rules"],
                active=True,
            )
            self.db.add(plan)
        self.db.commit()

    def get_plan(self, plan_id: int) -> Optional[InsurancePlan]:
        """Fetch a single active plan by its ID."""
        return self.db.query(InsurancePlan).filter_by(id=plan_id, active=True).first()

    def get_user_insurance_state(self, user_id: int) -> Dict[str, Any]:
        """
        Determine user's insurance backend state:
        NO_POLICY, PLAN_SELECTED, PURCHASE_REVIEW, PURCHASE_PENDING, ACTIVE, EXPIRED.
        """
        now = datetime.now(timezone.utc)
        active_policy = (
            self.db.query(InsurancePolicy)
            .filter(
                InsurancePolicy.user_id == user_id,
                InsurancePolicy.status == "ACTIVE",
                InsurancePolicy.end_date >= now,
            )
            .order_by(InsurancePolicy.created_at.desc())
            .first()
        )
        if active_policy:
            return {"state": "ACTIVE", "policy": active_policy, "selected_plan_id": active_policy.plan_id}

        # Check for draft/selected state
        draft_policy = (
            self.db.query(InsurancePolicy)
            .filter(
                InsurancePolicy.user_id == user_id,
                InsurancePolicy.status.in_(["PLAN_SELECTED", "PURCHASE_REVIEW", "PURCHASE_PENDING"]),
            )
            .order_by(InsurancePolicy.created_at.desc())
            .first()
        )
        if draft_policy:
            return {"state": draft_policy.status, "policy": draft_policy, "selected_plan_id": draft_policy.plan_id}

        # Check for recent expired policy
        expired_policy = (
            self.db.query(InsurancePolicy)
            .filter(
                InsurancePolicy.user_id == user_id,
                InsurancePolicy.status == "EXPIRED",
            )
            .order_by(InsurancePolicy.created_at.desc())
            .first()
        )
        if expired_policy:
            return {"state": "EXPIRED", "policy": expired_policy, "selected_plan_id": None}

        return {"state": "NO_POLICY", "policy": None, "selected_plan_id": None}

    def select_plan(self, user_id: int, plan_id: int) -> Dict[str, Any]:
        """Record plan selection for the user and transition state to PLAN_SELECTED."""
        plan = self.get_plan(plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Selected insurance plan not found or inactive")

        # Clean up any existing non-active draft policies for this user
        existing_drafts = (
            self.db.query(InsurancePolicy)
            .filter(
                InsurancePolicy.user_id == user_id,
                InsurancePolicy.status.in_(["PLAN_SELECTED", "PURCHASE_REVIEW", "PURCHASE_PENDING"]),
            )
            .all()
        )
        for d in existing_drafts:
            self.db.delete(d)

        now = datetime.now(timezone.utc)
        draft = InsurancePolicy(
            user_id=user_id,
            plan_id=plan.id,
            partner_id=plan.partner_id,
            policy_number=f"DRAFT-{user_id}-{plan.id}-{int(now.timestamp())}",
            status="PLAN_SELECTED",
            start_date=now,
            end_date=now + timedelta(days=7),
            premium=plan.premium,
            coverage_limit=plan.coverage_limit,
            covered_work_zone="Chennai Delivery Zone",
        )
        self.db.add(draft)
        self.db.commit()
        self.db.refresh(draft)

        return {
            "success": True,
            "message": f"Plan '{plan.name}' selected.",
            "plan_id": plan.id,
            "selected_plan_id": plan.id,
            "plan_name": plan.name,
            "state": "PLAN_SELECTED",
        }

    def get_user_policy(self, user_id: int) -> Optional[InsurancePolicy]:
        """Fetch current active policy for user."""
        now = datetime.now(timezone.utc)
        policy = (
            self.db.query(InsurancePolicy)
            .filter(
                InsurancePolicy.user_id == user_id,
                InsurancePolicy.status == "ACTIVE",
                InsurancePolicy.end_date >= now,
            )
            .order_by(InsurancePolicy.created_at.desc())
            .first()
        )
        return policy

    def purchase_policy(
        self,
        user_id: int,
        plan_id: int,
        terms_accepted: bool,
        terms_version: str = "v1.0",
        work_zone: str = "Chennai Delivery Zone",
    ) -> InsurancePolicy:
        """Enroll user into an insurance policy with explicit consent."""
        if not terms_accepted:
            raise HTTPException(
                status_code=400,
                detail="Explicit user consent and acceptance of policy terms is required",
            )

        plan = self.db.query(InsurancePlan).filter_by(id=plan_id, active=True).first()
        if not plan:
            raise HTTPException(status_code=404, detail="Selected insurance plan not found or inactive")

        # Check existing active policy
        existing = self.get_user_policy(user_id)
        # Expire previous policy and clean up any pending draft policies
        drafts = (
            self.db.query(InsurancePolicy)
            .filter(
                InsurancePolicy.user_id == user_id,
                InsurancePolicy.status.in_(["PLAN_SELECTED", "PURCHASE_REVIEW", "PURCHASE_PENDING"]),
            )
            .all()
        )
        for d in drafts:
            self.db.delete(d)

        if existing:
            # Expire previous policy to avoid duplicate billing
            existing.status = "EXPIRED"

        now = datetime.now(timezone.utc)
        # Record explicit consent
        consent = InsuranceConsent(
            user_id=user_id,
            plan_id=plan.id,
            terms_version=terms_version,
            confirmed=True,
            confirmed_at=now,
        )
        self.db.add(consent)

        # Provider issuance
        issuance = self.provider.purchase_policy(
            user_id=user_id,
            plan_code=plan.code,
            work_zone=work_zone,
            consent_confirmed=True,
        )

        policy_number = issuance["policy_number"]
        policy = InsurancePolicy(
            user_id=user_id,
            plan_id=plan.id,
            partner_id=plan.partner_id,
            policy_number=policy_number,
            status="ACTIVE",
            start_date=now,
            end_date=now + timedelta(days=7),
            premium=plan.premium,
            coverage_limit=plan.coverage_limit,
            covered_work_zone=work_zone,
        )
        self.db.add(policy)
        self.db.flush()

        # Generate default policy documents
        doc_schedule = InsuranceDocument(
            policy_id=policy.id,
            plan_id=plan.id,
            title=f"Policy Schedule — {policy.policy_number}",
            document_type="POLICY_SCHEDULE",
            file_url=f"/api/insurance/documents/{policy.policy_number}/schedule",
        )
        doc_terms = InsuranceDocument(
            policy_id=policy.id,
            plan_id=plan.id,
            title="Parametric Income Protection Terms & Conditions",
            document_type="TERMS_AND_CONDITIONS",
            file_url="/api/insurance/documents/terms-v1",
        )
        self.db.add(doc_schedule)
        self.db.add(doc_terms)

        # Audit log
        audit = AuditLog(
            user_id=user_id,
            event_type="insurance_policy_purchased",
            action=f"Enrolled in {plan.name} ({policy.policy_number}) with explicit consent",
            entity_type="insurance_policy",
            entity_id=policy.id,
        )
        self.db.add(audit)

        # Notification
        self.notifications.create(
            user_id=user_id,
            title="IncomeShield Active",
            message=f"Your {plan.name} coverage is now active until {(now + timedelta(days=7)).strftime('%d %b %Y')}.",
            notification_type="insurance_policy_activated",
            priority="high",
            action_url="/incomeshield/policy",
        )

        self.db.commit()
        self.db.refresh(policy)
        return policy

    def get_active_events(self, zone: Optional[str] = None) -> List[InsuranceEvent]:
        """Fetch active or recent disruption events."""
        query = self.db.query(InsuranceEvent).order_by(InsuranceEvent.start_time.desc())
        if zone:
            query = query.filter(InsuranceEvent.zone == zone)
        events = query.limit(10).all()

        # If none seeded, create initial verified heavy rain event in Chennai
        if not events:
            now = datetime.now(timezone.utc)
            initial_event = InsuranceEvent(
                event_type="HEAVY_RAIN",
                zone="Chennai Delivery Zone",
                start_time=now - timedelta(hours=2, minutes=45),
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
            self.db.add(initial_event)
            self.db.commit()
            self.db.refresh(initial_event)
            events = [initial_event]
        return events

    def get_user_payouts(self, user_id: int) -> List[InsurancePayout]:
        """Fetch all claim payouts for user's policies."""
        payouts = (
            self.db.query(InsurancePayout)
            .join(InsurancePolicy, InsurancePayout.policy_id == InsurancePolicy.id)
            .filter(InsurancePolicy.user_id == user_id)
            .order_by(InsurancePayout.created_at.desc())
            .all()
        )
        return payouts

    def get_user_documents(self, user_id: int) -> List[InsuranceDocument]:
        """Fetch legal policy documents for user."""
        docs = (
            self.db.query(InsuranceDocument)
            .join(InsurancePolicy, InsuranceDocument.policy_id == InsurancePolicy.id)
            .filter(InsurancePolicy.user_id == user_id)
            .order_by(InsuranceDocument.created_at.desc())
            .all()
        )
        if not docs:
            # Fallback to standard policy terms templates
            docs = [
                InsuranceDocument(
                    title="Parametric Income Protection Terms & Conditions",
                    document_type="TERMS_AND_CONDITIONS",
                    file_url="/api/insurance/documents/terms-v1",
                ),
                InsuranceDocument(
                    title="Exclusions & Geographical Scope Guide",
                    document_type="EXCLUSIONS_GUIDE",
                    file_url="/api/insurance/documents/exclusions-v1",
                ),
            ]
        return docs

    def get_insurance_status(self, user_id: int) -> Dict[str, Any]:
        """Unified dashboard context for the IncomeShield frontend."""
        policy = self.get_user_policy(user_id)
        events = self.get_active_events()
        payouts = self.get_user_payouts(user_id)
        latest_payout = payouts[0] if payouts else None

        # Determine backend state (Section 13)
        state_info = self.get_user_insurance_state(user_id)
        insurance_state = state_info["state"]

        # Existing Safety Wallet
        wallet = (
            self.db.query(Wallet)
            .filter(Wallet.user_id == user_id, Wallet.wallet_type == "SAFETY", Wallet.is_active == True)
            .first()
        )
        safety_bal = wallet.balance if wallet else 8200.0
        safety_tgt = wallet.target_amount if wallet else 10000.0

        # Existing Resilience Score
        profile = self.db.query(FinancialProfile).filter_by(user_id=user_id).first()
        score = profile.resilience_score if profile else 58

        # Existing Income Intelligence
        income_engine = IncomeIntelligenceService(self.db)
        income_summary = income_engine.get_income_summary(user_id)
        historical_monthly = income_summary.get("historical_avg_income", 27300.0)
        weekly_avg = round(historical_monthly / 4.33, 2)
        daily_avg = round(weekly_avg / 6.0, 2)

        return {
            "has_active_policy": policy is not None,
            "insurance_state": insurance_state,
            "selected_plan_id": state_info["selected_plan_id"],
            "policy": policy,
            "active_events": events,
            "latest_payout": latest_payout,
            "safety_wallet_balance": safety_bal,
            "safety_wallet_target": safety_tgt,
            "safety_wallet_shortfall": max(0.0, safety_tgt - safety_bal),
            "resilience_score": score,
            "average_daily_income": daily_avg,
            "average_weekly_income": weekly_avg,
        }
