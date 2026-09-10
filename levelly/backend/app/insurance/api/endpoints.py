"""
LEVELLY IncomeShield — API Endpoints
Provides authenticated REST endpoints for insurance discovery, enrollment,
disruption monitoring, trigger evaluations, payouts, and Safety Wallet integration.
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.insurance.models import (
    InsurancePlan,
    InsurancePolicy,
    InsuranceEvent,
    InsurancePayout,
    InsuranceTriggerEvaluation,
    InsuranceDocument,
)
from app.insurance.schemas import (
    InsurancePlanOut,
    InsurancePolicyOut,
    InsurancePurchaseRequest,
    InsuranceSelectPlanRequest,
    InsurancePersonalizedImpactOut,
    InsuranceEventOut,
    InsuranceIncomeImpactOut,
    InsuranceTriggerEvaluationOut,
    InsurancePayoutOut,
    InsurancePayoutMoveRequest,
    InsuranceDocumentOut,
    InsuranceStatusOut,
    SimulateDisruptionRequest,
)
from app.insurance.services import (
    InsuranceService,
    InsuranceIncomeImpactService,
    InsuranceTriggerService,
    InsurancePayoutService,
)

router = APIRouter()


def _format_policy(p: InsurancePolicy) -> Dict[str, Any]:
    return {
        "id": p.id,
        "user_id": p.user_id,
        "plan_id": p.plan_id,
        "plan_name": p.plan.name if p.plan else "IncomeShield Plan",
        "partner_name": p.partner.name if p.partner else "SafeWork Protection Partner",
        "policy_number": p.policy_number,
        "status": p.status,
        "start_date": p.start_date,
        "end_date": p.end_date,
        "premium": p.premium,
        "coverage_limit": p.coverage_limit,
        "covered_work_zone": p.covered_work_zone,
        "created_at": p.created_at,
        "documents": [
            {
                "id": d.id,
                "title": d.title,
                "document_type": d.document_type,
                "file_url": d.file_url,
                "created_at": d.created_at,
            }
            for d in (p.documents or [])
        ],
    }


def _format_payout(p: InsurancePayout) -> Dict[str, Any]:
    amt_display = f"₹{p.amount:,.0f}" if p.amount is not None else "Amount will be confirmed by your insurance partner."
    return {
        "id": p.id,
        "policy_id": p.policy_id,
        "event_id": p.event_id,
        "payout_id_from_partner": p.payout_id_from_partner,
        "amount": p.amount,
        "currency": p.currency,
        "status": p.status,
        "reason": p.reason,
        "processed_at": p.processed_at,
        "destination_reference": p.destination_reference,
        "destination_type": p.destination_type,
        "created_at": p.created_at,
        "amount_display": amt_display,
    }


# ============================================================
# 1. STATUS & DISCOVERY
# ============================================================

@router.get("/status", response_model=InsuranceStatusOut)
def get_insurance_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Unified status summary for the IncomeShield dashboard."""
    svc = InsuranceService(db)
    status_data = svc.get_insurance_status(current_user.id)
    policy_out = _format_policy(status_data["policy"]) if status_data["policy"] else None
    latest_payout_out = _format_payout(status_data["latest_payout"]) if status_data["latest_payout"] else None

    return {
        **status_data,
        "policy": policy_out,
        "latest_payout": latest_payout_out,
    }


@router.get("/plans", response_model=List[InsurancePlanOut])
def list_insurance_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all available parametric insurance plans."""
    try:
        svc = InsuranceService(db)
        plans = svc.get_plans()
        return [
            {
                "id": p.id,
                "name": p.name,
                "code": p.code,
                "description": p.description,
                "premium": p.premium,
                "premium_frequency": p.premium_frequency,
                "coverage_limit": p.coverage_limit,
                "policy_duration": p.policy_duration,
                "covered_events": p.covered_events or [],
                "trigger_conditions": p.trigger_conditions or {},
                "waiting_period": p.waiting_period,
                "exclusions": p.exclusions or [],
                "coverage_area_rules": p.coverage_area_rules or {},
                "active": p.active,
                "partner_name": p.partner.name if p.partner else "SafeWork Protection Partner",
            }
            for p in plans
        ]
    except HTTPException:
        raise
    except Exception as exc:
        import traceback
        tb = traceback.format_exc()
        print(f"[ERROR] /api/insurance/plans failed: {tb}")
        raise HTTPException(
            status_code=503,
            detail=f"Insurance plans unavailable: {type(exc).__name__}: {exc}",
        ) from exc


@router.get("/plans/{plan_id}", response_model=InsurancePlanOut)
def get_insurance_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve details for a specific parametric insurance plan."""
    svc = InsuranceService(db)
    plan = svc.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Insurance plan not found")
    return {
        "id": plan.id,
        "name": plan.name,
        "code": plan.code,
        "description": plan.description,
        "premium": plan.premium,
        "premium_frequency": plan.premium_frequency,
        "coverage_limit": plan.coverage_limit,
        "policy_duration": plan.policy_duration,
        "covered_events": plan.covered_events or [],
        "trigger_conditions": plan.trigger_conditions or {},
        "waiting_period": plan.waiting_period,
        "exclusions": plan.exclusions or [],
        "coverage_area_rules": plan.coverage_area_rules or {},
        "active": plan.active,
        "partner_name": plan.partner.name if plan.partner else "SafeWork Protection Partner",
    }


