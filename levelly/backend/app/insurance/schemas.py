"""
LEVELLY IncomeShield — Pydantic Schemas
Defines request and response contracts for insurance endpoints.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class InsurancePartnerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
    partner_type: str
    active: bool
    contact_info: Dict[str, Any] = {}


class InsurancePlanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
    description: str
    premium: float
    premium_frequency: str
    coverage_limit: float
    policy_duration: str
    covered_events: List[str]
    trigger_conditions: Dict[str, Any]
    waiting_period: str
    exclusions: List[str]
    coverage_area_rules: Dict[str, Any]
    active: bool
    partner_name: Optional[str] = None


class InsurancePurchaseRequest(BaseModel):
    plan_id: int
    terms_accepted: bool
    terms_version: str = "v1.0"
    work_zone: Optional[str] = "Chennai Delivery Zone"


class InsuranceDocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    document_type: str
    file_url: str
    created_at: datetime


class InsurancePolicyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    plan_id: int
    plan_name: str
    partner_name: Optional[str] = None
    policy_number: str
    status: str
    start_date: datetime
    end_date: datetime
    premium: float
    coverage_limit: float
    covered_work_zone: str
    created_at: datetime
    documents: List[InsuranceDocumentOut] = []


class InsuranceEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    zone: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: str
    source: str
    source_reference: Optional[str] = None
    verification_status: str
    severity: str
    telemetry_data: Dict[str, Any] = {}
    created_at: datetime


class InsuranceIncomeImpactOut(BaseModel):
    user_id: int
    event_id: Optional[int] = None
    event_type: str
    zone: str
    expected_daily_income: float
    typical_weekly_income: float
    estimated_disrupted_income: float
    estimated_income_impact: float
    volatility_level: str
    trend: str
    disclaimer: str = (
        "This estimate is based on your earning history. Your actual insurance payout "
        "depends on your policy terms and the insurance partner's determination."
    )


class InsuranceTriggerEvaluationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    policy_id: int
    event_id: int
    trigger_type: str
    threshold: str
    observed_value: str
    required_value: str
    status: str  # NOT_REACHED, REACHED, INVALID, PENDING
    evaluated_at: datetime
    reason: str


class InsurancePayoutOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    policy_id: int
    event_id: Optional[int] = None
    payout_id_from_partner: Optional[str] = None
    amount: Optional[float] = None
    currency: str = "INR"
    status: str  # PENDING, PROCESSING, COMPLETED, FAILED, REJECTED
    reason: str
    processed_at: Optional[datetime] = None
    destination_reference: Optional[str] = None
    destination_type: str
    created_at: datetime
    amount_display: str


class InsurancePayoutMoveRequest(BaseModel):
    amount: float


class InsuranceSelectPlanRequest(BaseModel):
    plan_id: int


class InsurancePersonalizedImpactOut(BaseModel):
    user_id: int
    plan_id: int
    plan_name: str
    plan_code: str
    premium: float
    premium_frequency: str
    coverage_limit: float
    expected_daily_income: float
    typical_weekly_income: float
    estimated_disrupted_income: float
    estimated_income_impact: float
    volatility_level: str
    trend: str
    work_zone: str
    example_event: Dict[str, Any]
    disclaimer: str
    impact_label: str = "ESTIMATED INCOME IMPACT"


class InsuranceStatusOut(BaseModel):
    has_active_policy: bool
    insurance_state: str = "NO_POLICY"  # NO_POLICY, PLAN_SELECTED, PURCHASE_REVIEW, PURCHASE_PENDING, ACTIVE, EXPIRED
    selected_plan_id: Optional[int] = None
    policy: Optional[InsurancePolicyOut] = None
    active_events: List[InsuranceEventOut] = []
    latest_payout: Optional[InsurancePayoutOut] = None
    safety_wallet_balance: float
    safety_wallet_target: float
    safety_wallet_shortfall: float
    resilience_score: int
    average_daily_income: float
    average_weekly_income: float


class SimulateDisruptionRequest(BaseModel):
    event_type: str = "HEAVY_RAIN"
    zone: str = "Chennai Delivery Zone"
    severity: str = "SEVERE"
    observed_rainfall_mm: float = 65.0
    threshold_rainfall_mm: float = 50.0
    duration_hours: int = 3