@router.post("/select-plan")
def select_insurance_plan(
    request: InsuranceSelectPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Select an insurance plan before viewing personalized income protection information.
    Records plan selection event and transitions backend state to PLAN_SELECTED.
    """
    svc = InsuranceService(db)
    result = svc.select_plan(current_user.id, request.plan_id)
    return result


@router.get("/personalized/{plan_id}", response_model=InsurancePersonalizedImpactOut)
def get_personalized_plan_impact(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return personalized protection and earning disruption calculations specifically
    for the selected plan.
    Consumes existing LEVELLY Income Intelligence and does not duplicate financial engines.
    """
    svc = InsuranceService(db)
    plan = svc.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Selected insurance plan not found")

    impact_svc = InsuranceIncomeImpactService(db)
    result = impact_svc.calculate_personalized_plan_impact(
        user_id=current_user.id,
        plan=plan,
        zone=current_user.city or "Chennai Delivery Zone",
    )
    return result


# ============================================================
# 2. POLICY MANAGEMENT & PURCHASE
# ============================================================

@router.get("/policy")
def get_current_policy(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve user's active IncomeShield policy."""
    svc = InsuranceService(db)
    policy = svc.get_user_policy(current_user.id)
    if not policy:
        return {"has_policy": False, "policy": None}
    return {"has_policy": True, "policy": _format_policy(policy)}


@router.post("/purchase")
def purchase_policy(
    request: InsurancePurchaseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Enroll in an IncomeShield plan with mandatory explicit consent.
    Does NOT auto-enroll or silently charge without acceptance of terms.
    """
    svc = InsuranceService(db)
    policy = svc.purchase_policy(
        user_id=current_user.id,
        plan_id=request.plan_id,
        terms_accepted=request.terms_accepted,
        terms_version=request.terms_version,
        work_zone=request.work_zone or "Chennai Delivery Zone",
    )
    return {
        "success": True,
        "message": "Your protection is active.",
        "policy": _format_policy(policy),
    }


# ============================================================
# 3. DISRUPTION EVENTS & IMPACT
# ============================================================

@router.get("/events", response_model=List[InsuranceEventOut])
def list_disruption_events(
    zone: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List recent and active disruption events affecting registered zones."""
    svc = InsuranceService(db)
    events = svc.get_active_events(zone)
    return events


@router.get("/events/{event_id}", response_model=InsuranceEventOut)
def get_event_details(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get granular telemetry and verification status for a disruption event."""
    event = db.query(InsuranceEvent).filter_by(id=event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Disruption event not found")
    return event


@router.get("/events/{event_id}/impact", response_model=InsuranceIncomeImpactOut)
def get_event_income_impact(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Calculate estimated income impact for this user during a disruption event.
    Reuses existing LEVELLY Income Intelligence Engine.
    """
    event = db.query(InsuranceEvent).filter_by(id=event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Disruption event not found")

    svc = InsuranceIncomeImpactService(db)
    impact = svc.calculate_estimated_impact(
        user_id=current_user.id,
        event_type=event.event_type,
        zone=event.zone,
        severity=event.severity,
        event_id=event.id,
    )
    return impact


@router.get("/events/{event_id}/trigger", response_model=InsuranceTriggerEvaluationOut)
def get_event_trigger_status(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Check parametric trigger condition evaluation for the current user's active policy.
    Never guarantees payout unless status is REACHED.
    """
    ins_svc = InsuranceService(db)
    policy = ins_svc.get_user_policy(current_user.id)
    if not policy:
        raise HTTPException(status_code=400, detail="No active policy found for user")

    trigger_svc = InsuranceTriggerService(db)
    evaluation = trigger_svc.evaluate_policy_for_event(policy.id, event_id)
    return evaluation


# ============================================================
# 4. PAYOUTS & SAFETY WALLET INTEGRATION
# ============================================================

@router.get("/payouts", response_model=List[InsurancePayoutOut])
def list_user_payouts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all claim payouts for the authenticated user."""
    svc = InsuranceService(db)
    payouts = svc.get_user_payouts(current_user.id)
    return [_format_payout(p) for p in payouts]


@router.get("/payouts/{payout_id}", response_model=InsurancePayoutOut)
def get_payout_details(
    payout_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get status and details of a specific claim payout."""
    payout = db.query(InsurancePayout).filter_by(id=payout_id).first()
    if not payout:
        raise HTTPException(status_code=404, detail="Payout record not found")

    # Security check: User A cannot inspect User B's payout
    policy = db.query(InsurancePolicy).filter_by(id=payout.policy_id).first()
    if not policy or policy.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied to this payout record")

    return _format_payout(payout)


@router.post("/payouts/{payout_id}/move-to-safety")
def move_payout_to_safety(
    payout_id: int,
    request: InsurancePayoutMoveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    User-directed transfer of an insurance payout into their existing LEVELLY Safety Wallet.
    Respects worker autonomy; never auto-deducts.
    """
    svc = InsurancePayoutService(db)
    result = svc.move_to_safety_wallet(
        user_id=current_user.id,
        payout_id=payout_id,
        amount=request.amount,
    )
    return result


# ============================================================
# 5. DOCUMENTS & SUPPORT
# ============================================================

@router.get("/documents", response_model=List[InsuranceDocumentOut])
def list_policy_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fetch policy schedules, terms, and exclusions documents."""
    svc = InsuranceService(db)
    docs = svc.get_user_documents(current_user.id)
    return docs


@router.get("/support")
def get_insurance_support(
    current_user: User = Depends(get_current_user),
):
    """Returns official support pathways and FAQ guidelines."""
    return {
        "faqs": [
            {
                "topic": "Coverage question",
                "question": "When does my IncomeShield coverage start?",
                "answer": "Coverage starts immediately upon confirmation. A 24-hour waiting period applies for new weather events.",
            },
            {
                "topic": "Payout question",
                "question": "How is my payout calculated?",
                "answer": "Parametric payouts are pre-fixed based on your plan's coverage limit and verified telemetry thresholds (e.g. >= 50mm rainfall in 3 hours).",
            },
            {
                "topic": "Policy question",
                "question": "Can I cancel or change my plan?",
                "answer": "IncomeShield runs on weekly renewals. You can switch plans or pause renewals at any time before the next billing cycle.",
            },
            {
                "topic": "Technical issue",
                "question": "What if weather telemetry in my zone was delayed?",
                "answer": "Telemetry evaluations sync every 15 minutes with IMD radar feeds. If delayed, retroactive settlements are automatically credited.",
            },
        ],
        "helpline": "1800-419-7443 (Toll-Free, 24/7)",
        "email": "incomeshield-support@levelly.in",
        "partner_contact": "SafeWork Claims Desk: claims@safework-shield.in",
        "coach_action": "/coach",
    }


# ============================================================
# 6. DEMO & SIMULATION ENDPOINTS (For testing end-to-end flows)
# ============================================================

@router.post("/demo/simulate-disruption")
def demo_simulate_disruption(
    request: SimulateDisruptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Demo helper: Spawns or updates a verified disruption event in Chennai."""
    from datetime import datetime, timezone, timedelta
    now = datetime.now(timezone.utc)
    event = InsuranceEvent(
        event_type=request.event_type,
        zone=request.zone,
        start_time=now - timedelta(hours=request.duration_hours),
        duration=f"{request.duration_hours}h 00m",
        source="IMD Chennai Radar Telemetry (Demo)",
        source_reference=f"DEMO-EVENT-{now.strftime('%H%M%S')}",
        verification_status="VERIFIED",
        severity=request.severity,
        telemetry_data={
            "observed_rainfall_mm": request.observed_rainfall_mm,
            "threshold_rainfall_mm": request.threshold_rainfall_mm,
            "duration_hours": request.duration_hours,
            "affected_subzones": ["Chennai South", "OMR-ECR", "Velachery", "Guindy"],
        },
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return {"message": "Simulated disruption event created", "event": event}


@router.post("/demo/evaluate-trigger")
def demo_evaluate_trigger(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Demo helper: Evaluates user's policy against an event and processes payout if reached."""
    ins_svc = InsuranceService(db)
    policy = ins_svc.get_user_policy(current_user.id)
    if not policy:
        raise HTTPException(status_code=400, detail="User must have an active policy to evaluate triggers")

    trigger_svc = InsuranceTriggerService(db)
    evaluation = trigger_svc.evaluate_policy_for_event(policy.id, event_id)
    return {"message": f"Trigger evaluated: {evaluation.status}", "evaluation": evaluation}


@router.post("/demo/complete-payout/{payout_id}")
def demo_complete_payout(
    payout_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Demo helper: Transitions payout from PROCESSING to COMPLETED."""
    svc = InsurancePayoutService(db)
    payout = svc.complete_payout(payout_id)
    return {"message": "Payout marked COMPLETED", "payout": _format_payout(payout)}
